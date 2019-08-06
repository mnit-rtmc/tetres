# -*- coding: utf-8 -*-
from pyticas_tetres.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.da.route import TTRouteDataAccess
from pyticas_tetres.rengine import categorization as DataCategorizer
from pyticas_tetres.util import task_logger

TASK_LOGGER_NAME = 'daily_task_categorization'


def run(prd):
    """

    :type prd: pyticas.ttypes.Period
    :return:
    """
    tlogger = task_logger.get_task_logger(TASK_LOGGER_NAME, capacity=365)

    ttr_route_da = TTRouteDataAccess()
    routes = ttr_route_da.list()
    ttr_route_da.close_session()
    logger = getLogger(__name__)
    has_error = 0
    for ttri in routes:
        try:
            result = DataCategorizer.categorize(ttri, prd)
            if result['has_error']:
                logger.debug('  - error occured when doing categorization for route %s (id=%s) during %s'
                             % (ttri.name, ttri.id, prd.get_date_string()))
                tlogger.add_log({'time': tlogger.now(), 'route_id': ttri.id, 'target_period': prd, 'failed': True})
                has_error += 1
        except Exception as ex:
            logger.debug('  - exception occured when doing categorization for route %s (id=%s) during %s'
                         % (ttri.name, ttri.id, prd.get_date_string()))
            tlogger.add_log({'time': tlogger.now(), 'route_id': ttri.id, 'target_period': prd, 'failed': True})
            has_error += 1

    logger.debug('  - categorization for %s routes are done (has_error=%s)' % (len(routes), has_error))

    tlogger.set_registry('last_executed', tlogger.now())
    tlogger.save()
