# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os

import xlsxwriter

from pyticas.tool import tb
from pyticas_tetres.est.helper import util
from pyticas_tetres.est.report import report_helper
from pyticas_tetres.logger import getLogger

MISSING_VALUE = -1


def write(uid, eparam, ext_filter_groups, whole, yearly, monthly):
    """
    :type uid: str
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type ext_filter_groups: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type whole: list[list[dict]]
    :type yearly: list[list[list[dict]]]
    :type monthly: list[list[list[dict]]]
    """
    output_dir = util.output_path(
        '%s/%s - %s' % (uid, eparam.travel_time_route.corridor, eparam.travel_time_route.name))

    # result file
    output_file = os.path.join(output_dir, 'time-of-day-reliabilities.xlsx')
    wb = xlsxwriter.Workbook(output_file)
    report_helper.write_operating_condition_info_sheet(eparam, wb)

    try:
        _write_tod_result_sheet(eparam, ext_filter_groups, wb, whole)
    except Exception as ex:
        getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    if yearly:
        try:
            _write_tod_yearly_result_sheet(eparam, ext_filter_groups, wb, yearly)
        except Exception as ex:
            getLogger(__name__).warning(
                'Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    if monthly:
        try:
            _write_tod_monthly_result_sheet(eparam, ext_filter_groups, wb, monthly)
        except Exception as ex:
            getLogger(__name__).warning(
                'Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    wb.close()


def _write_tod_result_sheet(eparam, operating_conditions, wb, results, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results_tod: list[list[dict]]
    """
    missing_value = kwargs.get('missing_value', MISSING_VALUE)
    fields, col_names = report_helper.get_indice_names()
    n_cols = len(col_names)
    missing_row = [missing_value] * n_cols

    for idx, oc in enumerate(operating_conditions):
        tod_results = results[idx]
        if not tod_results:
            continue

        is_head_written = False
        ws = wb.add_worksheet('reliabilites (OC=%d)' % idx)
        row = 0
        for didx, a_result in enumerate(tod_results):
            head, result_row = report_helper.get_result_list(a_result, missing_value=MISSING_VALUE)
            if not is_head_written:
                _, head  = report_helper.get_indice_names()
                ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
                ws.write_row(1, 0, ['Time'] + head)
                is_head_written = True
                if not row:
                    row += 2
            if not result_row:
                result_row = missing_row
            ws.write_row(row, 0, [oc.all_times[didx].strftime('%H:%M')] + result_row)
            row += 1


def _write_tod_yearly_result_sheet(eparam, operating_conditions, wb, results, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[list[list[dict]]]
    """
    missing_value = kwargs.get('missing_value', MISSING_VALUE)
    fields, col_names = report_helper.get_indice_names()
    n_cols = len(col_names)
    missing_row = [missing_value] * n_cols

    for idx, oc in enumerate(operating_conditions):
        yearly_results = results[idx]
        if not yearly_results:
            continue

        is_head_written = False
        ws = wb.add_worksheet('yearly (OC=%d)' % idx)
        row = 0
        for yidx, a_year_result in enumerate(yearly_results):
            if not a_year_result:
                # write empty data for a year
                for dt in oc.all_times:
                    ws.write_row(row, 0, [oc.all_years[yidx], dt.strftime('%H:%M')] + missing_row)
                    row += 1
                continue

            for tidx, a_result in enumerate(a_year_result):
                head, result_row = report_helper.get_result_list(a_result, missing_value=MISSING_VALUE)
                # write head row
                if not is_head_written:
                    _, head  = report_helper.get_indice_names()
                    ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
                    ws.write_row(1, 0, ['Year', 'Time'] + head)
                    is_head_written = True
                    if row == 0:
                        row += 2

                try:
                    ws.write_row(row, 0, [oc.all_years[yidx], oc.all_times[tidx].strftime('%H:%M')] + result_row)
                except Exception as ex:
                    print(yidx, tidx, len(oc.all_years), len(oc.all_times), len(yearly_results), len(a_year_result))
                    raise ex
                row += 1


def _write_tod_monthly_result_sheet(eparam, operating_conditions, wb, results, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[list[list[dict]]]
    """
    missing_value = kwargs.get('missing_value', MISSING_VALUE)
    fields, col_names = report_helper.get_indice_names()
    n_cols = len(col_names)
    missing_row = [missing_value] * n_cols

    for idx, oc in enumerate(operating_conditions):
        monthly_results = results[idx]
        if not monthly_results:
            continue

        is_head_written = False
        ws = wb.add_worksheet('monthly (OC=%d)' % idx)
        row = 0
        for midx, a_month_result in enumerate(monthly_results):
            if not a_month_result:
                # write empty data for a month
                for dt in oc.all_times:
                    ws.write_row(row, 0, ['%04d-%02d' % (oc.all_months[midx][0], oc.all_months[midx][1]),
                                          dt.strftime('%H:%M')] + missing_row)
                    row += 1
                continue

            for tidx, a_result in enumerate(a_month_result):
                head, result_row = report_helper.get_result_list(a_result, missing_value=missing_value)
                # write head row
                if not is_head_written:
                    _, head  = report_helper.get_indice_names()
                    ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
                    ws.write_row(1, 0, ['Month', 'Time'] + head)
                    is_head_written = True
                    if row == 0:
                        row += 2

                ws.write_row(row, 0, ['%04d-%02d' % (oc.all_months[midx][0], oc.all_months[midx][1]),
                                      oc.all_times[tidx].strftime('%H:%M')] + result_row)
                row += 1
