# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import numpy as np

from pyticas.moe import moe
from pyticas.moe.imputation import time_avg
from pyticas.ttypes import Route
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.core.est.target import get_target_stations, get_target_detectors
from pyticas_ncrtes.logger import getLogger

DEBUG_MODE = False

###########################################
# public functions
###########################################
def load_data(edata_list, snow_start_index, snow_end_index, s_limit, **kwargs):
    """
    :param edata_list: ESTData list in a same section
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :type snow_start_index: int
    :type snow_end_index: int
    :type s_limit: int
    :rtype: (numpy.ndarray, numpy.ndarray, numpy.ndarray,
             numpy.ndarray, numpy.ndarray, numpy.ndarray,
             list[pyticas.ttypes.RNodeObject],
             list[RNodeData], list[RNodeData]
             )
    """
    skip_check_ncrt = kwargs.get('skip_check_ncrt', False)
    sw = kwargs.get('sw', 41)

    min_ncrt, max_ncrt = None, None

    # find min-max NCRT in the same section
    #   : to be used in filtering stations
    if not skip_check_ncrt:
        min_ncrt, max_ncrt = _minmax_ncrt(edata_list)
        if min_ncrt is None:
            return None, None, None, None, None, None, None, None, None

    # detector checker
    stations, dc = _detector_checker(edata_list)

    # time period
    prd = edata_list[0].snow_event.data_period

    # filter missing and over-speed stations
    stations = _filter_stations(stations, prd, dc)

    if not any(stations):
        return None, None, None, None, None, None, None, None, None

    # load sectionwide data
    _route, speeds, densities = _load_data(stations, prd, dc)

    # filter data by speed at ncrt
    if not skip_check_ncrt:
        _route, speeds, densities = _filter_stations_by_speed_at_ncrt(_route,
                                                                      speeds, densities,
                                                                      min_ncrt, max_ncrt)
    if not any(speeds):
        return None, None, None, None, None, None, None, None, None

    # fix fluctuation in low-k area
    speeds, densities = _fix_speed_fluctuation(speeds, densities)

    # remove diffrent speed pattern data
    _route, speeds, densities = _filter_stations_by_speed_pattern(_route,
                                                                  speeds, densities,
                                                                  snow_start_index, snow_end_index,
                                                                  s_limit)

    # add virtual rnodes
    speeds = moe.add_virtual_rnodes(speeds, _route)
    densities = moe.add_virtual_rnodes(densities, _route)

    # make average u, k data
    avg_us, avg_ks = _avg_uk(speeds, densities)

    us, ks = np.array(avg_us), np.array(avg_ks)
    ks, us = data_util.fix_rapid_fluctuation(ks, us, udiff_threshold=7)
    sus = data_util.smooth(us, sw)
    sks = data_util.smooth(ks, sw)
    qus = data_util.stepping(sus, 5)
    qus = np.array(qus)
    qks = data_util.stepping(sks, 3)
    qks = np.array(qks)

    return us, ks, sus, sks, qus, qks, stations, speeds, densities


def find_alternatives_for_section(edata_list, ks, us, sks, sus, qks, qus, **kwargs):
    """

    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :type ks:  numpy.ndarray
    :type us:  numpy.ndarray
    :type sks:  numpy.ndarray
    :type sus:  numpy.ndarray
    :type qks:  numpy.ndarray
    :type qus:  numpy.ndarray
    :type sw:  int
    :rtype: int, float, int, int, int
    """
    s_limit = edata_list[0].target_station.s_limit
    snow_start_idx = edata_list[0].snow_event.snow_start_index
    snow_end_idx = edata_list[0].snow_event.snow_end_index

    search_from, search_to, widx = kwargs.get('search_from', None), kwargs.get('search_to', None), kwargs.get('widx',
                                                                                                              None)
    if search_from is None:
        search_from, search_to, widx = _ncrt_search_range(edata_list)
    elif widx is None:
        widx = search_from

    if not search_from:
        return None, None, None, None, None

    return find_alternatives(sus, sks, qus, qks, s_limit, search_from, search_to, snow_start_idx, widx, snow_end_idx)



def find_alternatives(sus, sks, qus, qks, s_limit, search_from, search_to, snow_start_index, widx, snow_end_idx):
    """
    :type sks:  numpy.ndarray
    :type sus:  numpy.ndarray
    :type qks:  numpy.ndarray
    :type qus:  numpy.ndarray
    :type s_limit: int
    :param search_from: ncrt search start index
    :type search_from: int
    :param search_to: ncrt search end index
    :type search_to: int
    :type snow_start_index: int
    :type widx: int
    :type snow_end_idx: int
    :rtype: int, float, int, int, int
    """
    snowday_ffs_idx, snowday_ffs, pst, ssbpst, ssapst = None, None, None, None, None

    snowday_ffs_idx, snowday_ffs = _find_ffs(sus, sks, qus, qks, s_limit, search_from, search_to, snow_end_idx)
    if not snowday_ffs:
        return snowday_ffs_idx, snowday_ffs, pst, ssbpst, ssapst

    pst = _find_pst(sus, sks, qus, qks, s_limit, search_from, search_to, snowday_ffs_idx, snowday_ffs)

    ssbpst = _find_stable_before_pst(sus, sks, qus, qks, s_limit, search_from, search_to, pst, widx, snowday_ffs_idx, snowday_ffs)
    ssapst = _find_stable_after_pst(sus, sks, qus, qks, s_limit, search_from, search_to, pst, widx, snowday_ffs_idx, snowday_ffs)

    return snowday_ffs_idx, snowday_ffs, pst, ssbpst, ssapst


def adjust_with_qdata(qdata, sdata, target_idx, target_u=None):
    """

    :type qdata: numpy.ndarray
    :type sdata: numpy.ndarray
    :type target_idx: int
    :type target_u: float
    :rtype: int
    """
    if target_idx is None:
        return None

    logger = getLogger(__name__)

    stick = None
    qu = qdata[target_idx]
    for idx in range(target_idx, 0, -1):
        cu = qdata[idx]
        if abs(qu - cu) < 2:
            continue
        stick = idx + 1
        break

    if not stick:
        return None

    target_u = (target_u or qu)
    for tidx in range(stick, len(qdata)):
        if sdata[tidx] >= target_u or tidx >= target_idx:
            logger.debug('  -> adjust point %d -> %d' % (target_idx, tidx))
            return tidx

    # never reaches to here
    logger.debug('  -> adjust point %d -> %d !!' % (target_idx, stick))
    return stick


###########################################
# sub functions for `load_data()`
###########################################
def _minmax_ncrt(edata_list):

    ncrts = [edata.ncrt_search_eidx for edata in edata_list if edata.ncrt]

    if not any(ncrts):
        return None, None

    min_ncrt = min(ncrts)
    max_ncrt = max(ncrts)

    if min_ncrt == max_ncrt:
        min_ncrt -= setting.INTV30MIN
        max_ncrt += setting.INTV30MIN

    return min_ncrt, max_ncrt


def _detector_checker(edata_list):
    """
    :param edata_list:
    :rtype: list[pyticas.ttypes.RNodeObject], function
    """
    infra = ncrtes.get_infra()
    stations_in_a_corridor = [rn.station_id for rn in get_target_stations(edata_list[0].target_station.corridor.name)]

    if len(edata_list) > 1:
        station_filter = lambda rn: rn.station_id in stations_in_a_corridor
        break_filter = lambda rn: rn.station_id == edata_list[-1].target_station.station_id
        stations = list(infra.geo.iter_to_downstream(edata_list[0].target_station,
                                                     filter=station_filter, break_filter=break_filter))
        stations = [edata_list[0].target_station] + stations + [edata_list[-1].target_station]
    else:
        stations = [edata_list[0].target_station]

    if not any(stations):
        return None, None, None, None, None, None, None, None, None

    target_detectors = []
    for idx, st in enumerate(stations):
        edatas = [edata for edata in edata_list if edata.target_station.station_id == st.station_id]
        if edatas and edatas[0].target_station_info.detectors:
            det_names = edatas[0].target_station_info.detectors.split(',')
        else:
            dets = get_target_detectors(st)
            det_names = [det.name for det in dets]

        if det_names:
            target_detectors.extend(det_names)

    # make detector checker
    return stations, lambda det: det.name in target_detectors


def _filter_stations(stations, prd, dc):
    """
    :type stations: list[pyticas.ttypes.RNodeObject]
    :type prd: pyticas.ttypes.Period
    :type dc: callable
    :rtype: list[pyticas.ttypes.RNodeObject], function
    """
    infra = ncrtes.get_infra()
    to_be_removed = []
    for st in stations:
        rndata = infra.rdr.get_speed(st, prd, dc=dc)
        if infra.is_missing(rndata.data):
            to_be_removed.append(st.station_id)
        sus = data_util.smooth(rndata.data, setting.SMOOTHING_SIZE)
        over_speeds = np.where(sus > (st.s_limit + 30))[0]
        if len(over_speeds) > setting.INTV3HOUR:
            to_be_removed.append(st.station_id)

    return [st for st in stations if st.station_id not in to_be_removed]


def _load_data(stations, prd, dc):
    """
    :type stations: list[pyticas.ttypes.RNodeObject]
    :type prd: pyticas.ttypes.Period
    :type dc: callable
    :rtype: pyticas.ttypes.Route, list[pyticas.ttypes.RNodeData], list[pyticas.ttypes.RNodeData]
    """
    r = Route()
    r.rnodes = stations

    speeds = moe.speed(r, prd, detector_checker=dc)
    speeds = moe.imputation(speeds)
    speeds = moe.imputation(speeds, imp_module=time_avg, allowed_time_diff=100)

    densities = moe.density(r, prd, detector_checker=dc)
    densities = moe.imputation(densities)
    densities = moe.imputation(densities, imp_module=time_avg, allowed_time_diff=100)

    return r, speeds, densities


def _filter_stations_by_speed_at_ncrt(r, speeds, densities, min_ncrt, max_ncrt):
    """
    :type r: pyticas.ttypes.Route
    :type speeds: list[pyticas.ttypes.RNodeData]
    :type densities: list[pyticas.ttypes.RNodeData]
    :type min_ncrt: int
    :type max_ncrt: int
    :rtype: pyticas.ttypes.Route, list[pyticas.ttypes.RNodeData], list[pyticas.ttypes.RNodeData]
    """
    to_be_removed = []
    for idx, udata in enumerate(speeds):
        avg_u_around_ncrt = np.mean(udata.data[min_ncrt:max_ncrt])
        if avg_u_around_ncrt < min(udata.speed_limit - 10, 40):
            to_be_removed.append(idx)

    speeds = [udata for idx, udata in enumerate(speeds) if idx not in to_be_removed]
    densities = [kdata for idx, kdata in enumerate(densities) if idx not in to_be_removed]
    r.rnodes = [st for idx, st in enumerate(r.rnodes) if idx not in to_be_removed]

    return r, speeds, densities


def _fix_speed_fluctuation(speeds, densities):
    """

    :type speeds: list[pyticas.ttypes.RNodeData]
    :type densities: list[pyticas.ttypes.RNodeData]
    :rtype: list[pyticas.ttypes.RNodeData], list[pyticas.ttypes.RNodeData]
    """
    for idx, udata in enumerate(speeds):
        kdata = densities[idx]
        ks, us = data_util.fix_rapid_fluctuation(np.array(kdata.data),
                                                 np.array(udata.data),
                                                 udiff_threshold=7)
        speeds[idx].data = us.tolist()
    return speeds, densities


def _filter_stations_by_speed_pattern(r, speeds, densities, snow_start_index, snow_end_index, s_limit):
    """
    :type r: pyticas.ttypes.Route
    :type speeds: list[pyticas.ttypes.RNodeData]
    :type densities: list[pyticas.ttypes.RNodeData]
    :type snow_start_index: int
    :type snow_end_index: int
    :type s_limit: int
    :rtype: pyticas.ttypes.Route, list[pyticas.ttypes.RNodeData], list[pyticas.ttypes.RNodeData]
    """
    logger = getLogger(__name__)
    n_data = len(speeds[0].data)
    _avg_us = []
    for idx in range(n_data):
        udata = [speed.data[idx] for speed in speeds if speed.data[idx] > 0]
        if any(udata):
            _avg_us.append(np.mean(udata))
        else:
            _avg_us.append(-1)

    minu_idx = np.argmin(_avg_us[snow_start_index:snow_end_index]) + snow_start_index
    n_over_slimit = []
    to_be_removed = []
    really_to_be_removed = []

    for idx, udata in enumerate(speeds):
        ar = np.array(udata.data)
        wh = np.where(ar[minu_idx:] > s_limit)
        n_over_slimit.append(len(wh[0]))
        su = data_util.smooth(ar, setting.SMOOTHING_SIZE)
        if len(np.where(su < s_limit - 5)[0]) < setting.INTV30MIN and max(su) - min(su) < 10:
            to_be_removed.append(idx)
            really_to_be_removed.append(idx)

    n_over_avg = np.mean(n_over_slimit)
    for idx, n_over in enumerate(n_over_slimit):
        if n_over_avg - n_over > setting.INTV2HOUR:
            to_be_removed.append(idx)

    if len(to_be_removed) != len(speeds) and to_be_removed:
        logger.debug('=> all stations : %s' % [udata.station_id for idx, udata in enumerate(speeds)])
        logger.debug('=> removed stations : %s' % [udata.station_id for idx, udata in enumerate(speeds) if idx in to_be_removed])
        speeds = [udata for idx, udata in enumerate(speeds) if idx not in to_be_removed]
        densities = [kdata for idx, kdata in enumerate(densities) if idx not in to_be_removed]
        r.rnodes = [st for idx, st in enumerate(r.rnodes) if idx not in to_be_removed]
    elif really_to_be_removed and len(to_be_removed) == len(speeds):
        logger.debug('=> all stations : %s' % [udata.station_id for idx, udata in enumerate(speeds)])
        logger.debug('=> removed stations : %s' % [udata.station_id for idx, udata in enumerate(speeds) if idx in really_to_be_removed])
        speeds = [udata for idx, udata in enumerate(speeds) if idx not in really_to_be_removed]
        densities = [kdata for idx, kdata in enumerate(densities) if idx not in really_to_be_removed]
        r.rnodes = [st for idx, st in enumerate(r.rnodes) if idx not in really_to_be_removed]

    logger.debug('remains : %s' % [udata.station_id for idx, udata in enumerate(speeds)])

    return r, speeds, densities


def _avg_uk(speeds, densities):
    """

    :type speeds: list[pyticas.ttypes.RNodeData]
    :type densities: list[pyticas.ttypes.RNodeData]
    :rtype: list[float], list[float]
    """
    n_data = len(speeds[0].data)
    avg_us, avg_ks = [], []
    for r in range(n_data):
        udata = [speed.data[r] for speed in speeds if speed.data[r] > 0]
        if any(udata):
            avg_us.append(np.mean(udata))
        else:
            avg_us.append(-1)
        kdata = [density.data[r] for density in densities if density.data[r] > 0]
        if any(kdata):
            avg_ks.append(np.mean(kdata))
        else:
            avg_ks.append(-1)
    return avg_us, avg_ks





###########################################
# sub functions for `load_data()`
###########################################
def _ncrt_search_range(edata_list):
    """
    :param edata_list: ESTData list in a same section
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :rtype: int, int, int
    """
    sidxs = [edata.ncrt_search_sidx for edata in edata_list if edata.ncrt_search_sidx]
    eidxs = [edata.ncrt_search_eidx for edata in edata_list if edata.ncrt_search_eidx]
    widxs = [edata.worst_ratio_idx for edata in edata_list if edata.worst_ratio_idx]
    return (min(sidxs) if any(sidxs) else None,
            max(eidxs) if any(eidxs) else None,
            min(widxs) if any(widxs) else None)


def _find_ffs(sus, sks, qus, qks, s_limit, search_from, search_to, snow_end_idx):
    """

    :type sus: numpy.ndarray
    :type sks: numpy.ndarray
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :type s_limit: int
    :type search_from: int
    :type search_to: int
    :type snow_end_idx: int
    :rtype: (int, float)
    """
    logger = getLogger(__name__)

    kth = 25
    indices = np.array(range(len(sus)))
    t_margin = setting.INTV1HOUR

    # Ur: May-Recovered-Speed
    Ur = None
    tus = sus[snow_end_idx:-t_margin]
    tks = sks[snow_end_idx:-t_margin]
    wsidx, weidx, whs = _where(tks < kth)
    if wsidx is not None:
        Ur = np.mean(tus[whs])
    if not Ur:
        Ur = s_limit


    # collect recovered-traffic data
    _search_to = search_to
    for idx in range(10):
        # find over-may-recovered-speed area
        wh = np.where(sus[search_from:_search_to+setting.INTV1HOUR*idx] > Ur)
        search_to = _search_to+setting.INTV1HOUR*idx
        if any(wh[0]) and len(wh[0]) > setting.INTV1HOUR:
            break

    # use may-recovered-speed if no over-speed-limit data
    if not any(wh[0]):
        wh = np.where(sus[search_from:] > s_limit)
        Ur = s_limit

    if not any(wh[0]):
        return None, None

    search_from = wh[0][0] + search_from

    # collect speed data over may-recovered-speed
    tus = sus[search_from:search_to]
    tus = tus[tus > Ur]

    if not any(tus) or len(tus) < setting.INTV30MIN:
        return None, None

    # find ffs using KDE
    speeds, freqs = _kde(tus)
    if not any(freqs):
        return None, None

    maxpoints = data_util.max_points(freqs)
    if any(maxpoints):
        local_max_us = np.array([speeds[idx] for idx in maxpoints])
        ffs = local_max_us[-1]
        # diffs = abs(local_max_us - maxu)
        # min_diff_idx = np.argmin(diffs)
        # ffs = local_max_us[min_diff_idx]
    else:
        max_freq_idx = np.argmax(freqs).item()
        ffs = speeds[max_freq_idx]

    # determine time when reaching FFS
    ffs_idx = _reaching_point(sus, ffs, search_from, search_to, t_intv=setting.INTV1HOUR, try_alt=True)

    logger.debug(' - snowday FFS idx (candidate1) = %s' % ffs_idx)

    # if not found, try to find just over-FFS point
    if ffs_idx is None:
        wh = np.where(qus[search_from:] >= ffs)
        if not any(wh[0]):
            wh = np.where(sus[search_from:] >= ffs)

        if any(wh[0]):
            ffs_idx = wh[0][0] + search_from

    logger.debug('  - snowday FFS idx (Candidate2) = %s' % ffs_idx)

    affs_idx = adjust_with_qdata(qus, sus, ffs_idx, ffs)
    if affs_idx:
        ffs_idx = affs_idx

    if ffs_idx < search_to:
        diffs = ffs - sus[ffs_idx:search_to]
        if len(diffs[diffs > 10]) > setting.INTV30MIN:
            minu_idx = np.argmin(sus[ffs_idx:search_to]).item() + ffs_idx
            return _find_ffs(sus, sks, qus, qks, s_limit, minu_idx, search_to, snow_end_idx)

    logger.debug('  - snowday FFS = %.1f' % ffs)
    logger.debug('  - snowday FFS Idx = %s' % ffs_idx)

    return (ffs_idx, ffs)



def _find_ffs_v0(sus, sks, qus, qks, s_limit, search_from, search_to, snow_end_idx):
    """

    :type sus: numpy.ndarray
    :type sks: numpy.ndarray
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :type s_limit: int
    :type search_from: int
    :type search_to: int
    :type snow_end_idx: int
    :rtype: (int, float)
    """
    logger = getLogger(__name__)

    kth = 25

    maxu = max(qus[search_from:search_to])

    may_recovered_speed = None

    tus = sus[snow_end_idx:snow_end_idx + setting.INTV4HOUR]
    tks = sks[snow_end_idx:snow_end_idx + setting.INTV4HOUR]

    wsidx, weidx, whs = _where(tks < kth)
    if wsidx:
        may_recovered_speed = np.mean(tus[whs])

    if not may_recovered_speed:
        may_recovered_speed = s_limit

    # find over-may-recovered-speed area
    wh = np.where(sus[search_from:] > may_recovered_speed)

    # use may-recovered-speed if no over-speed-limit data
    if not any(wh[0]):
        wh = np.where(qus[search_from:] > s_limit)
        may_recovered_speed = s_limit

    if not any(wh[0]):
        return None, None

    _search_from = wh[0][0] + search_from

    if _search_from > search_to:
        search_to = len(sus) - 1

    # collect speed data over may-recovered-speed
    tus = sus[_search_from:search_to]
    tus = tus[tus > may_recovered_speed]

    if not any(tus):  # or len(tus) < setting.INTV1HOUR:
        logger.warning('Freeflow speed may be low : %d(%d) - %d' % (_search_from, search_from, search_to))
        tus = sus[_search_from:search_to]
        # if data is not sufficient, try again after extending range
        if not any(tus):
            tus = sus[search_from:search_to]
            _search_from = search_from

    if not any(tus) or len(tus) < setting.INTV30MIN:
        tus = sus[_search_from:]
        tus = tus[tus > may_recovered_speed]
        search_to = len(sus) - 1

    if not any(tus) or len(tus) < setting.INTV30MIN:
        return None, None

    # find ffs using KDE
    speeds, freqs = _kde(tus)
    if not any(freqs):
        return None, None

    maxpoints = data_util.max_points(freqs)
    if any(maxpoints):
        local_max_us = np.array([speeds[idx] for idx in maxpoints])
        diffs = abs(local_max_us - maxu)
        min_diff_idx = np.argmin(diffs)
        ffs = local_max_us[min_diff_idx]
    else:
        max_freq_idx = np.argmax(freqs).item()
        ffs = speeds[max_freq_idx]

    # determine time when reaching FFS
    ffs_idx = _reaching_point(sus, ffs, _search_from, search_to, t_intv=setting.INTV1HOUR, try_alt=True)

    logger.debug(' - snowday FFS idx (candidate1) = %s' % ffs_idx)

    # if not found, try to find just over-FFS point
    if ffs_idx is None:
        wh = np.where(qus[_search_from:search_to] >= ffs)
        if not any(wh[0]):
            wh = np.where(sus[_search_from:search_to] >= ffs)

        if any(wh[0]):
            ffs_idx = wh[0][0] + _search_from

    logger.debug('  - snowday FFS idx (Candidate2) = %s' % ffs_idx)

    affs_idx = adjust_with_qdata(qus, sus, ffs_idx, ffs)
    if affs_idx:
        ffs_idx = affs_idx

    logger.debug('  - snowday FFS = %.1f' % ffs)
    logger.debug('  - snowday FFS Idx = %s' % ffs_idx)

    return (ffs_idx, ffs)


def _find_pst(sus, sks, qus, qks, s_limit, search_from, search_to, snowday_ffs_idx, snowday_ffs):
    """

    :type sus: numpy.ndarray
    :type sks: numpy.ndarray
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :type s_limit: int
    :type search_from: int
    :type search_to: int
    :type snowday_ffs_idx: int
    :type snowday_ffs: float
    :rtype: int
    """
    logger = getLogger(__name__)
    pst = _reaching_point(sus, s_limit,
                          search_from, search_to,
                          t_intv=setting.INTV1HOUR, try_alt=True)

    logger.debug('the found PST : %s' % pst)
    if pst:

        apst = adjust_with_qdata(qus, sus, pst, s_limit)
        if apst:
            pst = apst

        unders = np.where(sus[pst:snowday_ffs_idx] < s_limit)[0] + pst
        if any(unders):
            last_under = unders[-1]
            peaku = max(sus[pst:last_under])
            if snowday_ffs - peaku > 5 and peaku - min(sus[pst:last_under]) > 5:
                logger.debug(' - PST is detected too early(1) : %d -> %d' % (pst, last_under + 1))
                pst = last_under + 1
            elif snowday_ffs_idx - pst > setting.INTV5HOUR and peaku - min(sus[pst:last_under]) > 5:
                pst = last_under + 1
                logger.debug(' - PST is detected too early(2) : %d -> %d' % (pst, last_under + 1))


        logger.debug('The adjusted PST : %s' % pst)

    return pst


def _find_stable_before_pst(sus, sks, qus, qks, s_limit, search_from, search_to, pst, widx, snowday_ffs_idx, snowday_ffs):
    """

    :type sus: numpy.ndarray
    :type sks: numpy.ndarray
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :type s_limit: int
    :type search_from: int
    :type search_to: int
    :type pst: int
    :type widx: int
    :type snowday_ffs_idx: int
    :type snowday_ffs: float
    :rtype: int
    """
    logger = getLogger(__name__)
    ugap = 5
    udiff_th = 5
    t_intv = setting.INTV1HOUR
    n_data = len(sus)

    if not pst:
        if snowday_ffs_idx and  snowday_ffs > s_limit - 5:
            pst = snowday_ffs_idx
        else:
            return None

    u_limit = s_limit
    uth_bottom = u_limit - ugap
    uth_top = u_limit

    to = pst
    if to - search_from < t_intv:
        return None

    stable_idxs = []
    for idx in range(search_from, to):

        # check speed at current time interval
        if sus[idx] < uth_bottom or sus[idx] > uth_top:
            continue

        # target data set
        to = min(idx + t_intv, n_data - 1)
        tus = sus[idx:to + 1]

        # check continuously increase or decrease
        diffs = np.diff(tus)
        if np.all(diffs > 0) or np.all(diffs < 0):
            continue

        # check speed range
        minu, maxu, avgu = min(tus), max(tus), np.mean(tus)
        if maxu - minu <= udiff_th and avgu >= uth_bottom and avgu <= uth_top:
            stable_idxs.append(idx)

    if not any(stable_idxs):
        return None

    stable_idxs = np.array(stable_idxs)

    regions = list(reversed(_continuous_regions(stable_idxs)))

    stable_idx = stable_idxs[-1]

    for idx, (sidx, eidx) in enumerate(regions):
        if not idx:
            stable_idx = sidx
        else:
            btw_us = sus[eidx:regions[idx - 1][0]]
            minu = min(sus[stable_idx:to])
            if uth_bottom - min(btw_us) < udiff_th and uth_bottom - minu < udiff_th:
                stable_idx = sidx
            else:
                break

    # if stable_idx is before worst-ratio-idx
    if stable_idx and stable_idx < widx:
        stable_idx = None

    if stable_idx:
        astable_idx = adjust_with_qdata(qus, sus, stable_idx, sus[stable_idx])
        if astable_idx:
            stable_idx = astable_idx

    logger.debug('The found Stable Speed Region Start before PST : %s' % stable_idx)

    return stable_idx


def _find_stable_after_pst(sus, sks, qus, qks, s_limit, search_from, search_to, pst, widx, snowday_ffs_idx, snowday_ffs):
    """

    :type sus: numpy.ndarray
    :type sks: numpy.ndarray
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :type s_limit: int
    :type search_from: int
    :type search_to: int
    :type pst: int
    :type widx: int
    :type snowday_ffs_idx: int
    :type snowday_ffs: float
    :rtype: int
    """
    logger = getLogger(__name__)
    ugap = 5
    udiff_th = 5
    t_intv = setting.INTV1HOUR

    n_data = len(sus)

    u_limit = s_limit
    # if snowday_ffs:
    #     u_limit = min(snowday_ffs, u_limit)
    # pst = snowday_ffs_idx if snowday_ffs_idx else pst

    uth_bottom = u_limit - ugap

    if not pst:
        return

    _search_from = pst if pst else search_to

    stable_idx = None

    for idx in range(_search_from, search_to):

        # check speed at current time interval
        if sus[idx] < uth_bottom:
            continue

        # target data set
        to = min(idx + t_intv, n_data - 1)
        tus = sus[idx:to + 1]

        # check continuously increase or decrease
        diffs = np.diff(tus)
        if np.all(diffs > 0) or np.all(diffs < 0):
            continue

        # check speed range
        minu, maxu, avgu = min(tus), max(tus), np.mean(tus)
        if maxu - minu <= udiff_th and avgu >= uth_bottom:
            stable_idx = idx
            break

    if stable_idx:
        astable_idx = adjust_with_qdata(qus, sus, stable_idx, sus[stable_idx])
        if astable_idx:
            stable_idx = astable_idx

    logger.debug('The found Stable Speed Region Start after PST : %s' % stable_idx)

    return stable_idx


def _reaching_point(data, target_speed, search_from, search_to, t_intv=setting.INTV1HOUR, try_alt=False, op='gt'):
    """

    :type data: numpy.ndarray
    :type target_speed: float
    :type search_from:  int
    :type search_to:  int
    :type t_intv: int
    :type try_alt: bool
    :rtype: int
    """
    search_to = min(search_to, len(data))
    for idx in range(search_from, search_to):
        to = min(idx + t_intv, search_to)
        tus = data[idx:to]
        avgu = np.mean(tus)

        # check drop-again
        wh = np.where(data[idx:search_to] < target_speed - 5)[0]
        if len(wh) > setting.INTV1HOUR:
            continue

        if ((op == 'gt' and data[idx] >= target_speed and avgu >= target_speed)
            or (op == 'lt' and data[idx] <= target_speed and avgu <= target_speed)):
            return idx

    if try_alt:
        # find just the first over-target-speed point
        if op == 'gt':
            wh = np.where(data[search_from:search_to] >= target_speed)
        else:
            wh = np.where(data[search_from:search_to] <= target_speed)

        if any(wh[0]):
            return int(wh[0][0]) + search_from

    return None


def _continuous_regions(data):
    """

    :type data: numpy.ndarray
    :rtype: list[(int, int)]
    """
    wh_diffs = data[1:] - data[0:-1]
    wh_diffs[wh_diffs == 1] = 0
    iszero = np.concatenate(([0], np.equal(wh_diffs, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    zero_ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    res = []
    for zr in zero_ranges:
        sidx, eidx = data[zr[0]], data[zr[1]]
        res.append((sidx, eidx))

    return res


def _kde(data):
    """
    :type data: Union(list, numpy.ndarray)
    :rtype: numpy.ndarray, numpy.ndarray
    """
    data = np.array(data)
    from scipy import stats
    kernel = stats.gaussian_kde(data)
    data_range = np.arange(min(data), max(data), 0.1)
    res = kernel.evaluate(data_range)
    res = data_util.smoothing(res, 3)
    res = np.array(res)

    if DEBUG_MODE:
        # bins, counts = get_histogram(data, 0, normed=False)
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='white')
        ax1, ax2 = plt.subplot(121), plt.subplot(122)
        ax1.plot(data_range, res, c='b', marker='o')
        # ax1.plot(bins, counts, c='b', marker='o')
        ax2.plot(data)
        plt.grid()
        fig.tight_layout()
        fig.subplots_adjust(top=0.92)
        plt.show()

    return data_range, res


def _where(condition, offset=0):
    """
    :type condition: expression
    :type offset: int
    :rtype: int, int, numpy.ndarray
    """
    # if not found, try to find just over-FFS point
    wh = np.where(condition)
    if any(wh[0]):
        return wh[0][0] + offset, wh[0][-1], wh[0]
    return None, None, wh[0]
