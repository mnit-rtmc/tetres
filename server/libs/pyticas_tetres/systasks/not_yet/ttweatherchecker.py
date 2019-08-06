# -*- coding: utf-8 -*-
"""
    Travel Time and Weather Data Checker module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module checks if travel time data are linked to weather data
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas import period
from pyticas_tetres import cfg
from pyticas_tetres.da import route
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine import traveltime


def run(sdate, edate):
    """
    :type sdate: datetime.date
    :type edate: datetime.date
    :return:
    :rtype:
    """
    ttr_da = route.TTRouteDataAccess()
    ttris = ttr_da.list()
    ttr_da.close_session()

    periods = period.create_periods(sdate, edate, datetime.time(0, 0, 0, 0), datetime.time(23, 59, 0, 0),
                                    cfg.TT_DATA_INTERVAL,
                                    remove_holiday=False,
                                    target_days=[0,1,2,3,4,5,6],
                                    )

    logger = getLogger(__name__)
    logger.debug('>>> checking tt-weather data')
    for prd in periods:
        for ttri in ttris:
            _checkup_tt_weather_for_a_route(ttri, prd)

    logger.debug('<<< end of checking tt-weather data')


def _checkup_tt_weather_for_a_route(ttri, prd):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :rtype: list[(pyticas_tetres.ttypes.TTRouteInfo, pyticas.ttypes.Period)]
    """
    logger = getLogger(__name__)
    total_cnt, missed_cnt = 0, 0
    year = prd.start_date.year
    ttda = traveltime.TravelTimeDataAccess(year)
    tt_data_list = ttda.list_by_period(ttri.id, prd, as_model=True)
    for tti in tt_data_list:
        if not any(tti._tt_weathers):
            missed_cnt += 1
        total_cnt += 1

    if missed_cnt:
        logger.warning('   >  date=%s, route=%s - %s, total_cnt=%d, missed_cnt=%d' % (prd.get_date_string(), ttri.corridor, ttri.name, total_cnt, missed_cnt))
    else:
        logger.debug('   >  date=%s, route=%s - %s, total_cnt=%d, missed_cnt=%d' % (prd.get_date_string(), ttri.corridor, ttri.name, total_cnt, missed_cnt))

