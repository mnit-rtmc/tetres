# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.rn.route_config import const

def get_row(node_set, max_lane1, max_lane2, max_mp):
    """
    :type node_set: pyticas.ttypes.RouteConfigNodeSet
    :param max_lane1:
    :param max_lane2:
    :param max_mp:
    :rtype: list[str]
    """
    (rc_node1, rc_node2) = (node_set.node1, node_set.node2)
    return ([node_set.mile_point] +
            _get_row_a_direction(rc_node1, max_lane1, const.DIR1_CHAR, const.DIR2_CHAR) +
            [''] +
            list(reversed(_get_row_a_direction(rc_node2, max_lane2, const.DIR2_CHAR, const.DIR1_CHAR))) +
            [max_mp - node_set.mile_point])

def _get_row_a_direction(rc_node, max_lane, dir_char, dir_char_reversed):
    """
    :type rc_node: pyticas.ttypes.RouteConfigNode
    :rtype: list[str]
    """
    data = []
    ramp_status = const.OPEN_RAMP_CHAR if rc_node.is_ramp() else ''
    if rc_node.node_config.ramp_opened == -1:
        ramp_status = const.CLOSED_RAMP_CHAR
    rnode_name =  rc_node.rnode.name if rc_node.rnode else ''
    if rc_node.rnode:
        node_name = rc_node.rnode.station_id or '{}:{}'.format('E' if rc_node.is_entrance() else 'X', rc_node.rnode.label)
    else:
        node_name = ''
    data += [''] * (max_lane - rc_node.lanes)
    data.append(ramp_status) # Ramp Status

    lane_data = [dir_char] * rc_node.lanes

    # set direction-char for lanes used by opposite direction
    for idx, ln in enumerate(rc_node.node_config.od_lanes):
        lane_data[ln-1] = dir_char_reversed

    # set closed-lane-char for closed lanes
    for idx, ln in enumerate(rc_node.node_config.closed_lanes):
        lane_data[ln-1] = lane_data[ln-1] + const.CLOSED_LANE_CHAR

    # set shifted-lane-char for shifted lanes
    for idx, ln in enumerate(rc_node.node_config.shifted_lanes):
        if rc_node.node_config.shift_dirs.get(ln) == 'L':
            lane_data[ln-1] = lane_data[ln-1] + const.LANE_SHIFTED_CHAR
        else:
            lane_data[ln-1] = const.LANE_SHIFTED_CHAR + lane_data[ln-1]

    # set lane type
    for idx, ln in enumerate(lane_data):
        if rc_node.node_config.lane_types[idx]:
            lane_data[idx] = ln + ' (' + rc_node.node_config.lane_types[idx] + ')'

    data += lane_data
    data.append(node_name) # Station ID or Ramp Name
    data.append(rnode_name) # RNode Name
    data.append(rc_node.corridor.name if rc_node.corridor else '') # Corridor Name
    return data

def col_info(node_set, max_lane1, max_lane2, max_mp):
    """
    :type node_set: pyticas.ttypes.RouteConfigNodeSet
    :type max_lane1: int
    :type max_lane2: int
    :type max_mp: float
    :rtype: dict[str, mixed]
    """
    row1 = _get_row_a_direction(node_set.node1, max_lane1, const.DIR1_CHAR, const.DIR2_CHAR)
    row2 = list(reversed(_get_row_a_direction(node_set.node2, max_lane2, const.DIR2_CHAR, const.DIR1_CHAR)))
    n_cols = 3 + len(row1) + len(row2)
    info = {'cols' : n_cols,
            'center' : len(row1) + 1,
            'ramp_status1' : 1, 'ramp_status2': n_cols-2,
            'corridor1' : len(row1),
            'corridor2' : len(row1)+2,
            'lanes1' : [], 'lanes2' : [],
            'mile_point1' : 0,
            'mile_point2' : n_cols-1}
    ln_node1 = node_set.node1
    ln_node2 = node_set.node2

    if ln_node1.is_ramp():
        info['ramp_status1'] = 1 + (max_lane1 - ln_node1.lanes)
    if ln_node2.is_ramp():
        info['ramp_status2'] = n_cols - 2 - (max_lane2 - ln_node2.lanes)

    lane_start_1 = 2 + (max_lane1 - ln_node1.lanes)
    lane_start_2 = n_cols - 2 - max_lane2
    info['lanes1'] = [ v for v in range(lane_start_1, lane_start_1+ln_node1.lanes) ]
    info['lanes2'] = [ v for v in range(lane_start_2, lane_start_2+ln_node2.lanes) ]
    info['lanes2'].reverse()
    return info

def col_info_half(rc_node, max_lane, max_mp):
    """
    :type node: pyticas.ttypes.RouteConfigNode
    :type max_lane: int
    :type max_mp: float
    :rtype: dict[str, mixed]
    """
    row1 = _get_row_a_direction(rc_node, max_lane, const.DIR1_CHAR, const.DIR2_CHAR)
    n_cols = 1 + len(row1)
    info = {'cols' : n_cols,
            'corridor' : n_cols-1,
            'ramp_status' : 1,
            'lanes' : []}

    if rc_node.is_ramp():
        info['ramp_status'] = 1 + (max_lane - rc_node.lanes)

    lane_start_1 = 2 + (max_lane - rc_node.lanes)
    info['lanes'] = [v for v in range(lane_start_1, lane_start_1 + rc_node.lanes)]
    return info