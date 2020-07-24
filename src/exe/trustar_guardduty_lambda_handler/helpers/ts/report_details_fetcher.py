# encoding = utf-8

""" RepoortDetailsFetcher class definition. """

import time
from logging import getLogger

from trustar import IdType

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from logging import Logger
    from trustar import Report, TruStar

logger = getLogger(__name__)                                    # type: Logger

class ReportDetailsFetcher:
    """ A class for fetching report details. """

    def __init__(self, ts):                          # type: (TruStar) -> None
        self.ts = ts                                 # type: TruStar

    def fetch_for(self, external_id):          # type: (str) -> Report or None
        """ Fetch a report's details from TruStar. """
        logger.info("Fetching report saved in TruSTAR.")
        attempt = 0
        max_n_attempts = 10
        while attempt <= max_n_attempts:
            attempt += 1
            time.sleep(2)
            # noinspection PyUnusedLocal
            r = None                                   # type:  Report or None
            # noinspection PyBroadException
            try:
                r = self.ts.get_report_details(
                    external_id, id_type=IdType.EXTERNAL)
                logger.info("successfully fetched report.")
                return r
            except:
                logger.error("Failed attempt '{}' fetching report with ext "
                             "ID '{}'."
                             .format(attempt, external_id))
        logger.info("Done attempting to fetch report.  Failed.")
        return None
