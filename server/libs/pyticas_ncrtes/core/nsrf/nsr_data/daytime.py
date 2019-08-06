# -*- coding: utf-8 -*-

import numpy as np
from matplotlib import pyplot as plt

from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.core.nsrf.nsr_func import fitting
from pyticas_ncrtes.core.nsrf.target import lane
from pyticas_ncrtes.core.setting import SW_1HOUR
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

SHOW_GRAPH = False
UK = []
wb = None

def collect(target_station, periods, **kwargs):
    """ return recovery and reduction pattern UK data set

    :type target_station: pyticas.ttypes.RNodeObject
    :type periods: list[pyticas.ttypes.Period]

    :rtype: (list[pyticas.ttypes.Period],
             dict[float, float], dict[float, float], dict[float, float],
             list[list[float]], list[list[float]],
             list[pyticas.ttypes.RNodeData], list[pyticas.ttypes.RNodeData],
             list[pyticas.ttypes.DetectorObject,
             list[pyticas.ttypes.Period],
            dict[float, float])
    """
    # Procedure
    # 1. check malfunctioned detector in a given target station
    # 2. iterate for all time periods
    #    2.1 call _collect_data_a_data with a time period
    #    2.2 save the daily data from 2.1
    global wb

    logger = getLogger(__name__)
    allow_not_congested = kwargs.get('allow_not_congested', False)
    dc, valid_detectors = kwargs.get('dc', None), kwargs.get('valid_detectors', None)
    if not dc:
        dc, valid_detectors = lane.get_detector_checker(target_station)

    if not dc:
        return None, None, None, None, None, None, None, None, None, None, None

    n_count = 0
    uss, kss, rnode_data_ks, rnode_data_us, used_periods, all_hills = ([] for _ in range(6))
    all_patterns, recovery_patterns, reduction_patterns = {}, {}, {}

    import xlsxwriter
    import os
    from pyticas_ncrtes import ncrtes
    infra = ncrtes.get_infra()
    output_dir = infra.get_path('ncrtes/normal-data-set', create=True)
    data_file = os.path.join(output_dir, '(%d-%d) %s.xlsx' % (periods[0].start_date.year, periods[-1].end_date.year, target_station.station_id))

    wb = xlsxwriter.Workbook(data_file)

    not_congested_periods, not_congested_patterns = [], {}

    for prd in periods:

        all_uk, recovery_uk, reduction_uk, u_all, k_all, us, ks, hills_a_day, is_not_congested = _collect_data_a_day(target_station, prd, dc)

        if not recovery_uk:
            continue

        if is_not_congested:
            not_congested_periods.append(prd)
            for rk in recovery_uk.keys():
                _tk = rk if rk in not_congested_patterns else _unique_key(rk, list(not_congested_patterns.keys()))
                if not _tk:
                    continue
                not_congested_patterns[_tk] = recovery_uk[rk]
            continue

        if recovery_uk and reduction_uk:
            uss.append(u_all)
            kss.append(k_all)
            rnode_data_us.append(us)
            rnode_data_ks.append(ks)

        n_count += 1

        for rk in recovery_uk.keys():
            _tk = rk if rk in recovery_patterns else _unique_key(rk, list(recovery_patterns.keys()))
            if not _tk:
                continue
            recovery_patterns[_tk] = recovery_uk[rk]

        used_periods.append(prd)


    ks = list(recovery_patterns.keys())
    us = [ recovery_patterns[_k] for _k in ks ]

    if has_abnormal_ffs(target_station, recovery_patterns):
        logger.debug('!! has abnormal ffs : station=%s, s_limit=%s' % (target_station.station_id, target_station.s_limit))

        all_uk = dict(not_congested_patterns)
        all_uk.update(recovery_patterns)

        ks = list(all_uk.keys())
        us = [ all_uk[_k] for _k in ks ]

        ws = wb.add_worksheet('uk')
        ws.write_column(0, 0, ['k'] + ks)
        ws.write_column(0, 1, ['u'] + us)
        wb.close()
        return None, None, None, None, None, None, None, None, None, None, None

    ks, us = filter_abnormal_data(target_station, ks, us)
    recovery_patterns = { _k : us[idx] for idx, _k in enumerate(ks) }
    reduction_patterns = recovery_patterns
    all_patterns = recovery_patterns
    ws = wb.add_worksheet('uk')
    ws.write_column(0, 0, ['k'] + ks)
    ws.write_column(0, 1, ['u'] + us)
    wb.close()

    return (used_periods, all_patterns, recovery_patterns, reduction_patterns,
            uss, kss, rnode_data_us, rnode_data_ks, valid_detectors,
            not_congested_periods, not_congested_patterns)


def _collect_data_a_day(target_station, prd, dc):
    """ returns k,u data during speed recovery/reduction section on a day

    :type target_station: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    :type dc: function
    :rtype: (dict[float, float], dict[float, float], dict[float, float],
             list[float], list[float],
             pyticas.ttypes.RNodeData, pyticas.ttypes.RNodeData,
             list[pyticas_ncrtes.hill.hill.Hill],
             bool)
    """
    global wb

    logger = getLogger(__name__)
    _us, _ks, _qs = _station_data(target_station, prd, dc)

    if not _us:
        return None, None, None, None, None, None, None, None, False

    sw = SW_1HOUR
    us = np.array(_us.data)
    ks = np.array(_ks.data)
    qs = np.array(_qs.data)

    sks = data_util.smooth(ks, sw)
    sus = data_util.smooth(us, sw)
    sqs = data_util.smooth(qs, sw)

    if not any(sus):
        return None, None, None, None, None, None, None, None, False

    recovery_uk, reduction_uk, all_uk = {}, {}, {}
    dranges = _data_collecting_interval(target_station, ks, us, qs, sks, sus, sqs)

    is_not_congested = False
    if not dranges:
        minu_idx = np.argmin(sus).item()
        # toidx = min(minu_idx + setting.INTV2HOUR, len(sus)-1)

        toidx = None
        maxu = sus[minu_idx]
        for idx in range(minu_idx, len(sus)-1):
            if sus[idx] > sus[idx+1] and maxu - sus[idx+1] > 5:
                toidx = idx
                break
            maxu = sus[idx] if sus[idx] > maxu else maxu
        if not toidx:
            toidx = min(minu_idx + setting.INTV1HOUR, len(sus)-1)

        toidx = min(toidx, minu_idx + setting.INTV2HOUR)

        #print(target_station.station_id, prd.get_date_string(), '-> not congested : ', (minu_idx, toidx))

        if toidx < len(sus)-1 or sus[toidx] > target_station.s_limit:
            dranges = [(minu_idx, toidx)]
        is_not_congested = True

    if not dranges:
        return None, None, None, None, None, None, None, None, False

    ###########################

    ws = wb.add_worksheet(prd.get_date_string())
    ws.write_row(0, 0, [' ', 'k', 'u', 'q', 'sk', 'su', 'sq'])
    times = list(range(len(ks)))
    ws.write_column(1, 0, times)
    ws.write_column(1, 1, ks)
    ws.write_column(1, 2, us)
    ws.write_column(1, 3, qs)
    ws.write_column(1, 4, sks)
    ws.write_column(1, 5, sus)
    ws.write_column(1, 6, sqs)

    col = 8
    for (sidx, eidx) in dranges:
        ws.write_column(0, col, ['ks(%d-%d)' % (sidx, eidx)] + ks[sidx:eidx+1].tolist())
        ws.write_column(0, col+1, ['us(%d-%d)' % (sidx, eidx)] + us[sidx:eidx+1].tolist())
        col += 3


    ##############################
    sks2, sus2 = data_util.smooth(ks, 11), data_util.smooth(us, 11)
    # sks2, sus2 = ks, us
    already = []
    for (sidx, eidx) in dranges:
        # print(target_station.station_id, prd.get_date_string(), (sidx, eidx))
        for idx in range(sidx, eidx+1):
            if idx in already:
                continue

            _tk = (sks2[idx] if sks2[idx] not in recovery_uk
                   else _unique_key(sks2[idx], list(recovery_uk.keys())))
            recovery_uk[_tk] = sus2[idx]
            reduction_uk[_tk] = sus2[idx]
            all_uk[_tk] = sus2[idx]

            # _tk = (ks[idx] if ks[idx] not in recovery_uk
            #        else _unique_key(ks[idx], list(recovery_uk.keys())))
            # recovery_uk[_tk] = us[idx]
            # reduction_uk[_tk] = us[idx]
            # all_uk[_tk] = us[idx]

            already.append(idx)


    if SHOW_GRAPH:
        fig = plt.figure(facecolor='white', figsize=(16, 8))
        ax1 = plt.subplot(121)
        ax2 = ax1.twinx()
        ax3 = plt.subplot(122)
        ax1.plot(qs, label='qs')
        ax1.plot(sqs, label='sqs')
        ax2.plot(us, c='#EA8BD6', label='us')
        ax2.plot(sus, c='#CC3137', label='sus')
        ax2.plot(sks, c='#1DCC2E', label='sks')

        for (sidx, eidx) in dranges:
            ax1.axvline(x=sidx, c='g', label='start')
            ax1.axvline(x=eidx, c='r', label='end')

        ecs = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']
        markers = ['o', 'x', 'd', '^', '<', '>', 'v', 's', '*', '+']
        UK.append(recovery_uk)
        used = []
        for idx, _uk in enumerate(UK):
            c = ecs[idx % len(ecs)]
            marker = '|'
            for midx in range(len(markers)):
                marker_stick = '%s-%s' % (c, markers[midx])
                if marker_stick not in used:
                    marker = markers[midx]
                    used.append(marker_stick)
                    break
            _ks = list(_uk.keys())
            _us = [ _uk[_k] for _k in _ks]
            ax3.scatter(_ks, _us, c=c, marker=marker)


        # ax1.axvline(x=maxq_idx, c='g', label='maxq')
        # ax1.axvline(x=minu_idx, c='r', label='minu')
        # if recovered_idx:
        #     ax1.axvline(x=recovered_idx, c='b', label='recovered')
        ax3.set_xlim(xmin=0, xmax=80)
        ax3.set_ylim(ymin=0, ymax=90)

        plt.suptitle('%s (s_limit=%s, period=%s)' % (
            target_station.station_id, target_station.s_limit, prd.get_period_string()))
        ax1.legend()
        plt.grid()

        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
        plt.show()
        plt.close(fig)

    return all_uk, recovery_uk, reduction_uk, us, ks, _us, _ks, [], is_not_congested


def has_abnormal_ffs(station, uk):
    """

    :type station: pyticas.ttypes.RNodeObject
    :type uk: dic[float, float]
    :rtype: bool
    """
    ffs_threshold_upper_margin = 30
    ffs_threshold_under_margin = 5
    ffs_checking_krange = (15, 20)
    stddev_threshold = 8
    stddev_checking_n_limit = 10
    stddev_checking_krange = (55, 65)

    # check FFS (abnormal if FFS > S_LIMIT + 20 or FFS < S_LIMIT - 5)
    s_limit = station.s_limit
    max_u = s_limit + ffs_threshold_upper_margin
    fuk = data_util.filter_uk(uk)

    ks = list(fuk.keys())
    us = [ fuk[_k] for _k in ks ]

    ks = np.array(ks)
    us = np.array(us)

    wh = np.where( (ks > ffs_checking_krange[0]) & (ks < ffs_checking_krange[1]))
    if not any(wh[0]):
        return False

    avgu = np.mean(us[wh])
    if avgu >= max_u or avgu < s_limit - ffs_threshold_under_margin:
        return True


    # check stddev for high-density (abnormal if U-K is wide-spreaded)
    wh = np.where( (ks >= stddev_checking_krange[0]) & (ks <= stddev_checking_krange[1]))
    if not any(wh[0]) or len(wh[0]) < stddev_checking_n_limit:
        return False

    stddev = np.std(us[wh])
    if stddev > stddev_threshold:
        return True


    return False


def filter_abnormal_data(station, ks, us):
    """

    :type station: pyticas.ttypes.RNodeObject
    :type ks: list[float]
    :type us: list[float]
    :rtype: (list[float], list[float])
    """
    s_limit = station.s_limit
    max_u = s_limit + 25
    _ks, _us = [], []
    for idx, _u in enumerate(us):
        if _u > max_u or _u < 0 or ks[idx] < 0:
            continue
        _ks.append(ks[idx])
        _us.append(_u)

    return _ks, _us


def _data_collecting_interval(target_station, ks, us, qs, sks, sus, sqs):
    """

    :type target_station:
    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type qs: numpy.ndarray
    :type sks: numpy.ndarray
    :type sus: numpy.ndarray
    :type sqs: numpy.ndarray
    :rtype: list[(int, int)]
    """
    uth = 45 #target_station.s_limit - 5

    valleys = _low_speed_valley(target_station, ks, us, qs, sks, sus, sqs, uth)
    dranges = []
    for (vsidx, veidx) in valleys:
        _sidx, _eidx = _determine_data_collecting_range(target_station, vsidx, veidx, ks, us, qs, sks, sus, sqs, uth)
        if not _eidx:
            continue
        dranges.append([_sidx, _eidx])

    return dranges


def _determine_data_collecting_range(target_station, vsidx, veidx, ks, us, qs, sks, sus, sqs, uth):
    """

    :type target_station:
    :type vsidx: int
    :type veidx: int
    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type qs: numpy.ndarray
    :type sks: numpy.ndarray
    :type sus: numpy.ndarray
    :type sqs: numpy.ndarray
    :type uth: float
    :rtype: (int, int)
    """
    n_data = len(sus)
    intv1hour = int((60 * 60) / setting.DATA_INTERVAL)

    minu_idx = (np.argmin(sus[vsidx:veidx]) + vsidx).item()

    if minu_idx >= n_data - intv1hour:
        return None, None

    eidx, kth = _find_end_index_before_reduction(minu_idx, ks, us, sks, sus, uth, target_station.s_limit)

    if not eidx:
        eidx, kth = _find_end_index_before_reduction(minu_idx, ks, us, sks, sus, uth, target_station.s_limit - 5)


    if eidx and kth:
        ffs = _find_ffs(ks, qs, minu_idx, eidx, kth)
        _eidx = _find_end_index_for_data_collection(minu_idx, ks, us, sks, sus, ffs)
        if _eidx:
            eidx = _eidx

    return minu_idx, eidx


def _find_ffs(ks, qs, sidx, eidx, kth):
    """

    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type sidx: int
    :type eidx: int
    :type kth: float
    :return:
    :rtype:
    """
    tks = ks[sidx:eidx+1]
    tqs = qs[sidx:eidx+1]
    wh = np.where(tks < kth)
    ttks = tks[wh]
    ttqs = tqs[wh]
    func = lambda x, a: a * x
    _, popts, _, cfunc = fitting.curve_fit(func, ttks, ttqs, [1])
    return popts[0]


def _find_end_index_for_data_collection(minu_idx, ks, us, sks, sus, ffs):
    """

    :type minu_idx: int
    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type sks: numpy.ndarray
    :type sus: numpy.ndarray
    :type ffs: float
    :rtype: int
    """
    n_data = len(sus)
    t_margin = setting.INTV1HOUR
    for idx in range(minu_idx, n_data-t_margin):
        avgu = np.mean(us[idx:idx+t_margin])
        if avgu >= ffs * 0.95:
            return idx + t_margin
    return n_data - 1


def _find_end_index_before_reduction(minu_idx, ks, us, sks, sus, uth, uth2):
    """

    :type minu_idx: int
    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type sks: numpy.ndarray
    :type sus: numpy.ndarray
    :type uth: float
    :type s_limit: int
    :rtype:
    """

    n_data = len(sus)
    t_margin = setting.INTV1HOUR

    recovered_idx = None

    f_started = False
    for idx in range(minu_idx, n_data-t_margin):
        if sus[idx] > uth2:
            f_started = True

        if f_started and sus[idx] < uth:
            if idx > minu_idx and max(sus[minu_idx:idx]) > uth2:
                recovered_idx = np.where(sus[minu_idx:idx] > uth2)[0][0] + minu_idx
                return recovered_idx, None
            break

        if min(sus[idx:idx+t_margin]) > uth2:
            recovered_idx = idx + t_margin
            break

    if not recovered_idx:
        return None, None

    # set range : from minu_idx to before-reduction-under-uth
    eidx = n_data -1
    wh_down_again = np.where(sus[recovered_idx:] < uth)
    if any(wh_down_again[0]):
        eidx = wh_down_again[0][0] + recovered_idx
        for idx in range(eidx, recovered_idx, -1):
            pu, nu = sus[idx-1], sus[idx]
            if pu <= nu:
                eidx = idx
                break

    return eidx, max(sks[recovered_idx], 20)


def _low_speed_valley(target_station, ks, us, qs, sks, sus, sqs, uth):
    """

    :type target_station:
    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type qs: numpy.ndarray
    :type sks: numpy.ndarray
    :type sus: numpy.ndarray
    :type sqs: numpy.ndarray
    :type uth: float
    :rtype: (int, int)
    """
    wh_unders = np.where(sus <= uth)[0]
    wh_diffs = wh_unders[1:] - wh_unders[0:-1]
    wh_diffs[wh_diffs == 1] = 0

    iszero = np.concatenate(([0], np.equal(wh_diffs, 0).view(np.int8), [0]))
    absdiff = np.abs(np.diff(iszero))
    zero_ranges = np.where(absdiff == 1)[0].reshape(-1, 2)

    under_threshold_points = []
    psidx = None
    for zr in zero_ranges:
        sidx, eidx = wh_unders[zr[0]], wh_unders[zr[1]]

        if eidx < sidx:
            psidx = sidx
            continue
        elif psidx:
            sidx = psidx
            psidx = None

        prev_eidx = under_threshold_points[-1][1] if under_threshold_points else None

        if under_threshold_points and sidx < prev_eidx:
            under_threshold_points[-1][1] = eidx
        else:
            under_threshold_points.append([sidx, eidx])

    return [ (sidx, eidx) for (sidx, eidx) in under_threshold_points if eidx - sidx >= setting.INTV30MIN]


def _station_data(target_station, prd, dc):
    """ return q,k,u data for given period

    :type target_station: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    :type dc: function
    :rtype: (pyticas.ttypes.RNodeData, pyticas.ttypes.RNodeData, pyticas.ttypes.RNodeData)
    """
    rdr = ncrtes.get_infra().rdr
    logger = getLogger(__name__)

    us = rdr.get_speed(target_station, prd, dc)
    if not us or _is_missing_day(us.data, prd.interval):
        logger.debug('Station %s is missing at %s!!' % (target_station.station_id, prd.get_date_string()))
        return None, None, None
    ks = rdr.get_density(target_station, prd, dc)
    qs = rdr.get_average_flow(target_station, prd, dc)

    return us, ks, qs


def _is_missing_day(data, interval, limit_hour=1):
    """

    :type data: list[float]
    :type interval: int
    :type limit_hour: float
    :rtype: bool
    """
    n_missing = [d for d in data if d < 0]
    n_threshold = (limit_hour * 3600.0) / interval
    return len(n_missing) > n_threshold


def _unique_key(target_key, keys):
    """
    :type target_key: float
    :type keys: list[float]
    :rtype: float
    """
    if not target_key in keys:
        return target_key

    for idx in range(10000):
        tk = target_key + idx / 10000000.0
        if tk not in keys:
            return tk

    return None
