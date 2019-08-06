# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import xlsxwriter
from xlsxwriter.format import Format

from pyticas.rn.route_config import const, route_config
from pyticas.rn.route_config import node as NodeHelper
from pyticas.tool import json
from pyticas.ttypes import RouteConfig


def write(filepath, r):
    """
    :type filepath: str
    :type r: pyticas.ttypes.Route
    """
    wb = xlsxwriter.Workbook(filepath)
    write_layout_sheet(wb, r.cfg)
    write_meta_sheet(wb, r)
    wb.close()


def write_layout_sheet(wb, rc):
    """
    :type wb: xlsxwriter.Workbook
    :type rc: RouteConfig
    """
    sheet_name = const.DATA_SHEET_NAME
    ws = wb.add_worksheet(sheet_name)
    max_mp = route_config.get_max_mile_point(rc)
    rows = _get_rows(rc)
    (default_format, dir1_ml_format, dir1_ramp_format, dir2_ml_format, dir2_ramp_format) = _cell_formats(wb)
    (max_lane1, max_lane2) = (route_config.get_max_lanes(rc, 1), route_config.get_max_lanes(rc, 2))

    def _formats(node_set, ci):
        """
        :type node_set: pyticas.ttypes.RouteConfigNodeSet
        :type ci: dict
        :rtype: [int, Format]
        """
        formats = {ci['ramp_status1']: dir1_ramp_format if node_set.node1.is_ramp() else default_format,
                   ci['ramp_status2']: dir2_ramp_format if node_set.node2.is_ramp() else default_format}

        for c in ci['lanes1']:
            formats[c] = dir1_ml_format
        for c in ci['lanes2']:
            formats[c] = dir2_ml_format
        return formats

    def _format_by_value(cidx, value, ci):
        """
        :type cidx: int
        :type value: str
        :type ci: dict
        :rtype: Format
        """
        if not ci: return default_format
        is_dir1 = cidx < ci['center']
        format = formats.get(cidx, default_format)
        if is_dir1 and const.DIR2_CHAR in value:
            format = dir2_ml_format
        elif not is_dir1 and const.DIR1_CHAR in value:
            format = dir1_ml_format
        return format

    formats = {}
    col_info = None
    for ridx, row in enumerate(rows):
        if ridx != 0:
            node = rc.node_sets[ridx - 1]
            # set format dictionary by columns
            col_info = NodeHelper.col_info(node, max_lane1, max_lane2, max_mp)
            formats = _formats(node, col_info)
        for cidx, item in enumerate(row):
            format = _format_by_value(cidx, str(item), col_info)
            ws.write(ridx, cidx, item, format)


def write_meta_sheet(wb, r):
    """
    :type ws: xlsxwriter.Worksbook
    :type r: pyticas.ttypes.Route
    """
    ws_info = wb.add_worksheet(const.INFO_SHEET_NAME)
    ws_info.protect()
    ws_info.hide()

    # add route_config object as a JSON format
    # split json string to list
    meta_data = _meta_data(r)
    for ridx, data in enumerate(meta_data):
        ws_info.write(ridx, 0, data)

def _get_rows(rc, **kwargs):
    """
    :type rc: RouteConfig
    :rtype: list[str]
    """

    def _dir_string(rc, n_direction):
        """
        :type rc: RouteConfig
        :type n_direction: int
        :rtype: list[str, str]
        """
        dir_chars = ['', const.DIR1_CHAR, const.DIR2_CHAR]
        for rc_node in route_config.get_rc_nodes(rc, n_direction):
            if not rc_node.is_virtual():
                return [rc_node.rnode.corridor.dir, dir_chars[n_direction]]
        raise Exception('Wrongly configured RouteConfigNodeSet')

    (max_lane1, max_lane2) = (route_config.get_max_lanes(rc, 1), route_config.get_max_lanes(rc, 2))
    max_mp = kwargs.get('max_mp', route_config.get_max_mile_point(rc))
    rows = []
    # add header
    rows.append(['MilePoint', 'RampStatus'] +
                ['Lane' for ln in range(max_lane1)] +
                [' '.join(_dir_string(rc, 1)),
                 'RNodeName',
                 'Corridor',
                 '',
                 'Corridor',
                 'RNodeName',
                 ' '.join(reversed(_dir_string(rc, 2)))] +
                ['Lane' for ln in range(max_lane2, 0, -1)] +
                ['RampStatus', 'MilePoint'])
    # add data rows
    for node_set in rc.node_sets:
        rows.append(NodeHelper.get_row(node_set, max_lane1, max_lane2, max_mp))
    return rows


def _cell_formats(wb):
    """
    :type wb: xlsxwriter.Workbook
    :rtype: (Format, Format, Format, Format, Format)
    """
    dir1_mainline_format = wb.add_format({'bg_color': '#B0E1C0', 'locked': 0})
    dir1_mainline_format.set_align('center')
    dir1_ramp_format = wb.add_format({'bg_color': '#83B092', 'locked': 0})
    dir1_ramp_format.set_align('center')
    dir2_mainline_format = wb.add_format({'bg_color': '#D1EEF3', 'locked': 0})
    dir2_mainline_format.set_align('center')
    dir2_ramp_format = wb.add_format({'bg_color': '#A1B9BD', 'locked': 0})
    dir2_ramp_format.set_align('center')
    default_format = wb.add_format({'locked': 0})
    default_format.set_align('center')
    return default_format, dir1_mainline_format, dir1_ramp_format, dir2_mainline_format, dir2_ramp_format


def _meta_data(r):
    """
    :type r: pyticas.ttypes.Route
    :rtype: list[str]
    """
    json_str = json.dumps(r, sort_keys=True, indent=4)
    chunk_length = 10240
    meta_data = [json_str[i:i + chunk_length] for i in range(0, len(json_str), chunk_length)]
    return meta_data
