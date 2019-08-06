# -*- coding: utf-8 -*-

import copy
import statistics

from pyticas.moe import moe_helper
from pyticas.moe.imputation import spatial_avg

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """
    # load_data speed data
    us = moe_helper.get_speed(route.get_stations(), prd, **kwargs)
    us_results = moe_helper.add_virtual_rnodes(us, route)

    us_data = [res.data for res in us_results]
    us_data = spatial_avg.imputation(us_data)

    # make empty whole_data for STT by copying speed whole_data and reseting data
    stt_results = [res.clone() for res in us_results]
    for ridx, res in enumerate(stt_results):
        stt_results[ridx].data = [0] * len(prd.get_timeline())
        stt_results[ridx].prd = prd

    # calculate STT
    cm_data = _calculate_stt(us_data, prd.interval, **kwargs)
    for ridx, res in enumerate(stt_results):
        res.data = cm_data[ridx]

    return stt_results


def _calculate_stt(data, interval, **kwargs):
    """
     Travel Time
     Equation : TT(A and B) = SUM(Li/Ui)
       - There are i virtual stations between station A and B

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
    cm_data = copy.deepcopy(data)
    n_data = len(cm_data[0])
    for tidx in range(n_data):
        tt = 0
        for ridx, rnode_data in enumerate(data):
            if ridx == 0:
                cm_data[ridx][tidx] = 0
                continue
            tt_a_segment = vd / rnode_data[tidx] * 60
            tt += tt_a_segment
            cm_data[ridx][tidx] = tt

    return cm_data


def post_book_writer(wb, results, r, **kwargs):
    """
    :type wb: xlsxwriter.workbook.Workbook
    :type results: list[list[pyticas.ttypes.RNodeData]]
    :type r: pyticas.ttypes.Route
    :type row_cursor: int
    """
    sheet = wb.add_worksheet('Travel Time')
    sheet.write_column(1, 0, results[0][0].prd.get_timeline(without_date=True))

    tts = []
    for pidx, result in enumerate(results):
        date = result[0].prd.get_date_string()
        tt = result[-1].data
        tts.append(tt)
        sheet.write_column(0, pidx + 1, [date] + tt)

    col_avg = len(results) + 1
    sheet.write(0, col_avg, 'Average')
    row = 1
    row += 3 - [kwargs.get('print_lanes', False),
                kwargs.get('print_distance', False),
                kwargs.get('print_confidence', False)].count(False)

    n_data = len(results[0][0].data)
    for tidx in range(n_data):
        data = [tt[tidx] for tt in tts]
        avg = statistics.mean(data)
        sheet.write(row, col_avg, avg)
        row += 1


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

    writer.write_stt(os.path.join(infra.get_path('moe', create=True), 'stt.xlsx'), r, res)

    # writer.write(os.path.join(infra.get_path('moe', create=True), 'stt.xlsx'), r, res,
    #              sheet_writer=sheet_writer,
    #              post_book_writer=book_writer)
    #
    # from pyticas.moe.mods import speed
    #
    # ures1 = speed.run(r, prd1)
    # ures2 = speed.run(r, prd2)
    # ures1 = moe_helper.add_virtual_rnodes(ures1, r)
    # ures2 = moe_helper.add_virtual_rnodes(ures2, r)
    # ures = [ures1, ures2]
    # writer.write(os.path.join(infra.get_path('moe', create=True), 'u.xlsx'), r, ures)
