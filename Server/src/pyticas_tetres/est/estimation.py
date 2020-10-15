# -*- coding: utf-8 -*-
import uuid

from pyticas_tetres.db.tetres import conn

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import time

from pyticas.tool import timeutil
from pyticas_tetres.logger import getLogger

from pyticas_tetres import cfg
from pyticas_tetres.rengine import extractor, reliability
from pyticas_tetres.rengine.filter.ftypes import ExtFilterGroup, ExtData
from pyticas_tetres.est.helper import util
from pyticas_tetres.est import report, operating_condition as oc_filter_creator
import gc

def estimate(eparam, uid=None):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type uid: str
    :rtype:
    """
    use_pause = False

    if use_pause:
        a = input('Enter to continue (Starting Estimation): ')

    logger = getLogger(__name__)
    # retrieve travel time and non-traffic data during the given time period
    # each filter-group represents a `regime` as operating condition

    proc_start_time = time.time()
    logger.debug('>> Retrieving TT data from DB')
    operating_conditions = _retrieve_tt_data(eparam)
    logger.debug('<< End of retrieving TT data from DB (elapsed time=%s)' % (
    timeutil.human_time(seconds=(time.time() - proc_start_time))))

    if use_pause:
        b = input('Enter to continue (Data Retrieved): ')

    logger.debug('>> Number of Data for Each Operation Condition')
    for gidx, oc in enumerate(operating_conditions):
        logger.debug('  - %s : %d' % (eparam.operating_conditions[gidx].name, len(oc.whole_data) if oc.whole_data else 0))
    logger.debug('>> End of Number of Data for Each Operation Condition')

    sdate = eparam.get_start_date()
    edate = eparam.get_end_date()
    mode_TOD = eparam.estmation_mode.mode_tod
    mode_Whole = eparam.estmation_mode.mode_whole

    mode_yearly, mode_monthly = False, False
    if sdate.year != edate.year:
        mode_yearly = True
        mode_monthly = True
    elif sdate.month != edate.month:
        mode_monthly = True

    proc_start_time = time.time()

    logger.debug('>> Preparing Yearly-Monthly-Daily Data')
    _prepare_yearly_monthly_daily_data(eparam, operating_conditions)
    logger.debug('<< End of preparing Yearly-Monthly-Daily Data (elapsed time=%s)' % (
                    timeutil.human_time(seconds=(time.time() - proc_start_time))))

    proc_start_time = time.time()
    logger.debug('>> Calculate reliabilities for each operating condition')

    # estimate reliabilities
    whole, yearly, monthly, daily, TOD_whole, TOD_yearly, TOD_monthly = [], [], [], [], [], [], []
    for gidx, oc in enumerate(operating_conditions):
        proc_start_time2 = time.time()
        logger.debug('>>> Operating Condition : %s' % eparam.operating_conditions[gidx].name)

        if not oc.whole_data:
            logger.debug('  - No Data for %s' % eparam.operating_conditions[gidx].name)
            if mode_Whole:
                whole.append([])
                if mode_yearly:
                    yearly.append(([], []))
                if mode_monthly:
                    monthly.append(([], []))
                daily.append(([], []))
            if mode_TOD:
                TOD_whole.append([])
                if mode_yearly:
                    TOD_yearly.append([])
                if mode_monthly:
                    TOD_monthly.append([])
            continue

        # Estimation Mode = 'Whole Time Period Reliability'
        if mode_Whole:
            proc_start_time3 = time.time()
            logger.debug('>>>> calculate whole time period reliabilities')
            res = _calculate_reliabilities_whole(eparam, oc)
            whole.append(res)
            logger.debug('<<<< end of calculation of whole time period reliabilities (elapsed time=%s, n=%d)' % (
            timeutil.human_time(seconds=(time.time() - proc_start_time3)), len(res) if res else 0))

            if mode_yearly:
                proc_start_time3 = time.time()
                logger.debug('>>>> calculate yearly reliabilities')
                res_yearly, res_years = _calculate_reliabilities_by_ymd(eparam, oc.yearly_data)
                yearly.append((res_yearly, res_years))
                logger.debug('<<<< end of calculation of yearly reliabilities (elapsed time=%s, n=%d)' % (
                timeutil.human_time(seconds=(time.time() - proc_start_time3)), len(res_yearly) if res_yearly else 0))

            if mode_monthly:
                proc_start_time3 = time.time()
                logger.debug('>>>> calculate monthly reliabilities')
                res_monthly, res_months = _calculate_reliabilities_by_ymd(eparam, oc.monthly_data)
                monthly.append((res_monthly, res_months))
                logger.debug('<<<< end of calculation of monthly reliabilities (elapsed time=%s, n=%d)' % (
                timeutil.human_time(seconds=(time.time() - proc_start_time3)), len(res_monthly) if res_monthly else 0))

            proc_start_time3 = time.time()
            logger.debug('>>>> calculate daily reliabilities')
            res_daily, res_dates = _calculate_reliabilities_by_ymd(eparam, oc.daily_data)
            daily.append((res_daily, res_dates))
            logger.debug('<<<< end of calculation of daily reliabilities (elapsed time=%s, n=%d)' % (
            timeutil.human_time(seconds=(time.time() - proc_start_time3)), len(res_daily) if res_daily else 0))

        # Estimation Mode = 'Time of Day Reliability'
        if mode_TOD:
            proc_start_time3 = time.time()
            logger.debug('>>>> calculate whole TOD reliabilities')
            res_tod = _calculate_reliabilities_tod_whole(eparam, oc)
            TOD_whole.append(res_tod)
            logger.debug('<<<< end of calculation of TOD reliabilities (elapsed time=%s, n=%d)' % (
            timeutil.human_time(seconds=(time.time() - proc_start_time3)), len(res_tod) if res_tod else 0))

            if mode_yearly:
                proc_start_time3 = time.time()
                logger.debug('>>>> calculate yearly TOD reliabilities')
                res_tod_yearly = _calculate_reliabilities_tod_by_ymd(eparam, oc.all_years, oc.yearly_data)
                TOD_yearly.append(res_tod_yearly)
                logger.debug('<<<< end of calculation of yearly TOD reliabilities (elapsed time=%s, n=%d)' % (
                timeutil.human_time(seconds=(time.time() - proc_start_time3)), len(res_tod_yearly) if res_tod_yearly else 0))

            if mode_monthly:
                proc_start_time3 = time.time()
                logger.debug('>>>> calculate monthly TOD reliabilities')
                res_tod_monthly = _calculate_reliabilities_tod_by_ymd(eparam, oc.all_months, oc.monthly_data)
                TOD_monthly.append(res_tod_monthly)
                logger.debug('<<<< end of calculation of monthly TOD reliabilities (elapsed time=%s, n=%d)' % (
                timeutil.human_time(seconds=(time.time() - proc_start_time3)), len(res_tod_monthly) if res_tod_monthly else 0))

        logger.debug('<<< end of operating condition (elapsed time=%s)' % (
        timeutil.human_time(seconds=(time.time() - proc_start_time2))))

    logger.debug('<< End of calculation of reliabilities (elapsed time=%s)' % (
    timeutil.human_time(seconds=(time.time() - proc_start_time))))
    # print for debug
    # pprint.pprint(whole)

    if use_pause:
        c = input('Enter to continue (All Data Categorized): ')

    # write result
    if not uid:
        uid = str(uuid.uuid4())

    # write graphs
    report.write(uid, eparam, operating_conditions, (
        whole, yearly, monthly, daily, TOD_whole, TOD_yearly, TOD_monthly
    ))

    del operating_conditions
    gc.collect()


def _retrieve_tt_data(eparam):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :rtype: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    """
    # da_route = route.TTRouteDataAccess()
    # ttri = da_route.list()[0]
    # da_route.close()
    ttri = eparam.travel_time_route
    sdate = eparam.get_start_date()
    edate = eparam.get_end_date()
    stime = eparam.get_start_time()
    etime = eparam.get_end_time()

    ext_filter_groups = []
    """:type: list[ExtFilterGroup] """
    for finfo in eparam.operating_conditions:
        efg = ExtFilterGroup([
            oc_filter_creator.get_weather_filter(finfo.weather_conditions, eparam.oc_param),
            oc_filter_creator.get_incident_filter(finfo.incident_conditions, eparam.oc_param),
            oc_filter_creator.get_workzone_filter(finfo.workzone_conditions, eparam.oc_param),
            oc_filter_creator.get_specialevent_filter(finfo.specialevent_conditions, eparam.oc_param),
            oc_filter_creator.get_snowmanagement_filter(finfo.snowmanagement_conditions, eparam.oc_param),
        ], finfo.name)
        ext_filter_groups.append(efg)

    target_days = eparam.weekdays.get_weekdays()
    remove_holiday = eparam.except_holiday
    except_dates = []
    extractor.extract_tt(ttri.id,
                         sdate,
                         edate,
                         stime,
                         etime,
                         ext_filter_groups,
                         target_days=target_days,
                         remove_holiday=remove_holiday,
                         except_dates=except_dates)

    return ext_filter_groups


def _prepare_yearly_monthly_daily_data(eparam, operating_conditions):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    """
    sdate, edate = util.get_date(eparam.start_date), util.get_date(eparam.end_date)
    all_years = util.years(sdate, edate)
    all_months = util.months(sdate, edate)
    all_dates = util.dates(sdate, edate, weekdays=eparam.weekdays.get_weekdays(), except_holiday=eparam.except_holiday)
    all_times = [ dt.time() for (h, m, dt) in _time_of_day_generator(eparam) ]

    for oc in operating_conditions:
        oc.all_years = all_years
        oc.all_months = all_months
        oc.all_dates = all_dates
        oc.all_times = all_times
        if not oc.whole_data:
            continue
        prev_day = util.get_datetime(oc.whole_data[0].tti.time).date()
        years, results, one_year_data, one_month_data, one_day_data = [], [], [], [], []

        for ext_data in oc.whole_data:
            cur_day = util.get_datetime(ext_data.tti.time).date()
            if cur_day.year != prev_day.year:
                oc.yearly_data.append((prev_day.year, one_year_data))
                one_year_data = []
            if cur_day.month != prev_day.month:
                oc.monthly_data.append(([prev_day.year, prev_day.month], one_month_data))
                one_month_data = []
            if cur_day != prev_day:
                oc.daily_data.append((prev_day, one_day_data))
                one_day_data = []

            prev_day = cur_day
            one_year_data.append(ext_data)
            one_month_data.append(ext_data)
            one_day_data.append(ext_data)

        if one_year_data:
            oc.yearly_data.append((prev_day.year, one_year_data))
        if one_month_data:
            oc.monthly_data.append(([prev_day.year, prev_day.month], one_month_data))
        if one_day_data:
            oc.daily_data.append((prev_day, one_day_data))


def _calculate_reliabilities_whole(eparam, oc):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type oc: pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup
    :rtype: dict
    """
    return reliability.calculate(eparam.travel_time_route, oc.whole_data)


def _calculate_reliabilities_by_ymd(eparam, data_set):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type data_set: Union(list[(int, list[ExtData])],
                          list[([int, int], list[ExtData])],
                          list[(datetime.date, list[ExtData])])
    :rtype: list[dict], list
    """
    if not data_set:
        return None, None

    results, ymds = [], []
    for ymd, a_ymd_data in data_set:
        if a_ymd_data:
            res = reliability.calculate(eparam.travel_time_route, a_ymd_data)
            results.append(res)
            ymds.append(ymd)

    return results, ymds


def _calculate_reliabilities_tod_whole(eparam, oc):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type oc: pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup
    :rtype: list[dict]
    """
    results = []
    for h, m, dt in _time_of_day_generator(eparam):
        ext_datas = _extract_tod_data(oc.whole_data, h, m)
        if ext_datas:
            res = reliability.calculate(eparam.travel_time_route, ext_datas)
            results.append(res)
        else:
            results.append(None)

    return results


def _calculate_reliabilities_tod_by_ymd(eparam, all_ymds, data_set):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type all_ymds: Union(list[int], list[[int, int]])
    :type data_set: Union(list[(int, list[ExtData])],
                          list[([int, int], list[ExtData])],
                          list[(datetime.date, list[ExtData])])
    :rtype: list[list[dict]]
    """
    results = []
    for ymd in all_ymds:
        ext_data_list = None
        for idx, (_ymd, _ext_data_list) in enumerate(data_set):
            if _ymd == ymd:
                ext_data_list = _ext_data_list
                break
        if ext_data_list:
            a_ymd_results = []
            for h, m, dt in _time_of_day_generator(eparam):
                ext_datas = _extract_tod_data(ext_data_list, h, m)
                res = reliability.calculate(eparam.travel_time_route, ext_datas)
                a_ymd_results.append(res)
            results.append(a_ymd_results)
        else:
            results.append(None)

    return results


def _time_of_day_generator(eparam):
    """

    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :rtype: list[int, int, datetime.datetime]
    """
    today = datetime.date.today()
    stime = datetime.datetime.combine(today, util.get_time(eparam.start_time)).replace(second=0, microsecond=0)
    etime = datetime.datetime.combine(today, util.get_time(eparam.end_time)).replace(second=0, microsecond=0)
    cursor = stime
    step = datetime.timedelta(seconds=cfg.TT_DATA_INTERVAL)
    while cursor <= etime:
        h, m = cursor.hour, cursor.minute
        yield h, m, cursor
        cursor += step

def _extract_tod_data(data_set, hour, minute):
    """
    :type data_set: list[ExtData]
    :type hour: int
    :type minute: int
    :rtype: list[ExtData]
    """
    if not data_set:
        return data_set

    return [ext_data for ext_data in data_set
            if (ext_data.tti.time.hour == hour and ext_data.tti.time.minute == minute)]
