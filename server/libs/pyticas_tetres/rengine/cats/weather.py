# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas import route
from pyticas_noaa.isd import isd
from pyticas_tetres.da.noaaweather import NoaaWeatherDataAccess
from pyticas_tetres.da.tt_weather import TTWeatherDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.util.noop_context import nonop_with

WEATHER_STATION_DISTANCE_LIMIT = 15


def categorize(ttri, prd, ttdata, **kwargs):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type prd: pyticas.ttypes.Period
    :type ttdata: list[pyticas_tetres.ttypes.TravelTimeInfo]
    :rtype: int
    """
    lock = kwargs.get('lock', nonop_with())

    # prepare : coordinates, target year
    lat, lon = route.center_coordinates(ttri.route)
    year = prd.start_date.year

    # nearby weather station list
    all_isd_stations = isd.get_station_list('MN', None, False)
    isd_stations = isd.find_nearby_station(lat, lon, prd.start_date.date(), all_isd_stations)
    station_idx = 0
    if not isd_stations or not isd_stations[station_idx]:
        getLogger(__name__).warn('! weather.categorize(): no weather information for TTRI(%d)' % (ttri.id))
        return -1

    nearby = isd_stations[station_idx][1]

    cprd = prd.clone()
    cprd.extend_start_hour(1)
    cprd.extend_end_hour(1)

    # decide nearby weather station which has data during a given period
    # by trying to read weather data
    wiss = []
    hours = (len(cprd.get_timeline()) * prd.interval) / 60 / 60
    da_noaa = NoaaWeatherDataAccess(year)

    while True:

        nearby = isd_stations[station_idx][1]
        distance = isd_stations[station_idx][0]
        if distance > WEATHER_STATION_DISTANCE_LIMIT:
            nearby = None
            break

        wis = da_noaa.list_by_period(nearby.usaf, nearby.wban, cprd)
        if len(wis) < hours * 0.6:
            station_idx += 1
            continue

        if wis:
            break
        # if wis:
        #     wiss.append(wis)
        #     if len(wiss) >= 3:
        #         break
        #     continue

        if station_idx >= len(isd_stations) - 1:
            nearby = None
            break

    if not nearby:
        getLogger(__name__).warn('! weather.categorize(): no weather information for TTRI(%d)' % (ttri.id))
        da_noaa.close_session()
        return -1

    da_ttw = TTWeatherDataAccess(year)

    # avoid to save duplicated data
    with lock:
        is_deleted = da_ttw.delete_range(ttri.id, prd.start_date, prd.end_date)
        if not is_deleted or not da_ttw.commit():
            da_ttw.rollback()
            da_ttw.close_session()  # shared session with `da_noaa`
            da_noaa.close_session()
            return -1

    # insert weather data to database
    sidx = 0

    dict_data = []
    for idx, tti in enumerate(ttdata):
        sidx, wd = _find_wd(wis, tti.time, sidx)
        if not wd:
            getLogger(__name__).warn('! weather.categorize(): weather data is not found for (tti.time=%s, usaf=%s, wban=%s)'
                        % (tti.time, wis[-1].usaf, wis[-1].wban))
            continue
        dict_data.append({
            'tt_id': tti.id,
            'weather_id': wd.id
        })

    if dict_data:
        with lock:
            inserted_ids = da_ttw.bulk_insert(dict_data, print_exception=True)
            if not inserted_ids or not da_ttw.commit():
                getLogger(__name__).warn('! weather.categorize() fail to insert categorized data')
                da_ttw.rollback()
                da_ttw.close_session()
                da_noaa.close_session()
                return -1

    da_noaa.close_session()
    da_ttw.close_session()

    return len(dict_data)


def _find_wd(wis, dt, start_idx):
    """

    :type wis: list[NoaaWeatherInfo]
    :type dt: str
    :type start_idx: int
    :rtype: int, NoaaWeatherInfo
    """
    for idx, wd in enumerate(wis[start_idx:]):
        if wd.dtime >= dt:
            return start_idx + idx, wd

    try:
        wdt = (datetime.datetime.strptime(wis[-1].dtime, '%Y-%m-%d %H:%M:%S')
               if isinstance(wis[-1].dtime, str) else wis[-1].dtime)
        dtt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') if isinstance(dt, str) else dt
        diff = wdt - dtt
        diff_in_minute = abs(diff.seconds / 60.0)
        if diff_in_minute <= 30:
            return len(wis) - 1, wis[-1]
    except Exception as ex:
        print(wis[-1])
        raise ex

    return -1, None
