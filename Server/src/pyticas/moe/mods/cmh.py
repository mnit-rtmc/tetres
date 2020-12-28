# -*- coding: utf-8 -*-

import copy
from collections import defaultdict

from pyticas.moe import moe_helper
from pyticas.moe.imputation import spatial_avg

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.util.systemconfig import get_system_config_info


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """
    # load_data speed data
    moe_congestion_threshold_speed = kwargs.pop("moe_congestion_threshold_speed",
                                                get_system_config_info().moe_congestion_threshold_speed)
    us = moe_helper.get_speed(route.get_stations(), prd, **kwargs)
    us_results = moe_helper.add_virtual_rnodes(us, route)

    us_data = [res.data for res in us_results]
    us_data = spatial_avg.imputation(us_data)

    # make empty whole_data for congested miles by copying speed whole_data and reseting data
    cmh_results = [res.clone() for res in us_results]
    for ridx, res in enumerate(cmh_results):
        cmh_results[ridx].data = [0] * len(prd.get_timeline())
        cmh_results[ridx].prd = prd

    # calculate CMH
    cm_data = _calculate_cmh(us_data, prd.interval, moe_congestion_threshold_speed, **kwargs)
    for ridx, res in enumerate(cmh_results):
        res.data = cm_data[ridx]

    return cmh_results


def calculate_cmh_dynamically(data, interval, moe_congestion_threshold_speed, **kwargs):
    try:
        vd = moe_helper.VIRTUAL_RNODE_DISTANCE
        cmh_unit = (interval / 3600.0) * vd
        cmh_data = []
        for index, each_station_speed_data in enumerate(data['speed']):
            value = 0 if each_station_speed_data >= moe_congestion_threshold_speed or each_station_speed_data < 0 else cmh_unit
            if value < 0:
                value = 0
            cmh_data.append(value)
        cmh_data[-1] = 0

        return sum(cmh_data)
    except Exception as e:
        from pyticas_tetres.logger import getLogger
        logger = getLogger(__name__)
        logger.warning('fail to calculate calculate cmh dynamically. Error: {}'.format(e))
        return 0


def _calculate_cmh(data, interval, moe_congestion_threshold_speed, **kwargs):
    """
     Congested Miles*Hours (Miles, %)
     => CM(j): Sum of freeway segments whose speed values are less than or equal to 'User specified threshold'
     Equation : CM(j) = SUM([L(i) | ui less than threshold])

    :param data: list of speed data list for each rnode.
                 e.g. data = [
                                [ u(i,t), u(i,t+1), u(i,t+2) .. ],
                                [ u(i+1,t), u(i+1,t+1), u(i+1,t+2) .. ],
                                [ u(i+2,t), u(i+2,t+1), u(i+2,t+2) .. ],
                                ,,,
                            ]

    :type data: list[list[float]]
    :param interval: data interval in second
    :type interval: int
    :type kwargs: dict
    :return:
    """
    vd = moe_helper.VIRTUAL_RNODE_DISTANCE
    cmh_unit = (interval / 3600.0) * vd

    cmh_data = copy.deepcopy(data)
    for ridx, rnode_data in enumerate(data):
        for tidx, value in enumerate(rnode_data):
            cmh_data[ridx][tidx] = 0 if value >= moe_congestion_threshold_speed or value < 0 else cmh_unit
    cmh_data[-1] = ['-'] * len(cmh_data[-1])

    return cmh_data


def sheet_writer(wb, sheet, results, r, n_data, rows_before_data, rows_after_data, **kwargs):
    """
    :type wb: Workbook
    :type sheet: xlsxwriter.workbook.Worksheet
    :type results: list[pyticas.ttypes.RNodeData]
    :type r: pyticas.ttypes.Route
    :type n_data: int
    :type rows_before_data: int
    :type rows_after_data: int
    """
    n_nodes = len(results)

    tcm_row = rows_before_data + n_data + rows_after_data
    tcmp_row = tcm_row + 1
    sheet.write_string(tcm_row, 0, 'TCMH')
    sheet.write_string(tcmp_row, 0, 'TCMH(%)')
    start_col = 1
    for ridx, rnd in enumerate(results):
        # last rnode must be excepted because TCMP can exceed 100% if the last station is included
        if ridx == n_nodes - 1:
            break
        congested = [v for tidx, v in enumerate(rnd.data) if v and not isinstance(v, str) and v > 0]
        tcm = sum(congested)
        tcmp = len(congested) * 100 / n_data
        sheet.write_number(tcm_row, ridx + start_col, tcm)
        sheet.write_number(tcmp_row, ridx + start_col, tcmp)

    tcm_col = n_nodes + 1
    tcmp_col = tcm_col + 1
    sheet.write_string(0, tcm_col, 'TCMH')
    sheet.write_string(0, tcmp_col, 'TCMH(%)')

    acc_distances = moe_helper.accumulated_distances(results, r)

    for tidx in range(n_data):
        # accumulative distances can be same when distance between two stations is less than 0.1 mile
        congested = [acc_distances[ridx] for ridx, rnd in enumerate(results)
                     if rnd.data[tidx] and not isinstance(rnd.data[tidx], str) and rnd.data[tidx] > 0]
        congested = list(set(congested))
        n_congested = len(congested)
        tcm = n_congested * 0.1
        tcmp = n_congested * 100.0 / (n_nodes - 1)
        sheet.write_number(rows_before_data + tidx, tcm_col, tcm)
        sheet.write_number(rows_before_data + tidx, tcmp_col, tcmp)


def post_book_writer(wb, results, r, **kwargs):
    """
    :type wb: xlsxwriter.workbook.Workbook
    :type results: list[list[pyticas.ttypes.RNodeData]]
    :type r: pyticas.ttypes.Route
    :type row_cursor: int
    """

    def _find_str(sheet, idx):
        for k, v in sheet.str_table.string_table.items():
            if v == idx:
                return k
        return 'NA'

    def _to_list(sheet):
        data = defaultdict(dict)
        maxrows = 0
        maxcols = 0
        for row, v in sheet.table.items():
            for col, cell_value in v.items():
                if hasattr(cell_value, 'string'):
                    vv = _find_str(sheet, cell_value.string)
                elif hasattr(cell_value, 'number'):
                    vv = cell_value.number
                else:
                    vv = ''
                data[row][col] = vv
                maxrows = max(maxrows, row)
                maxcols = max(maxcols, col)
        return data, maxrows + 1, maxcols + 1

    data = []
    for sidx, sheet in enumerate(wb.worksheets()):
        if sidx == 0:
            continue
        tcms_a_sheet = []
        sheet_data, nrows, ncols = _to_list(sheet)
        tcm_col = ncols - 2
        for row in sheet_data.keys():
            if row == 0 or not tcm_col in sheet_data[row]:
                continue
            v = sheet_data[row][tcm_col]
            tcms_a_sheet.append(v)
        data.append((sheet.name, tcms_a_sheet))

    prd = results[0][0].prd
    timeline = prd.get_timeline(without_date=True)

    sheet = wb.add_worksheet('Congested MilesxHours')
    sheet.write_column(row=1, col=0, data=timeline + ['TCMH'])

    col = 1
    for tcm_data in data:
        tcm = sum(tcm_data[1])
        sheet.write_column(row=0, col=col, data=[tcm_data[0]] + tcm_data[1] + [tcm])
        col += 1

    avg_data = []
    for row in range(len(timeline)):
        tdata = [tcm_data[1][row] for tcm_data in data]
        avg_data.append(sum(tdata) / len(tdata))
    sheet.write_column(row=0, col=col, data=['Average'] + avg_data + [sum(avg_data)])


if __name__ == '__main__':
    import os
    from pyticas.infra import Infra
    from pyticas import route
    from pyticas import period
    from pyticas.moe import writer

    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../data'))
    Infra.initialize(data_path)
    infra = Infra.load_infra()
    r = route.load_route_by_name('Route I-494 WB')
    prd1 = period.create_period_from_string('2016-05-17 06:00:00', '2016-05-17 09:00:00', 300)
    prd2 = period.create_period_from_string('2016-05-18 06:00:00', '2016-05-18 09:00:00', 300)

    res1 = run(r, prd1)
    res2 = run(r, prd2)
    res = [res1, res2]

    writer.write_cmh(os.path.join(infra.get_path('moe', create=True), 'cmh.xlsx'), r, res)
