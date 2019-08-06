# -*- coding: utf-8 -*-
"""
Travel Time Calculation Task
============================

- run at beginning of the day to calculate tt of the previous day for all TTR routes

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine import traveltime
from pyticas_tetres.util import task_logger

TASK_LOGGER_NAME = 'daily_task_tt_calculation'


def run(prd):
    """

    :type prd: pyticas.ttypes.Period
    :return:
    """
    tlogger = task_logger.get_task_logger(TASK_LOGGER_NAME, capacity=365)
    res = traveltime.calculate_all_routes(prd)

    failed = [v['route_id'] for v in res if not v['done']]
    getLogger(__name__).debug('  - travel times for %s routes are calculated (has_error=%s)' % (len(res), len(failed)))

    tlogger.set_registry('last_executed', tlogger.now())
    tlogger.add_log({'time': tlogger.now(), 'target_period': prd, 'failed': failed})
    tlogger.save()
