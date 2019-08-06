# -*- coding: utf-8 -*-
import math

import numpy as np

from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.core.nsrf.nsr_func import fitting

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

DEFAULT_KT = 30
PARALLEL_DEGREE_LIMIT = 10
PATTERN_V_DEGREE_LIMIT = 10


def create_uk_hills(ks, us, sks, sus):
    """
    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type sks: numpy.ndarray
    :type sus: numpy.ndarray
    :rtype: list[pyticas_ncrtes.core.etypes.Hill]
    """
    from pyticas_ncrtes.core.etypes import Hill
    locs = [0]
    idx = 1
    to_idx = len(sus) - 1
    while idx < to_idx:
        pk, pu = sks[idx - 1], sus[idx - 1]
        ck, cu = sks[idx], sus[idx]
        nk, nu = sks[idx + 1], sus[idx + 1]
        pk_trend = 1 if pk < ck else -1
        pu_trend = 1 if pu < cu else -1
        nk_trend = 1 if ck < nk else -1
        nu_trend = 1 if cu < nu else -1
        if pk_trend != nk_trend or pu_trend != nu_trend:
            locs.append(idx)
            idx += 2
        else:
            idx += 1
    locs.append(len(sus) - 1)

    hills = []
    """:type: list[Hill] """
    for idx in range(1, len(locs)):
        sidx, eidx = locs[idx - 1], locs[idx]
        hills.append(Hill(idx - 1, sidx, eidx - 1,
                          ks[sidx:eidx], us[sidx:eidx],
                          sks[sidx:eidx], sus[sidx:eidx]))
    return hills


def create_speed_hills(ks, us, sks, sus, **kwargs):
    """
    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type sks: numpy.ndarray
    :type sus: numpy.ndarray
    :rtype: list[pyticas_ncrtes.core.etypes.Hill]
    """
    from pyticas_ncrtes.core.etypes import Hill
    kt = kwargs.get('kt', DEFAULT_KT)
    f_merge = kwargs.get('merge', True)
    lsw = setting.SW_30MIN
    lsus = data_util.smooth(us, lsw)
    lsks = data_util.smooth(ks, lsw)

    lsus_minmax_idxs = np.diff(np.sign(np.diff(lsus))).nonzero()[0].tolist()
    lsus_over_kt = np.where(sks > kt)
    lsus_under_kt = np.where(sks <= kt)

    high_k_minmax_idxs = np.intersect1d(lsus_minmax_idxs, lsus_over_kt[0])
    sus_minmax_idxs = np.diff(np.sign(np.diff(sus))).nonzero()[0].tolist()
    low_k_minmax_idxs = np.intersect1d(sus_minmax_idxs, lsus_under_kt[0])

    minmax_idxs = [0] + np.concatenate([low_k_minmax_idxs, high_k_minmax_idxs]).tolist() + [len(us) - 1]
    minmax_idxs = np.sort(np.unique(minmax_idxs))

    # remove same trend (decrease or increase)
    tmp = [minmax_idxs[0]]
    for midx in range(1, len(minmax_idxs)):
        if minmax_idxs[midx] - minmax_idxs[midx - 1] <= 2:
            continue
        tmp.append(minmax_idxs[midx])
    minmax_idxs = tmp

    cycles = []
    for idx in range(1, len(minmax_idxs)):
        cycles.append([minmax_idxs[idx - 1], minmax_idxs[idx]])

    if f_merge:
        cycles = merge_cycles(cycles, lsks, lsus)

    hills = []
    for idx, (sidx, eidx) in enumerate(cycles):
        hills.append(Hill(idx, sidx, eidx, ks[sidx:eidx], us[sidx:eidx], sks[sidx:eidx], sus[sidx:eidx]))

    return hills


def merge_cycles(cycles, ks, us, uth=5):
    """

    :type cycles: list[[int, int]]
    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type uth: float
    :rtype: list[[int, int]]
    """

    def _filter_cycles():
        idx = 1
        to = len(cycles) - 1
        to_be_filtered = []
        while True:
            ph_sidx, ph_eidx = cycles[idx - 1]
            ch_sidx, ch_eidx = cycles[idx]
            nh_sidx, nh_eidx = cycles[idx + 1]

            pks, pus = ks[ph_sidx:ph_eidx + 1], us[ph_sidx:ph_eidx + 1]
            cks, cus = ks[ch_sidx:ch_eidx + 1], us[ch_sidx:ch_eidx + 1]
            nks, nus = ks[nh_sidx:nh_eidx + 1], us[nh_sidx:nh_eidx + 1]

            c_diff = max(cus) - min(cus)
            p_diff = max(pus) - min(pus)
            n_diff = max(nus) - min(nus)
            pc_diff = max(pus) - min(cus)
            cp_diff = max(cus) - min(pus)

            if (pus[0] < pus[-1]  # increase
                and nus[0] < nus[-1]  # increase
                and c_diff < uth  # little drop
                and p_diff > uth  # big drop
                and pc_diff < uth):  # little drop
                to_be_filtered.append(idx)
                idx += 2
            elif (pus[0] >= pus[-1]  # decrease
                  and nus[0] >= nus[-1]  # decrease
                  and c_diff < uth  # little drop
                  and p_diff > uth  # big drop
                  and cp_diff < uth):  # little drop
                to_be_filtered.append(idx)
                idx += 2
            elif (c_diff < 2 and (c_diff * 2 < p_diff or c_diff * 2 < n_diff)):
                to_be_filtered.append(idx)
                idx += 2
            else:
                idx += 1

            if idx >= to - 2:
                break

        # print('cycles to be filtered : ', to_be_filtered)
        filtered_cycles = []
        idx = 0
        while idx < to:
            ph_sidx, ph_eidx = cycles[idx]
            if (idx + 1) in to_be_filtered:
                nh_sidx, nh_eidx = cycles[idx + 2]
                merged_cycle = [ph_sidx, nh_eidx]
                filtered_cycles.append(merged_cycle)
                idx += 3
            else:
                filtered_cycles.append([ph_sidx, ph_eidx])
                idx += 1

        if filtered_cycles[-1][1] < cycles[-1][1]:
            filtered_cycles.append(cycles[-1])

        return filtered_cycles, len(to_be_filtered)

    while True:
        cycles, n_filtered = _filter_cycles()
        if not n_filtered:
            break

    return cycles


def local_minmax_points(data):
    """
    :type data: numpy.ndarray
    :rtype: list[int]
    """
    minmax_idxs = np.diff(np.sign(np.diff(data))).nonzero()[0].tolist()
    return [0] + minmax_idxs + [len(data) - 1]


def is_overlapped(sidx1, eidx1, sidx2, eidx2):
    """

    :type sidx1:
    :type sidx2:
    :type eidx1:
    :type eidx2:
    :rtype: bool
    """
    return not (eidx2 < sidx1 or sidx2 > eidx1)


def prev_nonon_little_hill(hill, hills, kth=1, uth=1):
    """
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :rtype: pyticas_ncrtes.core.etypes.Hill
    """
    if hill.idx == 0:
        return None
    for idx in range(hill.idx - 1, 0, -1):
        if hills[idx].is_little_hill(kth, uth):
            continue
        return hills[idx]
    return None


def next_nonon_little_hill(hill, hills):
    """
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :rtype: pyticas_ncrtes.core.etypes.Hill
    """
    if hill.idx > hills[-1].idx - 1:
        return None
    for idx in range(hill.idx + 1, len(hills)):
        if hills[idx].is_little_hill():
            continue
        return hills[idx]
    return None


def prev_decreasing_hill(hill, hills):
    """
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :rtype: pyticas_ncrtes.core.etypes.Hill
    """
    for idx in range(hill.idx - 1, 0, -1):
        if hills[idx].is_little_hill():
            continue
        if hills[idx].is_decreasing():
            return hills[idx]
    return None

def prev_increasing_hill(hill, hills):
    """
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :rtype: pyticas_ncrtes.core.etypes.Hill
    """
    for idx in range(hill.idx - 1, 0, -1):
        if hills[idx].is_little_hill():
            continue
        if hills[idx].is_increasing():
            return hills[idx]
    return None


def prev_traffic_increase_hill(hill, hills):
    """
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :rtype: pyticas_ncrtes.core.etypes.Hill
    """
    for idx in range(hill.idx - 1, 0, -1):
        if hills[idx].is_little_hill():
            continue
        if hills[idx].sks[0] < hills[idx].sks[-1]:
            return hills[idx]
        break
    return None


def merge_hill(hills):
    """

    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :rtype: pyticas_ncrtes.core.etypes.Hill
    """
    # __init__(self, idx, sidx, eidx, ks, us, sks, sus):
    if len(hills) == 1:
        return hills[0]
    from pyticas_ncrtes.core.etypes import Hill
    return Hill(-1, hills[0].sidx, hills[-1].eidx,
                np.concatenate([h.ks for h in hills]),
                np.concatenate([h.us for h in hills]),
                np.concatenate([h.sks for h in hills]),
                np.concatenate([h.sus for h in hills]))


def extend_and_merge_hill(hills, hill):
    """
    
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :rtype: pyticas_ncrtes.core.etypes.Hill
    """
    shill, ehill = extend_hill(hills, hill)
    return merge_hill([ hills[idx] for idx in range(shill.idx, ehill.idx+1)])

def u_diff_hill(hill, other):
    """

    :type hill: pyticas_ncrtes.core.etypes.Hill
    :type other: pyticas_ncrtes.core.etypes.Hill
    :rtype: (bool, numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    """
    # set overlapping-k area
    _min_k, _max_k = overlapped_krange(hill, other)
    min_k, max_k = int(math.ceil(_min_k)), int(math.floor(_max_k))

    if max_k - min_k < 1:
        return False, None, None, None, None

    diffs = []
    ks = []
    u1s = []
    u2s = []
    for k in range(min_k, max_k + 1):
        u1 = hill.u_at_k(k)
        u2 = other.u_at_k(k)
        if u1 is not None and u2 is not None:
            diffs.append(u1 - u2)
            ks.append(k)
            u1s.append(u1)
            u2s.append(u2)

    return any(diffs), np.array(diffs), np.array(ks), np.array(u1s), np.array(u2s)


def k_diff_hill(hill, other):
    """

    :type hill: pyticas_ncrtes.core.etypes.Hill
    :type other: pyticas_ncrtes.core.etypes.Hill
    :rtype: (bool, numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    """
    umin, umax = hill.u_range()
    oumin, oumax = other.u_range()

    # set overlapping-k area
    max_u = min(umax, oumax)
    min_u = max(umin, oumin)

    if max_u - min_u < 1:
        return False, None, None, None, None

    diffs = []
    us = []
    k1s = []
    k2s = []
    for u in range(min_u, max_u + 1):
        k1 = hill.k_at_u(u)
        k2 = other.k_at_u(u)
        if k1 is not None and k2 is not None:
            diffs.append(k1 - k2)
            us.append(u)
            k1s.append(k1)
            k2s.append(k2)
    return any(diffs), np.array(diffs), np.array(us), np.array(k1s), np.array(k2s)


def extend_hill(hills, target_hill, direction=0, no_trim=False, trend_mode='u', **kwargs):
    """ extend hills if it is same speed trend

    :param direction: 0:both, -1:backword, 1:forward
    :param trend_mode: u:speed trend, k:density trend

    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :type direction: int
    :rtype: (pyticas_ncrtes.core.etypes.Hill, pyticas_ncrtes.core.etypes.Hill)
    """
    dbg = kwargs.get('dbg', False)
    if dbg: print('# extend hill : ', target_hill.idx, (target_hill.sidx, target_hill.eidx))
    trmode = 'trend_%s' % trend_mode
    start_hill, end_hill = target_hill, target_hill
    if direction in [0, -1]:
        for hill in reversed(prev_hills(hills, target_hill)):
            if getattr(hill, trmode) == getattr(target_hill, trmode) or hill.is_little_hill():
                if dbg: print('  - update start hill : ', hill.idx, (hill.sidx, hill.eidx))
                start_hill = hill
            else:
                break
        if not no_trim:
            for hill in hills[start_hill.idx:]:
                if hill.is_little_hill():
                    continue
                if hill.idx > target_hill.idx:
                    if dbg: print('  - trim little hill (start) : ', hill.idx, (hill.sidx, hill.eidx))
                    start_hill = hill
                break

    if direction in [0, 1]:
        for hill in next_hills(hills, target_hill):
            if getattr(hill, trmode) == getattr(target_hill, trmode) or hill.is_little_hill():
                if dbg: print('  - update end hill : ', hill.idx, (hill.sidx, hill.eidx))
                end_hill = hill
            else:
                break
        if not no_trim:
            for hill in reversed(hills[:end_hill.idx + 1]):
                if hill.is_little_hill():
                    continue
                if hill.idx > target_hill.idx:
                    if dbg: print('  - trim little hill (end) : ', hill.idx, (hill.sidx, hill.eidx))
                    end_hill = hill
                break

    if dbg:
        print('  - start hill : ', start_hill.idx, (start_hill.sidx, start_hill.eidx))
        print('  - end hill : ', end_hill.idx, (end_hill.sidx, end_hill.eidx))

    if start_hill.idx > end_hill.idx:
        start_hill, end_hill = target_hill, target_hill

    return (start_hill, end_hill)


def extended_sidx(hills, h):
    """
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :type h: pyticas_ncrtes.core.etypes.Hill
    :rtype: list[pyticas_ncrtes.core.etypes.Hill]
    """
    return extend_hill(hills, h)[0].sidx


def extended_eidx(hills, h):
    """
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :type h: pyticas_ncrtes.core.etypes.Hill
    :rtype: list[pyticas_ncrtes.core.etypes.Hill]
    """
    return extend_hill(hills, h)[1].eidx


def k_overlapped_hills(hills, hill):
    """
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :rtype: list[pyticas_ncrtes.core.etypes.Hill]
    """
    ohills = []
    kmin, kmax = hill.k_range()
    if kmax == kmin:
        return ohills

    for v in hills:
        vkmin, vkmax = v.k_range()
        if vkmax < kmin or vkmin > kmax:
            continue
        ohills.append(v)
    return ohills


def next_hills(hills, hill, trend=None):
    """
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :type trend: int
    :rtype: list[pyticas_ncrtes.core.etypes.Hill]
    """
    if trend is not None:
        return [h for h in hills if h.idx > hill.idx and h.trend_u == trend]
    return [h for h in hills if h.idx > hill.idx]


def prev_hills(hills, c, trend=None):
    """
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :type c: pyticas_ncrtes.core.etypes.Hill
    :type trend: int
    :rtype: list[pyticas_ncrtes.core.etypes.Hill]
    """
    if trend is not None:
        return [cy for cy in hills if cy.idx < c.idx and cy.trend_u == trend]
    return hills[:c.idx]


def between_hills(hills, phill, nhill, trend=None):
    """
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :type phill: pyticas_ncrtes.core.etypes.Hill
    :type nhill: pyticas_ncrtes.core.etypes.Hill
    :type trend: int
    :rtype: list[pyticas_ncrtes.core.etypes.Hill]
    """
    if trend is not None:
        return [cy for cy in hills if phill.idx < cy.idx < nhill.idx and cy.trend_u == trend]
    return hills[phill.idx + 1:nhill.idx]


def find_hill(tidx, hills):
    """

    :type tidx: idx
    :type hills: list[pyticas_ncrtes.core.etypes.Hill]
    :rtype: pyticas_ncrtes.core.etypes.Hill
    """
    for idx, hill in enumerate(hills):
        if hill.sidx <= tidx <= hill.eidx:
            return hill
    return None


def segmentize(hill, max_distance_limit=2):
    """ devide hill if there is curve on hill    
    
    :type hill: pyticas_ncrtes.core.etypes.Hill 
    :rtype: list[pyticas_ncrtes.core.etypes.Hill]
    """
    distances, us_on_line = distances_to_atoz_line(hill)
    max_distance = max(distances)

    if max_distance < max_distance_limit:
        return [hill]
    else:
        from pyticas_ncrtes.core.etypes import Hill
        max_distance_idx = distances.index(max_distance)
        sidx1, eidx1 = hill.sidx, hill.sidx + max_distance_idx - 1
        sidx2, eidx2 = hill.sidx + max_distance_idx, hill.eidx

        if min(len(hill.ks[:max_distance_idx]) , len(hill.ks[max_distance_idx:])) < 3:
            return [hill]

        hill1 = Hill(-1, sidx1, eidx1,
                     hill.ks[:max_distance_idx], hill.us[:max_distance_idx],
                     hill.sks[:max_distance_idx], hill.sus[:max_distance_idx])
        hill2 = Hill(-1, sidx2, eidx2,
                     hill.ks[max_distance_idx:], hill.us[max_distance_idx:],
                     hill.sks[max_distance_idx:], hill.sus[max_distance_idx:])

        return [hill1, hill2]


def distances_to_atoz_line(hill):
    """
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :rtype: (list[float], list[float])
    """
    x1, y1, x2, y2 = hill.sks[0], hill.sus[0], hill.sks[-1], hill.sus[-1]
    us_on_line = []
    distances = []
    for idx, k in enumerate(hill.sks):
        u = hill.sus[idx]
        us_on_line.append(data_util.get_value_on_line(k, y1, y2, x1, x2))
        distances.append(data_util.distance_to_line(k, u, y1, y2, x1, x2))
    return distances, us_on_line


def get_angle(host_hill, guest_hill):
    """    
    :type host_hill: pyticas_ncrtes.core.etypes.Hill 
    :type guest_hill: pyticas_ncrtes.core.etypes.Hill
    :rtype: float     
    """
    import math
    host_slope = get_slope(host_hill)
    guest_slope = get_slope(guest_hill)
    angle = math.atan((host_slope - guest_slope) / (1 + host_slope * guest_slope))
    degree = angle * 180 / math.pi
    return degree


def get_slope(hill):
    """    
    :type hill: pyticas_ncrtes.core.etypes.Hill 
    :rtype: float     
    """
    fit_func = lambda x, a, b: a * x + b
    _, popts, _, _ = fitting.curve_fit(fit_func, hill.sks, hill.sus, [-1, 2])
    return popts[0]

def get_segmentized_slopes(hill):
    """
    
    :type hill: pyticas_ncrtes.core.etypes.Hill
    :rtype: list[float] 
    """
    shills = segmentize(hill)
    return [ get_slope(h) for h in shills ]

def is_pattern_v(host_hill, guest_hill):
    """    
    :type host_hill: pyticas_ncrtes.core.etypes.Hill 
    :type guest_hill: pyticas_ncrtes.core.etypes.Hill
    :return: 
    """
    degree = get_angle(host_hill, guest_hill)
    return abs(degree) > PATTERN_V_DEGREE_LIMIT


def is_parallel(host_hill, guest_hill):
    """    
    :type host_hill: pyticas_ncrtes.core.etypes.Hill 
    :type guest_hill: pyticas_ncrtes.core.etypes.Hill
    :rtype: float 
    """
    degree = get_angle(host_hill, guest_hill)
    return abs(degree) < PARALLEL_DEGREE_LIMIT


def u_diff_only(host_hill, guest_hill):
    """    
    :type host_hill: pyticas_ncrtes.core.etypes.Hill 
    :type guest_hill: pyticas_ncrtes.core.etypes.Hill
    :rtype: numpy.ndarray 
    """
    _min_k, _max_k = overlapped_krange(host_hill, guest_hill)
    min_k, max_k = int(math.ceil(_min_k)), int(math.floor(_max_k))
    if max_k - min_k < 2:
        return np.array([])

    u1s = np.array([host_hill.u_at_k(k) for k in range(min_k, max_k)])
    u2s = np.array([guest_hill.u_at_k(k) for k in range(min_k, max_k)])

    wh_none = np.where((u1s != None) & (u2s != None))
    u1s = u1s[wh_none]
    u2s = u2s[wh_none]

    if not any(u1s) or not any(u2s):
        return np.array([])

    return u1s - u2s


def overlapped_krange(hill, ohill):
    """
    :type hill: pyticas_ncrtes.core.etypes.Hill 
    :type ohill: pyticas_ncrtes.core.etypes.Hill
    :rtype: (int, int)
    """
    (kmin, kmax) = hill.k_range()
    (okmin, okmax) = ohill.k_range()

    max_k = min(kmax, okmax)
    min_k = max(kmin, okmin)
    return min_k, max_k

def is_over(host_hill, guest_hill):
    """ Is host_hill over guest_hill ?
    
    :type host_hill: pyticas_ncrtes.core.etypes.Hill 
    :type guest_hill: pyticas_ncrtes.core.etypes.Hill
    """
    diffs = u_diff_only(host_hill, guest_hill)
    return np.average(diffs) > 0
