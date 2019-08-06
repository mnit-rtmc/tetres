# -*- coding: utf-8 -*-
"""
Load Weather Data (Pre-Fetch)
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.logger import getLogger
from pyticas_tetres.systasks.data_loader import noaa_loader
from pyticas_tetres.util import task_logger

TASK_LOGGER_NAME = 'daily_task_noaa_loader'

def run(prd):
    """

    :type prd: pyticas.ttypes.Period
    :return:
    """
    tlogger = task_logger.get_task_logger(TASK_LOGGER_NAME, capacity=365)

    res = noaa_loader.import_daily_data(prd.start_date)

    logger = getLogger(__name__)
    for v in res:
        logger.debug('  - weather station(usaf=%s, wban=%s) : %d data loaded' % (
            v['usaf'], v['wban'], v['loaded']))

    failed = [v for v in res if not v['loaded']]
    tlogger.set_registry('last_executed', tlogger.now())
    tlogger.add_log({'time': tlogger.now(), 'target_period': prd, 'failed': failed})
    tlogger.save()
