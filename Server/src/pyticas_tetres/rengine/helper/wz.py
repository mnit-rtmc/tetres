# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.rc import route_config
from pyticas.rn.route_config.const import VIRTUAL_NODE_DISTANCE
from pyticas.ttypes import RouteConfigNode
from pyticas_tetres.da.wz import WorkZoneDataAccess
from pyticas_tetres.ttypes import WZCharacteristics


# TODO: what if there are multiple configurations for a RNodeObject ?

def apply_workzone(r, prd):
    """

    :type r: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :rtype: pyticas.ttypes.Route
    """
    cloned = r.clone()

    # load_data workzones for the given period
    workzones = find_workzones(prd)
    lane_cfg_map = _lanecfg_map(workzones)
    _update_lanecfg(cloned, lane_cfg_map)

    return cloned


def find_workzones(prd):
    """

    :type prd: pyticas.ttypes.Period
    :rtype: list[pyticas_tetres.ttypes.WorkZoneInfo]
    """
    wzDA = WorkZoneDataAccess()
    data_list = wzDA.search_date_range(prd.start_date, prd.end_date)
    wzDA.close_session()
    return data_list

def _is_use_opposing_lane(node):
    """

    :type node: pyticas.ttypes.RouteConfigNode
    :rtype: bool
    """
    return any(node.node_config.co_lanes)


def _is_used_by_opposing_traffics(node):
    """

    :type node: pyticas.ttypes.RouteConfigNode
    :rtype: bool
    """
    return any(node.node_config.od_lanes)


def _is_shifted(node):
    """

    :type node: pyticas.ttypes.RouteConfigNode
    :rtype: bool
    """
    return any(node.node_config.shifted_lanes)


def _is_mainline_closed(node):
    """

    :type node: pyticas.ttypes.RouteConfigNode
    :rtype: bool
    """
    return any(node.node_config.closed_lanes)


def _is_ramp_closed(node):
    """

    :type node: pyticas.ttypes.RouteConfigNode
    :rtype: bool
    """
    return node.node_config.ramp_opened == -1


def features(wz, route_num):
    """

    :type wz: pyticas_tetres.ttypes.WorkZoneInfo
    :type route_num: int
    :return: (workzone length, list of workzone characteristics, lane configurations, number of closed ramps)
    :rtype: (float, list[WZCharacteristics], list[(int, int)], int)
    """
    _features = []
    _lncfgs = []
    closed_ramps = []
    start_mp = -1
    end_mp = -1
    n_wz = 0
    prev_mp = -1
    for idx, node_set in enumerate(wz.route1.cfg.node_sets):

        node = getattr(node_set, 'node%d' % route_num)
        assert isinstance(node, RouteConfigNode)

        if _is_use_opposing_lane(node):
            _features.append(WZCharacteristics.USE_OPPOSING_LANE)

        if _is_used_by_opposing_traffics(node):
            _features.append(WZCharacteristics.USED_BY_OPPOSING_TRAFFICS)

        if _is_shifted(node):
            _features.append(WZCharacteristics.HAS_SHIFTED_LANES)

        if _is_use_opposing_lane(node):
            _features.append(WZCharacteristics.USE_OPPOSING_LANE)

        if _is_ramp_closed(node):
            closed_ramps.append(WZCharacteristics.HAS_CLOSED_RAMPS)
            _features.append(WZCharacteristics.HAS_CLOSED_RAMPS)

        if (_is_mainline_closed(node) or
                _is_used_by_opposing_traffics(node) or
                _is_use_opposing_lane(node)):
            origin_lanes = node.lanes
            _features.append(WZCharacteristics.HAS_CLOSED_LANES)
            if _is_use_opposing_lane(node):
                open_lanes = origin_lanes - len(node.node_config.co_lanes)
            elif _is_used_by_opposing_traffics(node):
                open_lanes = origin_lanes - len(node.node_config.od_lanes)
            else:
                open_lanes = origin_lanes - len(node.node_config.closed_lanes)
            _lncfgs.append((origin_lanes, open_lanes))

        if (_is_mainline_closed(node) or
                _is_shifted(node) or
                _is_used_by_opposing_traffics(node) or
                _is_use_opposing_lane(node) or
                _is_ramp_closed(node)):

            if prev_mp != node_set.mile_point:
                n_wz += 1
            prev_mp = node_set.mile_point

            if start_mp < 0:
                start_mp = node_set.mile_point
            end_mp = node_set.mile_point

    _features = list(set(_features))
    _lncfgs = list(set(_lncfgs))


    n_closed_ramps = len(closed_ramps)

    if start_mp >= 0:
        # wz_length = (abs(end_mp - start_mp + 1)) # in mile
        wz_length = n_wz * VIRTUAL_NODE_DISTANCE # in mile
    else:
        wz_length = 0

    return wz_length, _features, _lncfgs, n_closed_ramps


def _lanecfg_map(workzones):
    """

    :type workzones: list[pyticas_tetres.ttypes.WorkZoneInfo]
    :rtype: dict[str, pyticas.ttypes.RouteConfigInfo]
    """
    map = {}
    for wzi in workzones:
        for ns in wzi.route1.cfg.node_sets:
            if ns.node1.rnode:
                map[ns.node1.rnode.name] = ns.node1.node_config
            if ns.node2.rnode:
                map[ns.node2.rnode.name] = ns.node2.node_config
    return map


def _update_lanecfg(r, lane_cfg_map):
    """

    :type r: pyticas.ttypes.Route
    :type lane_cfg_map: dict[str, pyticas.ttypes.RouteConfigInfo]
    """
    route_config.remove_virtual_nodesets(r.cfg)
    for ns in r.cfg.node_sets:
        if ns.node1.rnode:
            wz_cfg = lane_cfg_map.get(ns.node1.rnode.name, None)
            if wz_cfg:
                ns.node1.node_config = wz_cfg
        if ns.node2.rnode:
            wz_cfg = lane_cfg_map.get(ns.node2.rnode.name, None)
            if wz_cfg:
                ns.node2.node_config = wz_cfg

    route_config.organize(r.cfg)
