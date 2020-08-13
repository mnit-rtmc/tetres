# -*- coding: utf-8 -*-
"""
    Data Loader module
    ~~~~~~~~~~~~~~~~~~

    This module performs the followings for the given time period:

        - loading weather data
        - loading incident data
        - calculating travel time data
        - categoriing operating condition data

    Existing data for the given time period will be deleted before adding data.
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import gc
from multiprocessing import Process, Manager, Lock

from pyticas import period, ticas
from pyticas_tetres import cfg
from pyticas_tetres.da import actionlog
from pyticas_tetres.da.route import TTRouteDataAccess
from pyticas_tetres.da.tt import TravelTimeDataAccess
from pyticas_tetres.db.tetres.model_yearly import create_year_table
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine import traveltime
from pyticas_tetres.systasks.data_loader import incident_loader
from pyticas_tetres.systasks.data_loader import noaa_loader

DEFAULT_NUMBER_OF_PROCESSES = 5


def run(start_date, end_date, db_info):
    """
    :type start_date: datetime.date
    :type end_date: datetime.date
    :type db_info: dict
    """

    _create_yearly_db_tables(start_date, end_date)
    _load_weather_data(start_date, end_date)
    _load_incident_data(start_date, end_date)
    _calculate_tt_and_categorize(start_date, end_date, db_info)
    _update_actionlogs()


def load_incident_data(start_date, end_date):
    _create_yearly_db_tables(start_date, end_date)
    _load_incident_data(start_date, end_date)


def load_weather_data(start_date, end_date):
    _create_yearly_db_tables(start_date, end_date)
    _load_weather_data(start_date, end_date)


def calculate_tt_only(start_date, end_date, db_info, **kwargs):
    _create_yearly_db_tables(start_date, end_date)
    _calculate_tt_only(start_date, end_date, db_info, **kwargs)


def create_or_update_tt_and_moe(start_date, end_date, db_info):
    _create_yearly_db_tables(start_date, end_date)
    _create_or_update_tt_and_moe(start_date, end_date, db_info)


def categorize_tt_only(start_date, end_date, db_info):
    _create_yearly_db_tables(start_date, end_date)
    _categorize_tt_only(start_date, end_date, db_info)


def update_moe_values(rw_moe_param_json, db_info=None, *args, **kwargs):
    rw_moe_param_json['rw_moe_start_date'] = datetime.datetime.strptime(rw_moe_param_json['rw_moe_start_date'],
                                                                        '%Y-%m-%d %H:%M:%S').date()
    rw_moe_param_json['rw_moe_end_date'] = datetime.datetime.strptime(rw_moe_param_json['rw_moe_end_date'],
                                                                      '%Y-%m-%d %H:%M:%S').date()

    # _create_yearly_db_tables(rw_moe_param_json['rw_moe_start_date'], rw_moe_param_json['rw_moe_end_date'])
    _update_moe_values(rw_moe_param_json, db_info=db_info, *args, **kwargs)


def _update_moe_values(rw_moe_param_json,
                       db_info=None, *args, **kwargs):
    logger = getLogger(__name__)
    logger.debug('>> Updating MOE Values')
    _worker_process_to_update_moe_values(rw_moe_param_json['rw_moe_start_date'], rw_moe_param_json['rw_moe_end_date'],
                                         db_info, rw_moe_param_json=rw_moe_param_json)
    logger.debug('<< End of Updating MOE Values')


def _create_yearly_db_tables(start_date, end_date):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    """

    years = _years(start_date, end_date)
    for y in years:
        create_year_table(y)


def _load_weather_data(start_date, end_date):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    """
    logger = getLogger(__name__)
    logger.debug('>>> prepare_weather_data() : %s ~ %s' % (start_date, end_date))
    for y in _years(start_date, end_date):
        logger.debug(' > load NOAA weather data for %d' % y)
        res = noaa_loader.import_yearly_data(y)
        for inserted in res:
            logger.debug('- usaf=%s, wban=%s, inserted=%s' %
                         (inserted['usaf'], inserted['wban'], inserted['loaded']))
    logger.debug('<<< end of prepare_weather_data() : %s ~ %s' % (start_date, end_date))


def _load_incident_data(start_date, end_date):
    """
    :type start_date: datetime.date
    :type end_date: datetime.date
    """
    logger = getLogger(__name__)

    for sdt, edt in yearly_period(start_date, end_date):
        logger.debug('>>> _load_incident_data() : %s ~ %s' % (sdt, edt))
        n_inserted, has_error = incident_loader.import_all_corridor(sdt, edt)
        logger.debug('<<< end of _load_incident_data() : %s ~ %s' % (sdt, edt))


def _run_multi_process(target_function, start_date, end_date, db_info, **kwargs):
    """
    :type target_function: callable
    :type start_date: datetime.date
    :type end_date: datetime.date
    :type db_info: dict
    """
    logger = getLogger(__name__)

    stime = datetime.time(0, 0, 0, 0)
    etime = datetime.time(23, 55, 0, 0)

    daily_periods = period.create_periods(start_date, end_date,
                                          stime, etime,
                                          cfg.TT_DATA_INTERVAL,
                                          target_days=[0, 1, 2, 3, 4, 5, 6],
                                          remove_holiday=False)

    logger.debug('>>> Starting Multi Processing (duration= %s to %s)' % (start_date, end_date))

    m = Manager()
    queue = m.Queue()

    lck = Lock()
    N = DEFAULT_NUMBER_OF_PROCESSES
    data_path = ticas._TICAS_.data_path
    procs = []
    for idx in range(N):
        p = Process(target=target_function,
                    args=(idx, queue, lck, data_path, db_info), kwargs=kwargs)
        p.start()
        procs.append(p)
    rw_moe_param_json = kwargs.get("rw_moe_param_json")
    if rw_moe_param_json and rw_moe_param_json.get("reference_tt_route_id"):
        ttr_ids = [int(rw_moe_param_json.get("reference_tt_route_id"))]
    else:
        ttr_route_da = TTRouteDataAccess()
        ttr_ids = [ttri.id for ttri in ttr_route_da.list()]
        ttr_route_da.close_session()

    total = len(daily_periods) * len(ttr_ids)
    cnt = 1
    for pidx, prd in enumerate(daily_periods):
        for ridx, ttr_id in enumerate(ttr_ids):
            queue.put((ttr_id, prd, cnt, total))
            cnt += 1

    for idx in range(N * 3):
        queue.put((None, None, None, None))

    for p in procs:
        try:
            p.join()
        except:
            pass

    # flush queue
    while not queue.empty():
        queue.get()

    logger.debug('<<< End of Multi Processing (duration= %s to %s)' % (start_date, end_date))


def _calculate_tt_and_categorize(start_date, end_date, db_info):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    :type db_info: dict
    """
    logger = getLogger(__name__)
    logger.debug('>> Categorizing travel time data')
    _run_multi_process(_worker_process_to_calculate_tt_and_categorize, start_date, end_date, db_info)
    logger.debug('<< End of categorizing travel time data')


def _calculate_tt_only(start_date, end_date, db_info, **kwargs):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    :type db_info: dict
    """
    logger = getLogger(__name__)
    logger.debug('>> Categorizing travel time data')
    _run_multi_process(_worker_process_to_calculate_tt_only, start_date, end_date, db_info, **kwargs)
    logger.debug('<< End of categorizing travel time data')


def _create_or_update_tt_and_moe(start_date, end_date, db_info):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    :type db_info: dict
    """
    logger = getLogger(__name__)
    logger.debug('>> Categorizing travel time data')
    _run_multi_process(_worker_process_to_create_or_update_tt_and_moe, start_date, end_date, db_info)
    logger.debug('<< End of categorizing travel time data')


def _categorize_tt_only(start_date, end_date, db_info):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    :type db_info: dict
    """
    logger = getLogger(__name__)
    logger.debug('>> Categorizing travel time data')
    _run_multi_process(_worker_process_to_categorize_tt_only, start_date, end_date, db_info)
    logger.debug('<< End of categorizing travel time data')


def calculate_tt_for_routes(start_date, end_date, route_ids):
    _create_yearly_db_tables(start_date, end_date)
    _calculate_tt_for_routes(start_date, end_date, route_ids)


def _calculate_tt_for_routes(start_date, end_date, ttr_ids):
    stime = datetime.time(0, 0, 0, 0)
    etime = datetime.time(23, 55, 0, 0)
    da_route = TTRouteDataAccess()

    daily_periods = period.create_periods(start_date, end_date,
                                          stime, etime,
                                          cfg.TT_DATA_INTERVAL,
                                          target_days=[0, 1, 2, 3, 4, 5, 6],
                                          remove_holiday=False)
    for pidx, prd in enumerate(daily_periods):
        for ridx, ttr_id in enumerate(ttr_ids):
            ttri = da_route.get_by_id(ttr_id)
            is_inserted = traveltime.calculate_a_route(prd, ttri, dbsession=da_route.get_session())


def specific_tt_categorizer(start_date, end_date, categorizer_names, db_info):
    _create_yearly_db_tables(start_date, end_date)
    _specific_tt_categorization(start_date, end_date, categorizer_names, db_info)


def _specific_tt_categorization(start_date, end_date, categorizer_names, db_info):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    :type db_info: dict
    """
    logger = getLogger(__name__)
    logger.debug('>> Categorizing travel time data')
    _run_multi_process(_worker_process_to_specific_categorization, start_date, end_date, db_info,
                       categorizer_names=categorizer_names)
    logger.debug('<< End of categorizing travel time data')


def _worker_process_to_specific_categorization(idx, queue, lck, data_path, db_info, **kwargs):
    from pyticas_tetres.db.tetres import conn
    from pyticas.infra import Infra
    from pyticas.tool import tb
    from pyticas_tetres.rengine.cats import incident, snowmgmt, specialevent, weather, workzone

    logger = getLogger(__name__)
    # initialize
    logger.debug('[TT-Categorization Worker %d] starting...' % (idx))
    ticas.initialize(data_path)
    infra = Infra.get_infra()
    conn.connect(db_info)
    categorizers = []
    categorizer_names = kwargs.get("categorizer_names")
    categorizer_map = {
        "incident": incident,
        "snowmgmt": snowmgmt,
        "specialevent": specialevent,
        "weather": weather,
        "workzone": workzone
    }
    for categorizer_name in categorizer_names:
        categorizers.append(categorizer_map.get(categorizer_name))
    da_route = TTRouteDataAccess()
    logger.debug('[TT-Categorization Worker %d] is ready' % (idx))
    while True:
        ttr_id, prd, num, total = queue.get()
        if prd is None:
            da_route.close_session()
            exit(1)
        try:
            ttri = da_route.get_by_id(ttr_id)
            if not ttri:
                logger.debug('[TT-Categorization Worker %d] route is not found (%s)' % (idx, ttr_id))
                continue
            logger.debug('[TT-Categorization Worker %d] (%d/%d) %s (id=%s) at %s' % (
                idx, num, total, ttri.name, ttri.id, prd.get_date_string()))

            tt_da = TravelTimeDataAccess(prd.start_date.year)
            tt_data_list = tt_da.list_by_period(ttri.id, prd)
            tt_da.close_session()

            for cidx, categorizer in enumerate(categorizers):
                n_inserted = categorizer.categorize(ttri, prd, tt_data_list, lock=lck)

            gc.collect()

        except Exception as ex:
            tb.traceback(ex)
            continue


def _worker_process_to_calculate_tt_only(idx, queue, lck, data_path, db_info, **kwargs):
    from pyticas_tetres.db.tetres import conn
    from pyticas.infra import Infra
    from pyticas.tool import tb

    logger = getLogger(__name__)
    # initialize
    logger.debug('[TT-Categorization Worker %d] starting...' % (idx))
    ticas.initialize(data_path)
    infra = Infra.get_infra()
    conn.connect(db_info)

    da_route = TTRouteDataAccess()
    logger.debug('[TT-Categorization Worker %d] is ready' % (idx))
    while True:
        ttr_id, prd, num, total = queue.get()
        if prd is None:
            da_route.close_session()
            exit(1)
        try:
            ttri = da_route.get_by_id(ttr_id)
            if not ttri:
                logger.debug('[TT-Categorization Worker %d] route is not found (%s)' % (idx, ttr_id))
                continue
            logger.debug('[TT-Categorization Worker %d] (%d/%d) %s (id=%s) at %s' % (
                idx, num, total, ttri.name, ttri.id, prd.get_date_string()))
            is_inserted = traveltime.calculate_a_route(prd, ttri, dbsession=da_route.get_session(), lock=lck)
            if not is_inserted:
                logger.warning('[TT-Categorization Worker %d]  - fail to add travel time data' % idx)

            gc.collect()

        except Exception as ex:
            tb.traceback(ex)
            continue


def _worker_process_to_update_moe_values(start_date, end_date, db_info, **kwargs):
    from pyticas_tetres.db.tetres import conn
    from pyticas.tool import tb
    logger = getLogger(__name__)

    stime = datetime.time(0, 0, 0, 0)
    etime = datetime.time(23, 55, 0, 0)

    daily_periods = period.create_periods(start_date, end_date,
                                          stime, etime,
                                          cfg.TT_DATA_INTERVAL,
                                          target_days=[0, 1, 2, 3, 4, 5, 6],
                                          remove_holiday=False)

    logger.debug('>>> Starting Multi Processing (duration= %s to %s)' % (start_date, end_date))
    rw_moe_param_json = kwargs.get("rw_moe_param_json")
    reference_tt_route_id = rw_moe_param_json.get('reference_tt_route_id')
    if db_info:
        conn.connect(db_info)
    rw_moe_param_json = kwargs.get("rw_moe_param_json")
    da_route = TTRouteDataAccess()
    ttri = da_route.get_by_id(reference_tt_route_id)
    if not ttri:
        logger.debug('route is not found (%s)' % (reference_tt_route_id))
        return
    for pidx, prd in enumerate(daily_periods):
        if prd is None:
            da_route.close_session()
            exit(1)
        try:
            da_route.close_session()
            traveltime.update_moe_values_a_route(prd, ttri.id, dbsession=da_route.get_session(),
                                                 rw_moe_param_json=rw_moe_param_json)
            gc.collect()

        except Exception as ex:
            tb.traceback(ex)
            continue


def _worker_process_to_create_or_update_tt_and_moe(idx, queue, lck, data_path, db_info):
    from pyticas_tetres.db.tetres import conn
    from pyticas.infra import Infra
    from pyticas.tool import tb

    logger = getLogger(__name__)
    # initialize
    logger.debug('[TT-Categorization Worker %d] starting...' % (idx))
    ticas.initialize(data_path)
    infra = Infra.get_infra()
    conn.connect(db_info)

    da_route = TTRouteDataAccess()
    logger.debug('[TT-Categorization Worker %d] is ready' % (idx))
    while True:
        ttr_id, prd, num, total = queue.get()
        if prd is None:
            da_route.close_session()
            exit(1)
        try:
            ttri = da_route.get_by_id(ttr_id)
            if not ttri:
                logger.debug('[TT-Categorization Worker %d] route is not found (%s)' % (idx, ttr_id))
                continue
            logger.debug('[TT-Categorization Worker %d] (%d/%d) %s (id=%s) at %s' % (
                idx, num, total, ttri.name, ttri.id, prd.get_date_string()))
            traveltime.calculate_a_route(prd, ttri, dbsession=da_route.get_session(), lock=lck, create_or_update=True)
            gc.collect()

        except Exception as ex:
            logger.warning('[TT-Categorization Worker %d]  - fail to add travel time data' % idx)
            tb.traceback(ex)
            continue


def _worker_process_to_categorize_tt_only(idx, queue, lck, data_path, db_info):
    from pyticas_tetres.db.tetres import conn
    from pyticas.infra import Infra
    from pyticas.tool import tb
    from pyticas_tetres.rengine.cats import weather, incident, snowmgmt, specialevent, workzone

    logger = getLogger(__name__)
    # initialize
    logger.debug('[TT-Categorization Worker %d] starting...' % (idx))
    ticas.initialize(data_path)
    infra = Infra.get_infra()
    conn.connect(db_info)

    categorizers = [weather, incident, workzone, specialevent, snowmgmt]
    da_route = TTRouteDataAccess()
    logger.debug('[TT-Categorization Worker %d] is ready' % (idx))
    while True:
        ttr_id, prd, num, total = queue.get()
        if prd is None:
            da_route.close_session()
            exit(1)
        try:
            ttri = da_route.get_by_id(ttr_id)
            if not ttri:
                logger.debug('[TT-Categorization Worker %d] route is not found (%s)' % (idx, ttr_id))
                continue
            logger.debug('[TT-Categorization Worker %d] (%d/%d) %s (id=%s) at %s' % (
                idx, num, total, ttri.name, ttri.id, prd.get_date_string()))

            tt_da = TravelTimeDataAccess(prd.start_date.year)
            tt_data_list = tt_da.list_by_period(ttri.id, prd)
            tt_da.close_session()

            for cidx, categorizer in enumerate(categorizers):
                n_inserted = categorizer.categorize(ttri, prd, tt_data_list, lock=lck)

            gc.collect()

        except Exception as ex:
            tb.traceback(ex)
            continue


def _worker_process_to_calculate_tt_and_categorize(idx, queue, lck, data_path, db_info):
    from pyticas_tetres.db.tetres import conn
    from pyticas.infra import Infra
    from pyticas.tool import tb
    from pyticas_tetres.rengine.cats import weather, incident, snowmgmt, specialevent, workzone

    logger = getLogger(__name__)
    # initialize
    logger.debug('[TT-Categorization Worker %d] starting...' % (idx))
    ticas.initialize(data_path)
    infra = Infra.get_infra()
    conn.connect(db_info)

    categorizers = [weather, incident, workzone, specialevent, snowmgmt]
    da_route = TTRouteDataAccess()
    logger.debug('[TT-Categorization Worker %d] is ready' % (idx))
    while True:
        ttr_id, prd, num, total = queue.get()
        if prd is None:
            da_route.close_session()
            exit(1)
        try:
            ttri = da_route.get_by_id(ttr_id)
            if not ttri:
                logger.debug('[TT-Categorization Worker %d] route is not found (%s)' % (idx, ttr_id))
                continue
            logger.debug('[TT-Categorization Worker %d] (%d/%d) %s (id=%s) at %s' % (
                idx, num, total, ttri.name, ttri.id, prd.get_date_string()))
            is_inserted = traveltime.calculate_a_route(prd, ttri, dbsession=da_route.get_session(), lock=lck)
            if not is_inserted:
                logger.warning('[TT-Categorization Worker %d]  - fail to add travel time data' % idx)

            tt_da = TravelTimeDataAccess(prd.start_date.year)
            tt_data_list = tt_da.list_by_period(ttri.id, prd)
            tt_da.close_session()

            for cidx, categorizer in enumerate(categorizers):
                n_inserted = categorizer.categorize(ttri, prd, tt_data_list, lock=lck)

            gc.collect()

        except Exception as ex:
            tb.traceback(ex)
            continue


def _update_actionlogs():
    now = datetime.datetime.now()
    da = actionlog.ActionLogDataAccess()
    for an_actionlog in da.list(handled=False, as_model=True):
        da.update(an_actionlog.id, {'handled': True,
                                    'handled_date': now,
                                    'status': actionlog.ActionLogDataAccess.STATUS_DONE,
                                    'status_updated_date': now
                                    })
        da.commit()


def _prepare_periods(start_date, end_date):
    """

    :type start_date: datetime.datetime
    :type end_date: datetime.datetime
    """
    stime = datetime.time(0, 0, 0, 0)
    etime = datetime.time(23, 55, 0, 0)

    return period.create_periods(start_date, end_date,
                                 stime, etime,
                                 cfg.TT_DATA_INTERVAL,
                                 target_days=[0, 1, 2, 3, 4, 5, 6],
                                 remove_holiday=False)


def _years(start_date, end_date):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    """
    syear = start_date.year
    eyear = end_date.year
    return [y for y in range(syear, eyear + 1)]


def _daily_period(date):
    """

    :type date: datetime.date
    :rtype:
    """
    sdt = _set_time_to_date(date, '00:00:00')
    edt = _set_time_to_date(date, '23:59:00')
    return period.Period(sdt, edt, cfg.TT_DATA_INTERVAL)


def _set_time_to_date(date, time_string):
    """
    :type date: datetime.date
    :type time_string: str
    :rtype: datetime.datetime
    """
    time = datetime.datetime.strptime(time_string, '%H:%M:%S').time()
    return datetime.datetime.combine(date, time)


def yearly_period(start_date, end_date):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    :rtype: list[[datetime.datetime, datetime.datetime]]
    """
    syear = start_date.year
    eyear = end_date.year
    periods = [[datetime.datetime(y, 1, 1, 0, 0, 0, 0), datetime.datetime(y, 12, 31, 23, 59, 59, 0)] for y in
               range(syear, eyear + 1)]
    periods[0][0] = datetime.datetime.combine(start_date, datetime.time(0, 0, 0, 0))
    periods[-1][1] = datetime.datetime.combine(end_date, datetime.time(23, 59, 29, 0))
    return periods
