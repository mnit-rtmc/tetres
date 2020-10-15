import os

import xlsxwriter

from pyticas_tetres.est.helper import util
from pyticas_tetres.est.report import report_helper

MISSING_VALUE = ''


def write(uid, eparam, operating_conditions):
    """
    :type uid: str
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    """

    # faverolles 10/12/2019: Created function to write moe spreadsheets

    output_dir = util.output_path(
        '%s/%s - %s' % (uid, eparam.travel_time_route.corridor, eparam.travel_time_route.name))

    # data file
    output_file = os.path.join(output_dir, 'traveltime-moe-data.xlsx')
    # per_route_moe_file = os.path.join(output_dir, "per-route-moe-data.xlsx")
    wb = xlsxwriter.Workbook(output_file)
    report_helper.write_operating_condition_info_sheet(eparam, wb)
    report_helper.write_moe_data_sheet(eparam, operating_conditions, wb)
    wb.close()

    # cm_work_book = xlsxwriter.Workbook(os.path.join(output_dir, "travel-time-moe-cm.xlsx"))
    # cmh_work_book = xlsxwriter.Workbook(os.path.join(output_dir, "travel-time-moe-cmh.xlsx"))
    # sv_work_book = xlsxwriter.Workbook(os.path.join(output_dir, "travel-time-moe-sv.xlsx"))
    # report_helper.write_moe_per_route_sheets(eparam, operating_conditions,
    #                                          cm_work_book=cm_work_book,
    #                                          cmh_work_book=cmh_work_book,
    #                                          sv_work_book=sv_work_book)
    # cm_work_book.close()
    # cmh_work_book.close()
    # sv_work_book.close()


def write_daily(uid, eparam, operating_conditions, daily):
    """
        :type uid: str
        :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
        :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
        :type daily: list[(list[dict], list[datetime.date])]
        """
    output_dir = util.output_path(
        '%s/%s - %s' % (uid, eparam.travel_time_route.corridor, eparam.travel_time_route.name))
    output_file_daily = os.path.join(output_dir, 'traveltime-moe-data-daily.xlsx')
    wb_daily = xlsxwriter.Workbook(output_file_daily)
    report_helper.write_operating_condition_info_sheet(eparam, wb_daily)
    report_helper.write_moe_data_sheet_daily(eparam, operating_conditions, wb_daily, daily)
    wb_daily.close()
