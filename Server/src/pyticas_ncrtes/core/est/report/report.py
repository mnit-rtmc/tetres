# -*- coding: utf-8 -*-

import os

from pyticas.infra import Infra
from pyticas.tool import util
from pyticas_ncrtes.core.est.report import speed_contour, ratio_contour, station_chart
from pyticas_ncrtes.core.est.report import summary
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def report(case_name, edata_list, output_path):
    """

    :type case_name: str
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :type output_path: str
    :return:
    """
    logger = getLogger(__name__)
    # preparing output folder

    chart_path = os.path.join(output_path, 'charts')
    if not os.path.exists(chart_path):
        os.makedirs(chart_path)

    speed_countour_file = os.path.join(output_path, '%s-speed.png' % case_name)
    speed_contour.write(speed_countour_file, case_name, edata_list)

    # normal_ratio_countour_file = os.path.join(output_path, '%s-normal_ratio.png' % case_name)
    # wetnormal_ratio_countour_file = os.path.join(output_path, '%s-wetnormal_ratio.png' % case_name)
    # ratio_contour.write(normal_ratio_countour_file, wetnormal_ratio_countour_file, case_name, edata_list)

    summary_file = os.path.join(output_path, '%s.xlsx' % case_name)
    summary.write(summary_file, case_name, edata_list)

    station_chart.write(chart_path, case_name, edata_list)

    logger.debug('The whole_data are saved in %s' % output_path)


