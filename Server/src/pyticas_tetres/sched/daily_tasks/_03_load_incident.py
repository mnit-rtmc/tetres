# -*- coding: utf-8 -*-
"""
Load Incident Data
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.logger import getLogger
from pyticas_tetres.systasks.data_loader import incident_loader
from pyticas_tetres.util import task_logger

TASK_LOGGER_NAME = 'daily_task_incident_loader'


def run(prd):
    """

    :type prd: pyticas.ttypes.Period
    :return:
    """
    tlogger = task_logger.get_task_logger(TASK_LOGGER_NAME, capacity=365)
    n_inserted, has_error = incident_loader.import_all_corridor(prd.start_date, prd.end_date)
    getLogger(__name__).debug('  - %s incidents are loaded (has_error=%s)' % (n_inserted, has_error))
    tlogger.set_registry('last_executed', tlogger.now())
    tlogger.add_log({'time': tlogger.now(), 'target_period': prd, 'failed': has_error})
    tlogger.save()
