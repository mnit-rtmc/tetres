# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.core.data_util
==================================

- functions to process data such as smoothing and quntization used in other modules
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


import math
import numpy as np
import scipy.signal as sps

FUNC_MIN = 'min'
FUNC_MAX = 'max'

DIRECTION_FORWARD = 1
DIRECTION_BACKWARD = -1

def smooth(x, window_len=9, window='blackman', **kwargs):
    """

    :type x: Union(numpy.ndarray, list)
    :type window_len: int
    :type window: str
    :rtype: numpy.ndarray
    """

    # Import modules just in case they weren't already
    x = np.array(x)
    if len(x) < window_len:
        window_len = len(x)
        if window_len % 2 == 0:
            window_len -= 1

    # Check to see if the window is an odd number
    if (window_len % 2) == 0:
        raise ValueError("Window must be an odd length")

    window_len = int(window_len)

    # Create a mirror of the left and right parts of the nsr_data
    left_mirror = x[window_len - 1: 0: -1]
    right_mirror = x[-1: -window_len: -1]
    # Join the original nsr_data with mirrors
    mirrored = np.r_[left_mirror, x, right_mirror]

    # Generate the window nsr_data
    if window == 'flat':
        win = np.ones(window_len, 'd')
    else:
        win = getattr(np, window)(window_len)

    # Convolve the nsr_data with the normalized window function
    y = sps.fftconvolve(win / win.sum(), mirrored, mode='valid')

    # Retun the nsr_data with the mirrored stuff stripped away
    return np.array(y[int((window_len - 1) / 2):-int((window_len - 1) / 2)])


def trending(data, smoothing_window_size, stepping_threshold, **kwargs):
    """ return trend data

    :type data: list[float]

    :param smoothing_window_size: smoothing window size
    :type smoothing_window_size: int

    :param stepping_threshold: stepping threshold
    :type stepping_threshold: float

    :rtype: list[float]
    """

    less_shift = kwargs.get('less_shift', False)
    smoothing_method = kwargs.get('smoothing_function', smoothing)
    smoothed = smoothing_method(data, smoothing_window_size)
    stepped = stepping(smoothed, stepping_threshold)
    if less_shift:
        stepped.reverse()
        trended = smoothing_method(stepped, smoothing_window_size)
        trended.reverse()
    else:
        trended = smoothing_method(stepped, smoothing_window_size)
    return trended


def smoothing(data, wsize):
    """ return smoothed nsr_data

    :type data: list[float]

    :param wsize: smoothing window size
    :type wsize: int

    :rtype: list[float]
    """
    if data is None or not any(data) or len(data) < wsize * 2:
        return data

    # try:
    #     body = [avg(nsr_data[(idx-wsize):(idx+wsize)]) for idx in range(wsize, len(nsr_data)-wsize) ]
    #     return [body[0]]*wsize + body + [body[-1]]*wsize
    # except IndexError as ex:
    #     print(len(nsr_data), wsize, ': ', nsr_data)
    #     raise ex

    N = int((wsize - 1) / 2)
    fdata = [data[0] for i in range(N)] + data + [data[-1] for i in range(N)]
    try:
        return [avg(fdata[(idx - wsize):(idx + wsize + 1)]) for idx in range(wsize, wsize+len(data))]
    except IndexError as ex:
        print(len(data), wsize, ': ', data)
        raise ex


def smoothing_forward(data, wsize):
    """ return smoothed nsr_data with only future nsr_data

    :type data: list[float]

    :param wsize: smoothing window size
    :type wsize: int

    :rtype: list[float]
    """
    N = int((wsize - 1) / 2)
    fdata = data + [data[-1] for i in range(N)]
    return [avg(fdata[idx:(idx + wsize)]) for idx in range(len(data))]


def stepping(data, threshold, **kwargs):
    """ return quantization nsr_data

    nsr_data is updated if difference with previous-time-step nsr_data is greater than threshold
        while iterating nsr_data from 0 to length of nsr_data

    processing example (when threshold=2):
        nsr_data = [ 1, 2, 5, 6, 10, 9, 10, 11, 6, 5 ]
        result = [ 1, 1, 5, 5, 10, 10, 10, 10, 6, 6 ]

    in this example, difference between 3rd item of nsr_data (5) and 2nd item of nsr_data (2) is 3,
        which is greater than threshold 2.
        so result[2] is set to 5

    :type data: Union(list[float], numpy.ndarray)
    :type threshold: float

    """
    init_stick_length = kwargs.get('init_n', 3)
    stepped = []
    stick = avg(data[:init_stick_length])
    for idx in range(len(data)):
        if abs(stick - data[idx]) > threshold:
            stick = data[idx]
        stepped.append(stick)

    idx = 0
    n_data = len(data)
    while idx < n_data:
        same_level_data = []
        stick = stepped[idx]
        cidx = idx
        for cidx in range(idx, n_data):
            if stepped[cidx] != stick:
                break
            same_level_data.append(data[cidx])
        if same_level_data:
            avg_value = avg(same_level_data)
            for sidx in range(idx, cidx):
                stepped[sidx] = avg_value
        idx = cidx
        if idx == n_data-1:
            break

    return stepped


def avg(data, only_positive=True, **kwargs):
    """ return average of list

    :type data: list
    """
    if only_positive:
        target_data = [v for v in data if v > 0]
    else:
        target_data = data

    if target_data:
        return float(sum(target_data)) / len(target_data)
    else:
        return -1


def avg_multi(_2dlist, only_positive=True, **kwargs):
    """ making average nsr_data
    :type _2dlist: list[list[float]]
    :type only_positive: bool
    :rtype: list[float]
    """
    avg_data = []
    data_length = len(_2dlist[0])
    for r in range(data_length):
        target_data = [col[r] for col in _2dlist]
        a, s = avg_stddev(target_data, only_positive, **kwargs)
        avg_data.append(a)
    return avg_data


def filter_uk(uk, **kwargs):
    """ filtering noise of U-K plain

    :type uk: dict[float, float]
    :rtype: dict[float, float]
    """
    ks = np.array(sorted(uk.keys()))
    us = np.array([ uk[k] for k in ks ])

    nuk = dict()
    k_range = kwargs.get('k_range', 1)
    u_range = 2
    m = kwargs.get('m', 1.96)
    n_th = kwargs.get('n_threshold', 0)
    k_filter = kwargs.get('k_filter', lambda k: k)
    avg_filter = kwargs.get('avg_filter', None)
    accept_filter = kwargs.get('accept_filter', None)
    f_debug = kwargs.get('debug', False)

    # filter u-noise
    for idx, k in enumerate(ks):
        if k_filter is not None and not k_filter(k):
            continue
        u = us[idx]
        _avg, _stddev, _data = avg_y_of_around_x(ks, us, k, k_range)

        if _avg and len(_data) <= 2:
            _stddev = 0

        if accept_filter is not None and accept_filter(k, _avg, len(_data) if _avg else 0):
            nuk[k] = u
            continue

        if avg_filter is not None and not avg_filter(k, _avg, len(_data) if _avg else 0):
            continue

        if not _avg or abs(u - _avg) > m * _stddev or len(_data) < n_th:
            continue

        nuk[k] = u
        if f_debug:
            print('-> ', (k, u), ': ', (_avg, _stddev, _data))

    ks = np.array(sorted(nuk.keys()))
    us = np.array([ nuk[k] for k in ks ])

    # filter k-noise
    nnuk = {}
    for idx, u in enumerate(us):
        k = ks[idx]
        _avg, _stddev, _data = avg_y_of_around_x(us, ks, u, u_range)
        if len(_data) <= 2:
            _stddev = 0
        if not _avg or abs(k - _avg) > m * _stddev or len(_data) < n_th:
            continue
        nnuk[k] = u

    return nnuk


def avg_y_of_around_x(xs, ys, target_x, target_range=1):
    """

    :type xs: Union(numpy.ndarray, list[float])
    :type ys: Union(numpy.ndarray, list[float])    
    :type target_x: float
    :type target_range: float
    :rtype: (float, float, list[float])
    """
    xs = np.array(xs)
    ys = np.array(ys)
    cond = np.logical_and(xs >= target_x - target_range, xs <= target_x + target_range)
    arounds_y = np.extract(cond, ys)
    if not any(arounds_y):
        return None, None, None
    avg = np.mean(arounds_y)
    stddev = arounds_y.std()
    return avg, stddev, arounds_y.tolist()


def avg_stddev(data_list, only_positive=True, **kwargs):
    remove_outlier = kwargs.get('remove_outlier', False)
    ignore_values = kwargs.get('ignore_values', [None, -1])

    if data_list.count(data_list[0]) == len(data_list):
        return data_list[0], 0

    if only_positive:
        target_data = [v for v in data_list if v > 0]
    else:
        target_data = data_list

    data_list = target_data

    total = 0
    count = 0
    total_power_value = 0
    for value in data_list:
        if value in ignore_values: continue
        total += value
        total_power_value += value * value
        count += 1

    if not count:
        return -1, -1

    avg_value = total / count
    v = total_power_value / count - avg_value * avg_value
    stddev = math.sqrt(v)

    if count <= 2:
        return avg_value, 0

    if remove_outlier:
        total = 0
        count = 0
        for value in data_list:
            if value in ignore_values: continue
            if value > avg_value + 2 * stddev or value < avg_value - 2 * stddev:
                continue
            total += value
            count += 1

        if count == 0:
            return -1, -1

        avg_value = round(total / count, 2)

    return avg_value, stddev


def get_value_on_line(k, u1, u2, k1, k2):
    """ the value on the line that connects two points of (k1, u1) and (k2, u2)

    :type k: float
    :type u1: float
    :type u2: float
    :type k1: float
    :type k2: float
    :rtype: float
    """
    return ((u2 - u1) / (k2 - k1)) * (k - k1) + u1


def distance_to_line(x, y, u1, u2, k1, k2):
    """ distance from (x, y) to the line that connects two points of (k1, u1) and (k2, u2)

    :type x: float
    :type y: float
    :type u1: float
    :type u2: float
    :type k1: float
    :type k2: float
    :rtype: float
    """
    a = (u2 - u1) / (k2 - k1)
    b = -1
    c = get_value_on_line(0, u1, u2, k1, k2)
    return abs(a * x + b * y + c) / math.sqrt(a ** 2 + b ** 2)


def dict2sorted_list(dictionary, key_filter=None):
    """

    :type dictionary: dict[float, float]
    :type key_filter: function
    :rtype: list[float], list[float]
    """
    values = []
    keys = []
    for k in sorted(dictionary.keys()):
        if not key_filter or key_filter(k):
            values.append(dictionary[k])
            keys.append(k)
    return values, keys


def quantized_uk(us, ks):
    """

    :type us: list[float]
    :type ks: list[float]
    :rtype: (list[float],list[float])
    """
    avg_us = []
    avg_ks = []
    rounded_ks = np.around(ks)
    # make average nsr_data
    for k in range(5, 200):
        u_in_k = np.extract(rounded_ks == k, us)
        if any(u_in_k):
            avg_us.append(np.mean(u_in_k))
            avg_ks.append(k)

    return avg_us, avg_ks


def quantized_qk(qs, ks):
    """

    :type qs: Union(list[float], numpy.ndarray)
    :type ks: Union(list[float], numpy.ndarray)
    :rtype: (list[float],list[float])
    """
    avg_qs = []
    avg_ks = []

    rounded_ks = np.around(ks)

    # make average nsr_data
    for k in range(5, 200):
        q_in_k = np.extract(rounded_ks == k, qs)
        if any(q_in_k):
            avg_qs.append(np.mean(q_in_k))
            avg_ks.append(k)

    return avg_qs, avg_ks


def max_distance_point(sidx, eidx, xdata, ydata):
    """

    :type sidx: int
    :type eidx: int
    :type xdata: numpy.ndarray
    :type ydata: numpy.ndarray
    :return:
    """
    x1, y1, x2, y2 = xdata[sidx], ydata[sidx], xdata[eidx], ydata[eidx]
    dists = []
    for idx in range(sidx+1, eidx):
        d = distance_to_line(idx, ydata[idx], y1, y2, x1, x2)
        dists.append(d)
    return sidx + np.argmax(dists)


def local_minmax_points(data):
    """
    :type data: numpy.ndarray
    :rtype: list[int]
    """
    minmax_idxs = (np.diff(np.sign(np.diff(data))).nonzero()[0] + 1).tolist()
    last_idx = len(data) - 1
    if 0 not in minmax_idxs:
        minmax_idxs = [0] + minmax_idxs
    if minmax_idxs[-1] > last_idx:
        del minmax_idxs[-1]
    if last_idx not in minmax_idxs:
        minmax_idxs = minmax_idxs + [last_idx]
    return minmax_idxs


def max_points(data):
    """
    :type data: Union(list[int], numpy.ndarray)
    :rtype: list[int]
    """
    diffs = np.diff(np.sign(np.diff(data)))
    return np.where(diffs < 0)[0].tolist()


def _uk_in_range(tidx, tks, tus, w, uth):
    """
    :type tidx: int
    :type tks: numpy.ndarray
    :type tus: numpy.ndarray
    :type w: int
    :type uth: float
    :rtype: (float, float)
    """
    sidx = tidx - w if tidx >= w else tidx
    eidx = tidx + w if tidx < len(tks) - w - 1 else tidx

    us_in_range = [tus[idx] for idx in range(sidx, eidx + 1) if abs(tus[tidx] - tus[idx]) < uth]
    ks_in_range = [tks[idx] for idx in range(sidx, eidx + 1) if abs(tus[tidx] - tus[idx]) < uth]

    return np.mean(ks_in_range), np.mean(us_in_range)


def adaptive_aggregation(tks, tus, w, uth):
    """

    :type tks: numpy.ndarray
    :type tus: numpy.ndarray
    :type w: int
    :type uth: float
    :rtype: (numpy.ndarray, numpy.ndarray)
    """
    n_data = len(tks)
    rks, rus = [], []
    for idx in range(0, n_data):
        _k, _u = _uk_in_range(idx, tks, tus, w, uth)
        rks.append(_k)
        rus.append(_u)
    return np.array(rks), np.array(rus)


def fix_rapid_fluctuation(ks, us, n_try=0, low_k=10, **kwargs):
    """

    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type n_try:  int
    :type low_k: float
    :rtype:
    """
    u_diff_threshold = kwargs.get('udiff_threshold', 10)
    n_data = len(us)

    # make sure there's no same value data
    idx = 1
    while idx < n_data-1:
        if us[idx] == us[idx+1]:
            us[idx] = (us[idx-1] + us[idx]) / 2
            idx += 2
            continue
        idx += 1

    cp_values = {}

    minmax = local_minmax_points(us)

    for midx in range(1, len(minmax)-1):
        pidx, cidx, nidx = minmax[midx-1], minmax[midx], minmax[midx+1]
        pu, cu, nu = us[pidx], us[cidx], us[nidx]
        pk, ck, nk = ks[pidx], ks[cidx], ks[nidx]

        if min(pk, ck, nk) > low_k or max(pk, ck, nk) > 25:
            continue

        diff1 = abs(cu - pu)
        diff2 = abs(cu - nu)

        if diff1 < u_diff_threshold or diff2 < u_diff_threshold:
            continue

        new_cu = cu

        if cu > pu and cu > nu:
            new_cu = ((cu - diff1/2.0) + (cu - diff2 / 2.0)) / 2
        elif  cu < pu and cu < nu:
            new_cu = ((cu + diff1/2.0) + (cu + diff2 / 2.0)) / 2

        cp_values[cidx] = new_cu

    has_changed = False

    new_us = np.array(us)
    for midx in range(1, len(minmax)-1):
        pidx, cidx, nidx = minmax[midx-1], minmax[midx], minmax[midx+1]

        if cidx not in cp_values:
            continue

        new_cu = cp_values[cidx]
        new_pu = cp_values[pidx] if pidx in cp_values else us[pidx]
        new_nu = cp_values[nidx] if nidx in cp_values else us[nidx]
        new_us[cidx] = new_cu

        has_changed = True

        for idx in range(pidx+1, cidx):
            new_us[idx] = get_value_on_line(idx, new_pu, new_cu, pidx, cidx)
        for idx in range(cidx+1, nidx):
            new_us[idx] = get_value_on_line(idx, new_cu, new_nu, cidx, nidx)

    if has_changed and n_try < 100:
        return fix_rapid_fluctuation(ks, new_us, n_try=(n_try+1), low_k=low_k, **kwargs)

    return ks, new_us


def fix_rapid_fluctuation1(ks, us, n_try=0, low_k=10, **kwargs):
    """

    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type n_try:  int
    :type low_k: float
    :rtype:
    """
    u_diff_threshold = kwargs.get('udiff_threshold', 10)

    n_data = len(us)
    idx = 1
    while idx < n_data-1:
        if us[idx] == us[idx+1]:
            us[idx] = (us[idx-1] + us[idx]) / 2
            idx += 2
            continue
        idx += 1

    new_us = np.array(us)

    minmax = local_minmax_points(us)

    for midx in range(1, len(minmax)-1):
        pidx, cidx, nidx = minmax[midx-1], minmax[midx], minmax[midx+1]
        pu, cu, nu = us[pidx], us[cidx], us[nidx]
        pk, ck, nk = ks[pidx], ks[cidx], ks[nidx]

        if min(pk, ck, nk) > low_k:
            continue

        diff1 = abs(cu - pu)
        diff2 = abs(cu - nu)

        if diff1 < u_diff_threshold or diff2 < u_diff_threshold:
            continue

        new_cu = cu

        # ^
        if cu > pu and cu > nu:
            new_cu = ((cu - diff1/2.0) + (cu - diff2 / 2.0)) / 2
        elif  cu < pu and cu < nu:
            new_cu = ((cu + diff1/2.0) + (cu + diff2 / 2.0)) / 2

        new_us[cidx] = new_cu

        for idx in range(pidx+1, cidx):
            new_us[idx] = get_value_on_line(idx, pu, new_cu, pidx, cidx)
        for idx in range(cidx+1, nidx):
            new_us[idx] = get_value_on_line(idx, new_cu, nu, cidx, nidx)

        return fix_rapid_fluctuation(ks, new_us, n_try=n_try, low_k=low_k, **kwargs)
    return ks, new_us


def fix_rapid_fluctuation_origin(ks, us, n_try=0, low_k=10, **kwargs):
    """

    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type n_try:  int
    :type low_k: float
    :rtype:
    """
    u_diff_threshold = kwargs.get('udiff_threshold', 10)
    new_us = np.array(us)
    has_fixed = False
    for idx in range(2, len(us) - 2):
        ppidx, pidx, cidx, nidx, nnidx = idx - 2, idx - 1, idx, idx + 1, idx + 2
        ppu, pu, cu, nu, nnu = us[ppidx], us[pidx], us[cidx], us[nidx], us[nnidx]
        ppk, pk, ck, nk, nnk = ks[ppidx], ks[pidx], ks[cidx], ks[nidx], ks[nnidx]
        if ck > low_k:
            continue
        if ((pu - cu > u_diff_threshold and nu - cu > u_diff_threshold)
            or (cu - pu > u_diff_threshold and cu - nu > u_diff_threshold)):
            new_us[cidx] = (((pu + nu) / 2) + cu) / 2
            has_fixed = True
    us = new_us

    if has_fixed and n_try < 10:
        return fix_rapid_fluctuation(ks, us, n_try=(n_try + 1), low_k=low_k, **kwargs)
    else:
        return _fix_rapid_fluctuation2(ks, us, 0, low_k, **kwargs)


def _fix_rapid_fluctuation2(ks, us, n_try=0, low_k=10, **kwargs):
    """

    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type n_try:  int
    :type low_k: float
    :rtype: numpy.ndarray, numpy.ndarray
    """
    u_diff_threshold = kwargs.get('udiff_threshold', 10)
    new_us = np.array(us)
    has_fixed = False
    for idx in range(2, len(us) - 2):
        ppidx, pidx, cidx, nidx, nnidx = idx - 2, idx - 1, idx, idx + 1, idx + 2
        ppu, pu, cu, nu, nnu = us[ppidx], us[pidx], us[cidx], us[nidx], us[nnidx]
        ppk, pk, ck, nk, nnk = ks[ppidx], ks[pidx], ks[cidx], ks[nidx], ks[nnidx]
        if ck > low_k:
            continue

        _pu_min, _pu_max = min(ppu, pu), max(ppu, pu)
        _nu_min, _nu_max = min(nnu, nu), max(nnu, nu)

        if _pu_max - cu > u_diff_threshold and _nu_max - cu > u_diff_threshold:
            new_us[cidx] = (((_pu_max + _nu_max) / 2) + cu) / 2
            has_fixed = True

        elif cu - _pu_min > u_diff_threshold and cu - _nu_min > u_diff_threshold:
            new_us[cidx] = (((_pu_min + _nu_min) / 2) + cu) / 2
            has_fixed = True

    us = new_us

    if has_fixed and n_try < 10:
        return _fix_rapid_fluctuation2(ks, us, n_try=(n_try + 1), low_k=low_k, **kwargs)
    else:
        return _fix_rapid_fluctuation3(ks, us, n_try=0, low_k=low_k, **kwargs)


def _fix_rapid_fluctuation3(ks, us, n_try=0, low_k=10, **kwargs):
    """

    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type n_try:  int
    :type low_k: float
    :rtype: numpy.ndarray, numpy.ndarray
    """
    u_diff_threshold = kwargs.get('udiff_threshold2', 10)
    new_us = np.array(us)
    has_fixed = False
    for idx in range(0, len(us) - 1):
        cidx, nidx = idx, idx + 1
        cu, nu = us[cidx], us[nidx]
        ck, nk = ks[cidx], ks[nidx]
        if ck > low_k:
            continue

        diff = abs(cu - nu)
        if diff > u_diff_threshold:
            offset = diff / 4
            if cu > nu:
                new_us[cidx] = cu - offset
                new_us[nidx] = nu + offset
            else:
                new_us[cidx] = cu + offset
                new_us[nidx] = nu - offset
            has_fixed = True

    us = new_us

    if has_fixed and n_try < 10:
        return _fix_rapid_fluctuation3(ks, us, n_try=(n_try + 1), low_k=low_k, **kwargs)

    return ks, us