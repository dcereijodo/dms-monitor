import click
import botocore
import boto3
import logging
from dms_monitor import DMSWaiter


@click.command()
@click.argument('replication_task_arn')
@click.option('--polling-delay', default=15)
@click.option('--polling-max-attempts', default=40)
def dms_monitor(replication_task_arn, polling_delay, polling_max_attempts):
    """Start AWS Database Migration Service (DMS) tasks and waits for completion."""

    client = boto3.client('dms')
    monitor = DMSWaiter(
        dms_client=client,
        arn=replication_task_arn,
        polling_configuration={
            'delay': polling_delay,
            'maxAttempts': polling_max_attempts
        }
    )

    return monitor.start_task_and_wait_for_completion()

if __name__ == '__main__':
    dms_monitor()
