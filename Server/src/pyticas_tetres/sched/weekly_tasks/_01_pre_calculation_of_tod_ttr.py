# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_tetres import cfg
from pyticas_tetres.systasks import todreliability_calculator


def run():
    today = datetime.datetime.today()
    target_day = today - datetime.timedelta(days=cfg.DAILY_JOB_OFFSET_DAYS)
    todreliability_calculator.run(target_day)
