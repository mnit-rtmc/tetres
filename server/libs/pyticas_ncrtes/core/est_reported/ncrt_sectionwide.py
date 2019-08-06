# -*- coding: utf-8 -*-

import numpy as np

from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.core.est.helper import est_helper
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def adjust_ncrts(edata_list, sections):
    """

    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :type sections: list[list[pyticas_ncrtes.core.etypes.ESTData]]
    :rtype: float
    """
    logger = getLogger(__name__)
    logger.debug('>>>>>> Adjust Type1 NCRTs')
    for sidx, s in enumerate(sections):
        logger.debug('>>>>>>>> Section : %s' % [edata.target_station.station_id for edata in s])
        if any(s):
            _adjust_type1_ncrts(s)
        logger.debug('<<<<<<<< End of Section : %s' % [edata.target_station.station_id for edata in s])

    logger.debug('<<<<<< End of Adjust Type1 NCRTs')

    return edata_list


def _adjust_type1_ncrts(edata_list):
    """

    :param edata_list: ESTData list in a same section
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    """
    logger = getLogger(__name__)

    edatas = [edata for edata in edata_list if edata.ncrt]
    ncrts = [edata.ncrt for edata in edatas]

    logger.debug('# AdjustType1NCRTs of Section (%s): %s' % (
        edata_list[0].snow_route.id if edata_list[0].snow_route else None,
        [edata.target_station.station_id for edata in edata_list]
    ))

    if not ncrts or max(ncrts) - min(ncrts) < setting.INTV1HOUR:
        logger.debug('> not need to adjust : %s' % ncrts)
        return

    sorted_edatas = sorted(edatas, key=lambda edata: edata.ncrt)
    sorted_ncrts = [edata.ncrt for edata in sorted_edatas]

    logger.debug(' > stations : %s ' % [edata.target_station.station_id for edata in edatas])
    logger.debug(' > n_ncrt : %s ' % len(sorted_ncrts))
    logger.debug(' > avg ncrt : %s ' % np.mean(sorted_ncrts))
    logger.debug(' > stddev ncrt : %s ' % np.std(sorted_ncrts))
    logger.debug(' > ncrts : %s ' % sorted_ncrts)

    filtered_sorted_ncrts = list(sorted_ncrts)
    filtered_sorted_edatas = list(sorted_edatas)

    if len(ncrts) > 3:
        avg = np.mean(sorted_ncrts)
        t_margin = setting.INTV2HOUR
        filtered_sorted_ncrts = [ncrt for ncrt in sorted_ncrts if avg - t_margin <= ncrt <= avg + t_margin]
        filtered_sorted_edatas = [edata for edata in sorted_edatas if avg - t_margin <= edata.ncrt <= avg + t_margin]

    if not filtered_sorted_ncrts:
        filtered_sorted_ncrts = sorted_ncrts
        filtered_sorted_edatas = sorted_edatas

    logger.debug(' > filtered ncrts : %s ' % filtered_sorted_ncrts)

    for eidx, ncrt in enumerate(filtered_sorted_ncrts):
        logger.debug(' - check ncrt : %d' % ncrt)
        if _check_real_ncrt(ncrt, filtered_sorted_ncrts, filtered_sorted_edatas):
            logger.debug('  > updated ncrt : %d' % ncrt)
            for edata in sorted_edatas:
                _update_ncrt(ncrt, edata)
            break


def _check_real_ncrt(target_ncrt, sorted_ncrts, sorted_edatas):
    """

    :param target_ncrt:
    :type target_ncrt: int
    :param sorted_ncrts:
    :type sorted_ncrts: list[int]
    :param sorted_edatas:
    :type sorted_edatas: list[pyticas_ncrtes.core.etypes.ESTData]
    """
    for edata in sorted_edatas:
        if edata.ncrt <= target_ncrt:
            continue
        if not _may_recovered_here(target_ncrt, edata):
            return False
    return True


def _may_recovered_here(target_ncrt, edata):
    """

    :param target_ncrt:
    :type target_ncrt: int
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    LOW_K = 10
    CONGESTED_SPEED = 30
    rth = 0.8
    time_limit = setting.INTV30MIN

    logger = getLogger(__name__)
    own_ncrt = edata.ncrt
    wn_sratios = edata.wn_sratios

    if wn_sratios is None or not any(wn_sratios):
        wn_sratios = np.array([ _u / edata.wn_ffs for _u in edata.merged_sus ])

    # low-ratio
    if wn_sratios[target_ncrt] < rth:
        logger.debug(' -> low ratio : %s, %s' % (target_ncrt, edata.target_station.station_id))
        return False

    # # speed is too low
    # if edata.sus[own_ncrt] - edata.sus[target_ncrt] > 10 and edata.sus[target_ncrt] > CONGESTED_SPEED:
    #     return False

    # check snowing time or recoverying time
    cps = edata.estimated_nighttime_snowing + edata.reduction_by_snow + edata.uk_change_point + [edata.search_start_idx]
    if any(cps) and target_ncrt < max(cps):
        logger.debug(' -> before cps : %s, %s, %s' % (cps, target_ncrt, edata.target_station.station_id))
        return False

    # check low-ratios
    wn_tratios = wn_sratios[target_ncrt:own_ncrt + 1]
    sus, sks = edata.sus[target_ncrt:own_ncrt + 1], edata.sks[target_ncrt:own_ncrt + 1]
    losted = np.where((wn_tratios < rth) & (sus > CONGESTED_SPEED) & (sks > LOW_K))
    if len(losted[0]) > time_limit:
        logger.debug(' -> time limit : %s, %s' % (target_ncrt, edata.target_station.station_id))
        return False

    return True


def _update_ncrt(target_ncrt, edata):
    """

    :param target_ncrt:
    :type target_ncrt: int
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    qus = data_util.stepping(edata.sus, 2)
    cps = edata.estimated_nighttime_snowing + edata.reduction_by_snow + edata.uk_change_point

    logger = getLogger(__name__)
    logger.debug(
        'try to update : %s %s => %s (cps=%s)' % (edata.target_station.station_id, edata.ncrt, target_ncrt, cps))
    edata.own_ncrt = edata.ncrt
    edata.ncrt = target_ncrt

    # if abs(edata.ncrt - target_ncrt) < setting.INTV1HOUR:
    #     return

    u_at_ncrt = qus[target_ncrt]
    for idx in range(target_ncrt, edata.search_start_idx + setting.INTV30MIN, -1):
        if qus[idx] != u_at_ncrt:
            logger.debug('update ncrt(2) : %s : %s -> %s ( %s -> %s)' % (
                edata.target_station.station_id, edata.ncrt, idx + 1, u_at_ncrt, u_at_ncrt))
            if idx != target_ncrt:
                edata.ncrt = idx + 1
            return



def remove_section_with_single_station(edata_list, sections):
    """

    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :type sections: list[list[pyticas_ncrtes.core.etypes.ESTData]]
    :rtype: list[pyticas_ncrtes.core.etypes.ESTData], list[list[pyticas_ncrtes.core.etypes.ESTData]]
    """
    to_be_removed_section, to_be_removed_station = [], []
    for sidx, s in enumerate(sections):
        if len(s) > 1:
            continue
        #if not s[0].ncrt or s[0].ncrt_type == setting.NCRT_TYPE_SECTIONWISE:
        to_be_removed_station.append(s[0].target_station.station_id)
        to_be_removed_section.append(sidx)

    _edata_list = [edata for edata in edata_list if edata.target_station.station_id not in to_be_removed_station]
    _sections = [s for sidx, s in enumerate(sections) if sidx not in to_be_removed_section]

    return _edata_list, _sections