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

    @staticmethod
    def handle(event, context):                  # type: (Dict, Any) -> Report
        """ """
        destination_enclave = os.environ['ENCLAVE_ID']

        logger.info("starting lambda handler.")

        gd_report = GuardDutyReportBuilder.build_for(event)     # type: Report

        ts = ClientBuilder.from_env_vars(
            client_metatag="AWS_GUARD_DUTY")                   # type: TruStar

        permissions_checker = EnclavePermissionsChecker(ts)
        if not permissions_checker.can_create(destination_enclave):
            raise Exception("TruSTAR API creds do not have permissions to "
                            "write to enclave '{}'."
                            .format(destination_enclave))

        upserter = ReportUpserter(ts, [destination_enclave])
        upserted_report = upserter.upsert(gd_report)            # type: Report

        logger.info("lambda handler complete.")

        return upserted_report