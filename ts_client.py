import os
import configparser
import logging
from trustar import TruStar
from ts_exception import *

logger = logging.getLogger(__name__)


class TSClient(object):
    """Wrapper for TruSTAR SDK

    :ivar config: dict containing TruSTAR api config
    :ivar config_file: path to config file for TruSTAR api
    :ivar config_role: section name in the config file
    :ivar ts_handle: TruSTAR SDK Handle
    :ivar token: TruSTAR SDK API token

    """

    def __init__(self, config, dirpath="."):
        """ Init TruSTAR client

        :param config: dict with TruSTAR sdk config
        :param dirpath: dir where TruSTAR config file must be saved

        """
        self.config = config
        self.config_file = os.path.join(dirpath, "ts_api.config")
        self.config_role = "trustar"
        self.create_config_file()
        self.ts_handle = TruStar(config_file=self.config_file,
                                 config_role=self.config_role)
        self.token = None

    def create_config_file(self):
        """Creates TruSTAR sdk config file

        """
        config_parser = configparser.RawConfigParser()
        config = self.config
        section = self.config_role
        config_parser.add_section(section)
        config_parser.set(section,
                          'auth_endpoint',
                          config.get('auth_endpoint', ""))
        config_parser.set(section,
                          'api_endpoint',
                          config.get('api_endpoint', ""))
        config_parser.set(section,
                          'user_api_key',
                          config.get('user_api_key', ""))
        config_parser.set(section,
                          'user_api_secret',
                          config.get('user_api_secret', ""))
        enclave_ids = config.get('enclave_ids', "")
        config_parser.set(section, 'enclave_ids', enclave_ids)
        with open(self.config_file, 'w') as fp:
            config_parser.write(fp)

    def get_token(self):
        """Get token for TruSTAR API

        """
        try:
            self.token = self.ts_handle.get_token()
        except Exception as e:
            logger.warn("Failed to get token", exc_info=True)
            raise TSTokenError(e)

    def get_report(self, external_id):
        """Check if report with external id is present in TruSTAR API

        :param external_id: Report External ID
        :return: dict containing report details
        :raise: Any SDK errors

        """
        try:
            fetch_response = self.ts_handle.get_report_details(
                                self.token,
                                report_id=external_id,
                                id_type='external')
            logger.debug("Found report with external id {} as id {}"
                         .format(external_id, fetch_response['id']))
            return fetch_response
        except Exception as e:
            if '404' in e.message:
                logger.debug("Report ID {} does NOT yet exist in TruSTAR."
                            .format(external_id))
                raise TSNoReportError(e)
            else:
                logger.warn("System error while fetching report {}. Error {}"
                            .format(external_id, e), exc_info=True)
                raise TSSystemError(e, "Fetching report failed")

    def get_reports(self, from_time, to_time, enclave_ids):
        """Get reports in the given time window with the given enclave ids
        and distribution type.

        :param from_time: optional start of time window (Unix timestamp - seconds since epoch)
        :param to_time: optional end of time window (Unix timestamp - seconds since epoch)
        :param enclave_ids: optional comma separated list of enclave ids
        :return: list containing reports
        :raise: Any SDK errors

        """
        try:
            response = self.ts_handle.get_reports(
                self.token,
                from_time=from_time,
                to_time=to_time,
                enclave_ids=enclave_ids,
                distribution_type="ENCLAVE")

            if response:
                reports = response.get("data", {}).get("reports", [])
                logger.info("Fetched {} of {} reports from {} to {}"
                            .format(len(reports),
                                    response.get("totalElements"),
                                    from_time,
                                    to_time))
                return response
            else:
                logger.error("Could not fetch reports from {} to {}"
                             .format(from_time, to_time, ))
                raise None
        except Exception as e:
            logger.warn("System error while getting reports. Error {}"
                        .format(e), exc_info=True)
            raise TSSystemError(e, "Getting reports failed")

    def get_all_reports(self,
                        from_time,
                        to_time,
                        enclave_ids,
                        max_pages=5):
        """Get all reports in the given time window with the given enclave
        ids. Fetches all pages of reports in this time window until there
        are no results left.

        :param from_time: start of time window
        :param to_time: end of time window
        :param enclave_ids: comma separated list of enclave ids
        :param max_pages: max pages of reports to fetch
        :return: list containing reports
        :raise: Any SDK errors

        """
        try:
            reports = []
            for _ in range(max_pages):
                response = self.get_reports(from_time=from_time,
                                            to_time=to_time,
                                            enclave_ids=enclave_ids)

                if response is None or response.get("totalElements", 0) == 0:
                    break

                reports.extend(response.get("data", {}).get("reports", []))

                if not response.get('moreResults'):
                    break

                to_time = reports[-1].get("updated")/1000

            logger.info(
                "Fetched total of {} TS reports from {} to {} for enclaves {}"
                .format(len(reports), from_time, to_time, enclave_ids))
            return reports
        except Exception as e:
            raise

    def submit_report(self, report):
        """Submits report to TruSTAR API

        :param report:  dict with report detail
        :return: internal report id
        :raise: Any SDK errors

        """
        try:
            response = self.ts_handle.submit_report(
                            self.token,
                            report_body=report.get('report_body'),
                            title=report.get('title'),
                            time_began=report.get('time_began'),
                            external_id=report.get('externalTrackingId'),
                            external_url=report.get('external_url'),
                            enclave=True)
            logger.info("Submitted report with external id: {}. Got id {}"
                        .format(report.get('externalTrackingId'),
                                response.get('reportId')))
            return response.get('reportId')
        except Exception as e:
            if '413' in e.message:
                logger.warn("Report {} ignored for excess indicators"
                            .format(report['externalTrackingId']))
                raise TSLargeReportError(e)
            else:
                logger.warn("System error while submitting report {}. "
                            "Error {}"
                            .format(report.get('externalTrackingId'), e),
                            exc_info=True)
                raise TSSystemError(e, "Submitting report failed")

    def update_report(self, report):
        """Updates report to TruSTAR API

        :param report:  dict with report detail
        :return: internal report id
        :raise: Any SDK errors

        """
        try:
            response = self.ts_handle.update_report(
                self.token,
                report_id=report.get('externalTrackingId'),
                id_type='external',
                time_began=report.get('time_began'),
                external_url=report.get('external_url'),
                report_body=report.get('report_body'))
            logger.debug("Updated report with external id: {}. Got id {}"
                         .format(report.get('externalTrackingId'),
                                 response.get('reportId')))
            return response.get('reportId')
        except Exception as e:
            if '413' in e.message:
                logger.warn("Report {} ignored for excess indicators"
                            .format(report['externalTrackingId']))
                raise TSLargeReportError(e)
            else:
                logger.warn("System error while updating report {}. Error {}"
                            .format(report.get('externalTrackingId'), e),
                            exc_info=True)
                raise TSSystemError(e, "Updating report failed")

    def add_enclave_tags(self, report):
        """Adds tag to report already present on API
        Expects report['tags'] as array for tags

        :param report:  dict with report detail
        :return:
        :raise: Any SDK errors

        """
        enclave_ids = self.ts_handle.get_enclave_ids()
        tags = report.get('tags', [])

        # make sure we only have unique tag ids
        tags = list(set(tags))

        for tag in tags:
            tag = tag.strip()
            if not tag:
                continue
            for enclave_id in enclave_ids:
                try:
                    self.ts_handle.add_enclave_tag(
                                       self.token,
                                       report_id=report['externalTrackingId'],
                                       id_type="external",
                                       enclave_id=enclave_id,
                                       name=tag)
                except Exception as e:
                    logger.warn("Could not add enclave tag to report {}"
                                .format(report['externalTrackingId']))
                    raise TSSystemError(e, "Adding enclave tags failed")

    def send_report(self, report, update_report=None):
        """Sends report to TruSTAR server
        Check if report is present for the external id.
        If report with that id is not present, it submits the report.
        If report with that id is present, then checks for update_if_present
        If update flag is present, it will append the report body and
        push an update.

        :param report: dict with report detail
        :param update_if_present: update report flag if present
        :param update_report: should we update report if found. Options:
            None: Don't update (Default)
            append: Merge report body
            replace: Replace report body
        :return: Internal report id
        :raise: Any SDK errors

        """
        external_id = report.get('externalTrackingId', "")
        ts_report = None
        internal_report_id = None
        try:
            ts_report = self.get_report(external_id)
            internal_report_id = ts_report['id']
            report_found = True
        except TSNoReportError as e:
            report_found = False

        # if report is found and if we need to update the report
        if report_found:

            if update_report:
                # Join new report body with old
                if update_report == "append":
                    report['report_body'] = (report['report_body']
                                             + ts_report['reportBody'])
                # replace old report body with new one
                elif update_report == "replace":
                    report['report_body'] = report['report_body']

                report['time_began'] = ts_report['timeBegan']
                internal_report_id = self.update_report(report)

        else:
            internal_report_id = self.submit_report(report)

        return internal_report_id

