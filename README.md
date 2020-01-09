# DMS Monitor
Start AWS Database Migration Service (DMS) tasks and wait for completion.


# Installation and testing
Install the tool as CLI command with PIP.
## Installation
* From source
```bash
# checkout code and 'cd' to the project folder then
$ pip install -e .
```
* From a stable github release
```console
$ pip install -e git://github.com/dcereijodo/dms-monitor.git@<tag>#egg=dms-monitor
```
## Testing
Testing uses the `pytest` framework and boto3 request stubbing for mocking the
calls to AWS.
```console
pytest
```

# TL;DR
```bash
# get the available options from help
$ dms-monitor --help
# start a replication task and monitor completion
$ dms-monitor --polling-delay 5 --polling-max-attempts 5 arn:aws:dms:eu-west-1:XXXXXX:task:XXXXXXXXX
```
