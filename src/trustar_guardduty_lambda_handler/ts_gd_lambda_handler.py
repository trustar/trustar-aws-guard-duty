# encoding = utf-8

""" TruSTAR's Guard Duty Finding Lambda Handler. """

import os
from logging import getLogger
from .helpers.gd.report_builder import GuardDutyReportBuilder
from .helpers.ts.enclave_permissions_checker import EnclavePermissionsChecker
from .helpers.ts.report_upserter import ReportUpserter
from .helpers.ts.client_builder import ClientBuilder

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from logging import Logger
    from trustar import Report, TruStar

logger = getLogger(__name__)                                    # type: Logger


class TruStarGuardDutyLambdaHandler:
    """ The Lambda function handler for Guard Duty events. """

    CLIENT_METATAG = "AWS_GUARD_DUTY"

    def __init__(self):
        logger.info("Initializing lambda handler.")
        destination_enclave = os.environ['ENCLAVE_ID']             # type: str
        ts = ClientBuilder.from_env_vars(
            client_metatag=self.CLIENT_METATAG)                # type: TruStar

        permissions_checker = EnclavePermissionsChecker(ts)
        if not permissions_checker.can_create(destination_enclave):
            raise Exception("TruSTAR API creds do not have permissions to "
                            "write to enclave '{}'."
                            .format(destination_enclave))

        self.builder = GuardDutyReportBuilder(destination_enclave)
        self.upserter = ReportUpserter(ts, destination_enclave)

    def handle(self, event):                            # type: (Dict) -> Dict
        """ Processes a Guard-duty event. """
        logger.info("starting lambda handler.")
        report = self.builder.build_for(event)                  # type: Report
        upserted_report = self.upserter.upsert(report)          # type: Report
        logger.info("lambda handler complete.")
        return upserted_report.to_dict()