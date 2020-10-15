# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import time

from pyticas.tool import timeutil
from pyticas_tetres.est.report import (wholetime_reliability_writer, tod_reliabilities_writer,
                                       tod_reliability_graph_writer, wholetime_reliability_graph_writer,
                                       wholetime_reliability_by_oc_writer, tt_data_writer, tt_moe_data_writer)
from pyticas_tetres.logger import getLogger


def write(uid, eparam, operating_conditions, results):
    """

    :type uid: str
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results: tuple
    :rtype:
    """
    logger = getLogger(__name__)

    (whole, yearly, monthly, daily, TOD_whole, TOD_yearly, TOD_monthly) = results

    if eparam.write_spreadsheets:
        # write result sheets
        proc_start_time = time.time()
        logger.debug('>> Writing spread sheets')
        if whole:
            wholetime_reliability_writer.write(uid, eparam, operating_conditions, whole, yearly, monthly, daily)
            wholetime_reliability_by_oc_writer.write(uid, eparam, operating_conditions, whole, yearly, monthly, daily)
        if TOD_whole:
            tod_reliabilities_writer.write(uid, eparam, operating_conditions, TOD_whole, TOD_yearly, TOD_monthly)
        logger.debug('<< End of writing spread sheets (elapsed time=%s)' % (
            timeutil.human_time(seconds=(time.time() - proc_start_time))))

        # write data sheet
        tt_data_writer.write(uid, eparam, operating_conditions)

    if eparam.write_graph_images:
        # write graphs
        proc_start_time = time.time()
        logger.debug('>> Writing graphs')
        if whole:
            wholetime_reliability_graph_writer.write(uid, eparam, operating_conditions, whole, yearly, monthly, daily)
        if TOD_whole:
            tod_reliability_graph_writer.write(uid, eparam, operating_conditions, TOD_whole, TOD_yearly, TOD_monthly)
        logger.debug(
            '<< End of writing graphs (elapsed time=%s)' % (
                timeutil.human_time(seconds=(time.time() - proc_start_time))))
        logger.debug('UID = %s' % uid)

    if eparam.write_moe_spreadsheet:
        # faverolles 10/10/2019:
        #   Added condition to write MOE spreadsheet if requested in eparam
        proc_start_time = time.time()
        logger.debug('>> Writing MOE spread sheet')
        tt_moe_data_writer.write(uid, eparam, operating_conditions)
        # tt_moe_data_writer.write_daily(uid, eparam, operating_conditions, daily)
        logger.debug('<< End of writing MOE spread sheet (elapsed time=%s)' % (
            timeutil.human_time(seconds=(time.time() - proc_start_time))))
