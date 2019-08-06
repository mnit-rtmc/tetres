# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.logger import getLogger
from pyticas_tetres.sched import scheduler

logger = getLogger(__name__)


def start():
    """ start periodic jobs
    """
    logger.info('  - starting TeTRES Service')
    scheduler.start()
