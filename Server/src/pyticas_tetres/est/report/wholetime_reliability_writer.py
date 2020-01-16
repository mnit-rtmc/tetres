# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os

import xlsxwriter

from pyticas.tool import tb
from pyticas_tetres.est.helper import util
from pyticas_tetres.est.report import report_helper
from pyticas_tetres.logger import getLogger


MISSING_VALUE = ''

def write(uid, eparam, operating_conditions, whole, yearly, monthly, daily):
    """
    :type uid: str
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type whole: list[dict]
    :type yearly: list[(list[dict], list[int])]
    :type monthly: list[(list[dict], list[[int, int]])]
    :type daily: list[(list[dict], list[datetime.date])]
    """
    output_dir = util.output_path('%s/%s - %s' % (uid, eparam.travel_time_route.corridor, eparam.travel_time_route.name))

    # result file
    output_file = os.path.join(output_dir, 'reliabilities (whole-time-period).xlsx')

    wb = xlsxwriter.Workbook(output_file)

    try:
        report_helper.write_operating_condition_info_sheet(eparam, wb)
    except Exception as ex:
        getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    try:
        _write_whole_result_sheet(eparam, operating_conditions, wb, whole)
    except Exception as ex:
        getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    if yearly:
        try:
            _write_yearly_result_sheet(eparam, operating_conditions, wb, yearly)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    if monthly:
        try:
            _write_monthly_result_sheet(eparam, operating_conditions, wb, monthly)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    if daily:
        try:
            _write_daily_result_sheet(eparam, operating_conditions, wb, daily)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    wb.close()


def _write_whole_result_sheet(eparam, operating_conditions, wb, results):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[dict]
    """
    ws = wb.add_worksheet('reliabilities')
    row = 0
    is_head_written = False
    for idx, ef in enumerate(eparam.operating_conditions):
        head, result_row = report_helper.get_result_list(results[idx], missing_value=MISSING_VALUE)
        if not is_head_written:
            _, head = report_helper.get_indice_names()
            is_head_written = True
            ws.write_row(0, 0, ['OC Index', 'OC Name'] + head)
            row += 1
        if not result_row:
            result_row = [-1]*len(head)
        result_row = [ v if v else MISSING_VALUE for v in result_row ]
        ws.write_row(row, 0, [idx, ef.name] + result_row)
        row += 1


def _write_yearly_result_sheet(eparam, operating_conditions, wb, results):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[(list[dict], list[int])]
    :type dates: list[datetime.date]
    """
    for idx, ef in enumerate(eparam.operating_conditions):
        ws = wb.add_worksheet('yearly (OC=%d)' % idx)
        yearly_results, years = results[idx]
        if not yearly_results:
            continue

        row = 0
        is_head_written = False
        for didx, a_result in enumerate(yearly_results):
            head, result_row = report_helper.get_result_list(a_result, missing_value=MISSING_VALUE)
            if not is_head_written:
                _, head = report_helper.get_indice_names()
                is_head_written = True
                ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
                ws.write_row(1, 0, ['Year'] + head)
                if not row:
                    row += 2
            ws.write_row(row, 0, [years[didx]] + result_row)
            row += 1


def _write_monthly_result_sheet(eparam, ext_filter_groups, wb, results):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type ext_filter_groups: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[(list[dict], list[[int, int])]
    :type dates: list[datetime.date]
    """
    for idx, ef in enumerate(eparam.operating_conditions):
        ws = wb.add_worksheet('monthly (OC=%d)' % idx)
        monthly_results, months = results[idx]
        if not monthly_results:
            continue

        row = 0
        is_head_written = False
        for didx, a_result in enumerate(monthly_results):
            head, result_row = report_helper.get_result_list(a_result, missing_value=MISSING_VALUE)
            if not is_head_written:
                _, head = report_helper.get_indice_names()
                is_head_written = True
                ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
                ws.write_row(1, 0, ['Month'] + head)
                if not row:
                    row += 2
            ws.write_row(row, 0, ['%04d-%02d' % (months[didx][0], months[didx][1])] + result_row)
            row += 1


def _write_daily_result_sheet(eparam, ext_filter_groups, wb, results):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type ext_filter_groups: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[(list[dict], list[datetime.date])]
    :type dates: list[datetime.date]
    """
    for idx, ef in enumerate(eparam.operating_conditions):
        ws = wb.add_worksheet('daily (OC=%d)' % idx)
        daily_results, dates = results[idx]
        if not daily_results:
            continue

        row = 0
        is_head_written = False
        for didx, a_result in enumerate(daily_results):
            head, result_row = report_helper.get_result_list(a_result, missing_value=MISSING_VALUE)
            if not is_head_written:
                _, head = report_helper.get_indice_names()
                is_head_written = True
                ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
                ws.write_row(1, 0, ['Date'] + head)
                if not row:
                    row += 2
            ws.write_row(row, 0, [dates[didx].strftime('%Y-%m-%d')] + result_row)
            row += 1
