# encoding = utf-8

""" An object that can be used to check API creds' permissions to
varios enclaves. """

from logging import getLogger
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from logging import Logger
    from trustar import TruStar, EnclavePermissions

logger = getLogger(__name__)                                    # type: Logger


class TruStarEnclavePermissionsChecker:
    """ Verifies that the TruStar client's API creds have the specified
    level of access to the specified enclave. """

    true = 'true'
    false = 'false'

    def __init__(self, ts):                   # type: (TruStar) -> None
        enclaves = ts.get_user_enclaves()     # type: List[EnclavePermissions]
        self.permissions = {e.id: e for e in
                            enclaves}         # type: Dict[EnclavePermissions]

    def get_perms(self, enclave_id         # type: str
                  ):                       # type: (...) -> EnclavePermissions
        """ Raises exception if no access at all to the enclave. """
        if enclave_id not in self.permissions:
            msg = "TruSTAR API creds do not have any access to the enclave."
            logger.error(msg)
            raise Exception(msg)
        return self.permissions[enclave_id]

    def can_read(self, enclave_id):                      # type: (str) -> bool
        """ Checks to see if creds have read access to the enclave. """
        return self.get_perms(enclave_id).read == self.__class__.true

    def can_create(self, enclave_id):                    # type: (str) -> bool
        """ Checks to see if creds have create access to the enclave. """
        return self.get_perms(enclave_id).create == self.__class__.true

    def can_update(self, enclave_id):                    # type: (str) -> bool
        """ Checks to see if the creds have update access to the enclave. """
        return self.get_perms(enclave_id).update == self.__class__.true