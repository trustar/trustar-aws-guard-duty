# encoding = utf-8

""" An object that encodes TruSTAR external IDs. """

import uuid
import base64
from logging import getLogger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from logging import Logger

logger = getLogger(__name__)                                    # type: Logger

__RANDOM_UUID = 'f541adc0-f8b4-42a3-a1d9-fbcbfb2820a5'
ENCLAVE_UUID_NAMESPACE = uuid.UUID(__RANDOM_UUID)

class ExternalIdEncoder:
    """ Encodes eternal IDs for TruSTAR reports.
    External IDs need to:
    - calculate to the same thing every time, given the same inputs.
    - be url-encodeable. (some endpoints use them in query-string-params). """

    @staticmethod
    def irreversible(enclave_id, external_id):       # type: (str, str) -> str
        """ Uses enclave ID and desired external ID to produce an
        external ID that will always work with Station. """

        try:
            namespace_uuid = uuid.UUID(enclave_id)
        except ValueError:
            # if the enclave_id was not a valid UUID, hash it to create one.
            # some staging enclave_ids are not valid UUIDs.
            namespace_uuid = uuid.uuid5(ENCLAVE_UUID_NAMESPACE,
                                        enclave_id)

        return str(uuid.uuid5(namespace_uuid, external_id))

    @classmethod
    def reversible(cls, enclave_id, external_id):    # type: (str, str) -> str
        """ Makes a reversible external ID. """
        s = enclave_id + '|' + external_id                       # type: str
        b = s.encode('utf-8')                                    # type: bytes
        encoded = base64.b64encode(b)                            # type: bytes
        stringified_b64_encoding = encoded.decode('utf-8')       # type: str
        if cls.reverse(stringified_b64_encoding) != s:
            logger.error("External ID encoder produced an external ID "
                         "that does not reverse. String: '{}'.  "
                         "Stringified encoding:  '{}'."
                         .format(s, stringified_b64_encoding))
        return stringified_b64_encoding

    @staticmethod
    def reverse(stringified_b64_encoding):                # type: (str) -> str
        """ Reverses an external ID created by the 'reversible' method. """
        b64_encoding = stringified_b64_encoding.encode('utf-8')  # type: bytes
        b = base64.b64decode(b64_encoding)                       # type: bytes
        s = b.decode('utf-8')
        return s
