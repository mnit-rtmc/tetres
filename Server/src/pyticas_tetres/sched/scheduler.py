# -*- coding: utf-8 -*-
import threading

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import time
import schedule

from pyticas_tetres import cfg
from pyticas_tetres.logger import getLogger
from pyticas_tetres.sched import daily, weekly, monthly, worker


def start():
    t = threading.Thread(target=_start_and_pending)
    t.start()


def restart():
    getLogger(__name__).info('>> restarting periodic-data processing module')
    schedule.clear()
    _schedule_job()


def _start_and_pending():
    logger = getLogger(__name__)
    logger.info('>> starting task scheduler...')

    _schedule_job()

    t = threading.currentThread()
    while not getattr(t, 'to_be_killed', False):
        schedule.run_pending()
        time.sleep(1)
    logger.info('!! task scheduler has been ended')

def _schedule_job():
    logger = getLogger(__name__)

    # start scheduler for daily  tasks
    logger.info('  - adding daily tasks : at %s' % cfg.DAILY_JOB_START_TIME)
    schedule.every().day.at(cfg.DAILY_JOB_START_TIME).do(_run_scheduled_daily_tasks)

    # start scheduler for weekly tasks
    logger.info('  - adding weekly tasks : at %s on %s' % (cfg.WEEKLY_JOB_START_TIME, cfg.WEEKLY_JOB_START_WEEKDAY))
    getattr(schedule.every(), cfg.WEEKLY_JOB_START_WEEKDAY.lower()).at(cfg.WEEKLY_JOB_START_TIME).do(
        _run_scheduled_weekly_tasks)

    # start scheduler for monthly tasks
    logger.info('  - adding monthly tasks : at %s on day %s every month' % (cfg.MONTHLY_JOB_START_TIME, cfg.MONTHLY_JOB_START_DAY))
    schedule.every().day.at(cfg.MONTHLY_JOB_START_TIME).do(_run_scheduled_monthly_tasks)


def _run_scheduled_daily_tasks():
    """ execute all daily tasks """
    worker.add_task(daily.run)


def _run_scheduled_weekly_tasks():
    """ create thread to execute weekly tasks """
    worker.add_task(weekly.run)


def _run_scheduled_monthly_tasks():
    """ create thread to execute monthly tasks """
    today = datetime.date.today()
    if today.day == cfg.MONTHLY_JOB_START_DAY:
        worker.add_task(monthly.run)
