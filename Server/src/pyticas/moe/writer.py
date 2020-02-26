# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

"""
Result Writer Module for Traffic Measurement
"""

import xlsxwriter
from xlsxwriter.workbook import Workbook

from pyticas import cfg
from pyticas import rc
from pyticas.moe import moe_helper
from pyticas.ttypes import RNodeData


def write(_filepath, _route, _results, _work_book: xlsxwriter.Workbook = None, **kwargs):
    """

    :param _work_book:
    :type _filepath: str
    :type _route: pyticas.ttypes.Route
    :type _results: Union(list[RNodeData], list[list[RNodeData]])
    :keyword print_distance: bool, print accumulated distance into spread sheet if True
    :keyword print_confidence: bool, print confidence level of data into spread sheet if True
    :keyword print_average: bool, print average of data column into spread sheet if True
    :type **kwargs: dict
    """

    temp_work_book = _work_book

    if temp_work_book is None:
        temp_work_book = xlsxwriter.Workbook(_filepath)

    route_config = _route.cfg if _route.cfg \
        else rc.route_config.create_route_config(_route.rnodes, infra_cfg_date=_route.infra_cfg_date)

    # add lane configuration sheet
    rc.writer.write_layout_sheet(temp_work_book, route_config)

    # call additional book_writer (pre)
    pre_book_writer = kwargs.get('pre_book_writer', None)
    if pre_book_writer:
        assert callable(pre_book_writer)
        if isinstance(_results[0], RNodeData):
            pre_book_writer(temp_work_book, [_results], _route, **kwargs)
        else:
            pre_book_writer(temp_work_book, _results, _route, **kwargs)

    # add data sheets
    if isinstance(_results[0], RNodeData):
        _add_sheet(temp_work_book, _results, _route, **kwargs)
    else:
        for res in _results:
            _add_sheet(temp_work_book, res, _route, **kwargs)

    # call additional book_writer (post)
    post_book_writer = kwargs.get('post_book_writer', None)
    if post_book_writer:
        assert callable(post_book_writer)
        if isinstance(_results[0], RNodeData):
            post_book_writer(temp_work_book, [_results], _route, **kwargs)
        else:
            post_book_writer(temp_work_book, _results, _route, **kwargs)

    # add route information sheet (hidden sheet)
    rc.writer.write_meta_sheet(temp_work_book, _route)

    if _work_book is None:
        temp_work_book.close()


def _add_sheet(wb, results, _route, **kwargs):
    """
    :type wb: Workbook
    :type results: list[RNodeData]
    :type _route: pyticas.ttypes.Route
    :type kwargs: dict
    """
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)
    prd = results[0].prd
    timeline = prd.get_timeline()
    n_data = len(timeline)
    sheet = wb.add_worksheet(prd.get_date_string())

    # print rnode names
    sheet.write_row(row=0, col=1, data=[rnd.get_title(**kwargs) for rnd in results])

    data_start_row = 1
    rows_before_data = 1
    rows_after_data = 0

    # print used lane information
    if kwargs.get('print_lanes', True):
        rows_before_data += 1
        wrap = wb.add_format({'text_wrap': True})
        wrap.set_align('top')
        sheet.write_string(data_start_row, 0, 'Lane:Detector', wrap)
        sheet.write_row(row=data_start_row, col=1, data=moe_helper.used_lanes(results, _route), cell_format=wrap)
        data_start_row += 1

    # print accumulated distance from upstream
    if kwargs.get('print_distance', True):
        rows_before_data += 1
        sheet.write_string(data_start_row, 0, 'Distance')
        sheet.write_row(row=data_start_row, col=1, data=moe_helper.accumulated_distances(results, _route))
        data_start_row += 1

    # print confidence level (%)
    if kwargs.get('print_confidence', True):
        rows_before_data += 1
        sheet.write_string(data_start_row, 0, 'Confidence')
        sheet.write_row(row=data_start_row, col=1, data=moe_helper.confidences(results))
        data_start_row += 1

    # print timeline
    sheet.write_column(row=data_start_row, col=0, data=timeline)

    # print data
    for ridx, rnd in enumerate(results):
        sheet.write_column(row=data_start_row, col=ridx + 1, data=rnd.data)

    data_start_row = len(results[0].data) + data_start_row

    # print average
    if kwargs.get('print_average', False):
        rows_after_data += 1
        sheet.write_string(data_start_row, 0, 'Average')
        for ridx, rnd in enumerate(results):
            rnode_data = [v for v in rnd.data if v and not isinstance(v, str) and v > 0]
            if rnode_data:
                avg = sum(rnode_data) / len(rnode_data)
            else:
                avg = missing_data
            sheet.write_number(data_start_row, ridx + 1, avg)
        data_start_row += 1

    # call additional sheet_writer
    sheet_writer = kwargs.get('sheet_writer', None)
    if sheet_writer:
        assert callable(sheet_writer)
        sheet_writer(wb, sheet, results, _route, n_data, rows_before_data, rows_after_data, **kwargs)

    sheets = wb.worksheets()
    if len(sheets) >= 2:
        sheets[1].activate()


def write_cm(filepath, _route, results, work_book: xlsxwriter.Workbook = None, **kwargs):
    """

    :param filepath: str
    :param work_book: xlsxwriter.Workbook
    :type _route: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """

    # faverolles 1/22/2020: Added Workbook parameter for use by pyticas_tetres.est.report.report_helper
    from pyticas.moe.mods.cm import sheet_writer, post_book_writer
    write(_filepath=filepath, _route=_route, _results=results,
          sheet_writer=sheet_writer, post_book_writer=post_book_writer,
          _work_book=work_book, **kwargs)


def write_cmh(filepath, _route, results, work_book: xlsxwriter.Workbook = None, **kwargs):
    """
    :param work_book:
    :type filepath:
    :type _route: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """
    from pyticas.moe.mods.cmh import sheet_writer, post_book_writer
    write(_filepath=filepath, _route=_route, _results=results,
          sheet_writer=sheet_writer, post_book_writer=post_book_writer,
          _work_book=work_book, **kwargs)


def write_sv(filepath, _route, results, work_book: xlsxwriter.Workbook = None, **kwargs):
    """

    :param work_book:
    :type filepath:
    :type _route: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """
    from pyticas.moe.mods.sv import pre_book_writer, sheet_writer
    write(_filepath=filepath, _route=_route, _results=results,
          sheet_writer=sheet_writer, pre_book_writer=pre_book_writer,
          _work_book=work_book, **kwargs)


def write_stt(filepath, _route, results, work_book: xlsxwriter.Workbook = None, **kwargs):
    """

    :param work_book:
    :type filepath: str
    :type _route: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """
    from pyticas.moe.mods.stt import post_book_writer
    # faverolles 1/22/2020 NOTE: Why no pre_book writer=pre_book_writer
    write(filepath, _route, results, post_book_writer=post_book_writer,
          _work_book=work_book, **kwargs)


def write_mrf(filepath, _route, results, work_book: xlsxwriter.Workbook = None, **kwargs):
    """

    :param work_book:
    :type filepath: str
    :type _route: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """
    from pyticas.moe.mods.mrf import post_book_writer, sheet_writer
    write(filepath, _route, results, print_type=True, sheet_writer=sheet_writer,
          post_book_writer=post_book_writer, _work_book=work_book, **kwargs)
