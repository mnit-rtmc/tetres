# -*- coding: utf-8 -*-

import statistics

from pyticas.moe import moe_helper

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :rtype: list[RNodeData]
    """
    # load_data speed data
    return moe_helper.get_speed(route.get_stations(), prd, **kwargs)


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
    var_col = len(results) + 2
    avg_col = var_col + 1
    max_col = avg_col + 1
    min_col = max_col + 1
    diff_col = min_col + 1

    sheet.write_string(0, var_col, 'Variance')
    sheet.write_string(0, avg_col, 'Average')
    sheet.write_string(0, max_col, 'Maximum')
    sheet.write_string(0, min_col, 'Minimum')
    sheet.write_string(0, diff_col, 'Diff (Max-Min)')

    for tidx in range(n_data):
        data = [rnd.data[tidx] for ridx, rnd in enumerate(results) if rnd.data[tidx] > 0]
        avg = statistics.mean(data)
        variance = statistics.variance(data)
        max_u = max(data)
        min_u = min(data)

        row = tidx + rows_before_data
        sheet.write(row, var_col, variance)
        sheet.write(row, avg_col, avg)
        sheet.write(row, max_col, max_u)
        sheet.write(row, min_col, min_u)
        sheet.write(row, diff_col, max_u - min_u)


def pre_book_writer(wb, results, r, **kwargs):
    """
    :type wb: xlsxwriter.workbook.Workbook
    :type results: list[list[pyticas.ttypes.RNodeData]]
    :type r: pyticas.ttypes.Route
    :type row_cursor: int
    """

    sheets = []
    for sheet_name in ['variance', 'average', 'max', 'min', 'diff']:
        sheet = wb.add_worksheet(sheet_name)
        sheet.write_column(1, 0, results[0][0].prd.get_timeline(without_date=True))
        sheets.append(sheet)

    for pidx, result in enumerate(results):
        n_data = len(result[0].data)
        vars_a_day = []
        avgs_a_day = []
        maxs_a_day = []
        mins_a_day = []
        diffs_a_day = []
        for tidx in range(n_data):
            data = [rnd.data[tidx] for ridx, rnd in enumerate(result) if rnd.data[tidx] > 0]
            max_u = max(data)
            min_u = min(data)
            vars_a_day.append(statistics.variance(data))
            avgs_a_day.append(statistics.mean(data))
            maxs_a_day.append(max_u)
            mins_a_day.append(min_u)
            diffs_a_day.append(max_u - min_u)

        date = result[0].prd.get_date_string()
        sheet_data = [vars_a_day, avgs_a_day, maxs_a_day, mins_a_day, diffs_a_day]
        for sidx, sheet in enumerate(sheets):
            sheet.write_column(0, pidx + 1, [date] + sheet_data[sidx])


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

    writer.write_sv(os.path.join(infra.get_path('moe', create=True), 'sv.xlsx'), r, res)
