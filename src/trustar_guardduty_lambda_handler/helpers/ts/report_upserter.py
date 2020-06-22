# encoding = utf-8

""" Upserts TruSTAR Report objects. """

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
                 enclave_ids                                # type: List[str]
                 ):
        self.ts = ts                                        # type: TruStar
        self.enclave_ids = enclave_ids                      # type: List[str]

    def upsert(self, report):                       # type: (Report) -> Report
        """ Upserts report, returns True if success, False if fail. """
        logger.info("Starting upsert for report with external ID '{}'."
                    .format(report.external_id))

        if report.enclave_ids:
            if set(report.enclave_ids) != set(self.enclave_ids):
                raise Exception("Report object's enclave_ids do not match "
                                "the up-serter's enclave_ids.  Fix this.")
        else:
            report.enclave_ids = self.enclave_ids

        existing_report = None                          # type: None or Report
        try:
            existing_report = self.ts.get_report_details(
                report.external_id, id_type=IdType.EXTERNAL)
            logger.info("Report with external ID '{}' exists in destination "
                        "enclave.".format(report.external_id))
        except:
            logger.info("No report found in destination enclave with "
                        "external ID '{}'.".format(report.external_id))

        if existing_report:
            r = self.update_report(existing_report, report)     # type: Report
        else:
            r = self.submit_report(report)                      # type: Report

        logger.info("Upsert operation complete.")
        return r

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