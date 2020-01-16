# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.normalday
==========================

- module to identify normal dry days when making normal U-K function and night time U-T function
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_ncrtes.core import setting
from pyticas_noaa.isd import isd

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


def get_normal_period(target_station, prd, nd_offset):
    """
    :type target_station: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    :return:
    """
    next_offset = nd_offset
    prev_offset = -1 * nd_offset

    while True:
        cprd = prd.clone()
        cprd.start_date += datetime.timedelta(days=next_offset)
        cprd.end_date += datetime.timedelta(days=next_offset)
        if (cprd.start_date.weekday() in [0, 1, 2, 3, 4] and _is_dry_day(target_station, cprd)):
            return cprd
        next_offset += 1

        cprd = prd.clone()
        cprd.start_date += datetime.timedelta(days=prev_offset)
        cprd.end_date += datetime.timedelta(days=prev_offset)
        if (cprd.start_date.weekday() in [0, 1, 2, 3, 4] and _is_dry_day(target_station, cprd)):
            return cprd
        prev_offset -= 1


def _is_dry_day(target_station, prd):
    """ is dry day?

    How-to::

        check weather through RWIS at first,
        if RWIS is not available, use weather sensor (WEATHER_DEVICE.WS35W25)

    :type target_station: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    :rtype: (bool, str)
    """
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
    if non_cnt:  # non_cnt / len(interval_data) * 100 > 10:
        return False
    precip_dry = [isddata for isddata in interval_data if isddata.precipitation_type()[0] not in wet_precip_codes]
    return len(precip_dry) / len(interval_data) >= dry_rate
