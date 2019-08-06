# -*- coding: utf-8 -*-

import numpy as np

from pyticas.tool import tb
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import etypes
from pyticas_ncrtes.core import setting
from pyticas_ncrtes.core.est import target, wnffs_finder, phase
from pyticas_ncrtes.core.est.helper import est_helper
from pyticas_ncrtes.core.est.old import ncrt_finder
from pyticas_ncrtes.logger import getLogger

FFS_K = setting.FFS_K

UTH = 10
NTH = 5
UTH_FOR_HIGH_K = 30
LOW_K = 10

U_DIFF_THRESHOLD = 8
K_DIFF_THRESHOLD = 5

DEBUG_MODE = False
SAVE_CHART = False

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def estimate(num, tsi, edata):
    """

    :type num: int
    :type tsi: pyticas_ncrtes.itypes.TargetStationInfo
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: pyticas_ncrtes.core.etypes.ESTData
    """
    if not _check_edata(tsi, edata):
        return edata

    logger = getLogger(__name__)
    logger.info('>>> Determine NCRT Process for Target Station %s' % (edata.target_station.station_id))

    try:
        _pre_process_before_determination(edata)
        is_found, wnffs = wnffs_finder.determine(edata)
        ncrt = ncrt_finder.determine(edata)
    except Exception as ex:
        logger.error(tb.traceback(ex, f_print=False))

    logger.info('<<< End of NCRT Determination Process for Target Station %s' % (edata.target_station.station_id))

    return edata


def prepare_data(tsi, station, stime, etime, snow_routes, reported, normal_months, normal_func):
    """

    :type tsi: pyticas_ncrtes.itypes.TargetStationInfo
    :type station: pyticas.ttypes.RNodeObject
    :type stime: datetime.datetime
    :type etime: datetime.datetime
    :type snow_routes: list[pyticas_ncrtes.core.etypes.SnowRoute]
    :type reported: dict[str, list[pyticas_ncrtes.core.etypes.ReportedEvent]]
    :type normal_func: pyticas_ncrtes.core.etypes.NSRFunction
    :type normal_months: list[(int, int)]

    :rtype: pyticas_ncrtes.core.etypes.ESTData
    """
    sevent = etypes.SnowEvent(stime, etime)
    infra = ncrtes.get_infra()
    target_station = infra.get_rnode(tsi.station_id)

    if tsi:
        valid_detectors = [infra.get_detector(det_name.strip()) for det_name in tsi.detectors.split(',')]
    else:
        valid_detectors = target.get_target_detectors(station)

    try:
        edata = etypes.ESTData(tsi, target_station, sevent, snow_routes, reported, normal_func)
        edata.prepare_data(detectors=valid_detectors)
        return edata

    except Exception as ex:
        log = getLogger(__name__)
        log.warning('!!!!! Error : %s : %s' % (tsi.station_id, ex))
        from pyticas.tool import tb
        tb.traceback(ex)
        return None


def _check_edata(tsi, edata):
    """

    :type tsi: pyticas_ncrtes.itypes.TargetStationInfo
    :type nsr_func: pyticas_ncrtes.core.etypes.NSRFunction
    :rtype: bool
    """
    log = getLogger(__name__)
    if not edata:
        log.info('> %s : No ESTData' % tsi.station_id)
        return False

    if not edata or not edata.is_loaded:
        log.info('> %s : Data are not loaded for snow event' % tsi.station_id)
        return False

    # if not edata.search_start_idx:
    #     log.info('> %s : No Search Start Idx' % tsi.station_id)
    #     return False

    return True


def _pre_process_before_determination(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    logger = getLogger(__name__)

    # determine FFS
    ffs = _ffs(edata)
    edata.ffs = ffs

    # get/make normal ratios
    normal_ratios = _normal_ratios(edata, ffs)
    edata.normal_ratios = normal_ratios

    # ffs
    may_recovered_speed = _may_recovered_speed(edata, rth=0.9)
    if not may_recovered_speed:
        logger.debug(' - Cannot determine `may-recovered-speed` ')
        return

    edata.may_recovered_speed = may_recovered_speed

    # determine worst ratio point
    widx = est_helper.worst_ratio_point(edata, ratios=normal_ratios)
    edata.worst_ratio_idx = widx

    logger.debug(' - FFS : %s' % ffs)
    logger.debug(' - Worst Ratio Index : %s (%.2f)' % (widx, normal_ratios[widx]))

    phase._srst(edata)

    cps = est_helper.find_speed_change_point(edata, edata.aks, edata.aus, ffs)
    # cps = cps + [ _sidx for (_sidx, _eidx) in est_helper.find_speed_recovery_in_same_k(edata) ]
    reduction_by_snow = est_helper.find_speed_reduction_in_same_k(edata,
                                                                  low_k=LOW_K,
                                                                  u_diff_threshold=U_DIFF_THRESHOLD,
                                                                  k_diff_threshold=K_DIFF_THRESHOLD)

    estimated_nighttime_snowing = est_helper.find_nighttime_snowing(edata)
    search_start_idx = max([widx] + cps + estimated_nighttime_snowing + [_eidx for (_sidx, _eidx) in reduction_by_snow])

    if edata.srst and edata.srst < edata.snow_event.snow_start_index + setting.INTV5HOUR:
        search_start_idx = max(edata.srst+setting.INTV1HOUR, search_start_idx)

    edata.estimated_nighttime_snowing = estimated_nighttime_snowing
    edata.uk_change_point = cps
    edata.reduction_by_snow = [_eidx for (_sidx, _eidx) in reduction_by_snow]
    edata.search_start_idx = search_start_idx

    logger.debug(' - UK Change Point : %s' % edata.uk_change_point)
    logger.debug(' - Reduction by Snow : %s' % edata.reduction_by_snow)
    logger.debug(' - Nighttime Snowing : %s' % edata.estimated_nighttime_snowing)
    logger.debug(' - Search Start Index : %s' % search_start_idx)

    uth = _uth(edata)
    edata.ncrt_search_uth = uth

    over_uth_point, k_at_recovered = _find_start_point_over_threshold(edata, uth)

    if not over_uth_point:
        logger.debug(' - Cannot find Over-Uth-Point (%s)' % uth)
        return

    edata.ncrt_search_sidx = over_uth_point
    edata.ncrt_search_eidx = _data_range_to_find_ncrt(edata, over_uth_point)
    logger.debug(' - NCRT Search Start Index : %s' % edata.ncrt_search_sidx)
    logger.debug(' - NCRT Search End Index : %s' % edata.ncrt_search_eidx)


def _ffs(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: float
    """
    if edata.normal_func and edata.normal_func.is_valid():
        return edata.normal_func.daytime_func.get_FFS()
    else:
        tus, tks = edata.sus[:edata.snow_event.snow_start_index], edata.sks[:edata.snow_event.snow_start_index]
        wh = np.where(tks < FFS_K)[0]
        if any(wh):
            return np.mean(tus[wh])
        else:
            tus, tks = edata.sus[edata.snow_event.snow_end_index:], edata.sks[edata.snow_event.snow_end_index:]
            wh = np.where( (tks < FFS_K) & (tus > edata.target_station.s_limit) )[0]
            if any(wh):
                return np.mean(tus[wh])

    return None


def _normal_ratios(edata, ffs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type ffs: float
    :rtype: numpy.ndarray
    """
    if edata.normal_func and edata.normal_func.is_valid():
        return edata.normal_ratios
    else:
        return np.array([ u / ffs for u in edata.merged_sus ])


def _uth(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: float
    """
    uth = -1
    rth = 0.7

    maxu_limit = edata.ffs

    # _ssidx, _seidx = search_start_idx, min(search_start_idx + 4 * setting.INTV1HOUR, n_data - 1)
    _ssidx, _seidx = edata.snow_event.snow_start_index, edata.snow_event.snow_end_index
    minu = min(edata.sus[_ssidx:_seidx])
    while minu >= uth and rth < 1.0:
        uth = maxu_limit * rth
        rth += 0.05
    return uth


def _find_start_point_over_threshold(edata, uth):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type uth: float
    :rtype: int, float
    """
    search_start_idx = edata.search_start_idx
    sks, sus, s_limit = edata.sks, edata.sus, edata.target_station.s_limit

    n_data = len(sus)
    intv1hour = int((60 * 60) / setting.DATA_INTERVAL)
    intv2hour = intv1hour * 2
    recovered_idx = None

    for idx in range(search_start_idx, n_data - intv1hour):

        if sus[idx] > uth:

            if min(sus[idx:idx + intv1hour]) > uth + 5:
                recovered_idx = idx
                break

            k = sks[idx]
            tks = sks[idx:min(idx + intv2hour, n_data)]
            tus = sus[idx:min(idx + intv2hour, n_data)]
            wh = np.where(tks <= k)
            if any(wh[0]) and min(tus[wh]) > uth:
                recovered_idx = idx
                break

    if not recovered_idx:
        return None, None

    # 2011-11-19, I-35E (SB), S846
    # 2011-11-19, I-35W (SB), S584
    worstu = min(edata.sus[edata.worst_ratio_idx - setting.INTV30MIN:edata.worst_ratio_idx + setting.INTV30MIN])
    # worstu = min(edata.sus[edata.snow_event.snow_start_index:edata.snow_event.snow_end_index+1])
    # worstu_idx = np.where(edata.sus[edata.snow_event.snow_start_index:edata.snow_event.snow_end_index+1] == worstu)[0][0]
    logger = getLogger(__name__)
    logger.debug(
        'recovered_idx=%d, u_at_recovered=%.1f, worst_u=%.1f' % (recovered_idx, edata.sus[recovered_idx], worstu))
    if edata.sus[recovered_idx] - worstu < 5:
        for idx in range(recovered_idx, edata.n_data - setting.INTV30MIN):
            if min(edata.sus[idx:idx + setting.INTV30MIN]) > worstu + 5:
                for tidx in range(idx, recovered_idx, -1):
                    if edata.sus[tidx] <= edata.sus[tidx - 1]:
                        recovered_idx = tidx
                        break
                break

            # if there is speed down after worst ratio...
            if edata.sus[idx] < worstu - 3:
                for tidx in range(idx, edata.n_data - setting.INTV30MIN):
                    if edata.sus[tidx] > uth and np.mean(edata.sus[tidx:tidx+setting.INTV30MIN]) > uth:
                        recovered_idx = tidx
                        break
                break


    return recovered_idx, max(sks[recovered_idx], 15)


def _data_range_to_find_ncrt(edata, over_uth_point):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type over_uth_point: int
    :rtype: int
    """
    to_idx = min(over_uth_point + 6 * setting.INTV1HOUR, len(edata.us) - setting.INTV1HOUR)
    snow_end_index = edata.snow_event.snow_end_index
    to_idx = max(snow_end_index + setting.INTV4HOUR, to_idx)
    if edata.sks[to_idx] > FFS_K:
        wh = np.where(edata.sks[to_idx:] < FFS_K)
        if any(wh[0]):
            to_idx = min(to_idx + wh[0][0] + setting.INTV1HOUR, len(edata.sus)-1)
    return to_idx


def _may_recovered_speed(edata, rth=0.9):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype:
    """
    ffs_before_snowing = None
    tks = edata.merged_sks[:edata.snow_event.snow_start_index]#+setting.INTV2HOUR]
    wh = np.where(tks < FFS_K)[0]
    if any(wh):
        ffs_before_snowing = np.mean(edata.merged_sus[wh])

    getLogger(__name__).debug(' - FFS before Snowing : %s' % ffs_before_snowing)

    normal_ffs = edata.normal_func.daytime_func.get_FFS() if edata.normal_func else None

    if not normal_ffs and not ffs_before_snowing:
        return min(normal_ffs, ffs_before_snowing) * rth

    if normal_ffs:
        return normal_ffs* rth

    if ffs_before_snowing:
        return ffs_before_snowing * rth

    return None
