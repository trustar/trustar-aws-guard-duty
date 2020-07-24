# encoding = utf-8

""" TruSTAR's Guard Duty Finding Lambda Handler. """

from logging import getLogger
import os

from .helpers.gd.report_builder import GuardDutyReportBuilder
from .helpers.ts.enclave_permissions_checker import EnclavePermissionsChecker
from .helpers.ts.report_upserter import ReportUpserter
from .helpers.ts.client_builder import ClientBuilder
from .helpers.ts.report_comparer import ReportComparer
from .helpers.ts.report_details_fetcher import ReportDetailsFetcher

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from logging import Logger
    from trustar import Report, TruStar

logger = getLogger(__name__)                                    # type: Logger


class TruStarGuardDutyLambdaHandler:
    """ The Lambda function handler for Guard Duty events. """

    CLIENT_METATAG = "AWS_GUARD_DUTY"
    VARS_TO_SKIP = ("created", "updated", "id")

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
        self.details_fetcher = ReportDetailsFetcher(ts)
        self.ts = ts

    def handle(self, event):                            # type: (Dict) -> Dict
        """ Processes a Guard-duty event. """
        logger.info("starting lambda handler.")
        report = self.builder.build_for(event)                  # type: Report
        upserted = self.upserter.upsert(report)                 # type: Report
        if not self.check_saved_report:
            logger.info("lambda handler complete. returning upserted.")
            return upserted.to_dict()

        saved = self.details_fetcher.fetch_for(
            upserted.external_id)                       # type: Report or None
        if not saved:
            logger.error("Failed to fetch saved report from Station. "
                         "Ending lambda, returning the upserted report.")
            return upserted.to_dict()

        _ = ReportComparer.compare(upserted, saved, self.VARS_TO_SKIP)
        logger.info("lambda handler complete. returning report from "
                    "enclave.")
        return saved.to_dict()

    @property
    def check_saved_report(self):                           # type: () -> bool
        """ Determines whether the user specified to check the report saved
        in Station against the report it upserted. """
        check = False
        env_var = os.environ.get("RETURN_SAVED_REPORT")
        if isinstance(env_var, str):
            check = env_var == "True"
        elif isinstance(env_var, bool):
            check = env_var
        if check:
            logger.info("user wants saved report checked.")
        else:
            logger.info("user does not want saved report checked.")
        return check
