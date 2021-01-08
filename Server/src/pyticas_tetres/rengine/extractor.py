# -*- coding: utf-8 -*-

import datetime
import time

from pyticas import period
from pyticas.tool import tb, timeutil
from pyticas_tetres import cfg
from pyticas_tetres.da import tt
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine.filter.ftypes import ExtData

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def extract_tt(route_id, start_date, end_date, start_time, end_time, operating_conditions, **kwargs):
    """
    :type route_id: int
    :type start_date: datetime.date
    :type end_date: datetime.date
    :type start_time: datetime.time
    :type end_time: datetime.time
    :type filters: list[pyticas_tetres.rengine.filter.ExtFilterGroup]
    """
    remove_holiday = kwargs.get('remove_holiday', False)

    if 'remove_holiday' in kwargs:
        del kwargs['remove_holiday']

    target_days = kwargs.get('target_days', [0, 1, 2, 3, 4, 5, 6])

    if 'target_days' in kwargs:
        del kwargs['target_days']

    # python : 0 => Mon
    # postgresql : 1 => Mon
    target_days = [(d + 1) % 7 for d in target_days]  # convert to postgresql week days

    for sdate, edate in _divide_period_by_year(start_date, end_date):
        _retrieve_data_from_db(route_id, operating_conditions, sdate, edate, start_time, end_time, target_days, remove_holiday, **kwargs)


def _retrieve_data_from_db(route_id, operating_conditions, sdate, edate, start_time, end_time, target_days, remove_holiday, **kwargs):
    """
    :type route_id: int
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ExtFilterGroup]
    :type sdate: datetime.datetime
    :type edate: datetime.datetime
    :type start_time: datetime.time
    :type end_time: datetime.time
    :type target_days: list[int]
    :type remove_holiday: bool
    """
    # logger = getLogger(__name__)
    prd = period.Period(sdate, edate, cfg.TT_DATA_INTERVAL)
    # proc_start_time = time.time()
    # logger.debug('>>>> retrieving data for %s' % prd.get_date_string())

    year = sdate.year

    da_tt = tt.TravelTimeDataAccess(year)

    # generator
    traveltimes = da_tt.list_by_period(route_id, prd, start_time=start_time, end_time=end_time, weekdays=target_days,
                                       as_model=True)
    """:type: list[pyticas_tetres.db.model.TravelTime] """

    for ttm in traveltimes:

        dt = str2datetime(ttm.time)

        if remove_holiday and period.is_holiday(dt.date()):
            continue

        _tt_weathers = list(ttm._tt_weathers)
        _tt_incidents = list(ttm._tt_incidents)
        _tt_workzones = list(ttm._tt_workzones)
        _tt_specialevents = list(ttm._tt_specialevents)
        _tt_snowmanagements = list(ttm._tt_snowmanagements)

        if not _tt_weathers:
            getLogger(__name__).warning('No weather data for route(%d) at %s' % (route_id, dt.strftime('%Y-%m-%d %H:%M')))


        extdata = ExtData(ttm, _tt_weathers[0] if _tt_weathers else [], _tt_incidents, _tt_workzones, _tt_specialevents, _tt_snowmanagements)

        for fidx, ef in enumerate(operating_conditions):
            try:
                ef.check(extdata)
            except Exception as ex:
                tb.traceback(ex)
                continue

    # logger.debug('<<<< end of retrieving data for %s (elapsed time=%s)' % (
    # prd.get_date_string(), timeutil.human_time(seconds=(time.time() - proc_start_time))))


def _monthly_basis_data_extraction_multi_thread(route_id, start_date, end_date, start_time, end_time, operating_conditions, **kwargs):
    """
    :type route_id: int
    :type start_date: datetime.date
    :type end_date: datetime.date
    :type start_time: datetime.time
    :type end_time: datetime.time
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ExtFilterGroup]
    """
    # python : 0 => Mon
    # postgresql : 1 => Mon
    target_days = kwargs.get('target_days', [0, 1, 2, 3, 4, 5, 6])
    remove_holiday = kwargs.get('remove_holiday', False)
    target_days = [(d + 1) % 7 for d in target_days]  # convert to postgresql week days

    yearly_periods = _divide_period_by_year(start_date, end_date)

    from pyticas.tool.concurrent import Worker
    worker = Worker(len(yearly_periods))
    for (sdate, edate) in yearly_periods:
        worker.add_task(_retrieve_data_from_db, route_id, operating_conditions, sdate, edate, start_time, end_time, target_days, remove_holiday)

    worker.run()
    for oc in operating_conditions:
        oc.results = sorted(oc.results, key=lambda item: item.tti.time)


def _divide_period_by_year(start_date, end_date):
    """
    :type start_date: datetime.date
    :type end_date: datetime.date
    :rtype: list[[datetime.datetime, datetime.datetime]]
    """
    sdt = datetime.datetime.combine(start_date, datetime.time(0, 0, 0, 0))
    edt = datetime.datetime.combine(end_date, datetime.time(23, 59, 59, 0))
    from_year = sdt.year
    to_year = edt.year

    time_periods = []
    cursor = sdt
    for y in range(from_year, to_year + 1):
        last_date = datetime.datetime(y, 12, 31, 23, 59, 59, 0)
        time_periods.append([cursor, min(last_date, edt)])
        cursor = datetime.datetime(y + 1, 1, 1, 0, 0, 0, 0)

    return time_periods


def str2datetime(ds):
    """
    :type ds: str
    :rtype: datetime.datetime

    """
    if isinstance(ds, str):
        return datetime.datetime.strptime(ds, '%Y-%m-%d %H:%M:%S')
    else:
        return ds

