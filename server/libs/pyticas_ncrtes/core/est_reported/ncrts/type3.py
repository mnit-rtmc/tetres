# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import numpy as np

from pyticas_ncrtes.core.est.backup import ncrt_by_u
from pyticas_ncrtes.core import setting
from pyticas_ncrtes.core.est.ncrts import sectionwide
from pyticas_ncrtes.logger import getLogger

SHOW_GRAPH = True

FFS_K = 25


#########################################################
# TYPE3 : There is no Type1-NCRT in the same truck route
#########################################################
def determine(sections):
    """

    :type sections: list[list[pyticas_ncrtes.core.etypes.ESTData]]
    :type not_found_sections: list[int]
    :rtype: list[int]
    """
    logger = getLogger(__name__)
    _not_found_sections = []

    for sidx, s in enumerate(sections):

        logger.debug('# Type3 - Section (%s): %s' % (
            s[0].snow_route.id if s[0].snow_route else None,
            [edata.target_station.station_id for edata in s]
        ))

        snow_start_index = s[0].snow_event.snow_start_index
        snow_end_index = s[0].snow_event.snow_end_index
        s_limit = s[0].target_station.s_limit

        us, ks, sus, sks, qus, qks, used_stations, speeds, densities = sectionwide.load_data(s,
                                                                                             snow_start_index,
                                                                                             snow_end_index,
                                                                                             s_limit,
                                                                                             skip_check_ncrt=True)

        if us is None or not any(us):
            continue

        ncrt_by_u.estimate(s, us, ks, s[0].snow_event.snow_start_index, s[0].snow_event.snow_end_index)

        pst_search_sidx, pst_search_eidx = _find_pst_search_section(sks, sus, s_limit,
                                                                    s[0].snow_event.snow_start_index,
                                                                    s[0].snow_event.snow_end_index)

        logger.debug('  - search range : (%s, %s)' % (pst_search_sidx, pst_search_eidx))
        logger.debug('  - snow_end_index : %s' % s[0].snow_event.snow_end_index)
        logger.debug('  - n_data : %s' % (len(us) if us is not None and any(us) else '0'))

        if SHOW_GRAPH:
            title = '%s' % [edata.target_station.station_id for edata in s]
            import matplotlib.pyplot as plt
            fig = plt.figure()
            plt.plot(us, marker='.')
            plt.plot(sus, c='#888888')
            plt.plot(ks)
            plt.axhline(y=s_limit, c='g')
            if pst_search_sidx:
                plt.axvline(x=pst_search_sidx, c='b')
            if pst_search_eidx:
                plt.axvline(x=pst_search_eidx, c='r')
            plt.grid()
            plt.title(title)
            fig2 = plt.figure()
            for ed in s:
                if ed.sus is None or not any(ed.sus):
                    continue
                plt.plot(ed.sus, label=ed.target_station.station_id)
            plt.grid()
            plt.legend()
            plt.axhline(y=s_limit, c='g')
            plt.title(title)
            plt.show()
            plt.close(fig)
            plt.close(fig2)

        snowday_ffs_idx, snowday_ffs, pst, ssbpst, ssapst = sectionwide.find_alternatives_for_section(s, ks, us, sks, sus, qks,
                                                                                          qus,
                                                                                          search_from=pst_search_sidx,
                                                                                          search_to=pst_search_eidx)


        alts = np.array([a for a in [snowday_ffs_idx, ssbpst, ssapst] if a is not None])
        logger.debug('  - alts : %s' % alts.tolist())

        if not any(alts):
            continue

        _update_ncrt_without_ncrt_type1(s, alts, pst, ssbpst, ssapst, snowday_ffs_idx, sks, sus, pst_search_sidx, pst_search_eidx)

    return _not_found_sections


def _update_ncrt_without_ncrt_type1(edata_list, alts, pst, ssbpst, ssapst, snowday_ffs_idx, ks, us, pst_search_sidx, pst_search_eidx):
    """
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :type alts: numpy.ndarray
    :type pst: int
    :type ssbpst: int
    :type ssapst: int
    :type snowday_ffs_idx: int
    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type pst_search_sidx: int
    :type pst_search_eidx: int
    :rtype: float
    """
    logger = getLogger(__name__)
    for edata in edata_list:

        if edata.ncrt or edata.us is None or not any(edata.us):
            continue
        #
        # section_ncrt = ncrt
        # logger.debug('update ncrt of %s : %s' % (edata.target_station.station_id, section_ncrt))
        # moved_ncrt = sectionwide.adjust_with_qdata(edata.qus, edata.merged_sus, section_ncrt)
        # if moved_ncrt:
        #     section_ncrt = moved_ncrt
        # logger.debug('adjusted update ncrt of %s : %s' % (edata.target_station.station_id, section_ncrt))
        # edata.ncrt = max(section_ncrt, pst_search_sidx)
        # edata.ncrt_type = setting.NCRT_TYPE_SECTIONWISE

        edata.pst = pst
        edata.sbpst = ssbpst
        edata.sapst = ssapst
        edata.nfrt = snowday_ffs_idx

        # if pst:
        #     edata.pst = sectionwide.adjust_with_qdata(edata.qus, edata.merged_sus, pst)
        #
        # if ssbpst:
        #     edata.sbpst = sectionwide.adjust_with_qdata(edata.qus, edata.merged_sus, ssbpst)
        #
        # if ssapst:
        #     edata.sapst = sectionwide.adjust_with_qdata(edata.qus, edata.merged_sus, ssapst)
        #
        # if snowday_ffs_idx:
        #     edata.nfrt = sectionwide.adjust_with_qdata(edata.qus, edata.merged_sus, snowday_ffs_idx)


def _find_pst_search_section(ks, us, s_limit, snow_start_index, snow_end_index):
    """

    :type ks:  numpy.ndarray
    :type us:  numpy.ndarray
    :type s_limit:  int
    :type snow_start_index:  int
    :type snow_end_index:  int
    :rtype: int, int
    """
    if ks is None or not any(ks):
        return None, None

    n_data = len(ks)
    t_margin = setting.INTV30MIN

    sidx = _find_sidx_to_pst(ks, us, snow_start_index, snow_end_index, s_limit)
    if sidx is None:
        return None, None
    sidx = _move_to_beginning_of_recovery(ks, us, sidx, s_limit, t_margin)
    if sidx < snow_start_index:
        sidx = np.argmin(us[snow_start_index:snow_start_index + setting.INTV2HOUR]).item() + snow_start_index
    eidx = _eidx_after_pst(ks, us, snow_end_index, sidx)

    return sidx, eidx


def _find_sidx_to_pst(ks, us, snow_start_index, snow_end_index, s_limit):
    """

    :type ks:  numpy.ndarray
    :type us:  numpy.ndarray
    :type tidx: int
    :type s_limit: int
    :rtype:
    """
    t_margin = setting.INTV30MIN
    u_limit = s_limit - 5
    u_limit2 = s_limit - 10
    n_data = len(ks)
    minu_idx = np.argmin(us[snow_start_index:snow_end_index]).item() + snow_start_index
    for idx in range(minu_idx, n_data - t_margin):
        if us[idx] < u_limit:
            continue
        if np.mean(us[idx:idx + t_margin]) < u_limit:
            continue
        # wh = np.where((ks[idx:] < FFS_K) & (us[idx:] < s_limit))[0]
        wh2 = np.where((ks[idx:] < FFS_K) & (us[idx:] < u_limit2))[0]
        # if not any(wh) or (len(wh) < setting.INTV30MIN and not any(wh2) < setting.INTV1HOUR):
        if len(wh2) < setting.INTV1HOUR:
            return np.argmax(us[idx - t_margin:idx + t_margin]).item() + (idx - t_margin)
    return None


def _move_to_beginning_of_recovery(ks, us, tidx, s_limit, t_margin):
    """

    :type ks:  numpy.ndarray
    :type us:  numpy.ndarray
    :type tidx: int
    :type s_limit: int
    :type t_margin: int
    :rtype:
    """
    from_idx = max(tidx - t_margin, t_margin)
    for tidx in range(from_idx, t_margin, -1):
        _tus = us[tidx - t_margin:tidx + t_margin]
        if np.mean(_tus) < s_limit:
            for didx in range(tidx, 0, -1):
                if us[didx - 1] > us[didx]:
                    return max(didx, tidx)
    return tidx


def _eidx_after_pst(ks, us, snow_end_index, over_uth_point):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type over_uth_point: int
    :rtype: int
    """
    to_idx = min(over_uth_point + 6 * setting.INTV1HOUR, len(us) - setting.INTV1HOUR)
    to_idx = max(snow_end_index + setting.INTV4HOUR, to_idx)
    if ks[to_idx] > FFS_K:
        wh = np.where(ks[to_idx:] < FFS_K)
        if any(wh[0]):
            to_idx = min(to_idx + wh[0][0] + setting.INTV1HOUR, len(us) - 1)
    return to_idx
