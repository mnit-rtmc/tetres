# -*- coding: utf-8 -*-

import numpy as np
from scipy import stats

from pyticas_ncrtes.core import data_util

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

SHOW_GRAPH = False

def estimate(uk, **kwargs):
    """

    :type uk: dict[float, float]
    :rtype: (float, float)
    """
    n_th = 100
    smoothing_window_size = kwargs.get('smoothing_window_size', 5)

    avg_filter = lambda k, avgu, n_data: not (k < 20 and n_data < 40)
    k_filter = lambda k: k < 40

    fuk = data_util.filter_uk(uk, n_threshold=10, k_filter=k_filter)
    if not fuk or len(fuk) < n_th:
        return -1, -1

    fuk = _remove_outlier_by_u(fuk)
    fuk = _remove_outlier_by_k(fuk)

    if not fuk or len(fuk) < n_th:
        return -1, -1

    fus, fks = data_util.dict2sorted_list(fuk)

    quantized_ks, quantized_us = [], []
    n_limit = 30
    for k in fks:
        avgu, stddev, arounds = data_util.avg_y_of_around_x(fks, fus, k, 2)
        if avgu and len(arounds) > n_limit:
            quantized_ks.append(k)
            quantized_us.append(avgu)

    # quantized_us, quantized_ks = data_util.quantized_uk(fus, fks)
    quantized_us = np.array(quantized_us)
    quantized_ks = np.array(quantized_ks)
    tus = data_util.smooth(quantized_us, smoothing_window_size)

    ftus = tus[quantized_ks > 10]

    if SHOW_GRAPH:
        from pyticas_ncrtes.core.util import graph
        us = [ u for k, u in uk.items() ]
        ks = [ k for k, u in uk.items() ]
        graph.plot_scatter([ks, quantized_ks], 'k', [us, tus], 'u',
                           markers=['o', 'x'],
                           ymax=100, xmin=0, xmax=120)


    if len(ftus) < 20:
        return -1, -1

    # it is assumed that maximum speed in smoothed nsr_data is FFS
    ffs = max(ftus)

    # find Kf
    Kf = -1
    for idx, u in enumerate(tus):
        if u >= ffs:
            Kf = quantized_ks[idx]

    return ffs, int(Kf)


def _remove_outlier_by_u(uk):
    ku = {u: k for k, u in uk.items()}
    sks, sus = data_util.dict2sorted_list(ku)
    kernel = stats.gaussian_kde(sus)
    res = list(kernel.evaluate(sus))
    max_pk_idx = res.index(max(res))
    to_pk_idx = len(res)
    for idx in range(max_pk_idx + 1, len(res)):
        if (res[idx - 1] < res[idx] and res[idx - 1] < 0.01) or res[idx] < 0.001:
            to_pk_idx = idx - 1
            break
    from_pk_idx = 0
    for idx in range(max_pk_idx, 0, -1):
        if (res[idx - 1] > res[idx] and res[idx - 1] < 0.01) or res[idx] < 0.001:
            from_pk_idx = idx
            break
    filtered_us = sus[from_pk_idx:to_pk_idx]
    filtered_ks = sks[from_pk_idx:to_pk_idx]
    return {k: filtered_us[idx] for idx, k in enumerate(filtered_ks)}


def _remove_outlier_by_k(uk):
    sus, sks = data_util.dict2sorted_list(uk)
    kernel = stats.gaussian_kde(sks)
    res = list(kernel.evaluate(sks))
    max_pk_idx = res.index(max(res))
    to_pk_idx = len(res)
    for idx in range(max_pk_idx + 1, len(res)):
        if (res[idx - 1] < res[idx] and res[idx - 1] < 0.01) or res[idx] < 0.001:
            to_pk_idx = idx - 1
            break
    from_pk_idx = 0
    for idx in range(max_pk_idx, 0, -1):
        if (res[idx - 1] > res[idx] and res[idx - 1] < 0.01) or res[idx] < 0.001:
            from_pk_idx = idx
            break
    filtered_us = sus[from_pk_idx:to_pk_idx]
    filtered_ks = sks[from_pk_idx:to_pk_idx]
    return {k: filtered_us[idx] for idx, k in enumerate(filtered_ks)}
