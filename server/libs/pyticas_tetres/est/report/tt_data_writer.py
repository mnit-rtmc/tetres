# -*- coding: utf-8 -*-
import os

import xlsxwriter
from pyticas_tetres.est.helper import util

from pyticas_tetres.est.report import report_helper

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

MISSING_VALUE = ''


def write(uid, eparam, operating_conditions):
    """
    :type uid: str
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    """
    output_dir = util.output_path('%s/%s - %s' % (uid, eparam.travel_time_route.corridor, eparam.travel_time_route.name))

    # data file
    output_file = os.path.join(output_dir, 'traveltime-data.xlsx')
    wb = xlsxwriter.Workbook(output_file)
    report_helper.write_operating_condition_info_sheet(eparam, wb)
    report_helper.write_whole_data_sheet(eparam, operating_conditions, wb)
    wb.close()
