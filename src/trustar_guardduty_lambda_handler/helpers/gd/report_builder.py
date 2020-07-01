# encoding = utf-8

""" An object that converts a Guard Duty Finding to a TruSTAR Report. """

import json
from datetime import datetime
from logging import getLogger
from trustar import Report
from ..ts.external_id_encoder import ExternalIdEncoder

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from logging import Logger

logger = getLogger(__name__)                                    # type: Logger

class GuardDutyReportBuilder:
    """ Builds TruSTAR report from Guard Duty Finding event.
    NOTE: No validation of attribute values done by this object.  """

    GD_FINDING_DETAIL_KEYS = ['title', 'description', 'severity',
                              'createdAt', 'updatedAt', 'service']

    DEFAULT_TITLE = 'NO TITLE FOUND IN GUARDDUTY EVENT'

    def __init__(self, enclave_id):
        self.enclave_id = enclave_id                               # type: str
        self.ext_id_encoder = ExternalIdEncoder()

    def build_for(self, finding):                      # type: (Dict) -> Report
        """ Builds a Report for an event.
        Note:  Does NOT validate report attribute values to ensure they
        are valid / reasonable.  VALIDATE AFTER BUILDING! """

        detail = finding.get('detail')
        if not detail:
            raise Exception("Guard Duty Finding dictionary's 'detail' kv pair"
                            "is empty.  This integration builds TruSTAR "
                            "reports from that key's value.")

        title = detail.get('title', self.DEFAULT_TITLE)
        body = self._body_from_detail(detail)
        time_began = self._time_began_from_detail(detail)
        external_url = detail.get('arn')
        external_id = self.ext_id_encoder.reversible(self.enclave_id,
                                                     detail.get('id'))

        r = Report(title=title,
                   body=body,
                   time_began=time_began,
                   external_url=external_url,
                   external_id=external_id,
                   enclave_ids=[self.enclave_id])

        logger.info("TimeBegan in ReportBuilder after assigning to the "
                    "report object:  '{}'".format(r.time_began))

        d = r.to_dict()
        logger.info("TimeBegan in ReportBuiilder after converting report to "
                    "dict:  '{}'.")



        return r

    @staticmethod
    def _time_began_from_detail(detail):         # type: (Dict) -> str or None
        """ Gets the time_began from the detail dict. """
        service = detail.get('service')                    # type: Dict
        time_began = None                                  # type: None or str
        if service:
            time_began = service.get('eventFirstSeen')
            """
            format = '%Y-%m-%dT%H:%M:%S+%z'
            time_began = datetime.strptime(time_began, format)
            """
        logger.info("TimeBegan in report builder:  {}"
                    .format(time_began))
        return time_began

    @classmethod
    def _body_from_detail(cls, detail):          # type: (Dict) -> str
        body = {k: detail.get(k) for k in cls.GD_FINDING_DETAIL_KEYS}
        return json.dumps(body, indent=4, sort_keys=True)
