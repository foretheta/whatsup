# Whatsup -- A frugal serverless up/down monitor

## Purpose

This is a simple serverless up/down monitor that runs every 5 minutes and sends you an alert in Slack if your website is down (or goes from down->up).

I wanted to see if I could use AWS SSM Parameter Store as a free key-value DB. Nothing as brazen as [@QuinnyPig's route53 database](https://twitter.com/QuinnyPig/status/1120653859561459712), but still interesting:

* Use AWS Chalice to define a scheduled AWS Lambda job that runs every 5 minutes.
* Uses SSM Parameter Store as a database to store the last known status of each endpoint.

That's it!

## Prerequisites

- You must have an AWS account, and have your default credentials and AWS Region
  configured as described in the [AWS Tools and SDKs Shared Configuration and
  Credentials Reference Guide](https://docs.aws.amazon.com/credref/latest/refdocs/creds-config-files.html).
- Python 3.7 or later
- Boto3 1.14.20 or later
- AWS Chalice 1.15.1 or later
- Requests 2.23.0 or later
- PyTest 5.3.5 or later (to run unit tests)
- Access to [AWS SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html).

## Cautions

- As an AWS best practice, grant this code least privilege, or only the 
  permissions required to perform a task. For more information, see 
  [Grant Least Privilege](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege) 
  in the *AWS Identity and Access Management 
  User Guide*.
- This is an early version and has not been tested very thoroughly.
- Running this code might result in charges to your AWS account.

## Running the code

1. Clone the whatsup repository, initialize a virtual env, and install prerequisite packages.

    ```
    git clone https://github.com/foretheta/whatsup.git
    cd whatsup
    python3 -m venv
    source venv/bin/activate
    pip install -r requirements
    ```

1. Make a copy of the `sample_confg.yaml` file and edit to add the endpoints you want to monitor. Add your Slack webhook for notifications.

    ```
    cp sample_config.yaml config.yaml && vim config.yaml
    ```

1. Deploy the app to your AWS account.

    ```
    whatsup deploy
    ```


### Example structure

The example is divided into the following files:

**app.py**

Defines the scheduled function to monitor your endpoints.. Uses Chalice to decorate scheduled functions and
handle associated actions. Stores data in AWS SSM Parameter Store.

**requirements.txt**

Defines the minimum package versions to deploy to AWS Lambda.

**config.json**

Configuration for the application. It has a list of endpoints you want to monitor and provide the Slack webhook that will send a simple up/down notication to the channel associated with the webhook.

## Running the tests (coming soon)

The unit tests in this module use the moto AWS Services mocker. This captures requests before 
they are sent to AWS, and returns a mocked response. 
```    
python -m pytest
```

## Additional information

- [AWS Chalice Quickstart](https://aws.github.io/chalice/quickstart.html)
- [Boto3 AWS Lambda service reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html)
- [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)

---
Copyright Foretheta, Inc. All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
