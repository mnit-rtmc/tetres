# -*- coding: utf-8 -*-

import numpy as np

from pyticas.tool import tb
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import etypes, data_util
from pyticas_ncrtes.core import setting
from pyticas_ncrtes.core.est import target, wnffs_finder, ncrt_finder
from pyticas_ncrtes.logger import getLogger

FFS_K = setting.FFS_K

UTH = 10
NTH = 5
UTH_FOR_HIGH_K = 30
LOW_K = 10

U_DIFF_THRESHOLD = 8
K_DIFF_THRESHOLD = 5

CONGESTED_SPEED = 30

DEBUG_MODE = False
SAVE_CHART = False

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def make(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    logger = getLogger(__name__)

    logger.debug(' >>> wn_uk.make() ')
    is_recovered_from_congestion = _check_directly_recovered_from_congestion(edata)

    if is_recovered_from_congestion:
        edata.wn_ffs = None
        edata.wn_ffs_idx = None
        edata.ncrt_search_sidx = None
        edata.ncrt_search_eidx = None
        if edata.normal_func.is_valid() and edata.wn2_interval_sidx:
            logger.debug('  - make wet normal pattern without wn_ffs (tmp-recovered : %d - %d) ' % (edata.wn2_interval_sidx, edata.wn2_interval_eidx))
            edata.make_wet_normal_pattern_without_wnffs()
        else:
            logger.debug('  - cannot make wet normal pattern without wn_ffs (there is no temp-recovered area)')

    else:
        if edata.normal_func.is_valid():
            wn_sidx, k_at_wn_ffs = _k_at_wn_ffs(edata, edata.wn_ffs)
            edata.k_at_wn_ffs = k_at_wn_ffs
            logger.debug('  - make wet normal pattern with wn_ffs (wn_ffs=%.2f, wn_ffs_idx=%d, k_at_wn_ffs=%.2f)' % (edata.wn_ffs, edata.wn_ffs_idx, edata.k_at_wn_ffs))
            edata.make_wet_normal_pattern(edata.wn_ffs, edata.k_at_wn_ffs)
        else:
            logger.debug('  - cannot make wet normal pattern with wn_ffs (no normal uk function)')

    logger.debug(' <<< end of wn_uk.make() ')


def _check_directly_recovered_from_congestion(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    BIG_SPEED_DIFF = 20
    sidx, eidx = edata.ncrt_search_sidx, edata.ncrt_search_eidx
    wh = np.where(edata.sus[sidx:eidx] > edata.may_recovered_speed)[0]
    if not any(wh) or wh[0] == 0:
        return False

    rsidx, reidx = None, None
    minmax = data_util.local_minmax_points(edata.sus)
    for idx in range(1, len(minmax)):
        rsidx, reidx = minmax[idx-1], minmax[idx]
        if rsidx <= sidx <= reidx:
            break

    # if not recovery from congestion to may-recovered speed,
    if (edata.sus[rsidx] > CONGESTED_SPEED or edata.sus[reidx] < edata.may_recovered_speed):
        return False

    # move `eidx` to congested area
    usidx, ueidx = _under_duration(edata.lsus, CONGESTED_SPEED, rsidx)

    # check if it is first down from snow-start
    ssidx = edata.snow_event.snow_start_index
    if usidx > ssidx + setting.INTV1HOUR:
        if min(edata.sus[ssidx:usidx-setting.INTV1HOUR]) > edata.ncrt_search_uth:
            return False
        if edata.srst and usidx < edata.srst + setting.INTV3HOUR:
            return False

    # check if there is congestion before temporary-recovered area
    _sidx, _eidx = max(usidx - setting.INTV1HOUR, 0), min(usidx + setting.INTV1HOUR, edata.n_data-1)
    _maxu_idx = np.argmax(edata.sus[_sidx:_eidx]).item() + _sidx
    first_congestion_end_idx = 0
    for idx in range(_maxu_idx, 0, -1):
        if edata.sus[idx] < CONGESTED_SPEED:
            first_congestion_end_idx = idx
            break

    if ( (_maxu_idx - first_congestion_end_idx < setting.INTV2HOUR or edata.sus[_maxu_idx] < edata.ncrt_search_uth)
        and edata.sus[reidx] - edata.sus[rsidx] > BIG_SPEED_DIFF
        and ueidx - usidx > setting.INTV1HOUR):
        edata.wn2_after_congestion_idx = np.where(edata.sus[rsidx:reidx] > edata.ncrt_search_uth)[0][0] + rsidx
        _decide_wn2_reduction_interval(edata, usidx, ueidx, edata.wn2_after_congestion_idx)
        return True

    return False


def _k_at_wn_ffs(edata, wn_ffs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type wn_ffs: float
    :rtype: int, float
    """
    if not wn_ffs:
        return None, None

    # find k at wn_ffs
    k_at_wn_ffs, wn_sidx = None, None
    for idx in range(edata.ncrt_search_sidx, len(edata.ks)):
        if edata.sus[idx] >= wn_ffs:
            wn_sidx = idx
            k_at_wn_ffs = edata.sks[idx]
            break

    return wn_sidx, k_at_wn_ffs


def _decide_wn2_reduction_interval(edata, usidx, ueidx, after_congested_idx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type after_congested_idx: int
    :rtype:
    """
    rth = 0.8
    tmp_recovered_u_th = 20
    edata.should_wn_uk_without_ffs = True
    sidx, eidx = max(usidx - setting.INTV1HOUR, 0), min(usidx + setting.INTV1HOUR, edata.n_data-1)
    maxu_idx = np.argmax(edata.sus[sidx:eidx]).item() + sidx

    if edata.sratios[maxu_idx] < rth and edata.lsratios[maxu_idx] < rth:
        getLogger(__name__).debug('  - temporary recovered area is not found according to normal ratio (maxu_idx=%d, r=%f)'
                                  % (maxu_idx, edata.normal_ratios[maxu_idx]))
        edata.should_wn_uk_without_ffs = False
        return True


    edata.wn2_interval_sidx = maxu_idx
    edata.wn2_interval_eidx = maxu_idx
    for idx in range(maxu_idx, edata.n_data):
        if edata.sus[idx] < tmp_recovered_u_th:
            break
        edata.wn2_interval_eidx = idx

    getLogger(__name__).debug('   - wn2_interval (%d - %d), after_congestion_idx=%d' % (maxu_idx, usidx, edata.wn2_after_congestion_idx))
    return True


def _under_duration(us, uth, target_idx):
    """

    :type us: numpy.ndarray
    :type uth: float
    :type target_idx: int
    :rtype: (int, int)
    """
    prev_idx = target_idx
    for idx in range(target_idx, 0, -1):
        if us[idx] > uth:
            break
        prev_idx = idx

    next_idx = target_idx
    for idx in range(target_idx, len(us)):
        if us[idx] > uth:
            break
        next_idx = idx
    return (prev_idx, next_idx)