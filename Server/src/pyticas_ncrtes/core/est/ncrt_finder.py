# -*- coding: utf-8 -*-
from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def find(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    logger = getLogger(__name__)
    logger.debug(' >>> ncrt_finder.find() : wn_ffs_idx=%s, wn_ffs=%s' % (edata.wn_ffs_idx, edata.wn_ffs))
    has_normal_uk_function = edata.normal_func.is_valid()

    if has_normal_uk_function and edata.wn_ffs_idx:
        logger.debug('  - determine NCRT with wet-normal uk function')
        _determine_with_wnuk(edata)
    elif has_normal_uk_function and edata.should_wn_uk_without_ffs:
        if edata.wn2_interval_sidx:
            logger.debug('  - determine NCRT with wet-normal uk function (recovered-from-congested)')
            # recovered from congestion
            _determine_ncrt_from_congestion(edata)
        else:
            # NCRT cannot be determined
            logger.debug('  - cannot determine NCRT (recovered-from-congested)')

    elif edata.wn_ffs_idx:
        logger.debug('  - determine NCRT without wet-normal uk function')
        edata.ncrt = _adjust_with_speed(edata, edata.wn_ffs_idx)
    else:
        logger.debug('  - cannot determine NCRT')

    if edata.ncrt and edata.ncrt_search_sidx and edata.ncrt < edata.ncrt_search_sidx:
        edata.ncrt = edata.wn_ffs_idx

    logger.debug(' <<< end of ncrt_finder.find() ')


def _determine_with_wnuk(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    ncrt = edata.wn_ffs_idx
    if edata.sus[ncrt] > edata.wn_ffs - 5:
        for idx in range(ncrt, 0, -1):
            if edata.wn_sratios[idx] > 1.0 or edata.wn_qratios[idx] > 1.0:
                ncrt = idx
            else:
                break

    _ncrt = _adjust_with_wn_ratio(edata, ncrt)
    ncrt = _ncrt if _ncrt > edata.ncrt_search_sidx else ncrt

    if edata.qus[ncrt] > edata.wn_ffs - 5 :
        _ncrt = _adjust_with_speed(edata, ncrt)
        ncrt = _ncrt if _ncrt > edata.ncrt_search_sidx else ncrt

    edata.ncrt = ncrt

def _determine_ncrt_from_congestion(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    # wn2_interval_sidx : max-u point during temp-recovered-area
    ncrt = edata.wn2_interval_sidx

    for idx in range(ncrt, 0, -1):
        if edata.wn_sratios[idx] > 1.0 or edata.wn_qratios[idx] > 1.0:
            ncrt = idx
        else:
            break

    edata.ncrt = _adjust_with_wn_ratio(edata, ncrt)


def _adjust_with_wn_ratio(edata, target_idx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type target_idx: int
    :rtype:
    """

    wn_qratios = edata.wn_qratios
    moved_idx = target_idx
    ref_ratio = wn_qratios[target_idx]
    for idx in range(target_idx, 0, -1):
        if wn_qratios[idx] < ref_ratio - 0.02:
            moved_idx = idx + 2
            break

    return moved_idx


def _adjust_with_speed(edata, target_idx):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type target_idx: int
    :rtype: int
    """
    logger = getLogger(__name__)

    sdata = data_util.smooth(edata.us, setting.SW_30MIN)
    qdata = edata.qus #data_util.stepping(sdata, 2)

    stick = None
    qu = qdata[target_idx]
    for idx in range(target_idx, 0, -1):
        cu = qdata[idx]
        if cu != qu :
            stick = idx
            break

    if not stick:
        return target_idx

    _stick = stick
    for idx in range(stick, 0, -1):
        if sdata[idx] > qu:
            _stick = idx + 1
        else:
            break

    stick = _stick

    # for tidx in range(stick, stick+setting.INTV15MIN):
    #     if sdata[tidx] >= qu:
    #         return tidx + 1

    # never reaches to here
    return stick

# def _check_if_recovered_before_wnffs(edata):
#     """
#     :type edata: pyticas_ncrtes.core.etypes.ESTData
#     """
#     r_margin = 0.03
#     t_margin = setting.INTV1HOUR
#     wn_ffs_idx = edata.wn_ffs_idx
#     prev_wn_ratios = edata.wn_sratios[wn_ffs_idx-t_margin:wn_ffs_idx]
#
#     # ratio is stable...before wn-ffs
#     if max(prev_wn_ratios) - min(prev_wn_ratios) < r_margin or min(prev_wn_ratios) > 1 - r_margin:
#         return True
#     return False
