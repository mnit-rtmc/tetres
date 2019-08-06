# -*- coding: utf-8 -*-
"""
    Cleanr module
    ~~~~~~~~~~~~~~~~~~

    This module performs the followings for the given time period:

        - drop the yearly db tables (travel times and the relationship to non-traffic data (tt-* tables))
        - drop the yearly noaa data tables
        - delete all incident data during the given time period
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_tetres.da.incident import IncidentDataAccess
from pyticas_tetres.db.tetres import conn
from pyticas_tetres.db.tetres import model_yearly


def run(start_date, end_date):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    """

    years = _years(start_date, end_date)
    for y in years:
        tt_table = model_yearly.get_tt_table(y)
        tt_table.drop(conn.engine)

        noaa_table = model_yearly.get_noaa_table(y)
        noaa_table.drop(conn.engine)

    da = IncidentDataAccess()
    da.delete_range_all(datetime.datetime.combine(start_date, datetime.time(0, 0, 0)),
                        datetime.datetime.combine(end_date, datetime.time(23, 59, 59)))
    da.commit()
    da.close_session()


def _years(start_date, end_date):
    """

    :type start_date: datetime.date
    :type end_date: datetime.date
    """
    syear = start_date.year
    eyear = end_date.year
    return [y for y in range(syear, eyear + 1)]
