# encoding = utf-8

""" An object that converts a Guard Duty Finding to a TruSTAR Report. """

import json
from logging import getLogger
from typing import TYPE_CHECKING
from trustar import Report
if TYPE_CHECKING:
    from typing import *
    from logging import Logger

logger = getLogger(__name__)                                    # type: Logger

class GuardDutyReportBuilder:
    """ Builds TruSTAR report from Guard Duty Finding event. """

    GD_FINDING_DETAIL_KEYS = ['title', 'description', 'severity',
                              'createdAt', 'updatedAt', 'service']

    @classmethod
    def build_for(cls, finding):                      # type: (Dict) -> Report
        """ Builds a Report for an event. """
        report_body = {}
        detail = finding.get('detail')
        for key in cls.GD_FINDING_DETAIL_KEYS:
            report_body[key] = detail.get(key, '')

        r = Report(title=report_body['title'],
                   time_began=detail['service']['eventFirstSeen'],
                   external_url=detail['arn'],
                   external_id=detail['id'],
                   body=json.dumps(report_body, indent=4, sort_keys=True))
        return r