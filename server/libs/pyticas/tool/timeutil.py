# -*- coding: utf-8 -*-

import datetime
import math

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def human_time(*args, **kwargs):
    """ convert time to humanized time string

    :rtype: str
    """
    secs = float(datetime.timedelta(*args, **kwargs).total_seconds())
    units = [("day", 86400), ("hour", 3600), ("minute", 60), ("second", 1)]
    parts = []
    for unit, mul in units:
        if secs / mul >= 1 or mul == 1:
            if mul > 1:
                n = int(math.floor(secs / mul))
                secs -= n * mul
            else:
                n = secs if secs != int(secs) else int(secs)
            parts.append("%s %s%s" % (n, unit, "" if n == 1 else "s"))
    return ", ".join(parts)