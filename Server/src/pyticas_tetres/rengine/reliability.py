# -*- coding: utf-8 -*-

import datetime
import statistics

from pyticas import rc
from pyticas.moe.moe import VIRTUAL_RNODE_DISTANCE
from pyticas.tool import num
from pyticas.ttypes import Period
from pyticas_tetres.cfg import TT_DATA_INTERVAL
from pyticas_tetres.da.tt import TravelTimeDataAccess
from pyticas_tetres.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

CONGESTED_HOUR_FACTOR = 1.3
N_LIMIT_FOR_SEMI_VAR = 10
RATE_FOR_ON_TIME_RATE = 1.5
MISSING_VALUE = -1

"""
- calculate TTR by regimes for the given time period
"""


def calculate(ttri, extdata_list):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type extdata_list: list[pyticas_tetres.rengine.filter.ftypes.ExtData]
    :rtype: dict
    """
    # Preparing travel time data
    tts = [extdata.tti.tt for extdata in extdata_list if extdata.tti.tt > 0]

    if not tts:
        return None

    # Calculating reference travel times
    avg_tt = statistics.mean(tts)
    median_tt = statistics.median(tts)
    #tt_rate = avg_tt / ttri.route.length()
    tt_rate = avg_tt / milepoint_routeLength(ttri)
    ffs_tt = _tt_by_freeflowspeed(ttri) 
    congested_tts = _congested_travel_times(ffs_tt, tts)
    congested_avg_tt = statistics.mean(congested_tts) if congested_tts else MISSING_VALUE

    # Travel Time Index
    traveltime_index = (congested_avg_tt /ffs_tt ) if congested_tts else  MISSING_VALUE

    # Misery Index
    misery_index = (num.percentile(tts, 0.975) / ffs_tt)

    # Buffer Index and Planning Time Index
    percentiles = [0.5, 0.8, 0.85, 0.9, 0.95]
    ipercentiles = [ int(p*100) for p in percentiles ]
    buffer_indice = {}
    buffer_indice_median = {}
    planning_indice = {}
    percentile_tts = {}
    traveltime_Rate={}
    for idx, pct in enumerate(percentiles):

        ipct = ipercentiles[idx]
        pct_tt = num.percentile(tts, pct)
        percentile_tts[ipct] = pct_tt
        if pct < 0.8:
            continue
        bi = (pct_tt - avg_tt) / avg_tt
        if bi < 0:
            bi = 0
        bim = (pct_tt - median_tt) / median_tt
        if bim < 0:
            bim = 0
        buffer_indice[ipct] = bi
        buffer_indice_median[ipct] = bim
        planning_indice[ipct] = (pct_tt / ffs_tt)
        traveltime_Rate[ipct]= pct_tt/milepoint_routeLength(ttri)
        

    # Level of Travel Time Reliability (FHWA)
    #    - source: https://www.fhwa.dot.gov/tpm/faq.cfm
    lottr = percentile_tts[80] / percentile_tts[50]

    # On-Time-Arrival
    ontime_tt = RATE_FOR_ON_TIME_RATE * num.percentile(tts, 0.5)
    ontime_count = len([tt for tt in tts if tt < ontime_tt])
    on_time_arrival = ontime_count / len(tts)

    # Semi-Variance
    tts_for_sv = [tt for tt in tts if tt > avg_tt]
    if len(tts_for_sv) > N_LIMIT_FOR_SEMI_VAR:
        semi_variance = num.variance(tts_for_sv)
    else:
        semi_variance = -1

    res = {
        'count': len(tts),
        'avg_tt': avg_tt,
        'tt_rate': tt_rate,
        'tt_by_ffs': ffs_tt,
        'congested_hour_factor': CONGESTED_HOUR_FACTOR,
        'congested_avg_tt': congested_avg_tt,
        'congested_count': len(congested_tts),
        'travel_time_index': traveltime_index,
        'buffer_index': buffer_indice,
        'buffer_index_median': buffer_indice_median,
        'travel_time_rate': traveltime_Rate,
        'misery_index': misery_index,
        'on_time_arrival': on_time_arrival,
        'on_time_arrival_count': ontime_count,
        'semi_variance': semi_variance,
        'semi_variance_count': len(tts_for_sv),
        'lottr': lottr,
        'planning_time_index': planning_indice,
        'percentile_tts' : percentile_tts,
        
    }

    return res


def calculate_old(ttri, sdate, edate, stime, etime):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type sdate: datetime.date
    :type edate: datetime.date
    :type stime: datetime.time
    :type etime: datetime.time
    :return:
    """
    logger = getLogger(__name__)
    logger.info('calculate_reliability()')
    sdt = datetime.datetime.combine(sdate, stime)
    edt = datetime.datetime.combine(edate, etime)
    prd = Period(sdt, edt, TT_DATA_INTERVAL)
    years = prd.years()
    ttDAs = {}
    tt_data_all = []
    for y in years:
        if ttDAs.get(y, None):
            tt_da = ttDAs.get(y)
        else:
            tt_da = TravelTimeDataAccess(prd.start_date.year)
            ttDAs[y] = tt_da
        tt_data = tt_da.list_by_period(ttri.id, prd)
        tt_data_all.extend(tt_data)

    for ttd in tt_data_all:
        print(ttd.id, ttd.time, ttd.tt, ttd.speed, ttd.vmt)

    tts = [ttd.tt for ttd in tt_data_all if ttd.tt > 0]
    percentiles = [0.8, 0.85, 0.9, 0.95]
    avg_tt = statistics.mean(tts)
    ffs_tt = _tt_by_freeflowspeed(ttri)
    congested_tts = _congested_travel_times(ffs_tt, tts)
    congested_avg_tt = statistics.mean(congested_tts) if congested_tts else None

    traveltime_index = (congested_avg_tt / ffs_tt) if congested_tts else None
    buffer_indice = {}
    planning_indice = {}
    for pct in percentiles:
        pct_tt = num.percentile(tts, pct)
        buffer_indice[pct] = (pct_tt - avg_tt) / avg_tt
        planning_indice[pct] = (pct_tt / ffs_tt)

    print('Avg TT : ', avg_tt)
    print('TT by FFS : ', ffs_tt)
    print('Travel Time Index : ', traveltime_index)
    print('Buffer Index : ', buffer_indice)
    print('Planning Index : ', planning_indice)


def _congested_travel_times(freeflow_tt, tts):
    """

    :type freeflow_tt: float
    :type tts: list[float]
    :rtype: list[float]
    """
    tt_threshold = freeflow_tt * CONGESTED_HOUR_FACTOR
    return [tt for tt in tts if tt > tt_threshold]


def _tt_by_freeflowspeed(ttri):
    """
    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :rtype: float
    """
    
    
    r = ttri.route
    if not hasattr(r, 'cfg') or not r.cfg:
        r.cfg = rc.route_config.create_route_config(r.rnodes)

    s_limit = 0
    for ridx, node_set in enumerate(r.cfg.node_sets):
        if node_set.node1.rnode and node_set.node1.rnode.is_station():
            s_limit = node_set.node1.rnode.s_limit
            break
       
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

#changes for the route length
def milepoint_routeLength(ttri):
    """
    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :rtype: float
    """
    
    
    r = ttri.route
    if not hasattr(r, 'cfg') or not r.cfg:
        r.cfg = rc.route_config.create_route_config(r.rnodes)

    s_limit = 0
    for ridx, node_set in enumerate(r.cfg.node_sets):
        if node_set.node1.rnode and node_set.node1.rnode.is_station():
            s_limit = node_set.node1.rnode.s_limit
            break
       
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
    return prev_mp

