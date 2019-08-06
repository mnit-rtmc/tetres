# -*- coding: utf-8 -*-


__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import math

import numpy as np

from pyticas_ncrtes.core import data_util
from pyticas_ncrtes.core.est.helper import nighttime_helper as nh
from pyticas_ncrtes.core.est.helper import uk_helper

DEBUG_MODE = False
SAVE_CHART = False
STATION_NUM = 0


## Level 0
def make(snum, edata):
    """
    :type snum: int
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: (list[UKTrajectoryGroup], list[UKTrajectoryEdge], list[UKTrajectoryPoint])
    """
    global STATION_NUM

    STATION_NUM = snum

    w = 7
    tks, tus = data_util.smooth(edata.ks, w), data_util.smooth(edata.us, w)

    uk_points = _adaptive_aggregation(tks, tus, edata)
    uk_edges = _make_uk_edges(uk_points)
    uk_groups = _make_uk_groups(uk_points, uk_edges, edata)
    uk_groups = _set_nighttime_tag(uk_groups, edata)
    _dbg = True

    # print('## Groups ')
    # for g in uk_groups:
    #     print('> Group : ', g)
    #     for e in g.edges:
    #         print('     > ', e)

    if _dbg:
        _chart(uk_groups, uk_points, None, edata, 'UK-Region after init ', tks=tks, tus=tus)

    return (uk_groups, uk_edges, uk_points)


## Level 1

def _adaptive_aggregation(tks, tus, edata):
    """
    
    :type tks: numpy.ndarray 
    :type tus: numpy.ndarray 
    :type edata: pyticas_ncrtes.core.etypes.ESTData 
    :rtype: list[UKTrajectoryPoint] 
    """
    n_data = len(tks)
    regions = []
    gsidx = 0
    gks, gus = [tks[0]], [tus[0]]
    gck, gcu = tks[0], tus[1]  # center of group
    for idx in range(1, n_data):
        pk, pu = tks[idx - 1], tus[idx - 1]
        ck, cu = tks[idx], tus[idx]
        dist = math.sqrt((pk - ck) ** 2 + (pu - cu) ** 2)
        dist_from_group = math.sqrt((gck - ck) ** 2 + (gcu - cu) ** 2)
        if dist > uk_helper.UK_TRACKING_DISTANCE_THRESHOLD or dist_from_group > uk_helper.UK_TRACKING_DISTANCE_THRESHOLD:
            regions.append(
                uk_helper.UKTrajectoryPoint(-1, gsidx, idx - 1, tks[gsidx:idx], tus[gsidx:idx], edata))
            gsidx = idx
            gks, gus = [], []
        gks.append(ck)
        gus.append(cu)
        gck, gcu = np.mean(gks), np.mean(gus)

    regions.append(uk_helper.UKTrajectoryPoint(-1, gsidx, n_data - 1,
                                     tks[gsidx:n_data], tus[gsidx:n_data], edata))

    for idx, r in enumerate(regions):
        r.idx = idx

    return regions


def _make_uk_edges(uk_points):
    """

    :type: cp: UKTrajectoryPoint
    :type uk_points: list[UKTrajectoryPoint]
    :rtype: list[UKTrajectoryEdge]
    """
    edge_num = 0
    uk_edges = []
    """:type: list[UKTrajectoryEdge]"""
    for idx in range(1, len(uk_points)):
        uk_edges.append(uk_helper.UKTrajectoryEdge(edge_num, uk_points[idx - 1], uk_points[idx]))
        edge_num += 1
    return uk_edges


def _set_nighttime_tag(uk_groups, edata):
    """

    :type uk_groups: list[UKTrajectoryGroup]
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: list[UKTrajectoryGroup]
    """
    for g in uk_groups:
        if nh.has_nighttime(g, edata):
            g.tag = 'night'
            for _e in g.edges:
                _e.tag = 'night'
    return uk_groups


def _make_uk_groups(uk_points, uk_edges, edata):
    """

    :type uk_points: list[UKTrajectoryPoint]
    :type uk_edges: list[UKTrajectoryEdge]
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: list[UKTrajectoryGroup]
    """
    _dbg0 = False
    _dbg1 = False
    nighttime_uk_groups = _find_nighttime_uk_groups(uk_edges, 1000)
    highspeed_uk_groups = _find_high_speed_groups(uk_edges, edata.target_station.s_limit, 2000)

    if _dbg0:
        uk_groups = _groups_from_edges(uk_edges)
        _chart(uk_groups, uk_points, None, edata, 'UK-Region after init ')

    # horizontal_zigzag_uk_groups = _find_horizontal_zigzag_groups(uk_edges, 3000)
    #
    # if _dbg0:
    #     uk_groups = _groups_from_edges(uk_edges)
    #     _chart(uk_groups, uk_points, None, edata, 'UK-Region after _find_horizontal_zigzag_groups ')

    # vertical_zigzag_uk_groups = _find_vertical_zigzag_groups(uk_edges, 3000)
    #
    # if _dbg0:
    #     uk_groups = _groups_from_edges(uk_edges)
    #     _chart(uk_groups, uk_points, None, edata, 'UK-Region after _find_vertical_zigzag_groups ')

    cont_trends_groups = _find_continuous_trend_groups(uk_edges, 4000)

    if _dbg1:
        uk_groups = _groups_from_edges(uk_edges)
        _chart(uk_groups, uk_points, None, edata, 'UK-Region after _find_continuous_trend_groups')

    stable_speed_uk_groups = _find_stable_speed_groups(uk_edges, 5000)

    uk_groups = _groups_from_edges(uk_edges)

    if _dbg1:
        _chart(uk_groups, uk_points, None, edata, 'UK-Region after _find_stable_speed_groups')

    uk_groups = _merge_small_group_during_transition(uk_groups, uk_edges)
    if _dbg1:
        _chart(uk_groups, uk_points, None, edata, 'UK-Region after _merge_small_group_during_transition')

    uk_groups = _merge_single_small_uk_groups(uk_groups, uk_edges)
    if _dbg1:
        _chart(uk_groups, uk_points, None, edata, 'UK-Region after _merge_single_small_uk_groups')

    # uk_groups = _break_different_slope(uk_groups, uk_edges)
    # if _dbg1:
    #     _chart(uk_groups, uk_points, None, edata, 'UK-Region after _break_different_slope')


    uk_groups = _merge_high_density_fluctuations(uk_groups, uk_edges, edata.normal_func.daytime_func.get_Kt())
    if _dbg1:
        _chart(uk_groups, uk_points, None, edata, 'UK-Region after _merge_high_density_fluctuations')
    # uk_groups = _merge_same_uk_groups(uk_groups, uk_edges)
    # if _dbg1:
    #     _chart(uk_groups, uk_points, None, edata, 'UK-Region after _merge_same_uk_groups')





    return uk_groups



## Level 2

def _find_nighttime_uk_groups(uk_edges, initial_group_idx):
    """

    :type uk_edges: list[UKTrajectoryEdge]
    :type initial_group_idx: int
    :rtype: list[UKTrajectoryGroup]
    """
    idx = 0
    n_edges = len(uk_edges)
    new_groups = []
    while idx < n_edges:
        edge = uk_edges[idx]
        if not edge.contain_nighttime():
            idx = edge.idx + 1
            continue
        nighttime_edges = _find_next_nighttime_edges(edge.idx, uk_edges)
        if nighttime_edges:
            edges = [edge] + nighttime_edges
            before_nighttime, during_nighttime, after_nighttime = _break_nighttime_head_and_tail(edges)
            if during_nighttime:
                new_groups.append(uk_helper.UKTrajectoryGroup(-1, during_nighttime, 'night'))
                idx = nighttime_edges[-1].idx + 1
            else:
                idx = edge.idx + 1
        else:
            idx = edge.idx + 1

    return _update_group_indices(new_groups, initial_group_idx)


def _find_high_speed_groups(uk_edges, speed_threshold, initial_group_idx):
    """

    :type uk_edges: list[UKTrajectoryEdge]
    :type speed_threshold: float
    :type initial_group_idx: int
    :rtype: list[UKTrajectoryGroup]
    """
    idx = 0
    n_edges = len(uk_edges)
    new_groups = []
    while idx < n_edges:
        edge = uk_edges[idx]
        if edge.group >= 0:
            idx = edge.idx + 1
            continue

        if not _is_over_threshold(edge, speed_threshold):
            idx = edge.idx + 1
            continue

        over_speed_edges = _find_over_threshold_edges(edge.idx, uk_edges, speed_threshold)
        if over_speed_edges:
            edges = [edge] + over_speed_edges
            new_groups.append(uk_helper.UKTrajectoryGroup(-1, edges, 'freeflow'))
            idx = over_speed_edges[-1].idx + 1
        else:
            idx = edge.idx + 1

    return _update_group_indices(new_groups, initial_group_idx)


def _find_stable_speed_groups(uk_edges, initial_group_idx):
    """

    :type uk_edges: list[UKTrajectoryEdge]
    :type initial_group_idx: int
    :rtype: list[UKTrajectoryGroup]
    """
    idx = 0
    n_edges = len(uk_edges)
    new_groups = []
    while idx < n_edges:
        edge = uk_edges[idx]
        (mink, maxk), (minu, maxu) = edge.minmax()
        if edge.is_fixed or minu > edge.start_point.edata.target_station.s_limit:
            idx += 1
            continue
        next_stable_edges = _cont_stable_speed_edges(edge, uk_edges[edge.idx + 1:])
        if next_stable_edges:
            edges = [edge] + next_stable_edges
            new_groups.append(uk_helper.UKTrajectoryGroup(-1, edges, 'stable-speed'))
            idx = next_stable_edges[-1].idx + 1 if next_stable_edges else edge.idx + 1
        else:
            idx = edge.idx + 1

    return _update_group_indices(new_groups, initial_group_idx)


def _find_horizontal_zigzag_groups(uk_edges, initial_group_idx):
    """

    :type uk_edges: list[UKTrajectoryEdge]
    :type initial_group_idx: int
    :rtype: list[UKTrajectoryGroup]
    """

    def _collect_horizontal_zigzag_edges(edge, uk_edges):
        """

        :type edge: UKTrajectoryEdge
        :type uk_edges: list[UKTrajectoryEdge]
        :type speed_threshold: float
        :rtype: list[UKTrajectoryEdge]
        """
        res = []
        prev_edge = edge
        for idx, cursor in enumerate(uk_edges):
            if cursor.is_recovery == prev_edge.is_recovery:
                break
            prev_edge = cursor
            res.append(cursor)
        if len(res) < 3:
            return []

        center_ks = []
        for _e in res:
            (mink, maxk), (minu, maxu) = _e.minmax()
            center_k = (mink + maxk) / 2
            center_ks.append(center_k)
            if maxu - minu > uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD * 2:
                return []

        # k moves toward negative or positive continuously
        if len(np.sign(np.diff(center_ks))) != len(center_ks) - 1:
            return []

        return res

    idx = 0
    n_edges = len(uk_edges)
    new_groups = []
    while idx < n_edges:
        edge = uk_edges[idx]
        if edge.group >= 0 or (idx > 0 and uk_edges[idx-1].is_recovery == edge.is_recovery):
            idx = edge.idx + 1
            continue

        next_cont_trends = _collect_horizontal_zigzag_edges(edge, uk_edges[edge.idx + 1:])
        if next_cont_trends:
            edges = [edge] + next_cont_trends
            new_groups.append(uk_helper.UKTrajectoryGroup(-1, edges, 'horizontal zigzag'))
            idx = next_cont_trends[-1].idx + 1 if next_cont_trends else edge.idx + 1
        else:
            idx = edge.idx + 1

    return _update_group_indices(new_groups, initial_group_idx)


def _find_vertical_zigzag_groups(uk_edges, initial_group_idx):
    """

    :type uk_edges: list[UKTrajectoryEdge]
    :type initial_group_idx: int
    :rtype: list[UKTrajectoryGroup]
    """

    def _collect_vertical_zigzag_edges(edge, uk_edges):
        """

        :type edge: UKTrajectoryEdge
        :type uk_edges: list[UKTrajectoryEdge]
        :type speed_threshold: float
        :rtype: list[UKTrajectoryEdge]
        """
        res = []
        prev_edge = edge
        for idx, cursor in enumerate(uk_edges):
            if cursor.is_recovery != prev_edge.is_recovery:
                break
            if (cursor.is_k_increase == prev_edge.is_k_increase and (not cursor.is_vertical() and not edge.is_vertical())):
                break
            prev_edge = cursor
            res.append(cursor)

        if len(res) < 3:
            return []

        return res

    idx = 0
    n_edges = len(uk_edges)
    new_groups = []
    while idx < n_edges:
        edge = uk_edges[idx]
        if edge.group >= 0 or (idx > 0 and uk_edges[idx-1].is_recovery == edge.is_recovery):
            idx = edge.idx + 1
            continue

        next_zigzags = _collect_vertical_zigzag_edges(edge, uk_edges[edge.idx + 1:])
        if next_zigzags:
            edges = [edge] + next_zigzags
            new_groups.append(uk_helper.UKTrajectoryGroup(-1, edges, 'vertical zigzag'))
            idx = next_zigzags[-1].idx + 1 if next_zigzags else edge.idx + 1
        else:
            idx = edge.idx + 1

    return _update_group_indices(new_groups, initial_group_idx)


def _find_continuous_trend_groups(uk_edges, initial_group_idx):
    """

    :type uk_edges: list[UKTrajectoryEdge]
    :type initial_group_idx: int
    :rtype: list[UKTrajectoryGroup]
    """
    idx = 0
    n_edges = len(uk_edges)
    new_groups = []
    while idx < n_edges:
        edge = uk_edges[idx]
        if edge.group >= 0:
            idx = edge.idx + 1
            continue

        next_cont_trends = _cont_speed_trend_edges(edge, uk_edges[edge.idx + 1:])
        prev_cont_trends = list(reversed(_cont_speed_trend_edges(edge, reversed(uk_edges[:edge.idx]))))
        if next_cont_trends or prev_cont_trends:
            edges = prev_cont_trends + [edge] + next_cont_trends
            new_groups.append(uk_helper.UKTrajectoryGroup(-1, edges, 'cont-trend', True))
            idx = next_cont_trends[-1].idx + 1 if next_cont_trends else edge.idx + 1
        else:
            idx = edge.idx + 1

    return _update_group_indices(new_groups, initial_group_idx)


def _groups_from_edges(uk_edges):
    """

    :type uk_edges: list[UKTrajectoryEdge]
    :rtype: list[UKTrajectoryGroup]
    """
    groups = []
    tmp = []
    gidx = 0
    for edge in uk_edges:
        if edge.group <= 0:
            if tmp:
                groups.append(uk_helper.UKTrajectoryGroup(gidx, tmp, tmp[-1].tag))
                tmp = []
            groups.append(uk_helper.UKTrajectoryGroup(gidx, [edge], edge.tag))
            gidx += 1
            continue
        if not tmp:
            tmp.append(edge)
        elif tmp[-1].group == edge.group:
            tmp.append(edge)
        else:
            groups.append(uk_helper.UKTrajectoryGroup(gidx, tmp, tmp[-1].tag))
            gidx += 1
            tmp = [edge]

    if tmp:
        groups.append(uk_helper.UKTrajectoryGroup(gidx, tmp, tmp[-1].tag))

    return _update_group_indices(groups)


def _merge_small_group_during_transition(uk_groups, uk_edges):
    """

    :type uk_groups: list[UKTrajectoryGroup]
    :type uk_edges: list[UKTrajectoryEdge]
    :rtype: list[UKTrajectoryGroup]
    """
    def _is_small_ukgroup(g1, g2, g3):
        """

        :type g1: UKTrajectoryGroup
        :type g2: UKTrajectoryGroup
        :type g3: UKTrajectoryGroup
        :rtype: bool
        """
        if (len(g2.edges) > 1 or g1.is_recovery == g2.is_recovery or g1.is_recovery != g3.is_recovery):
            return False

        if uk_helper.has_overlapped_edge(g1) or uk_helper.has_overlapped_edge(g3):
            return False

        (mink1, maxk1), (minu1, maxu1) = g1.minmax()
        (mink2, maxk2), (minu2, maxu2) = g2.minmax()
        (mink3, maxk3), (minu3, maxu3) = g3.minmax()

        k_trend1 = g1.edges[-1].end_point.center_k > g1.edges[0].start_point.center_k
        k_trend3 = g3.edges[-1].end_point.center_k > g3.edges[0].start_point.center_k
        if k_trend1 != k_trend3:
            return False



        if maxu2 - minu2 < uk_helper.STABLE_SPEED_THRESHOLD and g1.is_recovery == g2.is_recovery:
            return True

        if ((maxu1 - minu1) < uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD
            or (maxu2 - minu2) > uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD
            or (maxu3 - minu3) < uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD):
            return False

        return True

    def _merge(uk_groups, uk_edges):
        is_updated = False
        idx = 1
        n_groups = len(uk_groups)
        small_groups = []
        while idx < n_groups-1:
            g1 = uk_groups[idx-1]
            g2 = uk_groups[idx]
            g3 = uk_groups[idx+1]

            if not _is_small_ukgroup(g1, g2, g3):
                idx += 1
                continue

            small_groups.append(uk_helper.UKTrajectoryGroup(-1, g1.edges + g2.edges + g3.edges, 'transition'))
            idx = g3.idx + 2
            is_updated = True


        if small_groups:
            new_groups = []
            for sg in small_groups:
                if not new_groups:
                    new_groups = [ g for g in uk_groups if g.edges[-1].idx < sg.edges[0].idx ]
                else:
                    prev_groups = [ g for g in uk_groups
                                    if new_groups[-1].edges[-1].idx < g.edges[-1].idx < sg.edges[0].idx ]
                    new_groups.extend(prev_groups)
                new_groups.append(sg)

            if new_groups[-1].edges[-1].idx < uk_edges[-1].idx:
                remains = [ g for g in uk_groups if new_groups[-1].edges[-1].idx < g.edges[-1].idx ]
                new_groups.extend(remains)
        else:
            new_groups = uk_groups

        return is_updated, _update_group_indices(new_groups)


    new_groups = uk_groups
    for _ in range(10):
        is_updated, new_groups = _merge(uk_groups, uk_edges)
        if not is_updated:
            break

    return new_groups


def _merge_same_uk_groups(uk_groups, uk_edges):
    """

    :type uk_groups: list[UKTrajectoryGroup]
    :type uk_edges: list[UKTrajectoryEdge]
    :rtype: list[UKTrajectoryGroup]
    """

    def _is_same_uk_group(g1, g2):
        """

        :type g1: UKTrajectoryGroup
        :type g2: UKTrajectoryGroup
        :rtype: bool
        """
        has_at_least_one = False

        udiffs, kdiffs = uk_helper.uk_abs_diffs(g1, g2)

        # pattern-v
        if udiffs != None and any(udiffs) and ((udiffs[-1] < 1 and udiffs[0] > 3) or (udiffs[-1] > 3 and udiffs[0] < 1)):
            return False

        # if recovery is over reduction
        if not g1.is_recovery and g2.is_recovery:
            udiffs, kdiffs = uk_helper.uk_diffs(g2, g1)
            if udiffs is not None:
                n_positives = len([ _u for _u in udiffs if _u > 0 ])
                n_negatives = len([ _u for _u in udiffs if _u < 0 ])
                if n_positives > n_negatives:
                    return False

        for _e1 in g1.edges:
            for _e2 in g2.edges:
                udiffs, kdiffs = uk_helper.uk_abs_diffs(_e1, _e2)
                if udiffs is None or not any(udiffs):
                    continue
                if any(udiffs) and max(udiffs) > uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD:
                    return False
                elif any(kdiffs) and max(kdiffs) > uk_helper.SAME_UK_GROUP_K_DISTANCE_THRESHOLD:
                    return False
                else:
                    has_at_least_one = True

        return has_at_least_one


    def _merge(uk_groups, uk_edges):
        """

        :type uk_groups: list[UKTrajectoryGroup]
        :type uk_edges: list[UKTrajectoryEdge]
        :rtype: (bool, list[UKTrajectoryEdge])
        """
        is_updated = False
        idx = 0
        n_groups = len(uk_groups)
        same_uk_group = []
        while idx < n_groups-1:
            g1 = uk_groups[idx]
            g2 = uk_groups[idx+1]

            if g1.tag == 'night' or g2.tag == 'night' or not _is_same_uk_group(g1, g2):
                idx += 1
                continue

            same_uk_group.append(uk_helper.UKTrajectoryGroup(-1, g1.edges + g2.edges, 'same-uk'))
            idx = g2.idx + 1
            is_updated = True


        if same_uk_group:
            new_groups = []
            for sg in same_uk_group:
                if not new_groups:
                    new_groups = [ g for g in uk_groups if g.edges[-1].idx < sg.edges[0].idx ]
                else:
                    prev_groups = [ g for g in uk_groups
                                    if new_groups[-1].edges[-1].idx < g.edges[-1].idx < sg.edges[0].idx ]
                    new_groups.extend(prev_groups)
                new_groups.append(sg)

            if new_groups[-1].edges[-1].idx < uk_edges[-1].idx:
                remains = [ g for g in uk_groups if new_groups[-1].edges[-1].idx < g.edges[-1].idx ]
                new_groups.extend(remains)
        else:
            new_groups = uk_groups

        return is_updated, _update_group_indices(new_groups)


    new_groups = uk_groups
    for _ in range(10):
        is_updated, new_groups = _merge(new_groups, uk_edges)
        if not is_updated:
            break

    return new_groups



def _merge_single_small_uk_groups(uk_groups, uk_edges):
    """

    :type uk_groups: list[UKTrajectoryGroup]
    :type uk_edges: list[UKTrajectoryEdge]
    :rtype: list[UKTrajectoryGroup]
    """
    def _is_same_uk_group(g1, g2):
        """

        :type g1: UKTrajectoryGroup
        :type g2: UKTrajectoryGroup
        :rtype: bool
        """
        has_at_least_one = False
        for _e1 in g1.edges:
            for _e2 in g2.edges:
                udiffs, kdiffs = uk_helper.uk_abs_diffs(_e1, _e2)
                if udiffs is None or not any(udiffs):
                    continue
                if any(udiffs) and max(udiffs) > uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD:
                    return False
                if any(kdiffs) and max(kdiffs) > uk_helper.SAME_UK_GROUP_K_DISTANCE_THRESHOLD:
                    return False
                else:
                    has_at_least_one = True

        return has_at_least_one


    def _merge(uk_groups, uk_edges):
        """

        :type uk_groups: list[UKTrajectoryGroup]
        :type uk_edges: list[UKTrajectoryEdge]
        :rtype: (bool, list[UKTrajectoryEdge])
        """
        is_updated = False
        idx = 1
        n_groups = len(uk_groups)
        same_uk_group = []
        while idx < n_groups-1:
            g1 = uk_groups[idx-1]
            g2 = uk_groups[idx]
            g3 = uk_groups[idx+1]

            if g2.tag == 'night' or len(g2.edges) > 1 or len(g1.edges) == 1 or len(g3.edges) == 1:
                idx = g2.idx + 1
                continue

            if g2.edges[0].is_recovery == g1.edges[-1].is_recovery and g2.edges[0].is_recovery != g3.edges[0].is_recovery:
                udiffs, kdiffs = uk_helper.uk_abs_diffs(g2.edges[0], g1.edges[-1])
                if udiffs == None or max(udiffs) < uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD:
                    same_uk_group.append(uk_helper.UKTrajectoryGroup(-1, g1.edges + g2.edges, 'same-uk'))
                    is_updated = True
                    idx = g3.idx + 1
                    continue

            if g2.edges[0].is_recovery != g1.edges[-1].is_recovery and g2.edges[0].is_recovery == g3.edges[0].is_recovery:
                udiffs, kdiffs = uk_helper.uk_abs_diffs(g2.edges[0], g3.edges[0])
                if udiffs == None or max(udiffs) < uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD:
                    same_uk_group.append(uk_helper.UKTrajectoryGroup(-1, g2.edges + g3.edges, 'same-uk'))
                    is_updated = True
                    idx = g3.idx + 1
                    continue

            idx = g2.idx + 1


        if same_uk_group:
            new_groups = []
            for sg in same_uk_group:
                if not new_groups:
                    new_groups = [ g for g in uk_groups if g.edges[-1].idx < sg.edges[0].idx ]
                else:
                    prev_groups = [ g for g in uk_groups
                                    if new_groups[-1].edges[-1].idx < g.edges[-1].idx < sg.edges[0].idx ]
                    new_groups.extend(prev_groups)
                new_groups.append(sg)

            if new_groups[-1].edges[-1].idx < uk_edges[-1].idx:
                remains = [ g for g in uk_groups if new_groups[-1].edges[-1].idx < g.edges[-1].idx ]
                new_groups.extend(remains)
        else:
            new_groups = uk_groups

        return is_updated, _update_group_indices(new_groups)


    new_groups = uk_groups
    for _ in range(10):
        is_updated, new_groups = _merge(new_groups, uk_edges)
        if not is_updated:
            break

    return new_groups



def _break_different_slope(uk_groups, uk_edges):
    """

    :type uk_groups: list[UKTrajectoryGroup]
    :type uk_edges: list[UKTrajectoryEdge]
    :rtype: list[UKTrajectoryGroup]
    """

    idx = 1
    n_groups = len(uk_groups)
    new_groups = []

    for idx, g in enumerate(uk_groups):

        if g.tag == 'night' or g.is_recovery:
            new_groups.append(g)
            continue

        (mink, maxk), (minu, maxu) = g.minmax()

        if maxu - minu < uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD * 2 or len(g.edges) < 2:
            new_groups.append(g)
            continue

        tmp = []
        last_edge = None
        for eidx in range(1, len(g.edges)):
            _pe, _ne = g.edges[eidx-1], g.edges[eidx]
            a = uk_helper.get_direction_change_angle(_pe, _ne)
            if a > uk_helper.LINEAR_LINE_DEGREE_THRESHOLD:
                tmp.append(_pe)
                new_groups.append(uk_helper.UKTrajectoryGroup(-1, tmp))
                last_edge = _pe
                tmp = []
            else:
                tmp.append(_pe)

        if last_edge is not None and last_edge != g.edges[-1]:
            new_groups.append(uk_helper.UKTrajectoryGroup(-1, [ _e for _e in g.edges if _e.idx > last_edge.idx]))

        if not last_edge:
            new_groups.append(g)


    return _update_group_indices(new_groups)



def _merge_high_density_fluctuations(uk_groups, uk_edges, kt):
    """

    :type uk_groups: list[UKTrajectoryGroup]
    :type uk_edges: list[UKTrajectoryEdge]
    :type kt: float
    :rtype: list[UKTrajectoryGroup]
    """
    def _is_same_uk_group(g1, g2):
        """

        :type g1: UKTrajectoryGroup
        :type g2: UKTrajectoryGroup
        :rtype: bool
        """
        has_at_least_one = False
        (mink1, maxk1), (minu1, maxu1) = g1.minmax()
        (mink2, maxk2), (minu2, maxu2) = g2.minmax()
        if maxu1 - minu1 > 10 or maxu2 - minu2 > 10 and g1.is_recovery != g2.is_recovery:
            return False

        for _e1 in g1.edges:
            for _e2 in g2.edges:
                udiffs, kdiffs = uk_helper.uk_abs_diffs(_e1, _e2)
                if udiffs is None or not any(udiffs):
                    continue
                if any(udiffs) and max(udiffs) > uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD:
                    return False
                else:
                    has_at_least_one = True

        return has_at_least_one


    def _same_trend_groups(edges):
        """

        :type edges: list[UKTrajectoryEdge]
        :rtype: list[UKTrajectoryGroup]
        """
        idx = 0
        n_edges = len(edges)
        new_groups = []
        while idx < n_edges:
            tmp = [edges[idx]]
            for tidx in range(idx+1, n_edges):
                if edges[tidx].is_recovery == edges[idx].is_recovery:
                    tmp.append(edges[tidx])
                else:
                    break
            new_groups.append(uk_helper.UKTrajectoryGroup(-1, tmp, 'high-k-group'))
            idx += len(tmp)
        return _update_group_indices(new_groups, 0)


    def _find_over_kt_groups(g, uk_groups, kt):
        """

        :type g: UKTrajectoryGroup
        :type uk_groups: list[UKTrajectoryGroup]
        :type kt: float
        :rtype: list[UKTrajectoryGroup], UKTrajectoryGroup
        """
        res = list(g.edges)
        (mink1, maxk1), (minu1, maxu1) = g.minmax()
        last_g = g
        for _g in uk_groups[g.idx+1:]:
            (mink2, maxk2), (minu2, maxu2) = _g.minmax()
            if mink2 < kt:
                break
            res.extend(_g.edges)
            last_g = _g
        return _same_trend_groups(res), last_g


    def _merge_same_uk_groups(uk_groups):
        """

        :type uk_groups: list[UKTrajectoryGroup]
        :rtype: bool, list[UKTrajectoryGroup]
        """
        is_updated = False
        idx = 0
        n_groups = len(uk_groups)
        same_uk_group = []
        while idx < n_groups-1:
            g1 = uk_groups[idx]
            g2 = uk_groups[idx+1]

            if not _is_same_uk_group(g1, g2):
                idx += 1
                continue

            same_uk_group.append(uk_helper.UKTrajectoryGroup(-1, g1.edges + g2.edges, 'same-uk'))
            idx = g2.idx + 1
            is_updated = True


        if same_uk_group:
            new_groups = []
            for sg in same_uk_group:
                if not new_groups:
                    new_groups = [ g for g in uk_groups if g.edges[-1].idx < sg.edges[0].idx ]
                else:
                    prev_groups = [ g for g in uk_groups
                                    if new_groups[-1].edges[-1].idx < g.edges[-1].idx < sg.edges[0].idx ]
                    new_groups.extend(prev_groups)
                new_groups.append(sg)

            if new_groups[-1].edges[-1].idx < uk_edges[-1].idx:
                remains = [ g for g in uk_groups if new_groups[-1].edges[-1].idx < g.edges[-1].idx ]
                new_groups.extend(remains)
        else:
            new_groups = uk_groups

        return is_updated, _update_group_indices(new_groups)

    idx = 0
    n_groups = len(uk_groups)
    new_groups = []
    while idx < n_groups-1:
        g1 = uk_groups[idx]
        g2 = uk_groups[idx+1]

        (mink1, maxk1), (minu1, maxu1) = g1.minmax()
        (mink2, maxk2), (minu2, maxu2) = g2.minmax()

        if min(mink1, mink2) < kt:
            idx += 1
            continue

        high_k_groups, last_g = _find_over_kt_groups(g1, uk_groups, kt)
        merged_groups = high_k_groups
        for _ in range(10):
            is_merged, merged_groups = _merge_same_uk_groups(merged_groups)
            if not is_merged:
                break

        if not new_groups:
            new_groups = (new_groups
                         + [ _g for _g in uk_groups if (_g.edges[-1].idx < merged_groups[0].edges[0].idx)]
                         + merged_groups)
        else:
            new_groups = (new_groups
                         + [ _g for _g in uk_groups if (_g.edges[-1].idx < merged_groups[0].edges[0].idx and _g.edges[0].idx > new_groups[-1].edges[-1].idx)]
                         + merged_groups)

        idx = last_g.idx + 1

    if not new_groups:
        return uk_groups

    new_groups = new_groups + [ _g for _g in uk_groups if (_g.edges[0].idx > new_groups[-1].edges[-1].idx) ]
    return _update_group_indices(new_groups)


## Level 3

def _find_next_nighttime_edges(eidx, uk_edges):
    """

    :type uk_edges: list[UKTrajectoryEdge]
    :rtype: list[UKTrajectoryEdge]
    """
    res = []
    for idx in range(eidx + 1, len(uk_edges)):
        cursor = uk_edges[idx]
        if not cursor.contain_nighttime() and cursor.minmax()[0][1] > uk_helper.LOW_K:
            break
        res.append(cursor)
    return res


def _break_nighttime_head_and_tail(nighttime_edges):
    """

    :type nighttime_edges: list[UKTrajectoryEdge]
    :rtype: (list[UKTrajectoryEdges], list[UKTrajectoryEdges], list[UKTrajectoryEdges])
    """
    before_nighttime, during_nighttime, after_nighttime = [], [], []
    for _e in nighttime_edges:
        if (not _e.start_point.in_nighttime or not _e.end_point.in_nighttime) or _e.minmax()[0][1] > uk_helper.LOW_K:
            before_nighttime.append(_e)
        else:
            break

    for _e in reversed(nighttime_edges):
        if (not _e.start_point.in_nighttime or not _e.end_point.in_nighttime) or _e.minmax()[0][1] > uk_helper.LOW_K:
            after_nighttime.append(_e)
        else:
            break

    after_nighttime = list(reversed(after_nighttime))

    for _e in nighttime_edges:
        if (not before_nighttime or _e.idx > before_nighttime[-1].idx) and (not after_nighttime or _e.idx < after_nighttime[0].idx):
            during_nighttime.append(_e)

    return before_nighttime, during_nighttime, after_nighttime


def _find_over_threshold_edges(eidx, uk_edges, speed_threshold):
    """

    :type eidx: int
    :type uk_edges: list[UKTrajectoryEdge]
    :type speed_threshold: float
    :rtype: list[UKTrajectoryEdge]
    """
    edge = uk_edges[eidx]

    (mink, maxk), (minu, maxu) = edge.minmax()
    res = []
    for idx in range(eidx + 1, len(uk_edges)):
        cursor = uk_edges[idx]
        if cursor.group >= 0:
            break

        if not _is_over_threshold(edge, speed_threshold):
            break

        if uk_helper.is_vertical_down_edge(edge):
            break

        (_mink, _maxk), (_minu, _maxu) = cursor.minmax()
        if maxu - _minu > uk_helper.SAME_UK_GROUP_U_DISTANCE_THRESHOLD * 2:
            break

        res.append(cursor)

    return res


def _is_over_threshold(edge, speed_threshold):
    """

    :type edge: UKTrajectoryEdge
    :type speed_threshold: float
    :return:
    """
    (mink, maxk), (minu, maxu) = edge.minmax()
    if minu < speed_threshold:
        return False
    return True


def _cont_stable_speed_edges(edge, uk_edges):
    """

    :type edge: UKTrajectoryEdge
    :type uk_edges: list[UKTrajectoryEdge]
    :return:
    """
    res = []
    prev_edge = edge
    total_minute = prev_edge.start_point.minutes + prev_edge.end_point.minutes
    for idx, cursor in enumerate(uk_edges):
        (mink1, maxk1), (minu1, maxu1) = prev_edge.minmax()
        (mink2, maxk2), (minu2, maxu2) = cursor.minmax()
        if cursor.is_fixed or minu2 > cursor.start_point.edata.target_station.s_limit:
            break
        total_minute += cursor.end_point.minutes
        if (maxu1 - minu1 < uk_helper.STABLE_SPEED_THRESHOLD
            and maxu2 - minu2 < uk_helper.STABLE_SPEED_THRESHOLD
            and abs(maxu2 - minu1) < uk_helper.STABLE_SPEED_THRESHOLD
            and abs(maxu1 - minu2) < uk_helper.STABLE_SPEED_THRESHOLD
            and total_minute > uk_helper.STABLE_TIME_THRESHOLD):
            res.append(cursor)
            prev_edge = cursor
        else:
            break
    return res


def _cont_speed_trend_edges(edge, uk_edges):
    """

    :type edge: UKTrajectoryEdge
    :type uk_edges: list[UKTrajectoryEdge]
    :type speed_threshold: float
    :rtype: list[UKTrajectoryEdge]
    """
    res = []
    prev_edge = edge

    for idx, cursor in enumerate(uk_edges):

        # overlapped
        udiffs, kdiffs = uk_helper.uk_abs_diffs(prev_edge, cursor)
        if udiffs != None and max(udiffs) > uk_helper.STABLE_SPEED_THRESHOLD:
            break

        (mink, maxk), (minu, maxu) = cursor.minmax()
        # a = uk_helper.get_direction_change_angle(prev_edge, cursor)
        if ((edge.is_recovery == cursor.is_recovery or (maxu - minu < uk_helper.STABLE_SPEED_THRESHOLD)) and cursor.start_point.minutes < 60
            and (cursor.is_recovery or uk_helper.get_direction_change_angle(prev_edge, cursor) < uk_helper.LINEAR_LINE_DEGREE_THRESHOLD)):
        # if ( (edge.is_recovery == cursor.is_recovery or (maxu - minu < uk_helper.STABLE_SPEED_THRESHOLD)) and cursor.start_point.minutes < 60):
            res.append(cursor)
            prev_edge = cursor
        else:
            break
    return res


def _update_group_indices(uk_groups, initial_group_idx=0):
    """        
    :type uk_groups: list[UKTrajectoryGroup]
    :type initial_group_idx: int
    :rtype: list[UKTrajectoryGroup]
    """
    res = []
    gidx = initial_group_idx
    for idx, g in enumerate(uk_groups):
        if not any(g.edges):
            continue
        g.idx = gidx
        res.append(g)
        for eidx, e in enumerate(g.edges):
            e.group = gidx
            e.group = gidx
        gidx += 1
    return res


def _chart(ukgroups, ukpoints, final_recovery_group, edata, chart_label, **kwargs):
    """

    :type ukgroups: list[UKTrajectoryGroup]
    :type ukpoints: list[UKTrajectoryPoint]
    :type final_recovery_group: UKTrajectoryGroup
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type chart_label: str
    :return:
    """
    global STATION_NUM
    if not DEBUG_MODE:
        return

    dt_func = cidata = None
    if edata.normal_func is not None:
        dt_func = edata.normal_func.daytime_func
        cidata = dt_func.recovery_cidata

    import matplotlib.pyplot as plt
    long_title = '%s (%s[s_limit=%d, label=%s], %s) - %s' % (
        edata.snow_event.snow_period.get_date_string(),
        edata.target_station.station_id,
        edata.target_station.s_limit,
        edata.target_station.label,
        edata.target_station.corridor.name,
        chart_label)

    # (ax1, ax2, ax3, ax4, ax5, ax6, ax7) = (plt.subplot(311),
    #                                        plt.subplot(334), plt.subplot(335), plt.subplot(336),
    #                                        plt.subplot(337), plt.subplot(338), plt.subplot(339))

    fig1 = plt.figure(figsize=(16, 9), dpi=100, facecolor='white')
    ax1 = fig1.add_subplot(211)
    (ax2, ax3, ax4) = (fig1.add_subplot(234), fig1.add_subplot(235), fig1.add_subplot(236))

    # ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=2)
    # ax8 = fig1.add_subplot(233)

    fig2 = plt.figure(figsize=(16, 9), dpi=100, facecolor='white')
    (ax5, ax6, ax7) = (fig2.add_subplot(131), fig2.add_subplot(132), fig2.add_subplot(133))


    target_ks, target_us = kwargs.get('tks', edata.lllsks), kwargs.get('tus', edata.lllsus)
    rp_ks = []
    rp_us = []
    region_us = []
    region_ks = []
    region_qs = []
    maxq = 800
    for p in ukpoints:
        _region_us = np.array([None] * len(target_ks))
        _region_ks = np.array([None] * len(target_ks))
        _region_qs = np.array([None] * len(target_ks))
        _rus, _rks = [], []
        for idx in range(p.sidx, p.eidx + 1):
            _region_us[idx] = target_us[idx]
            _region_ks[idx] = target_ks[idx]
            _rus.append(target_us[idx])
            _rks.append(target_ks[idx])
        rp_ks.append(np.mean(_rks))
        rp_us.append(np.mean(_rus))

        region_us.append(_region_us)
        region_ks.append(_region_ks)

        for idx in range(len(_region_us)):
            _region_qs[idx] = (_region_us[idx] * _region_ks[idx]) if _region_us[idx] is not None and _region_ks[
                                                                                                         idx] is not None else None

        _maxq = max(_region_qs[np.nonzero(_region_qs)])
        if _maxq > maxq:
            maxq = _maxq + 200
        region_qs.append(_region_qs)

    ecs = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']
    markers = ['o', 'x', 'd', '^', '<', '>', 'v', 's', '*', '+']
    used = []

    # ax1.plot(region_us, lw=3)
    ax2.plot(target_ks, target_us, c='#AAAAAA', zorder=1)
    ax3.plot(rp_ks, rp_us, c='#AAAAAA', zorder=1)

    ax5.plot(target_ks, target_ks*target_us, c='#AAAAAA', zorder=1)
    ax6.plot(rp_ks, np.array(rp_ks) * np.array(rp_us), c='#AAAAAA', zorder=1)

    # ax4.plot(rp_ks, rp_us, c='#AAAAAA', zorder=1)
    for idx in range(len(region_us)):
        c = ecs[idx % len(ecs)]
        marker = '|'
        for midx in range(len(markers)):
            marker_stick = '%s-%s' % (c, markers[midx])
            if marker_stick not in used:
                marker = markers[midx]
                used.append(marker_stick)
                break
        ax2.scatter(region_ks[idx], region_us[idx], marker=marker, c=c, zorder=2)
        ax3.scatter([rp_ks[idx]], [rp_us[idx]], marker=marker, c=c, zorder=2)

        ax5.scatter(region_ks[idx], region_qs[idx], marker=marker, c=c, zorder=2)
        ax6.scatter([rp_ks[idx]], [rp_ks[idx] * rp_us[idx]], marker=marker, c=c, zorder=2)

        # ax1.plot(region_us[idx], lw=2, c=c)

    # for idx, p in enumerate(ukpoints):
    #     c = ecs[idx % len(ecs)]
    #     if len(p.ks) == 1:
    #         ax1.scatter([p.sidx], [p.us[0]], marker='o', c=c)

    # for idx, p in enumerate(ukpoints):
    #     s = (int(len(p.ks) / 6) + 1) * 10
    #     ax4.scatter([p.center_k], [p.center_u], c='#AAAAAA', s=s, marker='o', zorder=1)

    ax7.scatter([p.center_k for idx, p in enumerate(ukpoints)],
                [p.center_u * p.center_k for idx, p in enumerate(ukpoints)],
                c='#AAAAAA', marker='.', zorder=1)

    used = []
    for gidx, g in enumerate(ukgroups):
        c = ecs[gidx % len(ecs)]
        marker = '|'
        for midx in range(len(markers)):
            marker_stick = '%s-%s' % (c, markers[midx])
            if marker_stick not in used:
                marker = markers[midx]
                used.append(marker_stick)
                break

        ls = '-'
        lw = 1

        ax4.plot([p.center_k for idx, p in enumerate(g.get_points())],
                 [p.center_u for idx, p in enumerate(g.get_points())],
                 c=c, ls=ls, lw=lw, zorder=2)
        # ax4.scatter([g.get_points()[0].center_k], [g.get_points()[0].center_u], marker=marker, c=c, zorder=2, s=20)
        for _e in g.edges:
            p = _e.start_point
            s = max((int(len(p.ks) / 6)) * 20, 5)
            ax4.scatter([p.center_k], [p.center_u], c=c, s=s, marker='o', zorder=1)

        ax7.plot([p.center_k for idx, p in enumerate(g.get_points())],
                 [p.center_u * p.center_k for idx, p in enumerate(g.get_points())],
                 c=c, ls=ls, lw=lw, zorder=2)
        ax7.scatter([g.get_points()[0].center_k], [g.get_points()[0].center_u * g.get_points()[0].center_k],
                    marker=marker, c=c, zorder=2,
                    s=20)

        _ks, _us = [None] * len(target_us), [None] * len(target_us)
        sidx, eidx = g.get_points()[0].sidx, g.get_points()[-1].eidx
        for idx in range(sidx, eidx + 1):
            _ks[idx] = target_ks[idx]
            _us[idx] = target_us[idx]
        ax1.plot(_us, lw=lw, ls=ls, c=c)

    p = ukgroups[-1].edges[-1].end_point
    s = max((int(len(p.ks) / 6)) * 20, 5)
    ax4.scatter([p.center_k], [p.center_u], c=c, s=s, marker='o', zorder=1)

    ax1.axvline(x=edata.snow_event.time_to_index(edata.snow_event.snow_start_time), c='k')
    ax1.axvline(x=edata.snow_event.time_to_index(edata.snow_event.snow_end_time), c='k')

    if final_recovery_group:
        # print(' Final Recovery Group : ', final_recovery_group.edges[0].start_point.sidx,
        #       final_recovery_group.edges[-1].end_point.eidx)
        ax1.axvline(x=final_recovery_group.edges[0].start_point.sidx)
        ax1.axvline(x=final_recovery_group.edges[-1].end_point.eidx)

    if dt_func is not None:
        _recv_ks = list(range(10, 120))
        if dt_func.recovery_function.is_valid():
            scatter_axs = [ax2, ax3, ax4]
            for ax in scatter_axs:
                ax.plot(cidata.ciks, cidata.cils, ls='-.', lw=2, label='normal-range')
                ax.plot(_recv_ks, dt_func.recovery_speeds(_recv_ks), ls='-.', lw=2, c='g', label='recovery-function')

        if dt_func.reduction_function.is_valid():
            scatter_axs = [ax2, ax3, ax4]
            for ax in scatter_axs:
                ax.plot(_recv_ks, dt_func.reduction_speeds(_recv_ks), ls='-.', c='r', lw=2, label='reduction-function')

        nt_us = edata.normal_func.nighttime_func.speeds(edata.snow_event.data_period.get_timeline(as_datetime=True))

        ax1.plot(nt_us, c='k', label='us (night)')

    ax1.plot(target_ks, c='#AAAAAA', label='k')

    # reported time
    for rp in edata.rps:
        data = np.array([None] * len(target_us))
        data[rp] = target_us[rp]
        ax1.plot(data, marker='o', ms=10, c='#FF0512', label='RBRT')  # red circle

    ax1.grid(), ax2.grid(), ax3.grid(), ax4.grid(), ax5.grid(), ax6.grid(), ax7.grid()
    ax1.set_xlim(xmin=0, xmax=len(edata.ks))
    ax1.set_ylim(ymin=0, ymax=90)
    max_k = max(target_ks) + 5
    max_u = max(target_us) + 5

    if not SAVE_CHART:
        max_k = max_u = 90

    for ax in [ax2, ax3, ax4]:
        ax.set_xlim(xmin=0, xmax=max_k)
        ax.set_ylim(ymin=0, ymax=max_u)

    for ax in [ax5, ax6, ax7]:
        ax.set_xlim(xmin=0, xmax=max_k)
        ax.set_ylim(ymin=0, ymax=maxq)

    # set time-label on x-axis of ax1
    if SAVE_CHART:
        timeline = edata.snow_event.data_period.get_timeline(as_datetime=True)
        ntimes = [t.strftime('%H:%M') for idx, t in enumerate(timeline) if idx % 12 == 0]
        loc_times = [idx for idx, t in enumerate(timeline) if idx % 12 == 0]
        ax1.set_xticks(loc_times)
        ax1.set_xticklabels(ntimes, rotation=90)
    else:
        loc_times = [idx for idx in range(len(edata.ks)) if idx % 24 == 0]
        ax1.set_xticks(loc_times)

    # ax1.legend(), ax2.legend(), ax3.legend()
    fig1.suptitle(long_title)
    fig2.suptitle(long_title)

    fig1.tight_layout()
    fig2.tight_layout()

    fig1.subplots_adjust(top=0.92)
    fig2.subplots_adjust(top=0.92)

    plt.close(fig2)

    import os
    from pyticas_ncrtes import ncrtes
    infra = ncrtes.get_infra()

    output_dir = os.path.join(infra.get_path('ncrtes', create=True), 'ukregion', '%s - %s' % (
        edata.snow_event.snow_period.get_date_string(), edata.target_station.corridor.name))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not SAVE_CHART:
        plt.show()
    else:
        fig1.savefig(os.path.join(output_dir, '%02d - %s.png' % (STATION_NUM, edata.target_station.station_id)),
                     dpi=100)
        # fig2.savefig(os.path.join(output_dir, '%02d - %s (qk).png' % (STATION_NUM, edata.target_station.station_id)), dpi=100)

    plt.clf()
    plt.close(fig1)
    plt.close(fig2)
    plt.close('all')
