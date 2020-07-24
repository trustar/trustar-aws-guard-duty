# encoding = utf-8

""" A script that receives a Guard Duty "Finding" and submits it to an
enclave as a Report. """

# noinspection PyUnresolvedReferences
from trustar_guardduty_lambda_handler import TruStarGuardDutyLambdaHandler

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict


# noinspection PyUnusedLocal
def lambda_handler(event, context):             # type: (Dict, Dict) -> Dict
    """ Sends Finding to Station.
    :param event: the GD event dictionary.
    :param context:  not used.  """
    handler = TruStarGuardDutyLambdaHandler()
    report = handler.handle(event)                                # type: Dict
    return report
