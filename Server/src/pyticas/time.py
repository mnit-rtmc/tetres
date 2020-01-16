# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_rwis import cfg
from datetime import datetime as py_datetime
import pytz
from pytz import timezone
from datetime import timedelta

def GMT(dt):
    """

    :type dt: datetime.datetime
    :return:
    """
    return timezone(cfg.TIME_ZONE).localize(dt).astimezone(timezone('GMT')).replace(tzinfo=None)

def UTC(dt):
    """

    :type dt: datetime.datetime
    :return:
    """
    return timezone(cfg.TIME_ZONE).localize(dt).astimezone(timezone('UTC')).replace(tzinfo=None)

def GMT2Local(dt):
    return timezone('GMT').localize(dt).astimezone(timezone(cfg.TIME_ZONE)).replace(tzinfo=None)

if __name__ == '__main__':

    fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    def test():
        dt = py_datetime(2012, 1, 2, 7, 56, 53)
        print('GMT: ', dt.strftime(fmt))
        print('GMT to Local : ', GMT2Local(dt), type(GMT2Local(dt)))

        print('GMT: ', GMT(dt).strftime(fmt))
        dt = GMT(dt)
        print('GMT to Local : ', GMT2Local(dt), type(GMT2Local(dt)))
        #print(GMT(dt).strftime(fmt))
        #print(UTC(dt).strftime(fmt))


    test()

    # utc = pytz.utc
    # print(utc.zone)
    #
    # mn = timezone('America/Chicago')
    # print(mn.zone)
    #
    # gmt = timezone('GMT')
    # print(gmt.zone)
    #
    #
    # loc_dt = mn.localize(datetime(2002, 10, 27, 6, 0, 0))
    # print(loc_dt.strftime(fmt))
    #
    # amsterdam = timezone('Europe/Amsterdam')
    # ams_dt = loc_dt.astimezone(amsterdam)
    # print(ams_dt.strftime(fmt))
    #
    # utc_dt = datetime(2002, 10, 27, 6, 0, 0, tzinfo=utc)
    # loc_dt = utc_dt.astimezone(mn)
    # gmt_dt = utc_dt.astimezone(gmt)
    # print(utc_dt.strftime(fmt), gmt_dt.strftime(fmt), loc_dt.strftime(fmt))





    # fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    #
    # # Current time in UTC
    # now_utc = datetime.now(timezone('UTC'))
    # print(now_utc.strftime(fmt))
    #
    # # Convert to US/Pacific time zone
    # now_pacific = now_utc.astimezone(timezone('US/Pacific'))
    # print(now_pacific.strftime(fmt))
    #
    # # Convert to Europe/Berlin time zone
    # now_berlin = now_pacific.astimezone(timezone('Europe/Berlin'))
    # print(now_berlin.strftime(fmt))
    #
    # now_mn = datetime.now(timezone('America/Chicago'))
    # print(now_mn.strftime(fmt))