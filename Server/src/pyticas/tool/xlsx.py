# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import xlsxwriter
from xlsxwriter.workbook import Workbook
from xlsxwriter.workbook import Worksheet

def create_workbook(filepath):
    return xlsxwriter.Workbook(filepath)

def get_sheet_by_name(workbook, sheet_name):
    """

    :type workbook: Workbook
    :type sheet_name: str
    :rtype: Worksheet
    """
    sheet_index = workbook._get_sheet_index(sheet_name)
    if not sheet_index:
        return workbook.add_worksheet(sheet_name)
    else:
        sheets = workbook.worksheets()
        return sheets[sheet_index]


def add_chart(workbook, sheet, chartLocCell, chartOption, seriesOptions ):
    chart = workbook.add_chart(chartOption)
    for sOpt in seriesOptions:
        chart.add_series(sOpt)
    sheet.insert_chart(chartLocCell, chart)
    return chart
