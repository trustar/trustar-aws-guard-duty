# encoding = utf-8

""" A script that receives a Guard Duty "Finding" and submits it to an
enclave as a Report.

- Intended to be used with AWS Lambda.

To deploy:

  pip install --target=. trustar
  zip -r ../GD-Station-Lambda.zip ./*

  .. then upload the resulting zip file to the Lambda function.
  You'll also need to set the following environment variables in the function:
  - TRUSTAR_URL
  - API_KEY
  - API_SECRET
  - ENCLAVE_ID

The associated API credential will need to have write access to the enclave
defined in the `ENCLAVE_ID` variable. """

from trustar_guardduty_lambda_handler.ts_gd_lambda_handler import TruStarGuardDutyLambdaHandler

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from trustar import Report

def lambda_handler(event, context):               # type: (Dict, Dict) -> Dict
    """ Sends Finding to Station. """
    r = TruStarGuardDutyLambdaHandler.handle(event, context)    # type: Report
    return r.to_dict()