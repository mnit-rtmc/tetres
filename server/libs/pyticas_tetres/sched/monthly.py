# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import tb
from pyticas_tetres.logger import getLogger
from pyticas_tetres.sched.monthly_tasks import _01_check_tt_data


def run(**kwargs):

    try:
        _01_check_tt_data.run()
    except Exception as ex:
        tb.traceback(ex)
        getLogger(__name__).warning('Exception occured while performing monthly task')
