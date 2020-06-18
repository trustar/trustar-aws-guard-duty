# encoding = utf-8

""" Builds TruStar client objects from Environment Variables. """

import os
from logging import getLogger
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import *
    from logging import getLogger
    from trustar import TruStar

logger = getLogger(__name__)


class TruStarClientBuilder:
    """ Builds TruStar client from Lambda's Environ Vars. """

    TRUSTAR_CLIENT_PARAMS = ['user_api_key',
                             'user_api_secret',
                             'http_proxy',
                             'https_proxy',
                             'auth_endpoint',
                             'api_endpoint']

    @classmethod
    def from_env_vars(cls, client_metatag):           # type: (str) -> TruStar
        """ Builds TruStar client. """
        if not client_metatag:
            raise Exception("must specify a client_metatag.")

        config = {param: os.environ.get(param.upper()) for param in
                  cls.TRUSTAR_CLIENT_PARAMS}
        config['client_metatag'] = client_metatag
        return TruStar(config=config)