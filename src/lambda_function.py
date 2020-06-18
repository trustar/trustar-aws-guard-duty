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

import json
import logging
import os
from trustar import TruStar, Report
from .helpers.ts_client_builder import TruStarClientBuilder
from .helpers.ts_report_upserter import TruStarReportUpserter
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *

logger = logging.getLogger(__name__)


def lambda_handler(event, context):  # type: (Dict, Dict) -> None
    """ Sends Finding to Station. """

    logger.info("starting lambda handler.")

    gd_report = GuardDutyReportBuilder.build_for(event)        # type: Report
    ts = TruStarClientBuilder.from_env_vars(
        client_metatag="AWS_GUARD_DUTY")                       # type: TruStar
    upserter = TruStarReportUpserter(ts, [os.environ['ENCLAVE_ID']])
    _ = upserter.upsert(gd_report)

    logger.info("lambda handler complete.")


class GuardDutyReportBuilder:
    """ Builds TruSTAR report from Guard Duty Finding event. """

    GD_FINDING_DETAIL_KEYS = ['title', 'description', 'severity',
                              'createdAt', 'updatedAt', 'service']

    @classmethod
    def build_for(cls, finding):                    # type: (Dict) -> Report
        """ Builds a Report for an event. """
        report_body = {}
        detail = finding.get('detail')
        for key in cls.GD_FINDING_DETAIL_KEYS:
            report_body[key] = detail.get(key, '')

        r = Report(title=report_body['title'],
                   time_began=detail['service']['eventFirstSeen'],
                   external_url=detail['arn'],
                   external_id=detail['id'],
                   body=json.dumps(report_body, indent=4, sort_keys=True))
        return r
