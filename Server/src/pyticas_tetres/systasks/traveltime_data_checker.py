# -*- coding: utf-8 -*-
"""
    Travel Time Data Checker module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module checks if travel time data is calculated or not,
    then, calculates travel time data
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import calendar
import datetime

from pyticas import period
from pyticas_tetres import cfg
from pyticas_tetres.da import route
from pyticas_tetres.da.tt import TravelTimeDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine import traveltime, categorization

DAILY_N = 24 * 60 * 60 / cfg.TT_DATA_INTERVAL - 1


def run():
    """
    :return:
    :rtype:
    """
    ttr_da = route.TTRouteDataAccess()
    ttris = ttr_da.list()
    ttr_da.close_session()

    for ttri in ttris:
        _checkup_tt_for_a_route(ttri)


def _checkup_tt_for_a_route(ttri):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :rtype: list[(pyticas_tetres.ttypes.TTRouteInfo, pyticas.ttypes.Period)]
    """
    R_TH = 0.9

    logger = getLogger(__name__)
    logger.debug('>>> checkup travel time data for a route : %s' % ttri)

    no_ttdata = []
    yearly_periods = _get_yearly_periods()
    for prd in yearly_periods:
        year = prd.start_date.year
        n = _get_count_of_tt_data(ttri, prd)
        expected = _get_expected_tt_data(prd)
        logger.debug('  - n of tt data for %s = %s/%d' % (year, n, expected))
        if expected - n >= DAILY_N:
            continue
        logger.debug('  -> check monthly data')

        monthly_periods = _get_monthly_periods_for_a_year(year)
        for mprd in monthly_periods:
            month = mprd.start_date.month
            n = _get_count_of_tt_data(ttri, mprd)
            expected = _get_expected_tt_data(mprd)
            logger.debug('  - n of tt data for %04d-%02d = %s/%d' % (year, month, n, expected))
            if expected - n >= DAILY_N:
                continue

            logger.debug('  -> check monthly data')

            daily_periods = _get_daily_periods_for_a_month(year, month)
            for dprd in daily_periods:
                day = dprd.start_date.day
                n = _get_count_of_tt_data(ttri, dprd)
                expected = _get_expected_tt_data(dprd)
                rate = n / expected
                logger.debug('  - n of tt data for %04d-%02d-%02d = %s/%d (%.2f)' % (
                    year, month, day, n, expected, rate))
                if rate >= R_TH:
                    continue
                logger.debug('     -> it needs to be re-calculated')
                try:
                    from pyticas_tetres.util.traffic_file_checker import has_traffic_files
                    start_date_str, end_date_str = prd.start_date.strftime('%Y-%m-%d'), prd.end_date.strftime('%Y-%m-%d')
                    if not has_traffic_files(start_date_str, end_date_str):
                        logger.warning(
                            'Missing traffic files for performing monthly check up for the time range starting from {} to {}'.format(
                                start_date_str, end_date_str))
                        return
                except Exception as e:
                    logger.warning(
                        'Exception occured while checking if traffic files exist during performing monthly task. Error: {}'.format(e))

                _perform_calculation_of_tt(ttri, prd)

    logger.debug('<<< end of checkup travel time data for a route : %s' % ttri)


def _get_count_of_tt_data(ttri, prd):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type prd: pyticas.ttypes.Period
    :rtype: int
    """
    da_tt = TravelTimeDataAccess(prd.start_date.year)
    cnt = da_tt.get_count(ttri.id, prd.start_date, prd.end_date)
    da_tt.close_session()
    return cnt


def _get_expected_tt_data(prd):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type prd: pyticas.ttypes.Period
    :rtype: int
    """
    tdiff = prd.end_date - prd.start_date
    return max((tdiff.days + 1) * DAILY_N, DAILY_N)


def _perform_calculation_of_tt(ttri, prd):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type prd: pyticas.ttypes.Period
    """
    inserted_ids = traveltime.calculate_a_route(prd, ttri)
    if inserted_ids:
        categorization.categorize(ttri, prd)


def _get_yearly_periods():
    stime = datetime.time(0, 0, 0)
    etime = datetime.time(23, 59, 59)
    periods = []
    for y in _all_years():
        first_day = datetime.date(y, 1, 1)
        last_day = datetime.date(y, 12, 31)
        prd = period.Period(datetime.datetime.combine(first_day, stime),
                            datetime.datetime.combine(last_day, etime),
                            cfg.TT_DATA_INTERVAL)
        periods.append(prd)

    last_day = datetime.date.today() - datetime.timedelta(days=cfg.DAILY_JOB_OFFSET_DAYS)
    last_prd = periods[-1]
    if last_prd.end_date.date() > last_day:
        last_prd.end_date = datetime.datetime.combine(last_day, etime)

    return periods


def _get_monthly_periods_for_a_year(year):
    """

    :type year: int
    :rtype: list[pyticas.ttypes.Period]
    """
    stime = datetime.time(0, 0, 0)
    etime = datetime.time(23, 59, 59)
    periods = []
    for month in range(1, 13):
        (weekday, last_date) = calendar.monthrange(year, month)
        first_day = datetime.date(year, month, 1)
        last_day = datetime.date(year, month, last_date)
        prd = period.Period(datetime.datetime.combine(first_day, stime),
                            datetime.datetime.combine(last_day, etime),
                            cfg.TT_DATA_INTERVAL)
        periods.append(prd)

    last_day = datetime.date.today() - datetime.timedelta(days=cfg.DAILY_JOB_OFFSET_DAYS)
    last_prd = periods[-1]
    if last_prd.end_date.date() > last_day:
        last_prd.end_date = datetime.datetime.combine(last_day, etime)

    return periods


def _get_daily_periods_for_a_month(year, month):
    """

    :type year: int
    :type month: int
    :rtype: list[pyticas.ttypes.Period]
    """
    stime = datetime.time(0, 0, 0)
    etime = datetime.time(23, 59, 59)
    periods = []
    (weekday, last_date) = calendar.monthrange(year, month)
    last_day = datetime.date.today() - datetime.timedelta(days=cfg.DAILY_JOB_OFFSET_DAYS)
    for day in range(1, last_date):
        the_day = datetime.date(year, month, day)
        if the_day > last_day:
            break

        prd = period.Period(datetime.datetime.combine(the_day, stime),
                            datetime.datetime.combine(the_day, etime),
                            cfg.TT_DATA_INTERVAL)
        periods.append(prd)

    return periods


def _all_years():
    """
    :rtype: list[int]
    """
    return [y for y in range(cfg.DATA_ARCHIVE_START_YEAR, datetime.datetime.today().year + 1)]
