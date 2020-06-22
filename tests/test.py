# encoding = utf-8

""" Definition for an object that tests the lambda function. """

import json
import os
from configparser import ConfigParser
from logging import getLogger, DEBUG, INFO
from trustar import Report
from lambda_function import lambda_handler

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from logging import Logger

logger = getLogger(__name__)                                   # type: Logger
logger.setLevel(INFO)

class TestScript:

    ENV_VARS_CONFIG_FILE_ROLE = 'env_vars'

    def __init__(self, sample_event_file_path,                    # type: str
                 config_file_path,                                # type: str
                 delete_reports_when_done = False                 # type: bool
                 ):
        self.sample_event_file_path = sample_event_file_path      # type: str
        self.config_file_path = config_file_path                  # type: str
        self.delete_reports_when_done = delete_reports_when_done  # type: bool

        # used by load/set/cleanup methods.
        self.__env_vars = None                            # type: None or Dict

        # used by load/atteempt methods.
        self.__test_event = None                          # type: None or Dict

    def main_(self):
        logger.info("Starting test main_.")

        self.load_test_event()                                  # type: Dict
        self.load_env_vars_from_config_file()                   # type: Dict
        self.set_env_vars()
        self.attempt_lambda()
        self.cleanup_env_vars()

        logger.info("test main_ complete.")

    def load_test_event(self):                              # type: () -> Dict
        """ Loads JSON test event from file path. """
        logger.info("Loading test event from file.")

        with open(self.sample_event_file_path, 'r') as f:
            d = json.load(f)
        self.__test_event = d

        logger.info("Done loading test event.")
        return d

    def load_env_vars_from_config_file(self):
        """ Loads env vars """
        logger.info("Loading env vars from config file.")

        parser = ConfigParser()
        parser.read(self.config_file_path)                # type: ConfigParser
        d = {}
        for option in parser.options(self.ENV_VARS_CONFIG_FILE_ROLE): # type: str
            upper = option.upper()
            d[upper] = parser.get(self.ENV_VARS_CONFIG_FILE_ROLE, option)
            logger.info("loaded '{}' = '{}'.".format(option, d[upper]))
        self.__env_vars = d

        logger.info("Done loading env vars.  Env vars to set:  '{}'."
                    .format(str(d)))

    def set_env_vars(self):
        """ Sets the environment variables required for the lambda. """

        logger.info("setting env vars.")

        for env_var, value in self.__env_vars.items():        # type: str, str
            os.environ[env_var] = value
            logger.info("set '{}' to '{}'.".format(env_var, value))

        logger.info("done setting env vars.")

    def attempt_lambda(self):                               # type: () -> None
        """ Attempts the lambda. """
        logger.info("attempting lambda.")

        """
        try:
        """


        d = lambda_handler(self.__test_event, {})               # type: Dict
        report = Report.from_dict(d)

        logger.info("lambda succeeded.")

        """
        except Exception as e:
            logger.error("lambda failed.  Exception: '{}'.".format(str(e)))
        """

        logger.info("lambda attempt complete.")

    def cleanup_env_vars(self):                             # type: () -> None
        """ Un-sets the environment vars set by this test. """
        logger.info("Cleaning up environment variables.")

        for env_var in self.__env_vars:
            if env_var in os.environ:
                del os.environ[env_var]
                logger.debug("Removed '{}' env var.".format(env_var))

        logger.info("Done cleaning up environment variables.")



if __name__ == "__main__":
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(this_file_dir, 'private', 'test.conf')
    sample_event_file_path = os.path.join(
        this_file_dir, 'data', 'test_event.json')
    t = TestScript(config_file_path=config_file_path,
                   sample_event_file_path=sample_event_file_path)
    t.main_()
