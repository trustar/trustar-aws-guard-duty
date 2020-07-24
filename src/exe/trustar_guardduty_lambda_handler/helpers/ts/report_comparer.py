# encoding = utf-8

""" ReportComparer class definition. """

from logging import getLogger

from .time_converter import TimeConverter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Tuple
    from logging import Logger
    from trustar import Report

logger = getLogger(__name__)                                    # type: Logger

class ReportComparer:
    """ Compares 2 TruStar Report objects and error-logs differences. """

    @classmethod
    def compare(cls, upserted,                          # type: Report
                from_enclave,                           # type: Report
                vars_to_ignore                          # type: Tuple
                ):                                      # type: (...) -> bool
        """ Compares the report in the enclave to the upserted report
        and logs any discrepancies. """
        logger.info("Comparing reports.")
        vars_ = [v for v in vars(from_enclave) if v not in vars_to_ignore]
        are_reports_equal = True
        for v in vars_:
            enclave_val = getattr(from_enclave, v)
            upserted_val = getattr(upserted, v)
            if v == 'time_began':
                are_reports_equal = cls.compare_time_begans(
                    upserted_val, enclave_val)                    # type: bool
            elif not enclave_val == upserted_val:
                msg = ("For instance-var '{}', upserted:  '{}', " 
                       "found in enclave:  '{}'."
                       .format(v, upserted_val, enclave_val))
                logger.error(msg)
                are_reports_equal = False
        logger.info("Done comparing reports.")
        if are_reports_equal:
            logger.info("Reports have differences.")
        else:
            logger.info("Reports are same.")
        return are_reports_equal

    @staticmethod
    def compare_time_begans(upserted_iso,                          # type: str
                            ms_from_enclave                        # type: int
                            ):                           # type: (...) -> bool
        """
        :param upserted_iso: string isoformat timestamp
        (ex:  2017-10-31T23:16:23+00:00) created by passing the
        guard-duty timestamp (2017-10-31T23:16:23Z) through the
        normalize_timestamp() function in the TruSTAR SDK.  This is
        what's expected to be passed into the "submit-report" and
        "update-report" endpoints.

        :param ms_from_enclave:  int, milliseconds timestamp found in
        the time_began attr of the Report object generated by the
        "get_report_details" method.

        :return: T/F whether time_begans are equal.
        """
        dt_upserted = TimeConverter.iso_to_dt(upserted_iso)
        dt_from_enclave = TimeConverter.ms_to_dt_utc(ms_from_enclave)
        if dt_upserted == dt_from_enclave:
            return True

        millis_upserted = TimeConverter.iso_to_ms(upserted_iso)
        iso_enclave = TimeConverter.ms_to_iso_utc(ms_from_enclave)
        msg = ("time_began upserted: '{}' (mills: {}).  time_began " 
               "stored in enclave: {} (ISO str: '{}')."
               .format(upserted_iso, millis_upserted,
                       ms_from_enclave, iso_enclave))
        logger.error(msg)
        return False
