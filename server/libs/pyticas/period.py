# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas.logger import getDefaultLogger
from pyticas.ttypes import Period

logging = getDefaultLogger(__name__)


def create_period(start_datetime, end_datetime, interval):
    """
    :param start_datetime: (start_year, start_month, start_day, start_hour, start_min)
    :type start_datetime: Union(datetime.datetime, str, tuple(int, int, int, int, int))
    :param end_datetime: (end_year, end_month, end_day, end_hour, end_min)
    :type end_datetime: Union(datetime.datetime, str, tuple(int, int, int, int, int))
    :type interval: int
    :return: Period
    """
    if isinstance(start_datetime, datetime.datetime):
        sdate = start_datetime
    elif isinstance(start_datetime, str):
        sdate = datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
    else:
        (start_year, start_month, start_day, start_hour, start_min) = start_datetime
        sdate = datetime.datetime(start_year, start_month, start_day, start_hour, start_min)

    if isinstance(end_datetime, datetime.datetime):
        edate = end_datetime
    elif isinstance(end_datetime, str):
        edate = datetime.datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
    else:
        (end_year, end_month, end_day, end_hour, end_min) = end_datetime
        edate = datetime.datetime(end_year, end_month, end_day, end_hour, end_min)

    return Period(sdate, edate, interval)


def create_period_with_duration(start_datetime, duration, interval):
    """

    :param start_datetime: (start_year, start_month, start_day, start_hour, start_min)
    :type start_datetime: tuple(int, int, int, int, int)
    :param duration: duration from start time in minutes
    :type duration: int
    :type interval: int
    :return: Period
    """
    (start_year, start_month, start_day, start_hour, start_min) = start_datetime
    sdate = datetime.datetime(start_year, start_month, start_day, start_hour, start_min)
    edate = sdate + datetime.timedelta(minutes=duration)
    return Period(sdate, edate, interval)


def create_period_from_string(sdate_str, edate_str, interval):
    """

    :param sdate_str: start datetime string e.g. 2015-09-01 07:00:00
    :type sdate_str: str
    :param edate_str: end datetime string e.g. 2015-09-01 07:30:00
    :type edate_str: str
    :param interval: data gathering interval in second
    :type interval: int
    :return:
    """
    sdate = datetime.datetime.strptime(sdate_str, '%Y-%m-%d %H:%M:%S')
    edate = datetime.datetime.strptime(edate_str, '%Y-%m-%d %H:%M:%S')
    return Period(sdate, edate, interval)


def create_period_from_string_with_duration(sdate_str, duration, interval):
    """

    :param sdate_str: start datetime string e.g. 2015-09-01 07:00:00
    :type sdate_str: str
    :param duration: duration from start time in minutes
    :type duration: int
    :param interval: data gathering interval in second
    :type interval: int
    :return:
    """
    sdate = datetime.datetime.strptime(sdate_str, '%Y-%m-%d %H:%M:%S')
    edate = sdate + datetime.timedelta(minutes=duration)
    return Period(sdate, edate, interval)


def create_periods(start_date, end_date, start_time, end_time, interval, **kwargs):
    """ create multiple period objects in a list

    :param start_date: start datetime or string e.g. 2015-09-01
    :type start_date: Union(datetime.date, str)
    :param end_date:  start datetime or string e.g. 2015-09-30
    :type end_date: Union(datetime.date, str)
    :param start_time:  start time or time string e.g. 07:00:00
    :type start_time: Union(datetime.time, str)
    :param end_time:  start time or time string e.g. 08:00:00
    :type end_time: Union(datetime.time, str)
    :param interval: data gathering interval in second
    :param kwargs: optional parameters
        - target_days : 0~6, (0=Mon, 6=Sun), default=[1,2, 3]
        - remove_holiday : do not create holiday if it is True
        - except_dates : list of date object
    :rtype: list[pyticas.ttypes.Period]
    """

    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    if isinstance(start_time, str):
        start_time = datetime.datetime.strptime(start_time, '%H:%M:%S').time()
    if isinstance(end_time, str):
        end_time = datetime.datetime.strptime(end_time, '%H:%M:%S').time()

    assert isinstance(start_date, datetime.date)
    assert isinstance(end_date, datetime.date)
    assert isinstance(start_time, datetime.time)
    assert isinstance(end_time, datetime.time)

    logging.debug('Start to create periods')

    # Mon = 0 ~ Sun =6
    # [1,2,3] = Tue, Wed, Thu
    target_days = kwargs.get('target_days', [1, 2, 3])
    remove_holiday = kwargs.get('remove_holiday', True)
    except_dates = kwargs.get('except_dates', [])

    holidays_cache = {}
    periods = []
    sdate = start_date + datetime.timedelta(days=-1)
    while (sdate < end_date):

        sdate = sdate + datetime.timedelta(days=1)

        s_date_time = datetime.datetime.combine(sdate, start_time)
        e_date_time = datetime.datetime.combine(sdate, end_time)

        if s_date_time.weekday() not in target_days:
            logging.debug('{0} : Skip! It\'s a {1}.'.format(sdate, sdate.strftime('%A')))
            continue

        if remove_holiday:
            if sdate.year not in holidays_cache.keys():
                holidays = [hday['date'] for hday in get_holidays(sdate.year)]
                holidays_cache[sdate.year] = holidays
            else:
                holidays = holidays_cache[sdate.year]

            if sdate in holidays:
                logging.debug('{0} : Skip! It\'s a holiday'.format(sdate))
                continue

        if sdate in except_dates or sdate.strftime('%Y-%m-%d') in except_dates:
            logging.debug('{0} : Skip! It\'s a except day'.format(sdate))
            continue

        periods.append(Period(s_date_time, e_date_time, interval))

    logging.debug('End of creating periods')
    return periods


def is_holiday(day):
    """
    :type day: datetime.date
    :rtype: bool
    """
    assert isinstance(day, datetime.date)
    return day in [hday['date'] for hday in get_holidays(day.year)]


def get_holidays(year):
    """ return holidays as list of datetime.date

    :type year: int
    :rtype: list[datetime.date]
    """
    holidays = [
        {
            'name': 'new years day',
            'date': datetime.date(year, 1, 1),
            'delta': [0, 0, 0, 0, 0, -1, 1]
        },
        {
            'name': 'martin luther king',
            'date': datetime.date(year, 1, 1),
            'delta': [14, 20, 19, 18, 17, 16, 15]
        },
        {
            'name': 'president day',
            'date': datetime.date(year, 2, 1),
            'delta': [14, 20, 19, 18, 17, 16, 15]
        },
        {
            'name': 'memorial day',
            'date': datetime.date(year, 5, 1),
            'delta': [28, 27, 26, 25, 24, 30, 29]
        },
        {
            'name': 'independence day',
            'date': datetime.date(year, 7, 4),
            'delta': [0, 0, 0, 0, 0, -1, 1]
        },
        {
            'name': 'labor day',
            'date': datetime.date(year, 9, 1),
            'delta': [0, 6, 5, 4, 3, 2, 1]
        },
        {
            'name': 'columbus day',
            'date': datetime.date(year, 10, 1),
            'delta': [7, 13, 12, 11, 10, 9, 8]
        },
        {
            'name': 'veterans day',
            'date': datetime.date(year, 11, 11),
            'delta': [0, 0, 0, 0, 0, -1, 1]
        },
        {
            'name': 'thanksgiving',
            'date': datetime.date(year, 11, 1),
            'delta': [24, 23, 22, 21, 27, 26, 25]
        },
        {
            'name': 'day after thanksgiving',
            'date': datetime.date(year, 11, 1),
            'delta': [25, 24, 23, 22, 28, 27, 26]
        },
        {
            'name': 'christmas eve',
            'date': datetime.date(year, 12, 24),
            'delta': [0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'christmas',
            'date': datetime.date(year, 12, 25),
            'delta': [0, 0, 0, 0, 0, -1, 1]
        }
    ]

    return [{'name': hday['name'],
             'date': hday['date'] + datetime.timedelta(days=hday['delta'][hday['date'].weekday()])} for hday in
            holidays]
