# A script to receive Threat Findings from AWS GuardDuty, and
# insert them into TruSTAR Station.
#
# This script is meant to be used with AWS Lambda.
#
# To deploy:
#  cd trustar-utilities/scripts/GD-Station-Lambda
#  pip install --target=. trustar==0.2.4
#  zip -r ../GD-Station-Lambda.zip ./*
#
# .. then upload the resulting zip file to the Lambda function.
# You'll also need to set the following environment variables in the function:
#  - TRUSTAR_URL
#  - API_KEY
#  - API_SECRET
#  - ENCLAVE_ID
#
# The associated API credential will need to have write access to the enclave
# defined in the `enclave_ids` variable below.


import json
from ts_client import *

# Authenticate into Station
config = {
    'user_api_key': os.environ['API_KEY'],
    'user_api_secret': os.environ['API_SECRET'],
    'enclave_ids': os.environ['ENCLAVE_ID'],
    'api_endpoint': os.environ['TRUSTAR_URL'] + '/api/1.2',
    'auth_endpoint': os.environ['TRUSTAR_URL'] + '/oauth/token'
}

conf_dir = "/tmp"  # tmp directory to store configuration file
ts_client = TSClient(config, conf_dir)  # TSClient object


def lambda_handler(event, context):
    # Report the Finding to Station
    """

    :param event: Event data
    :param context: context
    :return:
    """

    # Convert event to json object
    event_json = json.loads(json.dumps(event))

    # Assemble a report from the event, excluding information about the AWS resource
    report_body = {}
    for column in ['title', 'description', 'severity', 'createdAt', 'updatedAt', 'service']:
        # Using get() allows for specifying keys that may not exist
        report_body[column] = event_json.get('detail').get(column, '')

    try:
        report = dict()
        report["tags"] = ['AWS', 'GuardDuty']  # Tag(s) to add to every Finding reported to Station:
        report["title"] = u'[AWS GD] {}'.format(report_body['title'])
        report['time_began'] = event['detail']['service']['eventFirstSeen']
        report['external_url'] = u'{}'.format(event['detail']['arn'])
        report['distribution_type'] = "ENCLAVE"
        report['externalTrackingId'] = u'{}'.format(event['detail']['id'])
        report['report_body'] = json.dumps(report_body, indent=4, sort_keys=True)
        log_msg = u"Report: '{}' with ReportID: '{}'".format(report['title'], report['externalTrackingId'])
        logger.debug("log_msg :::::::: {}".format(log_msg))

        try:
            # Get access token
            ts_client.get_token()
        except TSTokenError as token_error:
            err_msg = "{} Got Error: '{}'".format(log_msg, token_error)
            logger.exception(err_msg)

        # Send Report to Trustar
        try:
            ts_client.send_report(report=report, update_report="replace")

        except TSSystemError as system_error:
            logger.exception("%s Got Error: '%s'", log_msg, system_error)
        except TSLargeReportError as large_report_error:
            logger.exception("%s Got Error: '%s'", log_msg, large_report_error)

        # Submit tags to TruSTAR
        try:
            ts_client.get_token()
            ts_client.add_enclave_tags(report)
            print "Reports submitted successfully"
        except TSSystemError as e:
            logger.exception("TSSystemError Submit Tag report: {}".format(str(e)))
    except Exception as exe:
        logger.exception("Got Error: '%s'", exe.message)
