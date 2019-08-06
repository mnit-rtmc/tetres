# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import xlrd
from xlrd.book import Book

from pyticas.rn.route_config import const, route_config
from pyticas.rn.route_config import node as NodeHelper
from pyticas.tool import json
from pyticas.ttypes import RouteConfig, RouteConfigInfo


def load(filepath, **kwargs):
    """
    :type filepath: str
    :rtype: pyticas.ttypes.Route
    """
    wb = xlrd.open_workbook(filepath)
    return _load(wb)


def load_from_contents(file_contents, **kwargs):
    """
    :type file_contents: str
    :rtype: pyticas.ttypes.Route
    """
    wb = xlrd.open_workbook(file_contents=file_contents)
    return _load(wb)


def _load(wb):
    info_ws = wb.sheet_by_name(const.INFO_SHEET_NAME)
    meta_data = []
    for ridx in range(info_ws.nrows):
        value = str(info_ws.cell(ridx, 0).value).strip()
        if value:
            meta_data.append(value)
    r = json.loads(''.join(meta_data))
    _read_lane_configs_from_sheet(wb, r.cfg, const.DATA_SHEET_NAME)
    return r


def _read_lane_configs_from_sheet(wb, rc, sheet_name):
    """

    :type wb: Book
    :type rc: RouteConfig
    :return:
    """
    ws = wb.sheet_by_name(sheet_name)
    (max_lanes1, max_lanes2) = (route_config.get_max_lanes(rc, 1), route_config.get_max_lanes(rc, 2))
    max_mp = route_config.get_max_mile_point(rc)
    for ridx in range(1, ws.nrows):
        row = [ c.value for c in ws.row(ridx) ]
        node_set = rc.node_sets[ridx - 1]

        col_info1 = NodeHelper.col_info_half(node_set.node1, max_lanes1, max_mp)
        _set_data_to_ln_node(node_set.node1, col_info1, row, max_lanes1, const.DIR1_CHAR, const.DIR2_CHAR)

        col_info2 = NodeHelper.col_info_half(node_set.node2, max_lanes2, max_mp)
        _set_data_to_ln_node(node_set.node2, col_info2, list(reversed(row)), max_lanes2, const.DIR2_CHAR, const.DIR1_CHAR)

        node_set.node1.node_config.co_lanes = list(node_set.node2.node_config.od_lanes)
        node_set.node2.node_config.co_lanes = list(node_set.node1.node_config.od_lanes)

def _set_data_to_ln_node(rc_node, col_info, row, max_lanes, dir_char, dir_char_reverse):
    """
    :type rc_node: RouteConfigNode
    :type col_info: dict
    :type row: list[str]
    :type max_lanes: int
    :type dir_char: str
    :type dir_char_reverse: str
    :return:
    """
    nInfo = RouteConfigInfo()
    nInfo.lane_types = list(rc_node.node_config.lane_types)

    ramp_status_col = col_info['ramp_status']
    ramp_opened = 1 if const.CLOSED_RAMP_CHAR not in row[ramp_status_col] else -1
    if rc_node.is_virtual() or rc_node.is_station():
        ramp_opened = 0
    closed_lanes = []
    used_by_opposite_direction = []
    shifted_lanes = []
    shift_direction = {}

    if rc_node.is_virtual():
        max_lane_range = range(col_info['ramp_status']+1, col_info['ramp_status']+1 + max_lanes)
        old_lanes = rc_node.lanes
        rc_node.lanes = len([v for v in max_lane_range if str(row[v]).strip()])
        if old_lanes < rc_node.lanes:
            nInfo.lane_types = ([''] * (rc_node.lanes - old_lanes)) + nInfo.lane_types
        elif old_lanes > rc_node.lanes:
            nInfo.lane_types = nInfo.lane_types[:rc_node.lanes]

    lane = 1
    col_lane1 = col_info['lanes'][-1] - rc_node.lanes + 1
    for cidx in range(col_lane1, col_lane1+rc_node.lanes):
        value = str(row[cidx])

        # virtual node and no value in the cell
        if not rc_node.rnode and not value:
            if lane in closed_lanes: closed_lanes.remove(lane)
            if lane in shift_direction.keys(): del shift_direction[lane]
            if lane in used_by_opposite_direction: used_by_opposite_direction.remove(lane)
            continue
        elif not value:
            continue

        if const.CLOSED_LANE_CHAR in value:
            closed_lanes.append(lane)
        if const.LANE_SHIFTED_CHAR in value:
            shift_direction[lane] = _shift_direction(value, 1)
            shifted_lanes.append(lane)
        if dir_char_reverse in value:
            used_by_opposite_direction.append(lane)
        lane += 1

    nInfo.ramp_opened = ramp_opened
    nInfo.closed_lanes = closed_lanes
    nInfo.od_lanes = used_by_opposite_direction
    nInfo.shifted_lanes = shifted_lanes
    nInfo.shift_dirs = shift_direction
    rc_node.node_config = nInfo

def _shift_direction(value, dir):
    """
    :type value: str
    :type dir: int
    :rtype: str:
    """

    sidx = value.index(const.LANE_SHIFTED_CHAR)
    dir1_idx = dir2_idx = -1
    try:
        dir1_idx = value.index(const.DIR1_CHAR)
    except ValueError:
        pass

    try:
        dir2_idx = value.index(const.DIR2_CHAR)
    except ValueError:
        pass

    if dir1_idx < 0 and dir2_idx < 0:
        return ''

    dir_idx = max(dir1_idx, dir2_idx)

    if dir == 1:
        return 'R' if sidx < dir_idx else 'L'
    else:
        return 'R' if sidx > dir_idx else 'L'

