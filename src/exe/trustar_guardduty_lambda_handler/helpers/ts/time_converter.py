# encoding = utf-8

""" TimeConverter class. """

import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from datetime import datetime as datetime_cls

class TimeConverter:
    """ A class that consolidates some often-needed time conversions
    so I don't have to google these every time anymore. """

    @classmethod
    def iso_to_ms(cls, iso):                              # type: (str) -> int
        """ Converts isoformat string to int millis.
        :param iso:  string in format 2017-10-31T23:16:23+00:00 - MUST
        HAVE TIMEZONE DESIGNATOR!
        :return: int millis """
        dt = cls.iso_to_dt(iso)
        if not dt.tzinfo:
            raise Exception("Could not deduce timezone info for ISO "
                            "timestamp string '{}'.".format(iso))
        ms = int(dt.timestamp() * 1000.0)
        return ms

    @staticmethod
    def iso_to_dt(iso):                          # type: (str) -> datetime_cls
        """ Converts an isoformat string to datetime object. """
        return datetime.datetime.fromisoformat(iso)

    @classmethod
    def ms_to_iso_utc(cls, ms):                          # type: (int) -> str
        """ Converts ms int to iso str in format
        2017-10-31T23:16:23+00:00. """
        dt = cls.ms_to_dt_utc(ms)
        iso = dt.isoformat(timespec='seconds')
        return iso

    @staticmethod
    def ms_to_dt_utc(ms):                        # type: (int) -> datetime_cls
        """ Converts mills int to timezone-aware datetime obj. """
        return datetime.datetime.fromtimestamp(ms / 1000.0,
                                               tz=datetime.timezone.utc)
