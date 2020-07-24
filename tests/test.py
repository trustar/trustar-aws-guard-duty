# encoding = utf-8

""" Definition for an object that tests the lambda function. """

import json
import os
from time import sleep
from configparser import ConfigParser
from logging import getLogger, INFO
from trustar import Report, TruStar, IdType
from lambda_function import lambda_handler
from trustar_guardduty_lambda_handler.ts_gd_lambda_handler import \
    TruStarGuardDutyLambdaHandler

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from logging import Logger

logger = getLogger(__name__)                                   # type: Logger
logger.setLevel(INFO)


class ConfigLoader:
    @staticmethod
    def from_file(path_, stanza):
        """ Loads configs from file/stanza into dict. """
        parser = ConfigParser()
        parser.read(path_)                                # type: ConfigParser
        d = {}
        for option in parser.options(stanza):                      # type: str
            d[option] = parser.get(stanza, option)
            logger.info("loaded '{}' = '{}'.".format(option, d[option]))
        return d


class TestGDLambdaFunction:
    """ Tests to ensure that the lambda function functions properly. """

    STANZA = 'env_vars'
    REPORT_ATTRS_TO_COMPARE = ('title',
                               'body',
                               'time_began',
                               'external_url',
                               'external_id',
                               'enclave_ids',
                               'id')

    def __init__(self, sample_event_file_path,                    # type: str
                 expected_report_file_path,                       # type: str
                 config_file_path,                                # type: str
                 delete_reports_when_done=False                   # type: bool
                 ):
        """ Some prep work. """
        configs = self.load_configs(config_file_path)             # type: dict
        self.__env_vars = self.env_vars_from_configs(configs)     # type: Dict
        self.set_env_vars_to_os(self.__env_vars)
        self.ts = self.build_ts_client()
        self.test_event = self.dict_from_file(
            sample_event_file_path)                               # type: Dict
        self.expected_report = Report.from_dict(
            self.dict_from_file(expected_report_file_path))       # type: Dict
        self.delete_reports_when_done = delete_reports_when_done  # type: bool

    def load_configs(self, path_):                       # type: (str) -> Dict
        """ Loads configs from file. """
        logger.info("Loading configs from file '{}', stanza '{}'."
                    .format(path_, self.STANZA))
        configs = ConfigLoader.from_file(path_, self.STANZA)
        logger.info("Configs loaded:  {}"
                    .format(json.dumps(configs, indent=4)))
        return configs

    def env_vars_from_configs(self, configs):
        """ Loads env vars """
        logger.info("Loading env vars from config dict.")
        env_vars = {}
        for k, v in configs.items():                   # type: str, str
            upper = k.upper()
            env_vars[upper] = v
            logger.info("'{}' = '{}'.".format(upper, env_vars[upper]))
        logger.info("Done loading env vars.  Env vars to set:  '{}'."
                    .format(str(env_vars)))
        return env_vars

    def set_env_vars_to_os(self, env_vars):             # type: (Dict) -> None
        """ Sets the environment variables required for the lambda. """
        logger.info("setting env vars.")
        for env_var, value in env_vars.items():               # type: str, str
            os.environ[env_var] = value
            logger.info("set '{}' to '{}'.".format(env_var, value))
        logger.info("done setting env vars.")

    def build_ts_client(self):
        """ Builds TruStar client using configs from environ vars. """
        logger.info("Building TruStar client.")
        ts_config = {'user_api_key': os.environ['USER_API_KEY'],
                     'user_api_secret': os.environ['USER_API_SECRET'],
                     'client_metatag':
                         TruStarGuardDutyLambdaHandler.CLIENT_METATAG}
        ts = TruStar(config=ts_config)
        logger.info("Done building TruStar client.")
        return ts

    def dict_from_file(self, path_):               # type: (str) -> Dict
        """ Loads JSON test event from file path. """
        logger.info("Loading file '{}'.".format(path_))
        with open(path_) as f:
            d = json.load(f)
        logger.info("Done loading file.")
        return d

    def main_(self):
        """ The test's main sequence. """
        logger.info("Starting test main_.")
        upserted_report = self.attempt_lambda(self.test_event)  # type: Report
        station_report = self.fetch_report_saved_in_trustar(
            upserted_report.external_id)                        # type: Report
        self.compare_reports(upserted_report,
                             station_report,
                             self.expected_report)
        self.cleanup_env_vars()
        if self.delete_reports_when_done:
            logger.info("deleting test report from enclave.")
            _ = self.ts.delete_report(station_report.external_id,
                                      id_type=IdType.EXTERNAL)
            logger.info("done deleting test report from enclave.")
        logger.info("test main_ complete.")

    def attempt_lambda(self, test_event):             # type: (Dict) -> Report
        """ Attempts the lambda. """
        logger.info("attempting lambda.")
        d = lambda_handler(test_event, {})
        logger.info("lambda attempt complete, success.")
        return Report.from_dict(d)

    def fetch_report_saved_in_trustar(self,
                                      external_id):    # type: (str) -> Report
        """ Fetching the recently-submitted report from the enclave. """
        logger.info("Fetching report from enclave.")
        report_in_enclave = self.ts.get_report_details(
            external_id, id_type=IdType.EXTERNAL)               # type: Report
        logger.info("Fetching complete.")
        return report_in_enclave

    def compare_reports(self, upserted_report,           # type: Report
                        report_in_enclave,               # type: Report
                        expected_report                  # type: Report
                        ):                               # type: (...) -> None
        """ Compares the report in the enclave to the expected report
        in the tests/data/expected_report.json. """
        logger.info("Comparing reports.")
        vars_to_ignore = ["created", "updated", "id"]
        for v in vars(report_in_enclave):
            if v in vars_to_ignore:
                continue

            val_in_enclave = getattr(report_in_enclave, v)
            upserted_val = getattr(upserted_report, v)
            expected_val = getattr(expected_report, v)
            if not val_in_enclave == expected_val == upserted_val:
                logger.error("For instance-var '{}', upserted:  '{}', "
                             "found in enclave:  '{}', expected:  '{}'."
                             .format(v, upserted_val, val_in_enclave,
                                     expected_val))
        logger.info("Done comparing reports.")

    def cleanup_env_vars(self):                             # type: () -> None
        """ Un-sets the environment vars set by this test. """
        logger.info("Cleaning up environment variables.")
        for env_var in self.__env_vars:
            if env_var in os.environ:
                del os.environ[env_var]
                logger.debug("Removed '{}' env var.".format(env_var))
        logger.info("Done cleaning up environment variables.")


class TestReportSubmit:

    body = 'test body'
    title = 'test title'
    external_url = 'https://testurl.com'
    external_id = 'test_ext_id'

    def __init__(self, config_file_path,                           # type: str
                 config_stanza):                    # type: (..., str) -> None
        configs = ConfigLoader.from_(config_file_path,
                                     config_stanza)               # type: Dict
        configs = {k.lower(): v for k, v in configs.items()}
        configs['client_metatag'] = TruStarGuardDutyLambdaHandler.CLIENT_METATAG
        self.ts = TruStar(config=configs)
        self.ts.logger.setLevel("DEBUG")
        """
        ch = StreamHandler()
        ch.setLevel("DEBUG")
        self.ts.logger.addHandler(ch)
        """
        self.enclave_id = configs['enclave_id']

    def go(self):
        time_begans = ['1577865600000',
                       1577865600456,
                       '1577865600',
                       1577865601,
                       '2020-02-01T00:00:01+00:00',
                       '2020-02-01T00:00:01.12345+00:00',
                       '2020-02-01T00:00:01.74839+00:00',
                       #datetime.now() - timedelta(days=5)
                       ]


        test_reports = []                                 # type: List[Report]
        for i, t in enumerate(time_begans):
            test_reports.append(self.build_test_report(i, t))

        for r in test_reports:
            try:
                self.ts.delete_report(r.external_id, id_type=IdType.EXTERNAL)
            except:
                pass

            _ = self.ts.submit_report(r)

        logger.info("Sleeping 20 seconds.")
        sleep(20)

        for r in test_reports:
            report = self.ts.get_report_details(
                r.external_id, id_type=IdType.EXTERNAL)        # type: Report

            if not report.body == r.body:
                logger.error("body")
            if not report.title == r.title:
                logger.error("title")
            if not report.external_url == r.external_url:
                logger.error("external_url")
            if not report.external_id == r.external_id:
                logger.error("external_id")
            if not report.time_began == r.time_began:
                logger.error("time_began submitted:  '{}',  retrieved: "
                             "'{}'".format(r.time_began, report.time_began))

    def build_test_report(self, i, time_began):
        r = Report()
        r.body = self.body
        r.title = self.title
        r.external_id = self.external_id + str(i)
        r.external_url = self.external_url
        r.enclave_ids = [self.enclave_id]
        #r.set_time_began(time_began)
        r.time_began = time_began
        return r

if __name__ == "__main__":
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(this_file_dir, 'private', 'test.conf')
    sample_event_file_path = os.path.join(
        this_file_dir, 'data', 'test_event.json')
    expected_report_file_path = os.path.join(
        this_file_dir, 'data', 'expected_report.json')

    """
    t = TestReportSubmit(config_file_path=config_file_path,
                         config_stanza=TestGDLambdaFunction.ENV_VARS_CONFIG_FILE_ROLE)
    t.go()
    """

    t = TestGDLambdaFunction(
        config_file_path=config_file_path,
        sample_event_file_path=sample_event_file_path,
        expected_report_file_path=expected_report_file_path,
        delete_reports_when_done=True)
    t.main_()
