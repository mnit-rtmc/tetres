# -*- coding: utf-8 -*-

from pyticas.infra import Infra
from pyticas.moe import ent as ent_helper
from pyticas.ttypes import RNodeData, TrafficType

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def run(route, prd, **kwargs):
    """

    :type route: pyticas.ttypes.Route
    :type prd: pyticas.ttypes.Period
    :return:
    """
    infra = kwargs.get('infra', Infra.get_infra())
    kwargs['detector_checker'] = route.get_detector_checker()
    return get_total_flow(infra, route.get_rnodes(), prd, **kwargs)


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
    ent_col = len(results) + 2
    ext_col = ent_col + 1

    sheet.write_string(0, ent_col, 'Entrance Total')
    sheet.write_string(0, ext_col, 'Exit Total')

    for tidx in range(n_data):
        ent_data = [rnd.data[tidx] for ridx, rnd in enumerate(results)
                    if rnd.data[tidx] > 0 and not isinstance(rnd.rnode, str) and rnd.rnode.is_entrance()]

        ext_data = [rnd.data[tidx] for ridx, rnd in enumerate(results)
                    if rnd.data[tidx] > 0 and not isinstance(rnd.rnode, str) and rnd.rnode.is_exit()]

        ent_total = sum(ent_data)
        ext_total = sum(ext_data)

        row = tidx + rows_before_data
        sheet.write(row, ent_col, ent_total)
        sheet.write(row, ext_col, ext_total)


def post_book_writer(wb, results, r, **kwargs):
    """
    :type wb: xlsxwriter.workbook.Workbook
    :type results: list[list[pyticas.ttypes.RNodeData]]
    :type r: pyticas.ttypes.Route
    :type row_cursor: int
    """
    sheet_summary = wb.add_worksheet('Summary')
    sheet_summary.write_column(1, 0, results[0][0].prd.get_timeline(without_date=True))

    sheet_ent = wb.add_worksheet('Sum_Entrance')
    sheet_ent.write_column(1, 0, results[0][0].prd.get_timeline(without_date=True))

    sheet_ext = wb.add_worksheet('Sum_Exit')
    sheet_ext.write_column(1, 0, results[0][0].prd.get_timeline(without_date=True))

    n_data = len(results[0][0].data)
    for pidx, result in enumerate(results):
        ent_totals_a_day = []
        ext_totals_a_day = []
        for tidx in range(n_data):
            ent_data = [rnd.data[tidx] for ridx, rnd in enumerate(result)
                        if rnd.data[tidx] > 0 and not isinstance(rnd.rnode, str) and rnd.rnode.is_entrance()]

            ext_data = [rnd.data[tidx] for ridx, rnd in enumerate(result)
                        if rnd.data[tidx] > 0 and not isinstance(rnd.rnode, str) and rnd.rnode.is_exit()]

            ent_total = sum(ent_data)
            ext_total = sum(ext_data)
            ent_totals_a_day.append(ent_total)
            ext_totals_a_day.append(ext_total)

        date = result[0].prd.get_date_string()
        sheet_summary.write_column(0, pidx * 2 + 1, ['%s_Entrance' % date] + ent_totals_a_day)
        sheet_summary.write_column(0, pidx * 2 + 2, ['%s_Exit' % date] + ext_totals_a_day)

        sheet_ent.write_column(0, pidx + 1, [date] + ent_totals_a_day)
        sheet_ext.write_column(0, pidx + 1, [date] + ext_totals_a_day)


def get_total_flow(infra, rnode_list, prd, **kwargs):
    """

    :typoe infra: Infra
    :type rnode_list: list[pyticas.ttypes.RNodeObject]
    :type prd: Period
    :rtype: list[RNodeData]
    """
    dc = kwargs.get('detector_checker', None)
    infra = kwargs.get('infra', Infra.get_infra())
    results = []
    for rnode in rnode_list:
        res = None
        if rnode.is_station():
            res = infra.rdr.get_total_flow(rnode, prd, dc)
        elif rnode.is_entrance():
            res = _tq_entrance(infra, rnode, prd, dc=dc)
        elif rnode.is_exit():
            res = _tq_exit(infra, rnode, prd, dc=dc)
        else:
            continue
        results.append(res)
    return results


def _tq_entrance(infra, ent, prd, **kwargs):
    """

    :typoe infra: Infra
    :type ent: pyticas.ttypes.RNodeObject
    :type prd: Period
    :rtype: RNodeData
    """
    flows = ent_helper.ramp_passage_flow(ent, prd)
    rnode_data_obj = RNodeData(ent, prd, TrafficType.flow)
    dets = ent.detectors
    rnode_data_obj.data = flows
    rnode_data_obj.detector_data = {det.name: [] for idx, det in enumerate(dets)}
    rnode_data_obj.detector_names = [det.name for det in dets]
    rnode_data_obj.detectors = dets
    rnode_data_obj.lanes = 1
    rnode_data_obj.missing_lanes = 0
    return rnode_data_obj


def _tq_exit(infra, ext, prd, **kwargs):
    """

    :typoe infra: Infra
    :type ext: RNodeObject
    :type prd: Period
    :rtype: RNodeData
    """
    return infra.rdr.get_total_flow(ext, prd)


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

    writer.write_mrf(os.path.join(infra.get_path('moe', create=True), 'mrf.xlsx'), r, res)
