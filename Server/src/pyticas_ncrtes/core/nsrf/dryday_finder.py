# -*- coding: utf-8 -*-

"""
Normal Dry Day Module
=====================

this module finds dry days for the given target station during the years and months

"""

import calendar
import datetime

from pyticas import period as prd_helper
from pyticas_ncrtes.logger import getLogger
from pyticas_ncrtes.core import setting
from pyticas_noaa.isd import isd

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

DRY_DAY_CACHE = {}
WEATHER_STATION_DISTANCE_LIMIT = 15
STATE = 'MN'
TARGET_ISD_STATIONS = [
    # (USAF, WBAN)
    ('726577', '94974'),  # ANOKA CO-BLNE AP(JNS FD) AP
    ('726575', '94960'),  # CRYSTAL AIRPORT
    ('726584', '14927'),  # ST PAUL DWTWN HOLMAN FD AP
    ('726580', '14922'),  # MINNEAPOLIS-ST PAUL INTERNATIONAL AP
    ('726603', '04974'),  # SOUTH ST PAUL MUNI-RICHARD E FLEMING FLD ARPT
    ('726579', '94963'),  # FLYING CLOUD AIRPORT
    ('726562', '04943'),  # AIRLAKE AIRPORT
]


def drydays_for_daytime(target_station, months, **kwargs):
    """

    :type target_station: pyticas.ttypes.RNodeObject
    :type months: list[(int, int)]
    :rtype: (list[pyticas.ttypes.Period], str)
    """
    data_interval = kwargs.get('interval', setting.DATA_INTERVAL)
    # dry days
    return _dry_days_for_daytime(target_station,
                                 months,
                                 datetime.time(setting.AM_START, 0, 0),
                                 datetime.time(setting.PM_END, 0, 0),
                                 data_interval)


def drydays_for_nighttime(target_station, months, **kwargs):
    """

    :type target_station: pyticas.ttypes.RNodeObject
    :type months: list[(int, int)]
    :rtype: (list[pyticas.ttypes.Period], str)
    """
    data_interval = kwargs.get('interval', setting.DATA_INTERVAL)
    return _dry_days_for_nighttime(target_station,
                                   months,
                                   data_interval)


def is_dry_day(target_station, prd):
    """ is dry day?

    How-to::

        check weather through RWIS at first,
        if RWIS is not available, use weather sensor (WEATHER_DEVICE.WS35W25)

    :type target_station: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    :rtype: (bool, str)
    """
    logger = getLogger(__name__)
    # wbans = [wban for (usaf, wban) in TARGET_ISD_STATIONS]
    # usafs = [usaf for (usaf, wban) in TARGET_ISD_STATIONS]
    # _weather_stations = isd.get_station_list('MN', lambda wst: wst.wban in wbans and wst.usaf in usafs)
    # isd_stations = isd.find_nearby_station(target_station.lat, target_station.lon, prd.start_date.date(), _weather_stations)
    isd_stations = weather_stations(target_station, prd)
    nearby = None
    isd_data_list = None

    cprd = prd.clone()
    cprd.extend_end_hour(2)

    # decide nearby weather station which has nsr_data during a given period
    # by trying to read weather nsr_data
    for dist, isd_station in isd_stations:

        cache_key = '%s-%s' % (isd_station.station_name, prd.get_period_string())
        if cache_key in DRY_DAY_CACHE:
            nearby, isd_data_list = DRY_DAY_CACHE[cache_key]
            break

        if dist > WEATHER_STATION_DISTANCE_LIMIT:
            break

        isd_data_list = isd.get_data(isd_station, cprd)
        """:type: list[pyticas_noaa.isd.isdtypes.ISDData] """

        if not isd_data_list:
            continue

        DRY_DAY_CACHE[cache_key] = (isd_station, isd_data_list)

        nearby = isd_station
        break

    if not nearby:
        #logger.warning('No weather information (for %s during %s)' % (target_station.station_id, prd.get_period_string()))
        return False, None

    if _is_dry(isd_data_list, prd, setting.DRY_RATE_THRESHOLD):
        return True, nearby.station_name
    else:
        return False, nearby.station_name



def weather_stations(target_station, prd):
    wbans = [wban for (usaf, wban) in TARGET_ISD_STATIONS]
    usafs = [usaf for (usaf, wban) in TARGET_ISD_STATIONS]
    weather_stations = isd.get_station_list('MN', lambda wst: wst.wban in wbans and wst.usaf in usafs)
    return isd.find_nearby_station(target_station.lat, target_station.lon, prd.start_date.date(), weather_stations)


def _dry_days_for_daytime(target_station, months, start_time, end_time, interval):
    """ return dry day list

    :type months: list[(int, int)]
    :type start_time: datetime.time
    :type end_time: datetime.time
    :type interval: int

    :rtype: (list[pyticas.ttypes.Period], str)
    """
    logger = getLogger(__name__)
    normal_days = []
    weather_source = ''
    weather_sources = []
    today = datetime.date.today()

    for idx, (year, month) in enumerate(months):
        day = datetime.date(year, month, 1)
        dayrange = calendar.monthrange(year, month)
        last_day = datetime.date(year, month, dayrange[1])

        while day < last_day and day < today:
            if prd_helper.is_holiday(day) or not _is_weekday(day):
                day = day + datetime.timedelta(days=1)
                continue
            prd = prd_helper.create_period((day.year, day.month, day.day, start_time.hour, start_time.minute),
                                           (day.year, day.month, day.day, end_time.hour, end_time.minute), interval)
            #logger.debug('   - checking : %s' % prd.get_period_string())
            is_dry, weather_source = is_dry_day(target_station, prd)
            #logger.debug('      > is_dry=%s, weather_station=%s' % (is_dry, weather_source))
            if is_dry:
                normal_days.append(prd)
                weather_sources.append(weather_source)
            day = day + datetime.timedelta(days=1)

    return (normal_days, weather_source)


def _dry_days_for_nighttime(target_station, months, interval):
    """ return dry day list

    :type months: list[(int, int)]
    :type interval: int

    :rtype: (list[pyticas.ttypes.Period], str)
    """

    normal_days = []
    weather_source = ''
    weather_sources = []
    today = datetime.date.today()

    if setting.LATE_NIGHT_START_TIME > setting.LATE_NIGHT_END_TIME:
        delta = 24 - setting.LATE_NIGHT_START_TIME + setting.LATE_NIGHT_END_TIME
    else:
        delta = setting.LATE_NIGHT_END_TIME - setting.LATE_NIGHT_START_TIME

    for idx, (year, month) in enumerate(months):
        sd = datetime.date(year, month, 1)
        dayrange = calendar.monthrange(year, month)
        last_day = datetime.date(year, month, dayrange[1])

        while sd < last_day and sd < today:
            if prd_helper.is_holiday(sd) or not _is_weekday(sd):
                sd = sd + datetime.timedelta(days=1)
                continue
            sdatetime = datetime.datetime(sd.year, sd.month, sd.day, setting.LATE_NIGHT_START_TIME, 0)
            ndatetime = sdatetime + datetime.timedelta(hours=delta)
            prd = prd_helper.create_period((sd.year, sd.month, sd.day, setting.LATE_NIGHT_START_TIME, 0),
                                           (ndatetime.year, ndatetime.month, ndatetime.day, setting.LATE_NIGHT_END_TIME, 0), interval)
            is_dry, weather_source = is_dry_day(target_station, prd)
            if is_dry:
                normal_days.append(prd)
                weather_sources.append(weather_source)
            sd = sd + datetime.timedelta(days=1)

    return (normal_days, weather_source)


def _is_dry(isd_data_list, prd, dry_rate=1.0):
    """

    :type isd_data_list: list[pyticas_noaa.isd.isdtypes.ISDData]
    :type prd: pyticas.ttypes.Period
    :type dry_rate: float
    :return:
    """
    interval_data = isd.apply_interval(isd_data_list, prd)
    wet_precip_codes = [2, 3, 4, 5, 6, 7, 8]
    non_cnt = len([isddata for isddata in interval_data if not isddata])
    if non_cnt: #non_cnt / len(interval_data) * 100 > 10:
        return False
    precip_dry = [isddata for isddata in interval_data if isddata.precipitation_type()[0] not in wet_precip_codes ]
    return len(precip_dry) / len(interval_data) >= dry_rate


def _is_weekday(day):
    """ is weekday (monday to thursday)? (0:monday)

    :param day: datetime.datetime
    :return:
    """
    return 0 <= day.weekday() <= 4
