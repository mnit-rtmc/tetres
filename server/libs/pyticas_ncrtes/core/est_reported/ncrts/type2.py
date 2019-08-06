# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import numpy as np

from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.core.est.ncrts import sectionwide
from pyticas_ncrtes.logger import getLogger

SHOW_GRAPH = False


####################################################
# TYPE2 : There is Type1-NCRT in the same section
####################################################
def determine(edata_list):
    """

    :param edata_list: ESTData list in a same section
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    """
    logger = getLogger(__name__)

    logger.debug('>>> Type2 - Section (%s): %s' % (
        edata_list[0].snow_route.id if edata_list[0].snow_route else None,
        [edata.target_station.station_id for edata in edata_list]
    ))

    # check if there is TYPE1 NCRT in the section
    ncrts = [edata.ncrt for edata in edata_list if edata.ncrt]
    if not any(ncrts):
        logger.debug('<<< Type2 - Section (%s): %s' % (
            edata_list[0].snow_route.id if edata_list[0].snow_route else None,
            [edata.target_station.station_id for edata in edata_list]
        ))
        return False

    snow_event = edata_list[0].snow_event
    snow_start_index = snow_event.snow_start_index
    snow_end_index = snow_event.snow_end_index
    s_limit = edata_list[0].target_station.s_limit

    us, ks, sus, sks, qus, qks, used_stations, speeds, densities = sectionwide.load_data(edata_list,
                                                                                         snow_start_index,
                                                                                         snow_end_index, s_limit)

    if us is None or not any(us):
        return False

    snowday_ffs_idx, snowday_ffs, pst, ssbpst, ssapst = sectionwide.find_alternatives_for_section(edata_list,
                                                                                      ks, us,
                                                                                      sks, sus,
                                                                                      qks, qus)

    if SHOW_GRAPH and us is not None and any(us):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.plot(us, marker='.')
        plt.plot(sus, c='#888888')
        plt.plot(ks)
        plt.axhline(y=s_limit, c='g')
        plt.grid()

        fig2 = plt.figure()
        for ed in edata_list:
            if ed.sus is None or not any(ed.sus):
                continue
            plt.plot(ed.sus, label=ed.target_station.station_id)
        plt.grid()
        plt.legend()
        plt.title('with nearby_ncrt')
        plt.axhline(y=s_limit, c='g')

        plt.show()
        plt.close(fig)
        plt.close(fig2)

    if pst is None:
        logger.debug('<<< Type2 - Section (%s): %s' % (
            edata_list[0].snow_route.id if edata_list[0].snow_route else None,
            [edata.target_station.station_id for edata in edata_list]
        ))
        return False

    # alrternatives of NCRT
    alts = np.array([a for a in [snowday_ffs_idx, ssbpst, ssapst] if a is not None])

    logger.debug(' - individual NCRTs : %s ' %
                 [(edata.target_station.station_id, edata.ncrt) for edata in edata_list if edata.ncrt])

    logger.debug(' - snowday_ffs_idx : %s, snowday_ffs : %s, pst=%s, ssbpst=%s, ssapst=%s'
                 % (snowday_ffs_idx, snowday_ffs, pst, ssbpst, ssapst))

    if not any(alts):
        logger.debug('<<< Type2 - Section (%s): %s' % (
            edata_list[0].snow_route.id if edata_list[0].snow_route else None,
            [edata.target_station.station_id for edata in edata_list]
        ))
        return False

    # when there is TYPE-1 NCRTs in the same section
    _update_ncrt_with_ncrt_type1(edata_list, ncrts, alts, pst, ssbpst, ssapst, snowday_ffs_idx, sus, sks)

    for edata in edata_list:
        logger.debug('  -> %s : NCRT=%s, NCRT_TYPE=%s' % (edata.target_station.station_id, edata.ncrt, edata.ncrt_type))

    logger.debug('<<< Type2 - Section (%s): %s' % (
        edata_list[0].snow_route.id if edata_list[0].snow_route else None,
        [edata.target_station.station_id for edata in edata_list]
    ))

    return True


def _update_ncrt_with_ncrt_type1(edata_list, ncrts, alts, pst, ssbpst, ssapst, snowday_ffs_idx, sus, sks):
    """
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :type ncrts: list[int]
    :type alts: numpy.ndarray
    :type pst: int
    :type ssbpst: int
    :type ssapst: int
    :type snowday_ffs_idx: int
    :type sus: numpy.ndarray
    :type sks: numpy.ndarray
    :rtype: float
    """

    # average NCRT in TYPE1 NCRTs
    avg_ncrt, to_be_removed = _avg_ncrt(ncrts)
    logger = getLogger(__name__)

    logger.debug('   -> min_ncrt=%s, avg_ncrt=%s, avg_ncrt(filtered)=%s, max_ncrt=%s' % (
        min(ncrts) if ncrts else None,
        np.mean(ncrts) if ncrts else None,
        avg_ncrt,
        max(ncrts) if ncrts else None,
    ))

    diffs = (alts - avg_ncrt)
    min_idx = np.argmin(diffs)
    min_diff_ncrt = alts[min_idx]

    # adjust min_diff_ncrt if it is too far from individual NCRT
    # when TYPE1 NCRT in the same truck route
    if min_diff_ncrt - avg_ncrt > setting.INTV2HOUR:
        min_diff_ncrt = max(ncrts)
    elif avg_ncrt - min_diff_ncrt > setting.INTV2HOUR:
        min_diff_ncrt = min(ncrts)

    for idx, edata in enumerate(edata_list):

        if edata.us is None or not any(edata.sus):
            continue

        if edata.ncrt:  # and idx not in to_be_removed:
            continue

        ncrt, ncrt_type = min_diff_ncrt, 2
        qus = data_util.stepping(edata.sus, 2)
        moved_ncrt = sectionwide.adjust_with_qdata(qus, edata.merged_sus, ncrt)
        if moved_ncrt:
            ncrt = moved_ncrt

        edata.ncrt = ncrt
        edata.ncrt_type = setting.NCRT_TYPE_SECTIONWISE

        edata.pst = pst
        edata.bpst = ssbpst
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



def _avg_ncrt(ncrts):
    """
    :type ncrts: list[int]
    :rtype: int, list[int]
    """
    to_be_removed = []

    if not any(ncrts):
        return None, to_be_removed

    if len(ncrts) <= 2:
        return int(np.mean(ncrts).item()), to_be_removed

    ncrts = np.array(ncrts)
    diff_max = setting.INTV2HOUR
    avg = np.mean(ncrts)
    diffs = abs(ncrts - avg)

    wh = np.where(diffs > diff_max)
    if any(wh[0]):
        t_ncrts = [ncrt for idx, ncrt in enumerate(ncrts) if idx not in wh[0]]
        to_be_removed = list(wh[0])
        if any(t_ncrts):
            return int(np.mean(t_ncrts).item()), to_be_removed

    return int(np.mean(ncrts).item()), to_be_removed
