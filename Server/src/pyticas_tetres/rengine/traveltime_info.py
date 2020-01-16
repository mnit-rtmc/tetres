# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import collections
import datetime

import math
from dateutil.relativedelta import relativedelta

from pyticas import rc, period
from pyticas.dr import rwis_scanweb as rwis
from pyticas.moe import moe
from pyticas.moe.imputation import time_avg
from pyticas.moe.moe import VIRTUAL_RNODE_DISTANCE
from pyticas.tool import json
from pyticas_tetres import cfg
from pyticas_tetres.da.route import TTRouteDataAccess
from pyticas_tetres.da.tod_reliability import TODReliabilityDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine import reliability, extractor
from pyticas_tetres.rengine.filter import weather, incident, workzone, specialevent
from pyticas_tetres.rengine.filter.ftypes import ExtFilterGroup
from pyticas_tetres.util.noop_context import nonop_with
from pyticas_tetres.ttypes import TODReliabilityInfo


WC_NORMAL = 1
WC_RAIN = 2
WC_SNOW = 3
WC_STRING = [None, 'Normal', 'Rain', 'Snow']

TOD_REGIME_N_0 = 1 # Dry, Monday
TOD_REGIME_N_123 = 2 # Dry, Tuesday - Thursday
TOD_REGIME_N_4 = 3 # Dry, Friday
TOD_REGIME_N_56 = 4 # Dry, Saturday - Sunday

TOD_REGIME_R_0 = 5 # Rain, Monday
TOD_REGIME_R_123 = 6 # Rain, Tuesday - Thursday
TOD_REGIME_R_4 = 7 # Rain, Friday
TOD_REGIME_R_56 = 8 # Rain, Saturday - Sunday

TOD_REGIME_S_0 = 9 # Snow, Monday
TOD_REGIME_S_123 = 10 # Snow, Tuesday - Thursday
TOD_REGIME_S_4 = 11 # Snow, Friday
TOD_REGIME_S_56 = 12 # Snow, Saturday - Sunday

REGIME_STRING = [ None,
                  'Dry, Monday',
                  'Dry, Tuesday - Thursday',
                  'Dry, Friday',
                  'Dry, Saturday - Sunday',
                  'Rain, Monday',
                  'Rain, Tuesday - Thursday',
                  'Rain, Friday',
                  'Rain, Saturday - Sunday',
                  'Snow, Monday',
                  'Snow, Tuesday - Thursday',
                  'Snow, Friday',
                  'Snow, Saturday - Sunday',
                  ]

def traveltime_route_list():
    """
    :rtype: list[dict]
    """
    da = TTRouteDataAccess()
    ttris = da.list()
    da.close_session()

    res = []
    for ttri in ttris:
        stations = ttri.route.get_stations()

        res.append({
            'id' : ttri.id,
            'name' : ttri.name,
            'start_station' : { 'station_id' : stations[0].station_id,
                                'label' : stations[0].label,
                                'lat' : stations[0].lat,
                                'lon' : stations[0].lon },
            'end_station' : { 'station_id' : stations[-1].station_id,
                              'label' : stations[-1].label,
                              'lat' : stations[-1].lat,
                              'lon' : stations[-1].lon }
        })
    return res


def traveltime_info(ttr_id, weather_type, depart_time, dbsession=None):
    """

    :type ttr_id: int
    :type weather_type: int
    :type depart_time: datetime.datetime
    :rtype: list[dict], list[float]
    """
    logger = getLogger(__name__)
    logger.debug('# public travel time information is requested (route_id=%s, weather_type=%s, depart_time=%s)'
                 % (ttr_id, weather_type, depart_time))

    ttrda = TTRouteDataAccess(session=dbsession)
    ttri = ttrda.get_by_id(ttr_id)

    if weather_type:
        try:
            weather_type = int(weather_type)
        except:
            weather_type = None

    if not weather_type or weather_type not in [WC_NORMAL, WC_RAIN, WC_SNOW]:
        weather_type = _weather(depart_time, ttri.route)

    regime_type = _regime_type(weather_type, depart_time)

    logger.debug('  > regime type = %d (%s)' % (regime_type, REGIME_STRING[regime_type]))

    da = TODReliabilityDataAccess(session=ttrda.get_session())

    tods = da.list_by_route(ttr_id, regime_type)
    res = []
    dbg_from, dbg_to = 60, len(tods) - 12
    for idx, tod in enumerate(tods):
        tod_res = json.loads(tod.result)
        if not tod_res:
            continue
        if idx >= dbg_from and idx < dbg_to:
            logger.debug('   -  time=%02d:%02d, avg_tt=%s, 95%%p_tt=%s, count=%s' %
                         (tod.hour, tod.minute, tod_res['avg_tt'],
                          tod_res['percentile_tts']['95'], tod_res['count']))

        res.append({'hour' : tod.hour, 'minute' : tod.minute, 'avg_tt' : _roundup(tod_res['avg_tt']),
                    'p95_tt' : _roundup(tod_res['percentile_tts']['95']),
                   'p90_tt' : _roundup(tod_res['percentile_tts']['90']),
                   'p85_tt' : _roundup(tod_res['percentile_tts']['85']),
                   'p80_tt' : _roundup(tod_res['percentile_tts']['80']),
                    'count' : tod_res['count']})


    today_to = depart_time
    now = datetime.datetime.now()

    if today_to >= now:
        today_to = now

    # 5 minute interval
    delta = (today_to.minute - math.floor(today_to.minute / 5) * 5) * 60 + today_to.second
    today_to = today_to - datetime.timedelta(seconds=delta)

    try:
        today_from = datetime.datetime.combine(today_to.date(), datetime.time(0, 0, 0))
        prd = period.Period(today_from, today_to, cfg.TT_DATA_INTERVAL)
        tts = moe.travel_time(ttri.route, prd)
        tts = moe.imputation(tts, imp_module=time_avg)
        traveltimes = _moving_average(tts[-1].data, 5)

    except Exception as ex:
        getLogger(__name__).warn('error to calculate travel times')
        traveltimes = []

    traveltimes = _roundup(traveltimes)

    ttrda.close_session()

    return res[60:-12], traveltimes[60:]



def _roundup(arr):
    if isinstance(arr, collections.Iterable):
        return [ round(v, 2) if isinstance(v, float) or isinstance(v, int) else None for v in arr ]
    else:
        return round(arr, 2) if isinstance(arr, float) or isinstance(arr, int) else None

def calculate_TOD_reliabilities(ttr_id, today, **kwargs):
    """

    :type ttr_id: int
    :type today: datetime.datetime
    """
    ttri = _tt_route(ttr_id)
    sdate, edate, stime, etime = _time_period(today)

    lock = kwargs.get('lock', nonop_with())
    # _calculate_for_a_regime(ttri, TOD_REGIME_N_0, WC_RAIN, sdate, edate, stime, etime, (1, 2, 3))  # Normal, Tuesday-Thursday

    _calculate_for_a_regime(ttri, TOD_REGIME_N_0, sdate, edate, stime, etime, (0,), lock=lock)  # Normal, Monday
    _calculate_for_a_regime(ttri, TOD_REGIME_N_123, sdate, edate, stime, etime, (1, 2, 3), lock=lock)  # Normal, Tuesday-Thursday
    _calculate_for_a_regime(ttri, TOD_REGIME_N_4, sdate, edate, stime, etime, (4,), lock=lock)  # Normal, Friday
    _calculate_for_a_regime(ttri, TOD_REGIME_N_56, sdate, edate, stime, etime, (5, 6), lock=lock)  # Normal, Saturday-Sunday

    _calculate_for_a_regime(ttri, TOD_REGIME_R_0, sdate, edate, stime, etime, (0,), lock=lock)  # Rain, Monday
    _calculate_for_a_regime(ttri, TOD_REGIME_R_123, sdate, edate, stime, etime, (1, 2, 3), lock=lock)  # Rain, Tuesday-Thursday
    _calculate_for_a_regime(ttri, TOD_REGIME_R_4, sdate, edate, stime, etime, (4,), lock=lock)  # Rain, Friday
    _calculate_for_a_regime(ttri, TOD_REGIME_R_56, sdate, edate, stime, etime, (5, 6), lock=lock)  # Rain, Saturday-Sunday

    _calculate_for_a_regime(ttri, TOD_REGIME_S_0, sdate, edate, stime, etime, (0,), lock=lock)  # Snow, Monday
    _calculate_for_a_regime(ttri, TOD_REGIME_S_123, sdate, edate, stime, etime, (1, 2, 3), lock=lock)  # Snow, Tuesday-Thursday
    _calculate_for_a_regime(ttri, TOD_REGIME_S_4, sdate, edate, stime, etime, (4,), lock=lock)  # Snow, Friday
    _calculate_for_a_regime(ttri, TOD_REGIME_S_56, sdate, edate, stime, etime, (5, 6), lock=lock)  # Snow, Saturday-Sunday


def _calculate_for_a_regime(ttri, regime_type, sdate, edate, stime, etime,
                            target_days=(1, 2, 3), except_dates=(), remove_holiday=True, **kwargs):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type regime_type: int
    :type sdate: datetime.date
    :type edate: datetime.date
    :type stime: datetime.time
    :type etime: datetime.time
    :type target_days: tuple[int]
    :rtype: bool
    """
    # Regime Filter
    ext_filter = _ext_filter(regime_type)

    lock = kwargs.get('lock', nonop_with())

    extractor.extract_tt(ttri.id,
                         sdate,
                         edate,
                         stime,
                         etime,
                         [ext_filter],
                         target_days=target_days,
                         remove_holiday=remove_holiday,
                         except_dates=except_dates)

    # print('# ', ext_filter.label)
    da = TODReliabilityDataAccess()

    # delete existings
    ttwis = [ ttwi for ttwi in da.list_by_route(ttri.id, regime_type) ]
    ttwi_ids = [ v.id for v in ttwis ]
    with lock:
        is_deleted = da.delete_items(ttwi_ids)
        if not is_deleted or not da.commit():
            return False

    tod_res = []
    cursor = datetime.datetime.combine(datetime.date.today(), stime)
    cursor += datetime.timedelta(seconds=cfg.TT_DATA_INTERVAL)
    edatetime = datetime.datetime.combine(datetime.date.today(), etime)
    dict_data = []
    while cursor <= edatetime:
        ctime = cursor.strftime('%H:%M:00')
        res = [extdata for extdata in ext_filter.whole_data if ctime == extdata.tti.time.strftime('%H:%M:00') ]
        ttr_res = reliability.calculate(ttri, res)
        tod_res.append(ttr_res)
        dict_data.append({
            'regime_type': regime_type,
            'route_id': ttri.id,
            'hour': cursor.hour,
            'minute': cursor.minute,
            'result': json.dumps(ttr_res),
        })
        cursor += datetime.timedelta(seconds=cfg.TT_DATA_INTERVAL)

    with lock:
        is_inserted = da.bulk_insert(dict_data)
        if not is_inserted or not da.commit():
            return False

    return True


def _tt_route(ttr_id):
    """

    :type ttr_id: int
    :rtype: pyticas_tetres.ttypes.TTRouteInfo
    """
    ttrda = TTRouteDataAccess()
    ttri = ttrda.get_by_id(ttr_id)
    #ttri = ttrda.list()[0]
    ttrda.close_session()
    return ttri


def _time_period(today):
    """
    :type today: datetime.datetime
    :rtype: (datetime.date, datetime.date, datetime.time, datetime.time)
    """
    yesterday = today - datetime.timedelta(days=1)
    year_ago = today - relativedelta(years=1)
    sdate = year_ago.date()
    edate = yesterday.date()
    stime = datetime.time(0, 0, 0)
    etime = datetime.time(23, 55, 0)

    return sdate, edate, stime, etime


def _tt_by_freeflowspeed(ttri):
    """
    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :rtype: float
    """
    r = ttri.route
    if not r.cfg:
        r.cfg = rc.route_config.create_route_config(r.rnodes)

    s_limit = 0
    tt = 0
    prev_mp = -1
    for ridx, node_set in enumerate(r.cfg.node_sets):
        if node_set.node1.rnode and node_set.node1.rnode.is_station():
            s_limit = node_set.node1.rnode.s_limit
        if not ridx:
            continue
        if prev_mp == node_set.mile_point:
            continue
        prev_mp = node_set.mile_point
        tt += (VIRTUAL_RNODE_DISTANCE / s_limit)

    return tt * 60


def _ext_filter(regime_type):
    """

    :type regime_type: int
    :rtype: ExtFilterGroup
    """
    ext_filter = ExtFilterGroup([
        workzone.no_workzone(distance_limit=1.0),
        incident.no_incident(distance_limit=1.0, keep_result_in_minute=120),
        specialevent.no_specialevent(),
    ], 'For Info Service')

    if regime_type in [ TOD_REGIME_N_0, TOD_REGIME_N_123, TOD_REGIME_N_4, TOD_REGIME_N_56]:
        ext_filter.ext_filters.append(weather.normal_implicit())
    elif regime_type == [ TOD_REGIME_R_0, TOD_REGIME_R_123, TOD_REGIME_R_4, TOD_REGIME_R_56 ]:
        ext_filter.ext_filters.append(weather.type_rain())
    elif regime_type == [TOD_REGIME_S_0, TOD_REGIME_S_123, TOD_REGIME_S_4, TOD_REGIME_S_56 ]:
        ext_filter.ext_filters.append(weather.type_snow())

    return ext_filter


def _regime_type(weather_type, depart_time):
    """

    :type weather_type: int
    :type depart_time: datetime.datetime
    :rtype:
    """
    regimes = [
        [ TOD_REGIME_N_0, TOD_REGIME_R_0, TOD_REGIME_S_0 ],
        [ TOD_REGIME_N_123, TOD_REGIME_R_123, TOD_REGIME_S_123 ],
        [ TOD_REGIME_N_4, TOD_REGIME_R_4, TOD_REGIME_S_4 ],
        [ TOD_REGIME_N_56, TOD_REGIME_R_56, TOD_REGIME_S_56 ],
    ]

    weekday_selection = [ 0, 1, 1, 1, 2, 3, 3 ]
    weather_selection = [ None, 0, 1, 2 ]

    weekday_idx = weekday_selection[depart_time.weekday()]
    weather_idx = weather_selection[weather_type]

    return regimes[weekday_idx][weather_idx]


def _weather(depart_time, r):
    """
    :type depart_time: datetime.datetime
    :type r: pyticas.ttypes.Route
    :return:
    :rtype:
    """
    from_time = depart_time - datetime.timedelta(hours=1)
    prd = period.Period(from_time, depart_time, interval=300)
    stations = r.get_stations()
    n_stations = len(stations)
    center_station = stations[int(n_stations/2)]
    sites = rwis.find_nearby_sites(center_station.lat, center_station.lon)
    nearby_site = sites[0]
    getLogger(__name__).debug('  - RWIS station : site_id=%d, lat=%f, lon=%f, distance=%f'
          % (nearby_site.site_id, nearby_site.lat, nearby_site.lon, nearby_site.distance_to_target))

    wd = rwis.get_weather(nearby_site, prd)

    surface_status = wd.get_surface_statuses()

    if wd.is_rain(0.5) or (surface_status and wd._contains(['rain', 'wet'], surface_status[-1], ['freezing'])):
        return WC_RAIN
    elif wd.is_snow(0.5) or (surface_status and wd._contains(['snow', 'slush', 'ice', 'chemical wet', 'freezing'], surface_status[-1], ['freezing'])):
        return WC_SNOW
    else:
        return WC_NORMAL


def _moving_average(data, sw = 3) :
    prev_ma = data[0]
    res =[]
    smoothing = 2.0 / (sw + 1.0)
    for v in data:
        ma = prev_ma + smoothing * (v - prev_ma)
        prev_ma = ma
        res.append(ma)

    return res