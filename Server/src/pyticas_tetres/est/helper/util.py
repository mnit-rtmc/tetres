# -*- coding: utf-8 -*-
import datetime
import os

from pyticas import period
from pyticas_tetres import tetres

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def get_datetime(dts):
    """
    :type dts: str
    :rtype: datetime.datetime
    """
    if isinstance(dts, datetime.datetime):
        return dts
    return datetime.datetime.strptime(dts, '%Y-%m-%d %H:%M:%S')


def get_date(dts):
    """
    :type dts: str
    :rtype: datetime.date
    """
    if isinstance(dts, datetime.date):
        return dts
    return datetime.datetime.strptime(dts, '%Y-%m-%d').date()

def get_time(time_string):
    """
    :type time_string: str
    :rtype: datetime.time
    """
    h, m = get_hour_and_minute(time_string)
    return datetime.time(hour=h, minute=m, second=0)


def get_hour_and_minute(time_string):
    """
    :type time_string: str
    :rtype: int, int
    """
    return int(time_string[0:2]), int(time_string[3:5])


def years(start_date, end_date):
    """

    :type start_date: Union(datetime.date, datetime.datetime, str)
    :type end_date: Union(datetime.date, datetime.datetime, str)
    :rtype: list[int]
    """
    if isinstance(start_date, str):
        start_date = get_date(start_date)
    if isinstance(end_date, str):
        end_date = get_date(end_date)

    syear = start_date.year
    eyear = end_date.year
    return [ y for y in range(syear, eyear+1)]


def months(start_date, end_date):
    """

    :type start_date: Union(datetime.date, datetime.datetime)
    :type end_date: Union(datetime.date, datetime.datetime)
    :rtype: list[[int, int]]
    """
    if isinstance(start_date, str):
        start_date = get_date(start_date)
    if isinstance(end_date, str):
        end_date = get_date(end_date)
    sdate = start_date if isinstance(start_date, datetime.date) else start_date.date()
    edate = end_date if isinstance(end_date, datetime.date) else end_date.date()
    cursor = sdate
    step = datetime.timedelta(days=1)
    months = []
    while cursor <= edate:
        ym = [cursor.year, cursor.month]
        if ym not in months:
            months.append(ym)
        cursor += step
    return months


def dates(start_date, end_date, except_holiday=False, weekdays=None):
    """

    :type start_date: Union(datetime.date, datetime.datetime)
    :type end_date: Union(datetime.date, datetime.datetime)
    :rtype: list[datetime.date]
    """
    weekdays = weekdays or [0,1,2,3,4,5,6]
    if isinstance(start_date, str):
        start_date = get_date(start_date)
    if isinstance(end_date, str):
        end_date = get_date(end_date)
    sdate = start_date if isinstance(start_date, datetime.date) else start_date.date()
    edate = end_date if isinstance(end_date, datetime.date) else end_date.date()
    cursor = sdate
    step = datetime.timedelta(days=1)
    dates = []
    while cursor <= edate:
        if cursor.weekday() not in weekdays or (except_holiday and period.is_holiday(cursor)):
            cursor += step
            continue

        dates.append(cursor)
        cursor += step
    return dates


def output_path(sub_dir='', create=True):
    infra = tetres.get_infra()
    if sub_dir:
        output_dir = infra.get_path('tetres/output/%s' % sub_dir, create=create)
    else:
        output_dir = infra.get_path('tetres/output', create=create)

    if create and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        return os.path.abspath(output_dir)

    if os.path.exists(output_dir):
        return os.path.abspath(output_dir)
    else:
        return output_dir
