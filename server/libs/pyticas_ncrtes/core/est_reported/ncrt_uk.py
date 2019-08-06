# -*- coding: utf-8 -*-

import numpy as np

from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.core.est.helper import uk_pattern, est_helper
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

DEBUG_MODE = False

def determine(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: int
    """
    logger = getLogger(__name__)

    logger.debug('>>>> NCRT Estimation with Wet-Normal U-K data')

    sks, sus, wn_sratios, normal_ffs = edata.aks, edata.aus, edata.wn_sratios, edata.ffs
    search_start_idx = edata.search_start_idx

    rth = max(0.8, wn_sratios[edata.worst_ratio_idx] + 0.02)

    # recoverying interval
    sidx, eidx = _recovering_interval(edata, search_start_idx, rth)

    if not sidx:
        logger.debug('Recovery-Interval is not found')
        logger.debug('<<< End of NCRT Estimation with Wet-Normal UK pattern')
        return None

    if _is_directly_recovered_from_congestion(sidx, eidx, edata):
        logger.debug('Recovered from congestion')
        ncrt = _determine_ncrt_from_congestion(sidx, eidx, edata)
        logger.debug('<<< End of NCRT Estimation with Wet-Normal UK pattern')
        return ncrt

    # initial NCRT as 100% time point
    ncrt = eidx
    for idx in range(sidx, eidx + 2):
        if idx < eidx - 1 and min(wn_sratios[idx:eidx + 1]) >= 1.0:
            ncrt = idx
            break

    # if NCRT is in freeflow k range and it is less than WN-FFS
    k_at_ncrt = edata.sks[ncrt]
    t_intv = setting.INTV1HOUR
    udiff_th = 5
    found = False
    if k_at_ncrt < 25:
        for idx in range(ncrt, min(ncrt + setting.INTV2HOUR, edata.n_data)):
            to = min(idx + t_intv, edata.n_data - 1)
            tus = edata.sus[idx:to + 1]

            # check continuously increase or decrease
            diffs = np.diff(tus)
            if np.all(diffs > 0) or np.all(diffs < 0):
                continue

            # check speed range
            minu, maxu, avgu = min(tus), max(tus), np.mean(tus)
            if maxu - minu <= udiff_th and edata.sus[idx] >= edata.wn_ffs and avgu >= edata.wn_ffs:
                ncrt = idx
                found = True
                break

        if not found:
            for idx in range(ncrt, min(ncrt + setting.INTV2HOUR, edata.n_data)):
                if edata.sus[idx] >= edata.wn_ffs:
                    ncrt = idx
                    break

    # 2012-12-09, I-35W (NB)
    # if u at ncrt is greater, ncrt must be less than Q-K data range start point used in finding WN-FFSs
    if edata.ncrt_qk_sidx and edata.merged_sus[ncrt] > edata.wn_ffs and ncrt < edata.ncrt_qk_sidx:
        _ssidx = edata.ncrt_qk_sidx - setting.INTV1HOUR
        ssidx = np.argmin(edata.merged_sus[_ssidx:edata.ncrt_qk_eidx]).item() + _ssidx
        for idx in range(ssidx, edata.n_data):
            if edata.merged_sus[idx] >= edata.wn_ffs:
                ncrt = idx
                break

    elif edata.merged_sus[ncrt] > edata.wn_ffs - 5:
        # adjust by speed
        qus = data_util.stepping(edata.sus, 2)
        moved_ncrt = _adjust_with_qdata(qus, edata.merged_sus, ncrt)
        if ncrt - moved_ncrt < setting.INTV1HOUR or edata.merged_sus[moved_ncrt] > edata.wn_ffs:
            ncrt = moved_ncrt

    if edata.wn_ffs_idx and ncrt > edata.wn_ffs_idx:
        ncrt = edata.wn_ffs_idx

    if edata.wn2_after_congestion_idx and ncrt > edata.wn2_after_congestion_idx:
        ncrt = edata.wn2_after_congestion_idx


    if DEBUG_MODE:
        import matplotlib.pyplot as plt
        plt.figure()
        ax1 = plt.subplot(111)
        ax1.plot(edata.sus, c='b', label='u')
        ax1.plot(edata.wn_avg_us, c='g', label='wnu')
        ax1.axvline(x=sidx, label='sidx')
        ax1.axvline(x=eidx, label='eidx')
        ax1.axvline(x=ncrt, label='ncrt', c='r')
        plt.legend()

        ax2 = ax1.twinx()
        ax2.plot(wn_sratios, c='r', label='ratio')
        plt.grid()
        plt.show()



    logger.info('! NCRT = %s' % ncrt)

    if ncrt:
        edata.additional['ncrt_u'] = edata.sus[ncrt]

    logger.debug('<<<< End of NCRT Estimation with Q-K data')

    edata.ncrt = ncrt
    edata.ncrt_type = setting.NCRT_TYPE_QK

    _schart(edata, edata.sks, edata.sus, edata.wn_sratios, edata.wn_avg_us, ncrt)

    return True, ncrt


def _recovering_interval(edata, search_start_idx, rth):
    """

    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :param search_start_idx:
    :type search_start_idx: int
    :param rth:
    :type rth: float
    :return:
    :rtype: (int, int)
    """
    logger = getLogger(__name__)

    logger.debug(' - _recovering_interval() : from %d, rth=%f' % (search_start_idx, rth))
    op1, op2 = _over_threshold_point(edata, search_start_idx, rth), None
    if op1:
        # second-recovered point
        op2 = _find_over_threshold_point(op1, edata.wn_sratios, 1.0, edata)
        logger.debug('op1=%s, op2=%s' % (op1, op2))
    else:
        logger.debug('op1 not found')

    time_limit = setting.INTV30MIN
    for _ in range(5):
        if op1 and _is_temporary_nighttime_reduction(op1, op2, edata):
            logger.debug(' --> temporary nighttime reductio : %d, %d' % (op1, op2))
            _op1 = op1
            op1, op2 = _over_threshold_point(edata, search_start_idx, rth, op1 - time_limit), None
            if op1:
                # second-recovered point
                op2 = _find_over_threshold_point(op1, edata.wn_sratios, 1.0, edata, _op1 - time_limit)
        else:
            break

    # commented by S1606, I-35W (SB), 2012-01-20
    # if op2 and edata.wn_ffs_idx:
    #     op2 = max(op2, edata.wn_ffs_idx)

    logger.debug(' - _recovering_interval() : (%s, %s)' % (op1, op2))

    return _adjust_recovery_interval(edata, op1, op2)


def _adjust_recovery_interval(edata, op1, op2):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type op1: int
    :type op2: int
    :rtype: (int, int)
    """
    if not op1 or not op2 or edata.is_recovered_at_lost:
        return op1, op2

    tks, tus = edata.merged_sks[op1:op2], edata.merged_sus[op1:op2]
    wh1 = np.where(tus >= edata.wn_ffs * 0.9)[0]
    if not any(wh1):
        return op1, op2

    t_recovered_idx = wh1[0] + op1
    tks, tus = edata.merged_sks[t_recovered_idx:op2], edata.merged_sus[t_recovered_idx:op2]
    wh2 = np.where( (tus < edata.wn_ffs * 0.8) & (tks > 20))[0]
    if len(wh2) > setting.INTV30MIN:
        _op2 = np.argmax(edata.merged_sus[t_recovered_idx:t_recovered_idx+setting.INTV30MIN]).item() + t_recovered_idx
        if _op2 < op2:
            minu_idx = np.argmin(edata.merged_sus[_op2:op2]).item() + _op2
            _op2k = np.mean(edata.merged_sks[_op2-setting.INTV15MIN:_op2+setting.INTV15MIN])
            minu_k = np.mean(edata.merged_sks[minu_idx-setting.INTV15MIN:minu_idx+setting.INTV15MIN])
            # if minu_k - _op2k > 3:
            if minu_k > 20:
                print('=> update ncrt (1) : ', t_recovered_idx, op2, '->', _op2)
                return op1, _op2

    tks, tus = edata.merged_sks[op1:op2], edata.merged_sus[op1:op2]
    wh1 = np.where(tus >= edata.wn_ffs * 0.95)[0]
    if not any(wh1):
        return op1, op2

    t_recovered_idx = wh1[0] + op1
    tks, tus = edata.merged_sks[t_recovered_idx:op2], edata.merged_sus[t_recovered_idx:op2]
    wh2 = np.where( tus < edata.wn_ffs * 0.8)[0]
    if not any(wh2):
        _op2 = np.argmax(edata.merged_sus[t_recovered_idx:t_recovered_idx+setting.INTV30MIN]).item() + t_recovered_idx
        if _op2 < op2:
            minu_idx = np.argmin(edata.merged_sus[_op2:op2]).item() + _op2
            _op2k = np.mean(edata.merged_sks[_op2-setting.INTV15MIN:_op2+setting.INTV15MIN])
            minu_k = np.mean(edata.merged_sks[minu_idx-setting.INTV15MIN:minu_idx+setting.INTV15MIN])
            # if minu_k - _op2k > 3:
            if minu_k > 20:
                print('=> update ncrt (2) : ', t_recovered_idx, op2, '->', _op2)
                return op1, _op2

    return op1, op2


def _is_directly_recovered_from_congestion(sidx, eidx, edata):
    """

    :param sidx:
    :type sidx: int
    :param eidx:
    :type eidx: int
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    LOW_K = 10
    CONGESTED_SPEED = 30
    BIG_SPEED_DIFF = 20
    aks, aus = edata.aks, edata.aus

    # move `eidx` to congested area
    _sidx = max(sidx, eidx - setting.INTV1HOUR)
    if _sidx >= eidx:
        return False

    _eidx = np.argmin(aus[_sidx:eidx]).item() + _sidx
    usidx, ueidx = _under_duration(edata.sus, CONGESTED_SPEED, _eidx)

    ssidx = edata.snow_event.snow_start_index
    if usidx > ssidx + setting.INTV1HOUR:
        if min(edata.merged_sus[ssidx:usidx-setting.INTV1HOUR]) > edata.ncrt_search_uth:
            return False
        if edata.srst and usidx < edata.srst + setting.INTV3HOUR:
            return False

    if ((edata.sus[_eidx] < CONGESTED_SPEED or edata.sus[eidx] - edata.sus[_eidx] > BIG_SPEED_DIFF)
        and edata.sks[_eidx] > LOW_K
        and edata.night_us[_eidx] is None
        and (ueidx and usidx and ueidx - usidx > setting.INTV1HOUR)):
        return True

    return False


def _determine_ncrt_from_congestion(sidx, eidx, edata):
    """

    :param sidx:
    :type sidx: int
    :param eidx:
    :type eidx: int
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    logger = getLogger(__name__)

    CONGESTED_SPEED = 20
    rth = 0.9
    time_limit = 60
    wn_qratios, wn_sratios = edata.wn_qratios, edata.wn_sratios
    aks, aus, wn_ffs = edata.aks, edata.aus, edata.wn_ffs
    sidx, eidx = int(sidx), int(eidx)

    logger.debug(' - _determin_ncrt_from_congestion() : %d - %d' % (sidx, eidx))

    # if reaching to 100% at lower speed (# 2012-01-20, S59)
    # if edata.sus[eidx] < edata.wn_ffs * 0.9:
    #    return eidx

    # move `eidx` to congested area
    _sidx = int(max(sidx, eidx - setting.INTV1HOUR))
    if _sidx >= eidx:
        return eidx

    _eidx = np.argmin(aus[_sidx:eidx]).item() + _sidx
    # if edata.sus[eidx] - edata.sus[_eidx] < 15 or edata.sus[_eidx] > 30:
    #     return _determin_ncrt(sidx, eidx, adata)

    eidx = _eidx

    tks, tus = aks[sidx:eidx], aus[sidx:eidx]
    tratios = edata.wn_ratios[sidx:eidx]

    recovered = np.where((tus > CONGESTED_SPEED) & (tratios > rth))

    # move `eidx` to temporary recovered area
    if any(recovered[0]):
        _eidx = eidx = recovered[0][-1] + sidx
        for idx in range(_eidx, sidx, -1):
            if wn_sratios[idx] > rth:
                if aus[idx] > CONGESTED_SPEED:
                    eidx = idx
            else:
                break
    else:
        # 2012-01-20, I-35W(NB), S668
        # 2012-01-20, I-494(EB), S201, S202
        n_congested = 0
        for idx in range(_eidx, sidx, -1):
            if aus[idx] < CONGESTED_SPEED:
                n_congested += 1
            else:
                break

        if n_congested < setting.INTV1HOUR:
            return eidx

        return None

    ncrt = eidx

    # still increase ? (2012-01-20, I-35W (NB), S60 vs S61)
    if wn_sratios[ncrt - 1] < wn_sratios[ncrt] < wn_sratios[ncrt + 1]:
        for idx in range(ncrt, edata.n_data - 1):
            print('-> ncrt=%d, check=%d (%f, %f)' % (ncrt, idx, wn_sratios[idx], wn_sratios[idx + 1]))
            if wn_sratios[idx] >= wn_sratios[idx + 1] or wn_sratios[idx] >= 1.0:
                ncrt = idx
                break
    else:
        # adjust by ratio
        ref_ratio = wn_qratios[eidx]
        for idx in range(eidx, sidx, -1):
            # if wn_qratios[idx] != ref_ratio:
            if wn_qratios[idx] < ref_ratio - 0.02:
                # if max(wn_sratios[idx:eidx]) - min(wn_sratios[idx:eidx]) < 0.02:
                #     ncrt = idx + 1
                ncrt = idx + 1
                break

    return ncrt


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


def _adjust_with_qdata(qdata, sdata, target_idx, target_u=None):
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
        if qu - cu < 2:
            continue
        if cu - qu > 5:
            stick = target_idx
            break

        stick = idx
        break

    if not stick:
        return None

    target_u = (target_u or qu)
    for tidx in range(stick, len(qdata)):
        if sdata[tidx] >= target_u:
            logger.debug('Adjust Point %d -> %d' % (target_idx, tidx))
            return tidx

    # never reaches to here
    logger.debug('Adjust Point %d -> %d !!' % (target_idx, stick))
    return stick


def _over_threshold_point(edata, search_start_idx, rth, search_end_idx=None):
    """

    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :param search_start_idx:
    :type search_start_idx: int
    :param rth:
    :type rth: float
    :param search_end_idx:
    :type search_end_idx: int
    :return:
    :rtype:
    """
    CONGESTED_SPEED = 30
    LOW_K = 5
    wn_sratios = edata.wn_sratios
    if not search_end_idx:
        search_end_idx = len(wn_sratios)
    kt = edata.normal_func.daytime_func.get_Kt()

    # 2013-01-27, I-35W(NB), S72
    drop_sections = _find_ratio_drop_section(search_start_idx, search_end_idx, edata.sus, wn_sratios, rth=0.1)
    for sidx, eidx in drop_sections:
        if edata.sus[eidx] > CONGESTED_SPEED and LOW_K < edata.sks[eidx] < kt and edata.night_us[eidx] is None and \
                        wn_sratios[eidx] < 0.9:
            search_start_idx = eidx

    wn_tratios = wn_sratios[search_start_idx:search_end_idx]
    sus, sks = edata.sus[search_start_idx:search_end_idx], edata.sks[search_start_idx:search_end_idx]
    indices = np.array(range(len(wn_tratios)))

    for idx in indices:
        recovered_after_here = np.where((wn_tratios > rth) & (indices > idx))
        if not any(recovered_after_here[0]) or len(recovered_after_here[0]) < setting.INTV1HOUR:
            break

        indices_after_here = np.where((wn_tratios < rth) & (sus > CONGESTED_SPEED) & (sks > LOW_K) & (indices > idx))
        if any(indices_after_here[0]) and len(indices_after_here) > setting.INTV1HOUR:
            continue

        return idx + search_start_idx

    return None


def _find_over_threshold_point(op1, wn_ratios, rth, edata, search_end_idx=None):
    """

    :param op1:
    :type op1: int
    :param wn_ratios:
    :type wn_ratios: numpy.ndarray
    :param rth:
    :type rth: float
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :param search_end_idx:
    :type search_end_idx: int
    :rtype: int
    """
    if not search_end_idx:
        search_end_idx = len(edata.sus)
    search_end_idx = int(search_end_idx)
    wn_ratios = wn_ratios[:search_end_idx]
    sus = edata.sus[:search_end_idx]
    op2 = op1
    for idx in range(op1, len(wn_ratios)):
        nr = wn_ratios[idx]
        if nr >= rth and (sus[idx] > edata.wn_ffs * 0.9 or sus[idx] > 30):
            op2 = idx
            break

    return int(op2)


def _is_temporary_nighttime_reduction(op1, op2, edata):
    """

    :param op1:
    :type op1: int
    :param op2:
    :type op2: int
    :param edata:
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :return:
    :rtype: (int, int)
    """
    if edata.night_us[op1] is None:
        return False
    rth = 0.9
    time_limit = setting.INTV30MIN

    sidx = int(max(0, op1 - time_limit))
    eidx = int(min(op1 + time_limit, len(edata.night_us) - 1))

    if edata.night_us[sidx] is None or edata.night_us[eidx] is None:
        return False

    if edata.night_sratios[sidx] > rth and edata.night_sratios[eidx] > rth:
        return True

    return False


def _find_ratio_drop_section(op1, op2, sus, wn_ratios, rth=0.05):
    """

    :param op1:
    :type op1: int
    :type sus: numpy.ndarray
    :param wn_ratios:
    :type wn_ratios: numpy.ndarray
    :param rth:
    :type rth: float
    :rtype: list[[int, int]]
    """
    drop_section = []
    decs = []
    decs_u = []
    d_sidx = None
    CONGESTED_SPEED = 30
    for idx in range(op1, op2):
        pr, nr = wn_ratios[idx - 1], wn_ratios[idx]
        pu, nu = sus[idx - 1], sus[idx]
        if pr > nr:
            if not d_sidx:
                d_sidx = idx - 1
            decs.append(pr)
            decs_u.append(pu)
        else:
            if decs:
                decs.append(pr)
                decs_u.append(pu)
                diff = max(decs) - min(decs)
                minu = min(decs_u)
                if diff > rth and minu > CONGESTED_SPEED:
                    drop_section.append([d_sidx, idx - 1])
                d_sidx = None
                decs = []
                decs_u = []
    return drop_section


def _find_speed_drop_section(op1, op2, sus, uth=5):
    """

    :param op1:
    :type op1: int
    :param sus:
    :type sus: numpy.ndarray
    :param uth:
    :type uth: float
    :rtype: list[[int, int]]
    """
    drop_section = []
    decs = []
    d_sidx = None
    for idx in range(op1, op2):
        pu, nu = sus[idx - 1], sus[idx]
        if pu > nu:
            if not d_sidx:
                d_sidx = idx - 1
            decs.append(pu)
        else:
            if decs:
                decs.append(pu)
                diff = max(decs) - min(decs)
                if diff > uth:
                    drop_section.append([d_sidx, idx - 1])
                d_sidx = None
                decs = []
    return drop_section


def _schart(edata, tks, tus, ratios, wetnormal_avg_us, ncrt):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type tks: numpy.ndarray
    :type tus: numpy.ndarray
    :type ratios: numpy.ndarray
    :type wetnormal_avg_us: numpy.ndarray
    :type uk_groups: list[pyticas_ncrtes.core.etypes.UKTrajectoryGroup]
    :type ri_sidx: int
    :type ri_eidx: int
    :type ris: list[[int, int]]
    :type show_chart: bool
    """
    if not DEBUG_MODE:
        return

    # phase._srst(edata)
    # phase._lst(edata)
    # phase._sist(edata)

    import matplotlib.pyplot as plt
    uk_groups, uk_edges, uk_points = uk_pattern.make(0, edata)

    long_title = '%s (%s[s_limit=%d, label=%s], %s) - (%s)' % (
        edata.snow_event.snow_period.get_date_string(),
        edata.target_station.station_id,
        edata.target_station.s_limit,
        edata.target_station.label,
        edata.target_station.corridor.name,
        'Interval=%d' % setting.DATA_INTERVAL)

    dt_func = None
    if edata.normal_func is not None:
        dt_func = edata.normal_func.daytime_func

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='white')
    ax1 = plt.subplot2grid((5, 4), (0, 0), colspan=4, rowspan=2)
    ax11 = plt.subplot2grid((5, 4), (2, 0), colspan=4)
    ax2 = plt.subplot2grid((5, 4), (3, 0), colspan=2, rowspan=2)
    ax3 = plt.subplot2grid((5, 4), (3, 2), colspan=2, rowspan=2)
    # ax1_2 = ax1.twinx()

    qs = tks * tus

    nt_us = edata.normal_func.nighttime_func.speeds(edata.snow_event.data_period.get_timeline(as_datetime=True))
    nt_ks = edata.normal_func.nighttime_func.densities(edata.snow_event.data_period.get_timeline(as_datetime=True))

    # ax3.scatter(tks, tus)

    # ax1.plot(tks, c='#AAAAAA', label='k')
    # ax1.plot(tus, c='#6891BA', label='u')

    sus2 = data_util.smooth(edata.aus, setting.SW_1HOUR)
    sus3 = data_util.smooth(edata.aus, setting.SW_15MIN)

    ax1.plot(edata.ks, c='#AAAAAA', label='k')
    ax1.plot(edata.us, c='#6891BA', label='u')
    # ax1.plot(edata.qus, c='#FFA91E', label='tus')
    ax1.plot(wetnormal_avg_us, c='#8C65C5', label='wn-u')
    # ax1.plot(sus3, c='#00FF1B', label='sus')
    # ax1.plot(sus2, c='#F374FF', label='sus2')

    if edata.wn_ffs:
        ax1.axhline(y=edata.wn_ffs, c='r')
        ax1.axhline(y=edata.k_at_wn_ffs, c='#888888')

    if ncrt:
        ax1.axvline(x=ncrt, c='r')
        ax11.axvline(x=ncrt, c='r')

    if edata.srst:
        ax1.axvline(x=edata.srst, c='#13AACC')
        ax11.axvline(x=edata.srst, c='#13AACC')

    if edata.lst:
        ax1.axvline(x=edata.lst, c='#CC924B')
        ax11.axvline(x=edata.lst, c='#CC924B')

    if edata.sist:
        ax1.axvline(x=edata.sist, c='#60CC55')
        ax11.axvline(x=edata.sist, c='#60CC55')

    for nidx in edata.estimated_nighttime_snowing:
        ax1.axvline(x=nidx, c='#1C7BFF')
        ax11.axvline(x=nidx, c='#1C7BFF')

    # ax2.scatter(edata.ks, edata.us)
    # ax3.scatter(tks, tus)

    # ax1.plot(data_util.smooth(tus, 11), c='#F564FF', label='su')
    # ax1_2.plot(qs, c='#F564FF', label='q')
    ax1.plot(nt_us, c='k', label='us (night)')
    ax1.plot(nt_ks, c='k', label='ks (night)')

    _night_us = np.array(edata.night_us)
    for idx, _nu in enumerate(_night_us):
        if _nu is not None:
            _night_us[idx] = edata.sus_for_night[idx]
    ax1.plot(_night_us, c='#9C5D8A')

    ax1.axvline(x=edata.snow_event.time_to_index(edata.snow_event.snow_start_time), c='k')
    ax1.axvline(x=edata.snow_event.time_to_index(edata.snow_event.snow_end_time), c='k')

    # reported time
    for rp in edata.rps:
        data = np.array([None] * len(tus))
        data[rp] = tus[rp]
        ax1.plot(data, marker='o', ms=10, c='#FF0512', label='RBRT')  # red circle

    ecs = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']
    markers = ['o', 'x', 'd', '^', '<', '>', 'v', 's', '*', '+']

    n_data = len(tks)
    ls = '-'

    used = []
    for gidx, ukg in enumerate(uk_groups):
        lw = 1
        c = ecs[gidx % len(ecs)]
        marker = '|'
        for midx in range(len(markers)):
            marker_stick = '%s-%s' % (c, markers[midx])
            if marker_stick not in used:
                marker = markers[midx]
                used.append(marker_stick)
                break

        _ks, _us = [None] * len(tks), [None] * len(tus)

        sidx, eidx = ukg.edges[0].start_point.sidx, ukg.edges[-1].end_point.eidx
        _sidx, _eidx = sidx, eidx

        if setting.SIDX and (setting.SIDX < sidx < setting.EIDX or setting.SIDX < eidx < setting.EIDX):
            _sidx, _eidx = max(setting.SIDX, sidx), min(setting.EIDX, eidx)
            ax2.plot(edata.ks[_sidx:_eidx + 1], edata.us[_sidx:_eidx + 1], c=c, marker=marker, ms=4, zorder=2)
            ax3.plot(tks[_sidx:_eidx + 1], tus[_sidx:_eidx + 1], c=c, marker=marker, ms=4, zorder=2)
        elif not setting.SIDX:
            ax2.plot(edata.ks[_sidx:_eidx + 1], edata.us[_sidx:_eidx + 1], c=c, marker=marker, ms=4, zorder=2)
            ax3.plot(tks[_sidx:_eidx + 1], tus[_sidx:_eidx + 1], c=c, marker=marker, ms=4, zorder=2)

        for idx in range(sidx, eidx + 1):
            if idx >= n_data - 1:
                break
            _ks[idx] = tks[idx]
            _us[idx] = tus[idx]

        ax1.plot(_us, lw=lw, ls=ls, c=c)

    # normal function
    if dt_func is not None:
        _recv_ks = list(range(5, 150))
        uk_function = dt_func.get_uk_function()

        if uk_function.is_valid():

            ax2.plot(_recv_ks, uk_function.speeds(_recv_ks), ls='-.', lw=2, c='g', label='recovery-function')
            ax3.plot(_recv_ks, uk_function.speeds(_recv_ks), ls='-.', lw=2, c='g', label='recovery-function')

            if edata.wn_ffs:
                ax2.plot(_recv_ks, uk_function.wet_normal_speeds(_recv_ks),
                         ls='-.', c='#F564FF', label='wn-avg')

                ax3.plot(_recv_ks, uk_function.wet_normal_speeds(_recv_ks),
                         ls='-.', c='#F564FF', label='wn-avg')

    if edata.wn_ffs:
        ax11.plot(ratios)
    ax11.plot(data_util.stepping(ratios, 0.05), c='orange')
    ax11.plot(edata.night_ratios, c='green')
    ax11.plot(edata.normal_ratios, c='#EA86FF')
    ax11.plot(data_util.smooth(edata.normal_ratios, 21), c='#EA86FF')
    ax11.plot(data_util.stepping(data_util.smooth(edata.normal_ratios, 21), 0.05), c='#BEFFAC')
    # ax11.plot(smoothed_ratios, c='g')
    ax11.set_ylim(ymax=1.2, ymin=0.6)
    ax11.set_yticks([0.6, 0.8, 0.9, 1.0])
    ax11.set_yticklabels([0.6, 0.8, '', 1.0])
    ax1.grid(), ax11.grid(), ax2.grid(), ax3.grid()

    if not setting.SIDX:
        ax1.set_xlim(xmin=0, xmax=len(tus))
        ax11.set_xlim(xmin=0, xmax=len(tus))
    else:
        ax1.set_xlim(xmin=setting.SIDX, xmax=setting.EIDX)
        ax11.set_xlim(xmin=setting.SIDX, xmax=setting.EIDX)

    ax1.set_ylim(ymin=0, ymax=90)
    max_k = max(tks) + 5
    max_u = max(tus) + 5

    max_k = max_u = 90

    ax2.set_xlim(xmin=0, xmax=150)
    ax2.set_ylim(ymin=0, ymax=max_u)

    ax3.set_xlim(xmin=0, xmax=150)
    ax3.set_ylim(ymin=0, ymax=max_u)

    fig.suptitle(long_title)
    fig.tight_layout()
    fig.subplots_adjust(top=0.92)

    plt.show()
    plt.clf()
    plt.close(fig)
    plt.close('all')