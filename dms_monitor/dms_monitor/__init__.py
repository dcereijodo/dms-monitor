import botocore
import boto3
import logging
import sys
import json

logging.basicConfig(stream=sys.stdout)

class DMSWaiter:

    def __init__(self, dms_client, arn, polling_configuration={'delay': 15, 'maxAttempts': 40}):
        self.logger = logging.getLogger('dms_monitor')
        self.logger.setLevel(logging.INFO)

        self.dms_client = dms_client
        self.arn = arn

        # maximum number of attempt for the task to get into a running state is hardcoded for now
        # we should not need more configurability for this
        running_waiter_model = botocore.waiter.WaiterModel({
            "version": 2,
            "waiters": {
                "DMSReplicationTaskRunning": {
                    "delay": 5,
                    "operation": "DescribeReplicationTasks",
                    "maxAttempts": 2,
                    "acceptors": [
                        {
                            "expected": True,
                            "matcher": "path",
                            "state": "success",
                            "argument": f"ReplicationTasks[?ReplicationTaskArn=='{arn}'].Status | [0] != 'stopped'"
                        }
                    ]
                }
            }
        })

        # for the task to get into a finished status, the timeout and polling interval should be configurable
        stopped_waiter_model = botocore.waiter.WaiterModel({
            "version": 2,
            "waiters": {
                "DMSReplicationTaskFinished": {
                    "delay": polling_configuration['delay'],
                    "operation": "DescribeReplicationTasks",
                    "maxAttempts": polling_configuration['maxAttempts'],
                    "acceptors": [
                        {
                            "expected": True,
                            "matcher": "path",
                            "state": "success",
                            "argument": f"ReplicationTasks[?ReplicationTaskArn=='{arn}'].Status | [0] == 'stopped'"
                        }
                    ]
                }
            }
        })

        self.running = botocore.waiter.create_waiter_with_client(
            'DMSReplicationTaskRunning',
            running_waiter_model,
            dms_client
        )
        self.finished = botocore.waiter.create_waiter_with_client(
            'DMSReplicationTaskFinished',
            stopped_waiter_model,
            dms_client
        )

    def get_replication_task_description(self):
        response = self.dms_client.describe_replication_tasks(
            Filters=[{'Name': 'replication-task-arn', 'Values': [self.arn]}]
        )
        if len(response['ReplicationTasks']) == 0:
            raise Exception(f"No running task found for ARN {self.arn}")
        else:
            return response['ReplicationTasks'][0]

    def start_and_wait_until_running(self):
        started_response = self.dms_client.start_replication_task(
            ReplicationTaskArn=self.arn,
            StartReplicationTaskType='resume-processing'
        )
        self.running.wait()

    def check_running_and_wait_until_finished(self):
        status = self.get_replication_task_description()['Status']
        if status != 'starting':
            raise Exception(f"Replication task status is not running ({status})")
        else:
            self.finished.wait()

    def start_task_and_wait_for_completion(self) -> int:
        self.logger.info(f"Starting replication task {self.arn}")
        self.start_and_wait_until_running()
        self.logger.info(f"Replication task {self.arn} has started waiting for completion")
        self.check_running_and_wait_until_finished()

        terminal_task_description = self.get_replication_task_description()
        stop_reason = terminal_task_description['StopReason']
        if stop_reason == 'Stop Reason FULL_LOAD_ONLY_FINISHED':
            self.logger.info(f"Replication task {self.arn} has finished successfully")
            return 0
        else:
            self.logger.error(f"Replication task {self.arn} has failed: {stop_reason}")
            self.logger.debug(f"Terminal replication task description: {json.dumps(terminal_task_description)}")
            return 1
