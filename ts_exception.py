from builtins import super

class TSException(Exception):
    """Base class for all TruSTAR SDK exceptions"""

    def __init__(self, err):
        """Inits TruSTAR Base Exception

        :param err: Error to generate when raising exception
        """
        super().__init__(err)

class TSNoReportError(TSException):
    """Exception raised when fetching a report with id, but its not found """

    def __init__(self, original_exception, msg = ""):
        """Inits TruSTAR exception

        :param original_exception: Original Exception
        :param msg: Custom message
        """
        err = "Report not found - {}".format(original_exception)
        if msg:
            err = "{} - {}".format(msg, err)
        super().__init__(err)

class TSBadRequestError(TSException):
    """Exception raised when fetching reports with invalid parameters """

    def __init__(self, original_exception, msg = ""):
        """Inits TruSTAR exception

        :param original_exception: Original Exception
        :param msg: Custom message
        """
        err = "Invalid parameters for reports search - {}".format(original_exception)
        if msg:
            err = "{} - {}".format(msg, err)
        super().__init__(err)

class TSLargeReportError(TSException):
    """Exception raised when submitting report with too many indicators"""

    def __init__(self, original_exception, msg = ""):
        """Inits TruSTAR exception

        :param original_exception: Original Exception
        :param msg: Custom message
        """
        err = ("Report has more indicators than supported - {}"
               .format(original_exception))
        if msg:
            err = "{} - {}".format(msg, err)
        super().__init__(err)

class TSTokenError(TSException):
    """Exception raised when getting token failed"""

    def __init__(self, original_exception, msg = ""):
        """Inits TruSTAR exception

        :param original_exception: Original Exception
        :param msg: Custom message
        """
        err = ("Could not get TruSTAR API token - {}"
               .format(original_exception))
        if msg:
            err = "{} - {}".format(msg, err)
        super().__init__(err)

# TODO: Split this into PermissionError, ConnectionError and others
class TSSystemError(TSException):
    """Exception raised when connection failure or any server issue"""

    def __init__(self, original_exception, msg = ""):
        """Inits TruSTAR exception

        :param original_exception: Original Exception
        :param msg: Custom message
        """
        err = ("Got system error - {}"
               .format(original_exception))
        if msg:
            err = "{} - {}".format(msg, err)
        super().__init__(err)
