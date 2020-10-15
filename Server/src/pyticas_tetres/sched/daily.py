# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import sys

from pyticas import period
from pyticas.tool import tb
from pyticas_tetres import cfg
from pyticas_tetres.da.tt import TravelTimeDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.systasks.data_loader import noaa_loader, incident_loader
from pyticas_tetres.util import task_logger

N_LIMIT_OF_DAYS_TO_PROCESS = 90


def run():
    if '_01_tt' not in sys.modules:
        from pyticas_tetres.sched.daily_tasks import _01_tt, _02_load_weather, _03_load_incident, _04_tagging

    periods = []

    # faverolles 1/16/2020 NOTE: always starts at datetime.today
    today = datetime.datetime.today()
    target_day = today - datetime.timedelta(days=cfg.DAILY_JOB_OFFSET_DAYS)
    last_day_with_tt_data = _find_last_date(today.year)

    if last_day_with_tt_data and last_day_with_tt_data <= target_day:
        periods = period.create_periods(last_day_with_tt_data.date(), target_day.date(), '00:00:00', '23:59:00',
                                        cfg.TT_DATA_INTERVAL)
    else:
        prd = period.create_period(target_day.strftime("%Y-%m-%d 00:00:00"),
                                   target_day.strftime("%Y-%m-%d 23:59:00"), cfg.TT_DATA_INTERVAL)
        periods.append(prd)

    try:
        non_completed_dates_and_routes = _check_logs()
        periods = [ _prd for _route_id, _prd in non_completed_dates_and_routes ] + periods
    except Exception as ex:
        getLogger(__name__).warning('error occured when checking daily-processing log : %s' % tb.traceback(ex, f_print=False))

    periods = list(set(periods))

    if len(periods) > N_LIMIT_OF_DAYS_TO_PROCESS:
        getLogger(__name__).warning(
            'too many days to process. please use data loader program to process the long-time periods')
        return
    try:
        from pyticas_tetres.util.traffic_file_checker import has_traffic_files
        for prd in periods:
            start_date_str, end_date_str = prd.start_date.strftime('%Y-%m-%d'), prd.end_date.strftime('%Y-%m-%d')
            if not has_traffic_files(start_date_str, end_date_str):
                getLogger(__name__).warning('Missing traffic files for performing daily task for the time range starting from {} to {}'.format(start_date_str, end_date_str))
                return
    except Exception as e:
        getLogger(__name__).warning('Exception occured while checking if traffic files exist during performing daily task. Error: {}'.format(e))

    for prd in periods:
        getLogger(__name__).info('>> running daily task for %s' % prd.get_date_string())
        try:
            _01_tt.run(prd)
            _02_load_weather.run(prd)
            _03_load_incident.run(prd)
            _04_tagging.run(prd)
        except Exception as ex:
            tb.traceback(ex)
            getLogger(__name__).warning('Exception occured while performing daily task')


def _find_last_date(current_year):
    for y in range(current_year, cfg.DATA_ARCHIVE_START_YEAR - 1, -1):
        tt_da = TravelTimeDataAccess(y)
        year_prd = period.Period(datetime.datetime(y, 1, 1, 0, 0, 0),
                                 datetime.datetime(y, 12, 31, 23, 59, 59),
                                 cfg.TT_DATA_INTERVAL)

        items = tt_da.list_by_period(None, year_prd, limit=1, order_by=('time', 'desc'))
        if not items:
            continue
        return datetime.datetime.strptime(items[0].time, '%Y-%m-%d %H:%M:%S')

    return None


def _check_logs():
    """
    :rtype: list[(int, pyticas.ttypes.Period)]
    """
    if '_01_tt' not in sys.modules:
        from pyticas_tetres.sched.daily_tasks import _01_tt, _02_load_weather, _03_load_incident, _04_tagging

    non_completed_dates = []

    # tt
    tlogger = task_logger.get_task_logger(_01_tt.TASK_LOGGER_NAME, capacity=365)
    for idx, log in enumerate(tlogger.logs):
        for vidx, ttri_id in enumerate(tlogger.logs[idx]['failed']):
            non_completed_dates.append((ttri_id, log['target_period']))
        tlogger.logs[idx]['failed'] = []
    tlogger.save()

    # weather (load if there is not-loaded weather data)
    tlogger = task_logger.get_task_logger(_02_load_weather.TASK_LOGGER_NAME, capacity=365)
    for idx, log in enumerate(tlogger.logs):
        for vidx, v in enumerate(tlogger.logs[idx]['failed']):
            res = noaa_loader.import_daily_data_for_a_station(log['target_period'].start_date, v['usaf'], v['wban'])
            if res['loaded']:
                del tlogger.logs[idx]['failed'][vidx]
    tlogger.save()

    # incident (load if there is not-loaded incident data)
    tlogger = task_logger.get_task_logger(_03_load_incident.TASK_LOGGER_NAME, capacity=365)
    for idx, log in enumerate(tlogger.logs):
        if not log['failed']:
            continue
        for vidx, v in enumerate(tlogger.logs[idx]['failed']):
            n_inserted, has_error = incident_loader.import_all_corridor(log['target_period'].start_date,
                                                                        log['target_period'].end_date)
            if not has_error:
                del tlogger.logs[idx]['failed'][vidx]
    tlogger.save()

    # tagging (load if there is not-loaded incident data)
    tlogger = task_logger.get_task_logger(_04_tagging.TASK_LOGGER_NAME, capacity=365)
    for idx, log in enumerate(tlogger.logs):
        if not log['failed']:
            continue
        non_completed_dates.append((log['route_id'], log['target_period']))
        tlogger.logs[idx]['failed'] = []
    tlogger.save()

    return non_completed_dates