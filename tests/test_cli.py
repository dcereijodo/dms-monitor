import pytest
from click.testing import CliRunner
from dms_monitor.dms_monitor import DMSWaiter
import botocore
from botocore.stub import Stubber
from tests import assert_duration

arn = 'it-doesnt-matter-as-we-are-faking-the-calls'

def create_client_with_stubbed_calls(calls):
    stubbed_dms_client = botocore.session.get_session().create_client('dms')
    stubber = Stubber(stubbed_dms_client)
    for call in calls:
        stubber.add_response(
            call['method'],
            call['response']
        )
    stubber.activate()
    return stubbed_dms_client

def test_running_waiter():

    stubbed_dms_client = create_client_with_stubbed_calls(
        [
            {'method': 'start_replication_task', 'response': {}},
            {'method': 'describe_replication_tasks', 'response': {'ReplicationTasks': [{'ReplicationTaskArn': arn, 'Status': 'stopped'}]}},
            {'method': 'describe_replication_tasks', 'response': {'ReplicationTasks': [{'ReplicationTaskArn': arn, 'Status': 'starting'}]}},
        ]
    )

    monitor = DMSWaiter(
        dms_client=stubbed_dms_client,
        arn=arn,
        polling_configuration={
            'delay': 15,
            'maxAttempts': 2
        }
    )

    assert_duration(monitor.start_and_wait_until_running, 5, 15)

def test_finished_waiter():

    stubbed_dms_client = create_client_with_stubbed_calls(
        [
            {'method': 'describe_replication_tasks', 'response': {'ReplicationTasks': [{'ReplicationTaskArn': arn, 'Status': 'starting'}]}},
            {'method': 'describe_replication_tasks', 'response': {'ReplicationTasks': [{'ReplicationTaskArn': arn, 'Status': 'running'}]}},
            {'method': 'describe_replication_tasks', 'response': {'ReplicationTasks': [{'ReplicationTaskArn': arn, 'Status': 'stopped'}]}},
        ]
    )

    monitor = DMSWaiter(
        dms_client=stubbed_dms_client,
        arn=arn,
        polling_configuration={
            'delay': 5,
            'maxAttempts': 2
        }
    )

    assert_duration(monitor.check_running_and_wait_until_finished, 5, 10)

def test_error_conditions():

    stubbed_dms_client_for_inexistent_arn = create_client_with_stubbed_calls(
        [
            {'method': 'describe_replication_tasks', 'response': {'ReplicationTasks': []}}
        ]
    )
    stubbed_dms_client_for_stopped_task = create_client_with_stubbed_calls(
        [
            {'method': 'describe_replication_tasks', 'response': {'ReplicationTasks': [{'ReplicationTaskArn': arn, 'Status': 'stopped'}]}}
        ]
    )

    monitor_inexistent = DMSWaiter(
        dms_client=stubbed_dms_client_for_inexistent_arn,
        arn=arn
    )
    monitor_stopped = DMSWaiter(
        dms_client=stubbed_dms_client_for_stopped_task,
        arn=arn
    )

    with pytest.raises(Exception) as e:
        assert_duration(monitor_inexistent.check_running_and_wait_until_finished, 15, 16)

    assert f"No running task found for ARN {arn}" in str(e.value)

    with pytest.raises(Exception) as e:
        assert_duration(monitor_stopped.check_running_and_wait_until_finished, 15, 16)

    assert f"Replication task status is not running (stopped)" in str(e.value)
