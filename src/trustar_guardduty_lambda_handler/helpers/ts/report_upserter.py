# encoding = utf-8

""" Upserts TruSTAR Report objects. """

import json
from logging import getLogger
from trustar import TruStar, IdType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from logging import Logger
    from trustar import Report

logger = getLogger(__name__)                                    # type: Logger

class ReportUpserter:
    """ Upserts Reports to Station. """

    def __init__(self, ts,                                  # type: TruStar
                 enclave_id,                                # type: str
                 exc_if_rpt_encls_diff=True                 # type: bool
                 ):
        if ts.enclave_ids:
            msg = self.msg_dont_use_ts_client_encl_ids()
            raise Exception(msg)

        self.ts = ts                                        # type: TruStar
        self.enclave_id = enclave_id                        # type: str
        self.exc_if_encls_diff = exc_if_rpt_encls_diff      # type: bool

    def upsert(self, report):                       # type: (Report) -> Report
        """ Upserts report, returns True if success, False if fail. """
        logger.info("Starting upsert for report with external ID '{}'."
                    .format(report.external_id))

        logger.info("TimeBegan:  {}".format(report.time_began))
        logger.info("TimeBegan type: '{}'.".format(str(type(report.time_began))))



        if not report.enclave_ids:
            report.enclave_ids = [self.enclave_id]

        if not self.eq_upserter_enclaves(report.enclave_ids):
            msg = self.msg_new_rpt_encls_dont_match(report)
            self.handle_enclaves_mismatch(msg)

        existing_report = self.fetch_existing_report(
            report.external_id)                         # type: Report or None

        if existing_report:

            if not self.eq_upserter_enclaves(existing_report.enclave_ids):
                msg = self.msg_existing_rpt_encls_dont_match(existing_report)
                self.handle_enclaves_mismatch(msg)

            r = self.update_report(existing_report=existing_report,
                                   gd_report=report)            # type: Report
        else:
            r = self.submit_report(report)                      # type: Report

        logger.info("Upsert operation complete.")
        return r

    def eq_upserter_enclaves(self, report_enclave_ids    # type: List[str]
                             ):                          # type: (...) -> bool
        """ Compares a report's list of enclave IDs to the upserter's
        enclave_id. """
        return set(report_enclave_ids) == set([self.enclave_id])

    def handle_enclaves_mismatch(self, msg):
        """ Logs an error message and raises an exception with it if the
        upserter is configured to do so. """
        logger.error(msg)
        if self.exc_if_encls_diff:
            raise Exception(msg)

    def fetch_existing_report(self, external_id                    # type: str
                              ):               # type: (...) -> Report or None
        """ Returns the existing report or None. """
        # TODO:  This assumes that the only reason for failure is that
        #  the report doesn't exist.  Could also fail because Station
        #  is down.  Add code that handles those two cases differently.

        existing_report = None
        try:
            existing_report = self.ts.get_report_details(
                external_id, id_type=IdType.EXTERNAL)
            logger.info("Report with external ID '{}' exists in destination "
                        "enclave.".format(external_id))
        except:
            logger.info("No report found in destination enclave with "
                        "external ID '{}'.".format(external_id))
        return existing_report

    def update_report(self, existing_report,           # type: Report
                      gd_report                        # type: Report
                      ):                               # type: (...) -> Report
        """ Updates the existing report in Station. """

        # overwrite the existing report with the gd_report's values so you
        # preserve the existing report's values for other attrs that are
        # not pertinent here but might have values in Station.
        # If we don't do this, Station overwrites existing attribute values
        # with null.
        new_report = existing_report
        new_report.title = gd_report.title
        new_report.time_began = gd_report.time_began
        new_report.external_url = gd_report.external_url
        new_report.external_id = gd_report.external_id
        new_report.body = gd_report.body

        try:
            logger.info("Submitting report \n{}"
                        .format(json.dumps(new_report.to_dict(), indent=4)))
            updated_report = self.ts.update_report(new_report)
            logger.info("Updated report with ID '{}', external ID '{}', "
                        "title '{}'.".format(updated_report.id,
                                             updated_report.external_id,
                                             updated_report.title))

        except Exception as e:
            logger.error("Failed to update report with ID '{}', external ID "
                         "'{}', title '{}'."
                         .format(existing_report.id,
                                 existing_report.external_id,
                                 existing_report.title))
            raise e
        return updated_report

    def submit_report(self, report):                # type: (Report) -> Report
        """ Submits the report, log error & throw exception if fail."""
        try:
            submitted_report = self.ts.submit_report(report)  # type: Report
            logger.info("Submitted report with ID '{}', external ID '{}', "
                        "title '{}'.".format(submitted_report.id,
                                             submitted_report.external_id,
                                             submitted_report.title))
        except Exception as e:
            logger.error(("Failed to submit report with external ID '{}', "
                          "title '{}'.".format(report.external_id,
                                               report.title)))
            raise e
        return submitted_report

    def msg_dont_use_ts_client_encl_ids(self):  # type: () -> str
        msg = ("Do not specify the TruStar client's  'enclave_ids' "
               "attribute when using the '{}' class.  This can lead to "
               "confusion regarding which enclave(s) the Upserter's "
               "reports will be upserted to."
               .format(self.__class__.__name__))
        return msg

    @staticmethod
    def msg_new_rpt_encls_dont_match(report):  # type: (Report) -> str
        """ Returns a message to be used for logging / exception. """
        msg = ("Report object's enclave_ids do not match the "
               "up-serter's enclave_ids.  Not going to submit this "
               "report.  Report:  \n'{}'"
               .format(json.dumps(report.to_dict(), indent=4)))
        return msg

    @staticmethod
    def msg_existing_rpt_encls_dont_match(report):  # type: (Report) -> str
        msg = ("Upserter found an existing report with external ID "
               "'{}' that lives in enclaves '{}'.  These enclaves do "
               "not match the enclave the upserter is supposed to "
               "upsert to.  Upserter is not going to submit or "
               "update this report to any enclaves.  Report: \n '{}'"
               .format(report.external_id,
                       str(report.enclave_ids),
                       json.dumps(report.to_dict(), indent=4)))
        return msg