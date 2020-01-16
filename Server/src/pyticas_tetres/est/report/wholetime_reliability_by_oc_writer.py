# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os

import xlsxwriter

from pyticas.tool import tb
from pyticas_tetres.est.helper import util
from pyticas_tetres.est.report import report_helper
from pyticas_tetres.logger import getLogger

MISSING_VALUE = -1


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
    output_dir = util.output_path(
        '%s/%s - %s' % (uid, eparam.travel_time_route.corridor, eparam.travel_time_route.name))

    # result file
    output_file = os.path.join(output_dir, 'reliabilities-by-indices (whole-time-period).xlsx')

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
            getLogger(__name__).warning(
                'Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    if monthly:
        try:
            _write_monthly_result_sheet(eparam, operating_conditions, wb, monthly)
        except Exception as ex:
            getLogger(__name__).warning(
                'Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    if daily:
        try:
            _write_daily_result_sheet(eparam, operating_conditions, wb, daily)
        except Exception as ex:
            getLogger(__name__).warning(
                'Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    wb.close()


def _write_whole_result_sheet(eparam, operating_conditions, wb, results, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[dict]
    """
    missing_value = kwargs.get('missing_value', MISSING_VALUE)
    ws = wb.add_worksheet('reliabilities')

    is_head_written = False
    row = 0
    for idx, ef in enumerate(eparam.operating_conditions):
        head, result_row = report_helper.get_result_list(results[idx], missing_value=missing_value)
        if not is_head_written:
            _, head = report_helper.get_indice_names()
            is_head_written = True
            ws.write_row(0, 0, ['OC Index', 'OC Name'] + head)
            if not row:
                row += 1

        if not result_row:
            result_row = [missing_value] * len(head)
        result_row = [v if v else missing_value for v in result_row]
        ws.write_row(row, 0, [idx, ef.name] + result_row)
        row += 1


def _write_yearly_result_sheet(eparam, operating_conditions, wb, results, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[(list[dict], list[int])]
    :type dates: list[datetime.date]
    """
    missing_value = kwargs.get('missing_value', MISSING_VALUE)
    fields, col_names, sheet_names = report_helper.get_indice_names_for_byindices()
    years = util.years(eparam.start_date, eparam.end_date)
    for sidx, sheet_name in enumerate(sheet_names):
        ws = wb.add_worksheet('yearly %s' % sheet_name)
        field_name = fields[sidx]
        list_by_oc, year_list, oc_names = _extract_indices(results, operating_conditions, field_name, missing_value)
        ws.write_row(0, 0, ['Year'] + oc_names)
        ws.write_column(1, 0, years)
        col = 1
        for oidx, list_for_a_oc in enumerate(list_by_oc):
            data = []
            for y in years:
                tidx = -1
                for midx, y2 in enumerate(year_list[oidx]):
                    if y == y2:
                        tidx = midx
                        break
                if tidx >= 0:
                    data.append(list_for_a_oc[tidx] if list_for_a_oc[tidx] else missing_value)
                else:
                    data.append(missing_value)
            ws.write_column(1, col, data)
            col += 1


def _write_monthly_result_sheet(eparam, operating_conditions, wb, results, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[(list[dict], list[[int, int])]
    :type dates: list[datetime.date]
    """
    missing_value = kwargs.get('missing_value', MISSING_VALUE)
    fields, col_names, sheet_names = report_helper.get_indice_names_for_byindices()
    months = util.months(eparam.start_date, eparam.end_date)
    for sidx, sheet_name in enumerate(sheet_names):
        ws = wb.add_worksheet('monthly %s' % sheet_name)
        field_name = fields[sidx]
        list_by_oc, months_list, oc_names = _extract_indices(results, operating_conditions, field_name, missing_value)
        ws.write_row(0, 0, ['Month'] + oc_names)
        ws.write_column(1, 0, ['%04d-%02d' % (month[0], month[1]) for month in months])
        col = 1
        for oidx, list_for_a_oc in enumerate(list_by_oc):
            data = []
            for (y, m) in months:
                tidx = -1
                for midx, (y2, m2) in enumerate(months_list[oidx]):
                    if y == y2 and m == m2:
                        tidx = midx
                        break
                if tidx >= 0:
                    data.append(list_for_a_oc[tidx] if list_for_a_oc[tidx] else missing_value)
                else:
                    data.append(missing_value)
            ws.write_column(1, col, data)
            col += 1


def _write_daily_result_sheet(eparam, operating_conditions, wb, results, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type results: list[(list[dict], list[datetime.date])]
    :type dates: list[datetime.date]
    """
    missing_value = kwargs.get('missing_value', MISSING_VALUE)
    fields, col_names, sheet_names = report_helper.get_indice_names_for_byindices()
    target_days = eparam.weekdays.get_weekdays()
    dates = util.dates(eparam.start_date, eparam.end_date, eparam.except_holiday, target_days)
    for sidx, sheet_name in enumerate(sheet_names):
        ws = wb.add_worksheet('daily %s' % sheet_name)
        field_name = fields[sidx]
        list_by_oc, date_list, oc_names = _extract_indices(results, operating_conditions, field_name, missing_value)
        ws.write_row(0, 0, ['Date'] + oc_names)
        ws.write_column(1, 0, [d.strftime('%Y-%m-%d') for d in dates])
        col = 1
        for oidx, list_for_a_oc in enumerate(list_by_oc):
            data = []
            for date in dates:
                tidx = -1
                for midx, date2 in enumerate(date_list[oidx]):
                    if date == date2:
                        tidx = midx
                        break
                if tidx >= 0:
                    data.append(list_for_a_oc[tidx] if list_for_a_oc[tidx] else missing_value)
                else:
                    data.append(missing_value)
            ws.write_column(1, col, data)
            col += 1


def _extract_indices(results, operating_conditions, field_name, missing_value):
    """

    :type results: list[(list[dict], list[[int, int])]
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type field_name: str
    :rtype: list[list[float]], list[list[[int, int]]],  list[str]
    """
    extracted, extracted_periods = [], []
    oc_names = []
    for oc_idx, (ym_results, ymd_list) in enumerate(results):
        values = []
        oc_names.append(operating_conditions[oc_idx].label)
        if not ym_results:
            extracted.append([missing_value] * len(ym_results))
            extracted_periods.append(ymd_list)
            continue

        for didx, a_result in enumerate(ym_results):
            value = report_helper._get_item(a_result, field_name, missing_value=missing_value)
            values.append(value)
        extracted.append(values)
        extracted_periods.append(ymd_list)
    return extracted, extracted_periods, oc_names
