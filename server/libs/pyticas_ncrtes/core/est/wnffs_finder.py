# -*- coding: utf-8 -*-

import numpy as np

from pyticas.tool import tb
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import etypes, data_util
from pyticas_ncrtes.core import setting
from pyticas_ncrtes.core.est import target
from pyticas_ncrtes.logger import getLogger

FFS_K = setting.FFS_K

UTH = 10
NTH = 5
UTH_FOR_HIGH_K = 30
LOW_K = 10

U_DIFF_THRESHOLD = 8
K_DIFF_THRESHOLD = 5

CONGESTED_SPEED = 30

DEBUG_MODE = True
SAVE_CHART = False

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

def find(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype:
    """
    # k < ffs_k
    # u > uth
    # stable (nighttime has big fluctuations)
    # there's no ratio drop after the area
    logger = getLogger(__name__)
    logger.debug(' >>> wnffs_finder.find() ')
    uth = edata.ncrt_search_uth
    rth = edata.ncrt_search_rth
    sus, sks, qus, qks = edata.sus, edata.sks, edata.qus, edata.qks
    ratios = data_util.smooth(edata.normal_ratios, setting.SW_4HOURS)

    # _sus = sus[edata.snow_event.snow_start_index:edata.snow_event.snow_end_index]
    # _ratios = ratios[edata.snow_event.snow_start_index:edata.snow_event.snow_end_index]
    # min_ratio = min(_ratios[_sus > CONGESTED_SPEED])
    #
    # rth = max(0.7, min(min_ratio+0.1, 0.95))

    logger.debug('  - uth : %.2f' % uth)
    logger.debug('  - rth : %.2f' % rth)

    # find all time intervals which is free-flow candidates
    wh = np.where( (sus > uth) & (sks < FFS_K) & (ratios > rth))[0]
    if not any(wh):
        logger.warning('  - cannot find the area which speed > %.2f' % uth)
        logger.debug(' <<< end of wnffs_finder.find() ')
        return False

    # make the continuous region data with individual time intervals
    # format :
    #     - regions = list of star-index and end-index pair
    #     - regions = [(int, int), (int, int) ..]
    regions = _continuous_regions(wh)

    # remove region before snow-start
    if regions and regions[0][0] < edata.snow_event.snow_start_index:
        del regions[0]

    logger.debug('  - regions : %s' % regions)

    # adjust region by ratio
    #   - if there is ration drop in a region, the region is splited
    regions, ratios, lsratios, sratios = _adjust_regions(edata, regions, rth)
    edata.ratios = ratios
    edata.lsratios = lsratios
    edata.sratios = sratios

    logger.debug('  - updated regions : %s' % regions)
    if None is ratios:
        logger.debug('  - updated ratios contains None')
        if None is edata.normal_ratios:
            logger.debug('  - origin ratios contains None')
        else:
            logger.debug('  - origin ratios does not contain None')

    if not regions:
        logger.warning('  - cannot find recovered regions')
        logger.debug(' <<< end of wnffs_finder.find() ')
        return False

    # determine FFS start point candidate
    _find_ffs_start_point(edata, regions, ratios, rth)

    logger.debug('NCRT search range : (%s ~ %s)' % (edata.ncrt_search_sidx, edata.ncrt_search_eidx))

    is_found, wn_ffs = _recovered_to_normal_directly(edata, qus, qks)

    if not is_found:
        is_found, wn_ffs = _find_wn_ffs_using_stable_time(edata, qus, qks)

    if not is_found:
        is_found, wn_ffs = _find_wn_ffs_using_vertex(edata, qus, qks)

    logger.debug(' <<< end of wnffs_finder.find() ')
    return True


def _find_ffs_start_point(edata, regions, ratios, rth):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type regions:  list[(int, int)]
    :type ratios:  numpy.ndarray
    :type rth:  float
    :rtype:
    """
    next_sidx, next_eidx = regions[-1]
    start_point = next_sidx
    for (sidx, eidx) in reversed(regions[:-1]):
        if _may_have_snowing_effect(edata, ratios, rth, sidx, eidx, next_sidx, next_eidx):
            break
        next_sidx, next_eidx = sidx, eidx
        start_point = sidx

    start_point = _adjust_ffs_candidate_start_point(edata, start_point, ratios, regions, rth)

    edata.ncrt_search_sidx = start_point
    eidx = _data_range_to_find_ncrt(edata)

    sidx = _check_vertical_recovery(edata, start_point, eidx)
    edata.ncrt_search_sidx = sidx
    eidx = _data_range_to_find_ncrt(edata)
    edata.ncrt_search_eidx = eidx

    # TODO: check this....
    sidx = _check_recovery_during_k_increase(edata, sidx, eidx)
    edata.ncrt_search_sidx = sidx
    eidx = _data_range_to_find_ncrt(edata)
    edata.ncrt_search_eidx = eidx


def _adjust_ffs_candidate_start_point(edata, start_point, ratios, regions, rth):
    """ move start point to previous-time interval if speed and ratio is high

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type start_point: int
    :type ratios: numpy.ndarray
    :type regions: list[(int, int)]
    :type rth: float
    :rtype: int
    """
    brefore_region_eidx = None
    for (sidx, eidx) in regions:
        if sidx >= start_point:
            break
        brefore_region_eidx = eidx

    if not brefore_region_eidx:
        return start_point

    _start_point = start_point

    for idx in range(start_point, 0, -1):
        if ((edata.sus[idx] > edata.ncrt_search_uth and ratios[idx] > rth)
            or (edata.qus[idx] >= edata.qus[start_point] and edata.sus[idx] > edata.qus[start_point] - 3)):
            _start_point = idx
        else:
            break

    if brefore_region_eidx and _start_point < brefore_region_eidx:
        _start_point = np.argmin(edata.sus[brefore_region_eidx:start_point]).item() + brefore_region_eidx

    return _start_point


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


def _same_data_regions(data, index_offset=0):
    """

    :type data: numpy.ndarray
    :rtype: list[[int, int]]
    """
    target_us = data[index_offset:]
    diffs = target_us[1:] - target_us[:-1]
    iszero = np.concatenate(([0], np.equal(diffs, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    stable_ranges = np.where(absdiff == 1)[0].reshape(-1, 2) + index_offset
    return stable_ranges


def _adjust_small_speed_diffs(regions, qus):
    """
    :type regions: list[(int, int)]
    :type qus: numpy.ndarray
    :rtype: list[[int, int]]
    """
    u_margin = 1
    _mereged = []
    for idx in range(1, len(regions)):
        psidx, peidx = regions[idx-1]
        nsidx, neidx = regions[idx]
        if abs(qus[neidx] - qus[psidx]) < u_margin:
            if _mereged and _mereged[-1][1] > psidx:
                _mereged[-1][1] = neidx
            else:
                _mereged.append([psidx, neidx])
        else:
            if not _mereged or _mereged[-1][1] < peidx:
                _mereged.append([psidx, peidx])

    if not _mereged:
        _mereged = regions
    else:
        merged_last_sidx, merged_last_eidx = _mereged[-1]
        last_sidx, last_eidx = regions[-1]
        if abs(qus[merged_last_eidx] - qus[last_sidx]) < u_margin:
            _mereged[-1][1] = last_eidx
        else:
            _mereged.append([last_sidx, last_eidx])


    return _mereged


def _adjust_regions(edata, regions, rth):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type regions:  list[(int, int)]
    :type ratios:  numpy.ndarray
    :type rth:  float
    :rtype:list[(int, int)], numpy.ndarray, numpy.ndarray
    """
    ratios = np.array(edata.normal_ratios)
    for idx, r in enumerate(ratios):
        if edata.night_ratios[idx] is not None:
            ratios[idx] = max(edata.night_ratios[idx], edata.normal_ratios[idx])

    lsratios = data_util.smooth(ratios, setting.SW_2HOURS)
    sratios = data_util.smooth(ratios, setting.SW_4HOURS)
    new_regions = []
    for (sidx, eidx) in regions:
        _regions = []
        _divide_region_by_ratio(edata, sidx, eidx, sratios, lsratios, _regions, rth)
        new_regions.extend(_regions)

    new_regions = [ (sidx, eidx) for (sidx, eidx) in new_regions if (sidx < eidx) ]

    return new_regions, ratios, lsratios, sratios


def _recovered_to_normal_directly(edata, qus, qks):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :rtype: (bool, float)
    """
    logger = getLogger(__name__)
    logger.debug(' >> checking recovered_to_normal_directly')
    nrth = 0.6
    u_change = 5
    small_u_change = 3
    sidx, eidx = edata.ncrt_search_sidx, edata.ncrt_search_eidx
    tus, tks = qus[sidx:eidx], qks[sidx:eidx]
    maxu, minu = max(tus), min(tus)

    logger.debug('  - Speed Variations Max=%.2f, Min=%.2f' % (maxu, minu))
    # speed is not changed during recovery interval
    if maxu - minu < small_u_change or minu >= edata.may_recovered_speed:
        wn_ffs = max(edata.qus[sidx-setting.INTV1HOUR:sidx+setting.INTV1HOUR])
        edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs, sidx, eidx)
        # edata.wn_ffs = wn_ffs
        edata.wn_ffs = edata.sus[edata.wn_ffs_idx]
        logger.debug('  - Directly Recovered to Normal (1) : wn_ffs = %.1f, wn_ffs_idx = %d' %
                     (edata.wn_ffs, edata.wn_ffs_idx))
        return True, wn_ffs

    wh = np.where(tus >= edata.may_recovered_speed)[0]
    n_recovered = float(len(wh))
    n_data = len(tus)

    logger.debug('  - Number of May-Recovered : %d (%.2f)' % (n_recovered, n_data*nrth))
    if n_recovered > n_data * nrth:#and tus[0] > edata.may_recovered_speed:
        tidx = wh[0]+sidx
        wn_ffs = edata.qus[tidx] #max(edata.qus[tidx-setting.INTV1HOUR:tidx+setting.INTV1HOUR])
        edata.wn_ffs_idx = tidx
        # edata.wn_ffs = wn_ffs
        edata.wn_ffs = edata.sus[edata.wn_ffs_idx]
        logger.debug('  - Directly Recovered to Normal (2) : wn_ffs = %.1f, wn_ffs_idx = %d' %
                     (edata.wn_ffs, edata.wn_ffs_idx))
        return True, wn_ffs

    logger.debug(' << end of checking recovered_to_normal_directly')
    return False, None


def _find_wn_ffs_using_stable_time(edata, qus, qks):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :rtype: (bool, float)
    """
    logger = getLogger(__name__)
    logger.debug(' >> finding wn_ffs using stable_time')
    nrth = 0.6
    sidx, eidx, tus, tks = _ut_data_range(edata, qus, qks)

    cregions = _same_data_regions(tus)
    cregions = _adjust_small_speed_diffs(cregions, tus)
    sorted_cregions = sorted(cregions, key=lambda r: r[1] - r[0])
    s_sidx, s_eidx = sorted_cregions[-1]
    region_duration = len(np.where(tus[s_sidx:s_eidx+1] > edata.ncrt_search_uth)[0])
    recovery_duration = len(np.where(tks < FFS_K)[0])

    logger.debug(' - WN-FFS using Stable Time Duration : adjust range (%d, %d) -> (%d, %d), %s=%d/%d' %
                 (edata.ncrt_search_sidx, edata.ncrt_search_eidx, sidx, eidx,
                  (region_duration/recovery_duration) if recovery_duration else 'N/A',
                  region_duration, recovery_duration))

    if recovery_duration and region_duration > setting.INTV1HOUR and region_duration / recovery_duration >= nrth:
        s_sidx, s_eidx = s_sidx + sidx, s_eidx + sidx
        wn_ffs = np.mean(edata.sus[s_sidx:s_eidx]).item()
        edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs, sidx, eidx)
        # edata.wn_ffs = wn_ffs
        edata.wn_ffs = edata.sus[edata.wn_ffs_idx]
        logger.debug(' - WN-FFS using Stable Time Duration : stable_region=(%d, %d), wn_ffs=%.1f, wn_ffs_idx=%d' %
                     (s_sidx, s_eidx, edata.wn_ffs, edata.wn_ffs_idx))

        return True, wn_ffs

    logger.debug(' << end of finding wn_ffs using stable_time')
    return False, None


def _find_wn_ffs_using_vertex(edata, qus, qks):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :rtype: (bool, float)
    """
    logger = getLogger(__name__)
    logger.debug(' >> finding wn_ffs using vertex')
    sidx, eidx, tus, tks = _ut_data_range(edata, qus, qks)

    logger.debug(' - WN-FFS using Vertex : adjust range (%d, %d) -> (%d, %d)' %
                 (edata.ncrt_search_sidx, edata.ncrt_search_eidx, sidx, eidx))

    indices = list(range(sidx, eidx))

    up_vertex_idx, d_to_up_vertex, _, _ = _find_vertex(indices, tus, find_under=False, offset=sidx)

    if up_vertex_idx < 0:
        logger.debug(' - cannot find vertex : data range = (%d, %d)' % (sidx, eidx))
        wn_ffs = max(edata.sus[sidx-setting.INTV30MIN:sidx+setting.INTV30MIN])
        edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs, edata.ncrt_search_sidx, eidx)
        # edata.wn_ffs = wn_ffs
        edata.wn_ffs = edata.sus[edata.wn_ffs_idx]
        logger.debug(' - WN-FFS using Vertex : wn_ffs = %.1f, wn_ffs_idx = %d' %
                     (edata.wn_ffs, edata.wn_ffs_idx))
        return True, wn_ffs

    wn_ffs = max(edata.sus[up_vertex_idx-setting.INTV30MIN:up_vertex_idx+setting.INTV30MIN])
    edata.wn_ffs_idx = _find_wn_ffs_idx(edata, wn_ffs, edata.ncrt_search_sidx, eidx)
    # edata.wn_ffs = wn_ffs
    edata.wn_ffs = edata.sus[edata.wn_ffs_idx]

    logger.debug(' - WN-FFS using Vertex : wn_ffs = %.1f, wn_ffs_idx = %d' %
                 (edata.wn_ffs, edata.wn_ffs_idx))

    logger.debug(' << end of finding wn_ffs using vertex')
    return True, wn_ffs


def _may_have_snowing_effect(edata, ratios, rth, prev_sidx, prev_eidx, next_sidx, next_eidx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :param ratios: mixed ratios of daytime and nighttime ratios
    :type ratios:  numpy.ndarray
    :type rth:  float
    :type prev_sidx: int
    :type prev_eidx: int
    :type next_sidx: int
    :type next_eidx: int
    :rtype: bool
    """
    little_ffs_k = 25
    rth_may_recovered = 0.9
    rth_may_lost_again = 0.8

    prev_sus = edata.sus[prev_sidx:prev_eidx+1]
    prev_sks = edata.sks[prev_sidx:prev_eidx+1]
    prev_ratios = ratios[prev_sidx:prev_eidx+1]

    btw_sus = edata.sus[prev_eidx+1:next_sidx]
    btw_us = edata.us[prev_eidx+1:next_sidx]
    btw_sks = edata.sks[prev_eidx+1:next_sidx]
    btw_ks = edata.ks[prev_eidx+1:next_sidx]
    btw_ratios = ratios[prev_eidx+1:next_sidx]

    next_sus = edata.sus[next_sidx:next_eidx+1]
    next_sks = edata.sks[next_sidx:next_eidx+1]
    next_ratios = ratios[next_sidx:next_eidx+1]

    logger = getLogger(__name__)

    t_margin = setting.INTV30MIN
    last_prev_ks = edata.sks[max(prev_sidx, prev_eidx-t_margin):prev_eidx]
    first_next_ks = edata.sks[next_sidx:min(next_eidx, next_sidx+t_margin)]

    last_prev_us = edata.sus[max(prev_sidx, prev_eidx-t_margin):prev_eidx]
    first_next_us = edata.sus[next_sidx:min(next_eidx, next_sidx+t_margin)]

    last_prev_ratios = ratios[max(prev_sidx, prev_eidx-t_margin):prev_eidx]
    first_next_ratios = ratios[next_sidx:min(next_eidx, next_sidx+t_margin)]
    n_btw = len(btw_sks)

    min_ratio_btw_region =  min(btw_ratios[btw_sus > CONGESTED_SPEED])
    r_btw_congested = (len(np.where((btw_us < CONGESTED_SPEED) & (btw_ks > little_ffs_k))[0]) / n_btw)
    r_btw_nighttime = (len([ v for v in edata.night_us[prev_eidx+1:next_sidx] if v is not None]) / n_btw)
    is_nighttime = ( r_btw_nighttime > 0.9 )

    last_u_of_prev_region = np.percentile(last_prev_us, 90)
    first_u_of_next_region = np.percentile(first_next_us, 50)

    last_ratio_of_prev_region = np.percentile(last_prev_ratios, 90)
    first_ratio_of_next_region = np.percentile(first_next_ratios, 50)

    lower_than_rth_in_btw_region =  np.where((btw_sus > CONGESTED_SPEED) & (btw_ratios < rth))[0]
    lower_than_uth_in_btw_region =  np.where((btw_sus > CONGESTED_SPEED) & (btw_sus < edata.ncrt_search_uth))[0]
    n_lower_than_rth_in_btw_region = 0
    n_lower_than_uth_in_btw_region = 0

    if any(lower_than_rth_in_btw_region):
        _tmp = _continuous_regions(lower_than_rth_in_btw_region)
        if _tmp:
            lower_than_rth_in_btw_region = sorted(_tmp, key=lambda r: r[1] - r[0])[0]
            n_lower_than_rth_in_btw_region = len(lower_than_rth_in_btw_region)

    if any(lower_than_uth_in_btw_region):
        _tmp = _continuous_regions(lower_than_uth_in_btw_region)
        if _tmp:
            lower_than_uth_in_btw_region = sorted(_tmp, key=lambda r: r[1] - r[0])[0]
            n_lower_than_uth_in_btw_region = len(lower_than_uth_in_btw_region)

    ratio_drop_without_congestion = 0.
    speed_drop_without_congestion = 0.
    btw_min_ratio_without_congestion = 0.
    btw_min_u_without_congestion = 0.
    n_under_uth = 0.

    wh = np.where((btw_sus > CONGESTED_SPEED) & (btw_sks < little_ffs_k))[0]
    if any(wh):
        t_btw_ratios = btw_ratios[wh]
        t_btw_sus = btw_sus[wh]
        btw_minu_idx = np.argmin(t_btw_sus)
        btw_min_u_without_congestion = t_btw_sus[btw_minu_idx]
        btw_min_ratio_without_congestion = t_btw_ratios[btw_minu_idx]
        ratio_drop_without_congestion = last_ratio_of_prev_region - btw_min_ratio_without_congestion
        speed_drop_without_congestion = last_u_of_prev_region - btw_min_u_without_congestion
        n_under_uth = len(np.where(t_btw_sus < edata.ncrt_search_uth)[0])

    logger.debug('>> check snow effect(%d, %d) ~ (%d, %d)' % (prev_sidx, prev_eidx, next_sidx, next_eidx))
    logger.debug('  - last_ratio_of_prev_region : %.2f' % last_ratio_of_prev_region)
    logger.debug('  - first_ratio_of_next_region : %.2f' % first_ratio_of_next_region)
    logger.debug('  - last_spped_of_prev_region : %.2f' % last_u_of_prev_region)
    logger.debug('  - first_speed_of_next_region : %.2f' % first_u_of_next_region)
    logger.debug('  - r_btw_congested : %.2f' % r_btw_congested)
    logger.debug('  - r_btw_nighttime : %.2f' % r_btw_nighttime)
    logger.debug('  - min_ratio_btw_region : %.2f' % min_ratio_btw_region)
    logger.debug('  - lower_than_rth_in_btw_region : %d' % len(lower_than_rth_in_btw_region))
    logger.debug('  - lower_than_uth_in_btw_region : %d' % len(lower_than_uth_in_btw_region))


    # check surely snow-effect
    may_lost_again = (btw_min_ratio_without_congestion < rth_may_lost_again)

    has_same_uk_pattern = (last_ratio_of_prev_region >= 0.8 and
                           _is_same_uk_trajectory(edata, prev_sidx, prev_eidx, next_sidx, next_eidx, little_ffs_k))

    # ratio drop > 15%
    if (ratio_drop_without_congestion > 0.15
        and not has_same_uk_pattern
        and ((not is_nighttime and (btw_min_ratio_without_congestion < rth_may_recovered  or may_lost_again))
                or (is_nighttime and may_lost_again))):


        logger.debug('  -> !! snow-effect : big ratio drop in FFS_K range (1)')
        return True

    # ratio drop > 10% and lost time > 30min
    if (ratio_drop_without_congestion > 0.1
        and not has_same_uk_pattern
        and (n_under_uth > setting.INTV30MIN or may_lost_again)):
        logger.debug('  -> !! snow-effect : big ratio drop in FFS_K range (2)')
        return True

    # minimum ratio < rth and lost time > 30min
    if btw_min_ratio_without_congestion < rth_may_lost_again and n_under_uth > setting.INTV30MIN:
        logger.debug('  -> !! snow-effect : minimum ratio of btween-region is %.2f (rth=%.2f)'
                     % (btw_min_ratio_without_congestion, rth_may_lost_again))
        return True

    # lost more than 1hour (speed and ratio)
    if n_lower_than_rth_in_btw_region > setting.INTV1HOUR and n_lower_than_uth_in_btw_region > setting.INTV1HOUR:
        logger.debug('  -> !! snow-effect : long time intervals lower than rth and rth in btween-region (%s and %s)'
                     % (n_lower_than_rth_in_btw_region, n_lower_than_uth_in_btw_region))
        return True


    # check if reduction and recovery u-k pattern in btween-region are significantly different
    if max(btw_sks) > FFS_K and max(btw_sks) - min(btw_sks) > 2:

        btw_minu_idx = np.argmin(btw_sus).item()
        btw_maxk_idx = np.argmax(btw_sks).item()

        if btw_sks[btw_maxk_idx] - btw_sks[btw_minu_idx] < 5 and btw_sus[btw_maxk_idx] - btw_sus[btw_minu_idx] < 5:
            has_big_drop = False
            for _k in range(int(min(btw_sks)), int(max(btw_sks))):
                avgu, stddev, arounds = data_util.avg_y_of_around_x(btw_sks, btw_sus, _k)
                if arounds and len(arounds) > 1:
                    udiff = max(arounds) - min(arounds)
                    if udiff > U_DIFF_THRESHOLD:
                        has_big_drop = True
                        break
            if has_big_drop:
                logger.debug('  -> snow-effect : different u-k region during btw-region')
                return True

    logger.debug('  -> no snow-effect')
    return False


def _is_same_uk_trajectory(edata, prev_sidx, prev_eidx, next_sidx, next_eidx, ffs_k):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type prev_sidx: int
    :type prev_eidx: int
    :type next_sidx: int
    :type next_eidx: int
    :type ffs_k: float
    :rtype: bool
    """
    btw_sks, btw_sus = edata.sks[prev_eidx:next_sidx], edata.sus[prev_eidx:next_sidx]

    btw_min_k, btw_max_k = min(btw_sks), max(btw_sks)
    btw_min_u, btw_max_u = min(btw_sus), max(btw_sus)

    if btw_max_k - btw_min_k < 5 or btw_max_k < LOW_K:
        return False

    recovered_idx = None
    for idx in range(next_sidx, next_eidx):
        _k, _u = edata.sks[idx], edata.sus[idx]
        if _k < btw_min_k or _u > btw_max_u:
            break
        recovered_idx = idx

    if not recovered_idx:
        return False


    btw_sks, btw_sus = edata.sks[prev_eidx:recovered_idx], edata.sus[prev_eidx:recovered_idx]

    if max(btw_sks) < ffs_k:
        return False

    u_diff_threshold = 15

    btw_max_k_idx = np.argmax(btw_sks).item()

    btw_uk_diffs = []
    btw_ks_before_maxk, btw_us_before_maxk = btw_sks[:btw_max_k_idx], btw_sus[:btw_max_k_idx]
    btw_ks_after_maxk, btw_us_after_maxk = btw_sks[btw_max_k_idx + 1:], btw_sus[btw_max_k_idx + 1:]
    for _k in range(int(min(btw_sks)), int(max(btw_sks))):
        # reduction
        avgu1, stddev1, arounds1 = data_util.avg_y_of_around_x(btw_ks_before_maxk, btw_us_before_maxk, _k)
        # recovery
        avgu2, stddev2, arounds2 = data_util.avg_y_of_around_x(btw_ks_after_maxk, btw_us_after_maxk, _k)

        if arounds1 and arounds2:
            # reduction - recovery
            udiff = avgu1 - avgu2
            btw_uk_diffs.append(udiff)

    if not any(btw_uk_diffs):
        return False

    btw_is_reduction_over_recovery = (len([ v for v in btw_uk_diffs if v > -1 ]) / len(btw_uk_diffs) > 0.3)
    if not btw_is_reduction_over_recovery:
        return False

    btw_max_uk_diff = max(btw_uk_diffs)
    btw_min_uk_diff = min(btw_uk_diffs)
    if btw_max_uk_diff < u_diff_threshold:
        return True

    return False


def _data_range_to_find_ncrt(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: int
    """
    to_idx = min(edata.ncrt_search_sidx + 6 * setting.INTV1HOUR, len(edata.us) - setting.INTV1HOUR)
    snow_end_index = edata.snow_event.snow_end_index
    to_idx = max(snow_end_index + setting.INTV4HOUR, to_idx)
    if edata.sks[to_idx] > FFS_K:
        wh = np.where(edata.sks[to_idx:] < FFS_K)
        if any(wh[0]):
            to_idx = min(to_idx + wh[0][0] + setting.INTV1HOUR, len(edata.sus)-1)

    return to_idx


def _check_vertical_recovery(edata, sidx, eidx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type sidx:  int
    :type eidx:  int
    :rtype: int
    """

    wh = np.where(edata.sus[sidx:eidx] > edata.may_recovered_speed)[0]
    if not any(wh) or wh[0] == 0:
        return sidx

    cutline_idx = wh[0]+sidx
    minmax = data_util.local_minmax_points(edata.sus)
    for idx in range(1, len(minmax)):
        pidx, nidx = minmax[idx-1], minmax[idx]
        if pidx < cutline_idx < nidx:
            tks = edata.sks[pidx:nidx]
            tus = edata.sus[pidx:nidx]
            maxu, minu = max(tus), min(tus)
            maxk, mink = max(tks), min(tks)
            # print('=> ', (pidx, nidx), (minu, maxu), (mink, maxk))
            if maxk - mink < K_DIFF_THRESHOLD and maxu - minu > U_DIFF_THRESHOLD:
                return pidx

    return sidx


def _check_recovery_during_k_increase(edata, sidx, eidx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type sidx:  int
    :type eidx:  int
    :rtype: int
    """
    k_diff_threshold = 5
    u_diff_threshold = 5
    tks, tus = edata.sks[sidx:eidx+1], edata.sus[sidx:eidx+1]
    if max(tks) - min(tks) < 5:
        return sidx

    minmax = data_util.local_minmax_points(tks)
    for idx in range(1, len(minmax)):
        pidx, nidx = minmax[idx-1], minmax[idx]
        if tks[nidx] - tks[pidx] >= k_diff_threshold and tus[nidx] - tus[pidx] >= u_diff_threshold:
            if edata.night_us[pidx+sidx] is None:
                return pidx + sidx
            else:
                return sidx

    return sidx


def _divide_region_by_ratio(edata, sidx, eidx, sratios, lsratios, new_regions, rth):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type sidx:  int
    :type eidx:  int
    :type sratios:  numpy.ndarray
    :type lsratios:  numpy.ndarray
    :type new_regions: list
    :type rth:  float
    :rtype:bool, list[(int, int)]
    """
    lminmax = data_util.local_minmax_points(lsratios[sidx:eidx+1])
    minmax = data_util.local_minmax_points(sratios[sidx:eidx+1])
    ln_minmax = len(minmax)
    n_minmax = len(minmax)
    r_sidx = sidx
    next_stick = sidx

    # iterate local minimum and maximum points
    for idx in range(1, n_minmax):

        # for a hill
        msidx, meidx = minmax[idx-1]+sidx, minmax[idx]+sidx

        # ratio drop < 5% ==> pass
        if max(sratios[r_sidx:msidx+1]) - sratios[meidx] < 0.05:
            continue

        # if ratio is high...
        if sratios[meidx] > 0.95:
            continue

        # if the first hill is ratio-drop hill
        if r_sidx == msidx:
            r_sidx = meidx
            continue

        # if it is not recovered from ratio-drop
        if msidx < next_stick:
            r_sidx = meidx
            continue

        # if there's another little ratio drop
        for tidx in range(1, n_minmax):
            mmsidx, mmeidx = minmax[tidx-1]+sidx, minmax[tidx]+sidx
            if mmsidx <= r_sidx:
                continue
            if mmeidx >= msidx:
                break
            if sratios[mmsidx] - sratios[mmeidx] > 0.02:
                new_regions.append((r_sidx, mmsidx))
                r_sidx = mmeidx

        # if there's another big ratio drop with less-smoothed ratios
        for tidx in range(1, ln_minmax):
            mmsidx, mmeidx = lminmax[tidx-1]+sidx, lminmax[tidx]+sidx
            if mmsidx <= r_sidx:
                continue
            if mmeidx >= msidx:
                break
            if lsratios[mmsidx] - lsratios[mmeidx] > 0.1:
                new_regions.append((r_sidx, mmsidx))
                r_sidx = mmeidx

        new_regions.append((r_sidx, msidx))
        r_sidx = meidx

        next_r_th = sratios[msidx] * 0.98
        for tidx in range(r_sidx, eidx):
            if sratios[tidx] >= next_r_th:
                next_stick = tidx
                break

    if sratios[r_sidx] < sratios[eidx] or not new_regions:
        new_regions.append((r_sidx, eidx))


def _find_wn_ffs_idx(edata, wn_ffs, sidx, eidx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type wn_ffs: float
    :type sidx: int
    :type eidx: int
    :rtype: int
    """

    _sidx, _eidx = edata.ncrt_search_sidx, eidx
    if (sidx - _sidx > setting.INTV2HOUR
        and max(edata.sus[_sidx:sidx]) - min(edata.sus[_sidx:sidx]) > 10):
        _sidx = sidx

    for idx in range(_sidx, 0, -1):
        if edata.sus[idx] >= wn_ffs - 5:
            _sidx = idx
        else:
            break

    wh = np.where(edata.sus[_sidx:] >= wn_ffs)[0]
    if any(wh):
        _sidx = wh[0] + _sidx

    wn_ffs_idx = _eidx
    for idx, _u in enumerate(edata.sus[_sidx:_eidx]):
        if _u < wn_ffs:
            continue
        wn_ffs_idx = idx + _sidx
        break

    wn_ffs_idx = _adjust_with_qdata(edata.qus, edata.sus, wn_ffs_idx)

    if wn_ffs_idx < sidx:
        wn_ffs_idx = sidx

    return wn_ffs_idx


def _ut_data_range(edata, qus, qks):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type qus: numpy.ndarray
    :type qks: numpy.ndarray
    :rtype: (int, int, numpy.ndarray, numpy.ndarray)
    """
    sidx, eidx = edata.ncrt_search_sidx, edata.ncrt_search_eidx
    #sidx = np.argmin(qus[sidx:eidx]).item() + sidx

    tus, tks = qus[sidx:eidx], qks[sidx:eidx]
    wh = np.where(tus >= edata.may_recovered_speed)[0]

    if any(wh):
        eidx = wh[0] - 1 + sidx
        tus, tks = qus[sidx:eidx], qks[sidx:eidx]

    return sidx, eidx, tus, tks


def _find_vertex(xs, ys, find_under=True, offset=0):
    """
    :type target_x: numpy.ndarray
    :type target_y: numpy.ndarray
    :rtype: (int, float, float, float)
    """
    x_first, y_first, x_last, y_last = xs[0], ys[0], xs[-1], ys[-1]
    max_d, x_at_max_d, y_at_max_d, max_d_idx = -1, -1, -1, -1
    for idx, x in enumerate(xs):
        y = ys[idx]
        fy = data_util.get_value_on_line(x, y_first, y_last, x_first, x_last)
        d = data_util.distance_to_line(x, y, y_first, y_last, x_first, x_last)
        if d > max_d and ((find_under and fy >= y) or (not find_under and fy <= y)):
            max_d = d
            x_at_max_d = x
            y_at_max_d = y
            max_d_idx = idx

    return max_d_idx+offset if max_d_idx > 0 else -1, max_d, x_at_max_d, y_at_max_d

#
# def _wn_ffs(edata, recovered_idx):
#     """
#
#     :type edata: pyticas_ncrtes.core.etypes.ESTData
#     :type recovered_idx: int
#     :rtype: float
#     """
#     return np.percentile(edata.sus[recovered_idx-setting.INTV15MIN:recovered_idx+setting.INTV15MIN], 80).item()


def _adjust_with_qdata(qdata, sdata, target_idx):
    """

    :type qdata: numpy.ndarray
    :type sdata: numpy.ndarray
    :type target_idx: int
    :rtype: int
    """
    logger = getLogger(__name__)

    stick = None
    qu = qdata[target_idx]
    for idx in range(target_idx, 0, -1):
        cu = qdata[idx]
        if cu != qu :
            stick = target_idx
            break

    if not stick:
        return target_idx

    for tidx in range(stick, stick+setting.INTV15MIN):
        if sdata[tidx] >= qu:
            return tidx

    # never reaches to here
    logger.debug('Adjust Point %d -> %d !!' % (target_idx, stick))
    return stick