# encoding = utf-8

""" A script that receives a Guard Duty "Finding" and submits it to an
enclave as a Report. """

from trustar_guardduty_lambda_handler import TruStarGuardDutyLambdaHandler

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from trustar import Report

def lambda_handler(event, context):               # type: (Dict, Dict) -> Dict
    """ Sends Finding to Station. """
    handler = TruStarGuardDutyLambdaHandler()
    return handler.handle(event, context)                       # type: Report
