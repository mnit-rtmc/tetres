# -*- coding: utf-8 -*-

"""
Daytime Function Maker
========================

this module creates the density-speed function for daytime

"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import numpy as np
from scipy.signal import argrelextrema

from pyticas_ncrtes.core import etypes, data_util
from pyticas_ncrtes.core.nsrf.nsr_func import ffs as ncr_ffs
from pyticas_ncrtes.core.nsrf.nsr_func import fitting
from pyticas_ncrtes.logger import getLogger

DEBUG_MODE = False
UK_FILTER_STDDEV_MULTIPLIER = 1.96
MINIMUM_MAX_K = 40

def make(daytime_data):
    """ makes NSR function with the collected normal dry day data

    :type daytime_data: pyticas_ncrtes.core.etypes.DaytimeData
    :rtype: pyticas_ncrtes.core.etypes.DaytimeFunction, dict[float, float]
    """
    # Procedure
    # 1. validate recovery and reduction speed-density data respectively
    # 2. calibrate normal speed recovery function
    # 3. calibrate normal speed reduction function

    logger = getLogger(__name__)
    logger.debug('>> %s : try to make normal u-k function' % daytime_data.station.station_id)

    recovery_uk = _filter_splited_patterns(daytime_data.recovery_uk)
    recovery_uk_origin = daytime_data.recovery_uk

    recovery_function = _segmented_function(daytime_data, recovery_uk, recovery_uk_origin)
    daytime_function = etypes.DaytimeFunction(daytime_data.station, recovery_function)

    logger.debug('  -> ffs=%s, is_valud=%s'
                 % (daytime_function.get_FFS(), daytime_function.recovery_function.is_valid()))

    return daytime_function


def _filter_splited_patterns(uk):
    """ check if there are U-K patterns more than two

    :type uk: dict[float, float]
    :rtype: dict[float, float]
    """
    logger = getLogger(__name__)

    # check if there is data
    if not uk:
        logger.debug(' -> ! normal u-k data is not loaded')
        return None

    # filter by stddev
    filtered_uk = data_util.filter_uk(uk, m=UK_FILTER_STDDEV_MULTIPLIER,
                                      accept_filter=lambda k, avg, n: n < 10,
                                      n_threshold=0, debug=False)

    # sorted k and u list
    ks = np.array(sorted(list(filtered_uk.keys())))
    us = np.array([filtered_uk[_k] for _k in ks])

    # check if there is high density data
    max_k = max(ks)
    if max_k < MINIMUM_MAX_K and len(np.where(ks > 30)[0]) < 10:
        logger.debug(' -> ! maximum density is low')
        return None

    # speed range to filter
    from_u = int(max(us) - 5)
    to_u = int(min(us) + 5)

    # make sure data range is valid
    if from_u < to_u:
        logger.debug(' -> ! strange u-k pattern')
        return None

    # find Kt, which is usded to decide search range by k
    smoothing_window_size = 5
    ffs, Kf = ncr_ffs.estimate(filtered_uk, smoothing_window_size=smoothing_window_size)
    Kt = max(ks[np.where(us >= ffs)])

    # acceptable k margin
    #    -> most_freq_k at each speed - k_margin < k < most_freq_k at each speed - k_margin
    k_margin = 7.5

    # iterate speed range and check density frequency
    to_be_removed = {}
    for u in range(from_u, to_u, -1):

        # collect data points around the given u
        avgk, stddev, around_us, around_ks = _avg_y_of_around_x(us, ks, u, 2)
        if not avgk or len(around_us) < 10:
            continue

        # make histogram
        densities, freqs = _get_histogram(around_ks, xmin=0, xmax=200, step=2)

        # find the most concentrated density value at the speed
        max_freq_idx = np.argmax(freqs).item()
        max_freq_k = densities[max_freq_idx]
        if max_freq_k < Kt:
            continue

        # set acceptable k range
        min_limit_k, max_limit_k = max_freq_k - k_margin, max_freq_k + k_margin

        # add points out of the range to list
        wh = np.where((around_ks < min_limit_k) | (around_ks > max_limit_k))[0]
        for idx in wh:
            to_be_removed[around_ks[idx]] = around_us[idx]

    # iterate density range and check speed frequency
    from_k, to_k, u_margin = 5, int(Kt) - 2, 10
    for k in range(from_k, to_k):

        # collect data points around the given u
        avgu, stddev, around_ks, around_us = _avg_y_of_around_x(ks, us, k, 2)
        if not avgu:
            continue

        if len(around_us) < 10:
            for idx, _k in enumerate(around_ks):
                to_be_removed[_k] = around_us[idx]
            continue

        # make histogram
        speeds, freqs = _get_histogram(around_us)

        # find the most concentrated density value at the speed
        max_freq_idx = np.argmax(freqs).item()
        max_freq_u = speeds[max_freq_idx]

        # set acceptable u range
        min_limit_u, max_limit_u = max_freq_u - u_margin, max_freq_u + u_margin

        # add points out of the range to list
        wh = np.where((around_us < min_limit_u) | (around_us > max_limit_u))[0]
        for idx in wh:
            to_be_removed[around_ks[idx]] = around_us[idx]

    # remove outliers
    filtered_uk_origin = dict(filtered_uk)
    for k, u in to_be_removed.items():
        del filtered_uk[k]

    # remove malfunctioned data points
    filtered_uk = {k: u for k, u in filtered_uk.items() if not (k < 20 and u < 30)}

    ks = np.array(sorted(list(filtered_uk.keys())))
    us = np.array([filtered_uk[_k] for _k in ks])

    tks = ks[np.where(us < 30)]
    k_at_low_speed = min(tks) if any(tks) else max(ks)

    # make average densities by speed
    smoothing_window_size = 5
    ffs, Kf = ncr_ffs.estimate(filtered_uk, smoothing_window_size=smoothing_window_size)
    Kt = max(ks[np.where(us >= ffs)])

    # make average speeds by density
    stddevs = []
    for k in range(int(Kt), int(min(max(Kt + 20, k_at_low_speed), max(ks)))):
        avgu, stddev, around_ks, around_us = _avg_y_of_around_x(ks, us, k, 2)
        if avgu and len(around_us) > 5:
            stddevs.append(stddev)

    multiple_maximas = []

    # check if there is multiple peaks in histogram
    for u in range(from_u, to_u, -1):

        # collect data points around the given u
        avgk, stddev, around_us, around_ks = _avg_y_of_around_x(us, ks, u, 2)
        if not avgk or len(around_us) < 10:
            continue

        # make histogram
        densities, freqs = _get_histogram(around_ks, xmin=0, xmax=200, step=3)

        # find the most concentrated density value at the speed
        max_freq_idx = np.argmax(freqs).item()
        max_freq_k = densities[max_freq_idx]
        if max_freq_k < Kt:
            continue

        # count peaks
        maxima = argrelextrema(np.array(freqs), np.greater)

        if len(maxima[0]) > 1:
            mks = np.array([densities[idx] for idx in maxima[0]])
            mfreqs = np.array([freqs[idx] for idx in maxima[0]])
            sk = np.argsort(mfreqs)
            mks, mfreqs = mks[sk], mfreqs[sk]
            _1k, _1f = mks[-1], mfreqs[-1]
            _2k, _2f = mks[-2], mfreqs[-2]
            if abs(_1k - _2k) > 3 and abs(_1f - _2f) > 5 and _2f > 10:
                multiple_maximas.append(len(maxima[0]))

    has_multiple_peaks = len(multiple_maximas) > 1
    avg_stddevs = np.mean(stddevs) if any(stddevs) else 0
    n_stddevs = len(stddevs)

    logger.debug(' -> has_multiple_peak=%s, n_stddevs=%d, avg_stddevs=%.1f' % (
        has_multiple_peaks, n_stddevs, avg_stddevs
    ))

    if ((has_multiple_peaks and avg_stddevs > 4) or avg_stddevs > 5):
        logger.info(
            ' -> !!! u-k data are not valid (wide-spreaded) : has_multiple_peak=%s, n_stddevs=%d, avg_stddevs=%.1f' % (
                has_multiple_peaks, n_stddevs, avg_stddevs
            ))
        return None

    return filtered_uk


def _avg_y_of_around_x(xs, ys, target_x, target_range=1):
    """ returns average `y`-values (and stddev and data points) at each `x`

    :type xs: Union(numpy.ndarray, list[float])
    :type ys: Union(numpy.ndarray, list[float])
    :type target_x: float
    :type target_range: float
    :rtype: (float, float, numpy.ndarray, numpy.ndarray)
    """
    xs = np.array(xs)
    ys = np.array(ys)
    cond = np.logical_and(xs >= target_x - target_range, xs <= target_x + target_range)
    arounds_x = np.extract(cond, xs)
    arounds_y = np.extract(cond, ys)
    if not any(arounds_x):
        return None, None, None, None
    avg = np.mean(arounds_y)
    stddev = arounds_y.std()
    return avg, stddev, arounds_x, arounds_y


def _get_histogram(data, xmin=0, xmax=200, step=2):
    """ return histogram (bins and frequencies)

    :type data: numpy.ndarray
    :type xmin: int
    :type xmax: int
    :type step: int
    :rtype:
    """
    res = np.histogram(data, bins=list(range(xmin, xmax, step)), normed=False)
    counts = list(res[0])
    bins = list(res[1][1:])
    return bins, counts


def _segmented_function(ddata, uk, uk_origin):
    """ make U-K functions as a group of segmented functions (linear functions + log function)

    :type ddata: pyticas_ncrtes.core.etypes.DaytimeData
    :type uk: dict[float, float]
    :type uk_origin: dict[float, float]
    :rtype: etypes.SegmentedFunction
    """
    if uk is None or not any(uk):
        return etypes.SegmentedFunction([], None, None, None)

    # estimate FFS
    smoothing_window_size = 5
    ffs, Kf = ncr_ffs.estimate(uk, smoothing_window_size=smoothing_window_size)

    if ffs < 0:
        return etypes.SegmentedFunction([], None, None, None)

    filtered_uk = uk
    filtered_us, filtered_ks = data_util.dict2sorted_list(filtered_uk)
    filtered_target_uk = filtered_uk
    filtered_target_ks = np.array(filtered_ks)
    filtered_target_us = np.array(filtered_us)

    Kt = max(filtered_target_ks[np.where(filtered_target_us >= ffs)])

    # max_k with FFS
    margink = 1

    wh_around_maxk = np.where((filtered_target_ks <= Kt + margink) & (filtered_target_ks >= Kt - margink))
    median_u_at_kt = np.median(filtered_target_us[wh_around_maxk])

    # prepare avg u-k data
    _ks, _us = [], []
    for _k in range(10, 100):
        avg, stddev, arounds = data_util.avg_y_of_around_x(filtered_target_ks, filtered_target_us, _k, 2)
        if avg:
            _ks.append(_k)
            _us.append(avg)
    _ks = np.array(_ks)
    _us = np.array(_us)

    # smoothing
    _sus = data_util.smooth(_us, 11)
    _sus2 = data_util.smooth(_us, 21)

    # find k-range for calibration of log function
    u_under_limit = min(ddata.station.s_limit - 5, 40)
    k_at_lowu = _ks[np.where(_us < u_under_limit)[0][0]]
    wh = np.where((_ks <= k_at_lowu) & (_ks >= Kt))
    _tks, _tus = _ks[wh], _sus[wh]

    if any(_tks):
        vk, vu, d = _find_vertex(_tks, _tus)
    else:
        vk, vu, d = -1, -1, -1

    # set Kth
    if (d < 1 or (vu > 0 and median_u_at_kt - vu > 10)):
        kth, uth = Kt, median_u_at_kt
    else:
        kth, uth = vk, vu

    # log-function calibration
    logfunc = _after_kt(ddata.station, filtered_target_uk, kth)

    # find Kt from average u-k data and calibrated function
    # print('kth=', kth)
    kth2 = max(Kt, vk)

    Kl = _find_func_matching_point(logfunc, kth, kth2, _ks, _sus)
    for _ in range(10):
        kth2 = kth2 + 5
        Kl = _find_func_matching_point(logfunc, kth, kth2, _ks, _sus)
        if Kl is not None:
            break

    # result segmented functions ([0] = FFS function)
    lfunc = etypes.LineFunction((0, ffs), 0, Kf)
    funcs = [lfunc]

    # K_vertex
    if not Kl:
        Kl = Kt + 5
    Kv = vk if vk < Kl else -1

    if Kt < Kv and Kv - Kt > 2:
        # funcs[1] = FFS to Kt
        u_at_kt, _, _ = data_util.avg_y_of_around_x(filtered_target_ks, filtered_target_us, Kt, 2)
        popts = _line_func(lfunc.x2, lfunc.get_speed(lfunc.x2),
                           Kt, u_at_kt)
        lfunc = etypes.LineFunction(popts, lfunc.x2, Kt)
        funcs.append(lfunc)

        # funcs[2] = FFS to Kv
        u_at_kv, _, _ = data_util.avg_y_of_around_x(filtered_target_ks, filtered_target_us, Kv, 2)
        popts = _line_func(Kt, u_at_kt,
                           Kv, u_at_kv)
        lfunc = etypes.LineFunction(popts, lfunc.x2, Kv)
        funcs.append(lfunc)
    else:
        # funcs[2] = FFS to Kt
        u_at_kt, _, _ = data_util.avg_y_of_around_x(filtered_target_ks, filtered_target_us, Kt, 2)
        popts = _line_func(lfunc.x2, lfunc.get_speed(lfunc.x2),
                           Kt, u_at_kt)
        lfunc = etypes.LineFunction(popts, lfunc.x2, Kt)
        funcs.append(lfunc)

    # funcs[3] = Kv to Kl
    u_at_kl = logfunc.get_speed(Kl)
    popts = _line_func(lfunc.x2, lfunc.get_speed(lfunc.x2),
                       Kl, u_at_kl)
    lfunc = etypes.LineFunction(popts, lfunc.x2, Kl)
    funcs.append(lfunc)

    # func[4] = logfunc
    logfunc.x1 = Kl
    logfunc.x2 = 9999
    funcs.append(logfunc)

    seg_func1 = etypes.SegmentedFunction(funcs, Kf, Kt, ffs)

    funcs2 = list(funcs[:2])
    logfunc2 = _after_kt(ddata.station, filtered_target_uk, Kt)

    Kl2 = _find_func_matching_point(logfunc2, Kt, kth2, _ks, _sus)
    for _ in range(10):
        kth2 = kth2 + 5
        Kl2 = _find_func_matching_point(logfunc2, Kt, kth2, _ks, _sus)
        if Kl2 is not None:
            break

    if not Kl2:
        Kl2 = Kt + 5

    lfunc = funcs2[-1]
    u_at_kl2 = logfunc2.get_speed(Kl)
    popts = _line_func(lfunc.x2, lfunc.get_speed(lfunc.x2),
                       Kl2, u_at_kl2)
    lfunc = etypes.LineFunction(popts, lfunc.x2, Kl2)
    funcs2.append(lfunc)

    # func[4] = logfunc
    logfunc2.x1 = Kl2
    logfunc2.x2 = 9999
    funcs2.append(logfunc2)

    seg_func2 = etypes.SegmentedFunction(funcs2, Kf, Kt, ffs)

    checked1, max_diff1 = _check_seg_func(seg_func1, _ks, _sus2)
    checked2, max_diff2 = _check_seg_func(seg_func2, _ks, _sus2)

    if not checked1 and not checked2:
        print('! fail to calibrate function')
        return etypes.SegmentedFunction([], Kf, Kt, ffs)

    seg_func = None

    if not checked1 or not checked2:
        seg_func = seg_func1 if checked1 else seg_func2
    else:
        seg_func = seg_func1 if max_diff1 < max_diff2 else seg_func2

    if seg_func and seg_func.is_valid():
        _write_chart_and_data(ddata, uk_origin, Kl, seg_func)

    return seg_func


def _find_vertex(target_x, target_y):
    """
    :type target_x: numpy.ndarray
    :type target_y: numpy.ndarray
    :rtype: (float, float, float)
    """
    x1, y1 = target_x[0], target_y[0]
    x2, y2 = target_x[-1], target_y[-1]
    max_d = -1
    x_at_max_d = -1
    y_at_max_d = -1
    for idx, x in enumerate(target_x):
        y = target_y[idx]
        fy = data_util.get_value_on_line(x, y1, y2, x1, x2)
        d = data_util.distance_to_line(x, y, y1, y2, x1, x2)
        if d > max_d and fy < y:
            max_d = d
            x_at_max_d = x
            y_at_max_d = y
    return x_at_max_d, y_at_max_d, max_d


def _find_func_matching_point(logfunc, kth1, kth2, avg_ks, avg_us):
    """

    :type logfunc: etypes.LogFunction
    :type kth1: float
    :type kth2: float
    :type avg_ks: numpy.ndarray
    :type avg_us: numpy.ndarray
    :rtype: float
    """
    ks, aus, fus = [], [], []
    first_diff = None
    first_diff_sign = None

    k_at_diffs, diffs = [], []

    for idx, _k in enumerate(avg_ks):
        if _k < kth1 or _k > kth2:
            continue
        _au = avg_us[idx]
        _fu = logfunc.get_speed(_k)
        diffs.append(abs(_au - _fu))
        k_at_diffs.append(_k)

    if not any(k_at_diffs):
        # print('case0 : no diffs')
        return None

    diffs = np.array(diffs)
    if not any(np.where(diffs > 1)[0]):
        # print('case1 : ', k_at_diffs[0])
        return k_at_diffs[0]

    # max speed difference point
    k_at_diffs = np.array(k_at_diffs)
    max_diff_idx = np.argmax(diffs).item()

    # after max_diff_idx
    tdiffs = diffs[max_diff_idx:]
    tks = k_at_diffs[max_diff_idx:]

    sign_changed_k = -1
    for idx, _k in enumerate(avg_ks):
        if _k < kth1 or _k > kth2:
            continue
        ks.append(_k)
        _au = avg_us[idx]
        _fu = logfunc.get_speed(_k)
        diff = _au - _fu
        if diff == 0:
            sign = 0
        else:
            sign = (diff > 0)

        if first_diff is None:
            if abs(diff) < 1:
                sign_changed_k = _k
                break

            first_diff = diff
            first_diff_sign = sign
        else:
            if sign != first_diff_sign:
                sign_changed_k = _k
                break
    # print('sign_changed_k:', sign_changed_k)
    if sign_changed_k >= 0:
        wh = np.where(k_at_diffs > sign_changed_k)
        if any(wh[0]) and max(diffs[wh]) < 5:
            return sign_changed_k

    # find the point having difference within threshold
    wh_within_threshold1 = np.where(tdiffs < 0.1)
    wh_within_threshold2 = np.where(tdiffs < 1.0)
    # wh_within_threshold3 = np.where(tdiffs < 2)

    kl = None
    kth = 40

    if any(wh_within_threshold1[0]) and tks[wh_within_threshold1[0][0]] < kth:
        # print('case2-1 : ', tks[wh_within_threshold1[0][0]])
        kl = tks[wh_within_threshold1[0][0]]
    elif any(wh_within_threshold2[0]) and tks[wh_within_threshold2[0][0]] < kth:
        # print('case2-2 : ', tks[wh_within_threshold2[0][0]])
        kl = tks[wh_within_threshold2[0][0]]
    # elif any(wh_within_threshold3[0]) and tks[wh_within_threshold3[0][0]] < kth:
    #     print('case2-3 : ', tks[wh_within_threshold3[0][0]])
    #     kl = tks[wh_within_threshold3[0][0]]

    return kl


def _check_seg_func(seg_func, avg_ks, avg_us):
    """
    :type seg_func: etypes.SegmentedFunction
    :type avg_ks: numpy.ndarray
    :type avg_us: numpy.ndarray
    :rtype: bool, float
    """
    uth = 5
    checked = True
    diffs = []
    for func in seg_func.funcs[1:-1]:
        # print('!!! func : ', func, (func.get_speed(func.x1), func.get_speed(func.x2)))
        for idx, _k in enumerate(avg_ks):
            if _k < func.x1 or _k > func.x2:
                continue
            _au = avg_us[idx]
            _fu = func.get_speed(_k)
            diff = abs(_au - _fu)
            diffs.append(diff)
            if diff > uth:
                checked = False

    return checked, np.mean(diffs)


def _after_kt(station, uk, Kt):
    """ make exponential decay function

    :type station: pyticas.ttypes.RNodeObject
    :type uk: dict[float, float]
    :type Kt: float
    :rtype: etypes.LogFunction
    """
    fit_func = lambda x, a, b: a * x + b
    target_us, target_ks = data_util.dict2sorted_list(uk, key_filter=lambda k: k > Kt)

    knots = _knots(np.array(target_ks), np.array(target_us), fit_func, 1)
    knot = knots[0]
    for knot in range(int(knots[0]), int(Kt), -2):
        _target_us, _target_ks = data_util.dict2sorted_list(uk, key_filter=lambda k: k > knot)
        if len(_target_ks) > 50:
            target_ks, target_us = _target_ks, _target_us
            break

    popts = [90, 0.02]

    target_ks = target_ks + [200]
    target_us = target_us + [2]
    N = len(target_ks)
    sigma = np.ones(N)
    sigma[-1] = 0.01
    try:
        info, popts, rep, func = fitting.curve_fit(etypes.LogFunction.get_fitting_function(),
                                                   target_ks,
                                                   target_us,
                                                   popts)
        return etypes.LogFunction(popts, {}, Kt)
    except Exception as ex:
        getLogger(__name__).warn('cannot calibrate linear function')
        return etypes.LogFunction(None, {}, Kt)


def _knots(target_x, target_y, fit_func, N=1):
    """
    :type target_x: numpy.ndarray
    :type target_y: numpy.ndarray
    :type fit_func: callable
    :type N: int
    :rtype: list[float]
    """
    popts = _fitting(target_x, target_y, fit_func)
    knot_x, knot_y = _find_knot_candidate(target_x, target_y, fit_func, popts)

    # fx = list(range(int(target_x[0]), int(target_x[-1])))
    # fy = [ fit_func(x, *popts) for x in fx ]
    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.scatter(target_x, target_y, marker='x', c='#EAEAEA')
    # plt.scatter(fx, fy, marker='^')
    # plt.scatter([knot_x], [knot_y], marker='o', s=40)
    # plt.show()

    knots = [knot_x]

    if N <= 0:
        return knots

    wh1 = np.where(target_x < knot_x)
    wh2 = np.where(target_x >= knot_x)

    n_limit = 10
    if len(wh1[0]) < n_limit or len(wh2[0]) < n_limit:
        return knots

    target_x1 = target_x[wh1]
    target_y1 = target_y[wh1]
    knots.extend(_knots(target_x1, target_y1, fit_func, N - 1))

    target_x2 = target_x[wh2]
    target_y2 = target_y[wh2]
    knots.extend(_knots(target_x2, target_y2, fit_func, N - 1))

    return list(sorted(knots))


def _find_knot_candidate(target_x, target_y, fit_func, popts):
    """
    :type target_x: numpy.ndarray
    :type target_y: numpy.ndarray
    :type fit_func: callable
    :type popts: (float, float)
    :rtype: (float, float)
    """
    x1 = target_x[0]
    y1 = fit_func(x1, *popts)
    x2 = target_x[-1]
    y2 = fit_func(x2, *popts)
    max_d = -1
    x_at_max_d = -1
    y_at_max_d = -1
    for idx, x in enumerate(target_x):
        y = target_y[idx]
        d = data_util.distance_to_line(x, y, y1, y2, x1, x2)
        fx = x
        fy = fit_func(fx, *popts)
        if d > max_d and fy > y:
            max_d = d
            x_at_max_d = x
            y_at_max_d = y
    return x_at_max_d, y_at_max_d


def _fitting(target_x, target_y, fit_func, knot0=(-1, -1)):
    """
    :type target_x: numpy.ndarray
    :type target_y: numpy.ndarray
    :type fit_func: callable
    :type knot0: (float, float)
    """
    knot_x, knot_y = knot0
    sigma = None
    if knot_x > 0:
        target_x = np.array([knot_x] + target_x.tolist())
        target_y = np.array([knot_y] + target_y.tolist())
        N = len(target_x)
        sigma = np.ones(N)
        sigma[0] = 0.01

    ret = fitting.curve_fit(fit_func, target_x, target_y, [-80, 0], sigma=sigma)
    return ret[1]


def _line_func(sx, sy, ex, ey):
    """

    :type sx:
    :type sy:
    :type ex:
    :type ey:
    :rtype: (float, float)
    """
    a = (ey - sy) / (ex - sx)
    b = -a * sx + sy
    return (a, b)


def _output_path(*filename):
    import os
    from pyticas_ncrtes import ncrtes
    infra = ncrtes.get_infra()
    ncrtesdir = infra.get_path('ncrtes', create=True)
    outputdir = os.path.join(ncrtesdir, 'debug')
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    if filename:
        outputfile = os.path.join(outputdir, *filename)
        _outputdir = os.path.dirname(outputfile)
        if not os.path.exists(_outputdir):
            os.makedirs(_outputdir)
        return outputfile
    else:
        return outputdir


def _write_chart_and_data(ddata, uk_origin, Kl, seg_func):
    if not DEBUG_MODE:
        return

    ecs = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']
    cnt = 0

    import matplotlib.pyplot as plt
    plt.figure()

    _us_origin, _ks_origin = data_util.dict2sorted_list(uk_origin)
    ks_origin = np.array(_ks_origin)
    us_origin = np.array(_us_origin)

    plt.scatter(ks_origin, us_origin, marker='x', color='#999999')

    for func in seg_func.funcs:

        # print('> ', func.x1, func.x2, func.line_func, type(func))
        isinstance(func, etypes.FitFunction)
        uf = func.get_function()
        lus = []
        lks = []
        for _k in range(int(func.x1 * 10), int(func.x2 * 10)):
            k = _k / 10.0
            if k > 140:
                break
            lks.append(k)
            lus.append(uf(k))

        c = ecs[cnt % len(ecs)]
        cnt += 1
        # plt.scatter(lks, lus, marker='^', color=c)

    _ks, _us = [], []
    for k in range(10, 200):
        _ks.append(k)
        _us.append(seg_func.speed(k))

    plt.plot(_ks, data_util.smooth(_us, 11), c='b', lw=2)

    plt.xlim(xmin=0, xmax=160)
    plt.ylim(ymin=0, ymax=120)
    plt.title('%s (Kt=%.2f, SL=%s, label=%s)' % (ddata.station.station_id, Kl,
                                                 ddata.station.s_limit,
                                                 ddata.station.label))
    plt.grid()
    periods = sorted(ddata.periods + ddata.not_congested_periods, key=lambda prd: prd.start_date)
    ffpath = _output_path('normal_function', '(%d-%d) %s.png' % (
        periods[0].start_date.year, periods[-1].end_date.year, ddata.station.station_id))
    plt.tight_layout()
    plt.savefig(ffpath, dpi=100, bbox_inches='tight')
    # plt.show()
    plt.close()

    import xlsxwriter
    import os
    from pyticas_ncrtes import ncrtes
    infra = ncrtes.get_infra()
    output_dir = infra.get_path('ncrtes/normal-data-set', create=True)
    data_file = os.path.join(output_dir, '(%d-%d) %s (func).xlsx' % (
        periods[0].start_date.year, periods[-1].end_date.year, ddata.station.station_id))
    wb = xlsxwriter.Workbook(data_file)
    ws = wb.add_worksheet('uk')
    ws.write_column(0, 0, ['k'] + _ks)
    ws.write_column(0, 1, ['u'] + _us)
    wb.close()
