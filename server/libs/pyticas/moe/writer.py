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


def write(filepath, r, results, **kwargs):
    """

    :type filepath: str
    :type r: pyticas.ttypes.Route
    :type results: Union(list[RNodeData], list[list[RNodeData]])
    :keyword print_distance: bool, print accumulated distance into spread sheet if True
    :keyword print_confidence: bool, print confidence level of data into spread sheet if True
    :keyword print_average: bool, print average of data column into spread sheet if True
    :type **kwargs: dict
    """
    wb = xlsxwriter.Workbook(filepath)
    route_config = r.cfg if r.cfg else rc.route_config.create_route_config(r.rnodes, infra_cfg_date=r.infra_cfg_date)

    # add lane configuration sheet
    rc.writer.write_layout_sheet(wb, route_config)

    # call additional book_writer (pre)
    pre_book_writer = kwargs.get('pre_book_writer', None)
    if pre_book_writer:
        assert callable(pre_book_writer)
        if isinstance(results[0], RNodeData):
            pre_book_writer(wb, [results], r, **kwargs)
        else:
            pre_book_writer(wb, results, r, **kwargs)

    # add data sheets
    if isinstance(results[0], RNodeData):
        _add_sheet(wb, results, r, **kwargs)
    else:
        for res in results:
            _add_sheet(wb, res, r, **kwargs)


    # call additional book_writer (post)
    post_book_writer = kwargs.get('post_book_writer', None)
    if post_book_writer:
        assert callable(post_book_writer)
        if isinstance(results[0], RNodeData):
            post_book_writer(wb, [results], r, **kwargs)
        else:
            post_book_writer(wb, results, r, **kwargs)

    # add route information sheet (hidden sheet)
    rc.writer.write_meta_sheet(wb, r)

    wb.close()

def _add_sheet(wb, results, r, **kwargs):
    """
    :type wb: Workbook
    :type results: list[RNodeData]
    :type r: pyticas.ttypes.Route
    :type kwargs: dict
    """
    missing_data = kwargs.get('missing_data', cfg.MISSING_VALUE)
    prd = results[0].prd
    timeline = prd.get_timeline()
    n_data = len(timeline)
    sheet = wb.add_worksheet(prd.get_date_string())


    # print rnode names
    sheet.write_row(row=0, col=1, data=[ rnd.get_title(**kwargs) for rnd in results ])

    data_start_row = 1
    rows_before_data = 1
    rows_after_data = 0

    # print used lane information
    if kwargs.get('print_lanes', True):
        rows_before_data += 1
        wrap = wb.add_format({'text_wrap': True})
        wrap.set_align('top')
        sheet.write_string(data_start_row, 0, 'Lane:Detector', wrap)
        sheet.write_row(row=data_start_row, col=1, data=moe_helper.used_lanes(results, r), cell_format=wrap)
        data_start_row += 1

    # print accumulated distance from upstream
    if kwargs.get('print_distance', True):
        rows_before_data += 1
        sheet.write_string(data_start_row, 0, 'Distance')
        sheet.write_row(row=data_start_row, col=1, data=moe_helper.accumulated_distances(results, r))
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
        sheet.write_column(row=data_start_row, col=ridx+1, data=rnd.data)

    data_start_row = len(results[0].data) + data_start_row

    # print average
    if kwargs.get('print_average', False):
        rows_after_data += 1
        sheet.write_string(data_start_row, 0, 'Average')
        for ridx, rnd in enumerate(results):
            rnode_data = [ v for v in rnd.data if v and not isinstance(v, str) and v > 0 ]
            if rnode_data:
                avg = sum(rnode_data) / len(rnode_data)
            else:
                avg = missing_data
            sheet.write_number(data_start_row, ridx+1, avg)
        data_start_row += 1

    # call additional sheet_writer
    sheet_writer = kwargs.get('sheet_writer', None)
    if sheet_writer:
        assert callable(sheet_writer)
        sheet_writer(wb, sheet, results, r, n_data, rows_before_data, rows_after_data, **kwargs)

    sheets = wb.worksheets()
    if len(sheets) >= 2:
        sheets[1].activate()


def write_cm(filepath, r, results, **kwargs):
    """

    :type filepath: str
    :type r: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """
    from pyticas.moe.mods.cm import sheet_writer, post_book_writer
    write(filepath, r, results, sheet_writer=sheet_writer, post_book_writer=post_book_writer, **kwargs)

def write_cmh(filepath, r, results, **kwargs):
    """

    :type filepath: str
    :type r: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """
    from pyticas.moe.mods.cmh import sheet_writer, post_book_writer
    write(filepath, r, results, sheet_writer=sheet_writer, post_book_writer=post_book_writer, **kwargs)

def write_stt(filepath, r, results, **kwargs):
    """

    :type filepath: str
    :type r: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """
    from pyticas.moe.mods.stt import post_book_writer
    write(filepath, r, results, post_book_writer=post_book_writer, **kwargs)

def write_sv(filepath, r, results, **kwargs):
    """

    :type filepath: str
    :type r: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """
    from pyticas.moe.mods.sv import pre_book_writer, sheet_writer
    write(filepath, r, results, sheet_writer=sheet_writer, pre_book_writer=pre_book_writer, **kwargs)


def write_mrf(filepath, r, results, **kwargs):
    """

    :type filepath: str
    :type r: pyticas.ttypes.Route
    :type results: list[RNodeData]
    :type whole_data: list[list[RNodeData]]
    :type kwargs: dict
    """
    from pyticas.moe.mods.mrf import post_book_writer, sheet_writer
    write(filepath, r, results, print_type=True, sheet_writer=sheet_writer, post_book_writer=post_book_writer, **kwargs)