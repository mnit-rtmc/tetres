import os
import xlsxwriter
from pyticas_tetres.est.helper import util
from pyticas_tetres.est.report import report_helper
import math
from pyticas_noaa.isd import isdtypes
from pyticas_tetres import ttypes

MISSING_VALUE = ''


def write(uid, eparam, operating_conditions):
    # faverolles 10/12/2019 [A]:
    #   Created function to write moe spreadsheet
    """
    :type uid: str
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    """
    output_dir = util.output_path(
        '%s/%s - %s' % (uid, eparam.travel_time_route.corridor, eparam.travel_time_route.name))

    # data file
    output_file = os.path.join(output_dir, 'traveltime-moe-data.xlsx')
    wb = xlsxwriter.Workbook(output_file)
    report_helper.write_operating_condition_info_sheet(eparam, wb)
    report_helper.write_moe_data_sheet(eparam, operating_conditions, wb)
    wb.close()


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
