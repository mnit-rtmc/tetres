# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas.tool import tb
from pyticas_tetres import cfg
from pyticas_tetres.logger import getLogger
from pyticas_tetres.sched.weekly_tasks import _01_pre_calculation_of_tod_ttr


def run(**kwargs):
    today = datetime.datetime.today()
    target_day = today - datetime.timedelta(days=cfg.DAILY_JOB_OFFSET_DAYS)
    try:
        _01_pre_calculation_of_tod_ttr.run(target_day)
    except Exception as ex:
        tb.traceback(ex)
        getLogger(__name__).warning('Exception occured while performing weekly task')
