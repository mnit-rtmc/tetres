# -*- coding: utf-8 -*-

import datetime

from pyticas_tetres.da.specialevent import SpecialEventDataAccess

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def find_specialevents(prd, ARRIVAL_WINDOW_IN_MINUTE, DEPARTURE_WINDOW_IN_MINUTE1, DEPARTURE_WINDOW_IN_MINUTE2):
    """

    :type prd: pyticas.ttypes.Period
    :type ARRIVAL_WINDOW_IN_MINUTE: int
    :type DEPARTURE_WINDOW_IN_MINUTE1: int
    :type DEPARTURE_WINDOW_IN_MINUTE2: int
    :rtype: list[pyticas_tetres.ttypes.SpecialEventInfo]
    """
    seDA = SpecialEventDataAccess()
    sdt = prd.start_date - datetime.timedelta(minutes=ARRIVAL_WINDOW_IN_MINUTE)
    edt = prd.end_date + datetime.timedelta(minutes=DEPARTURE_WINDOW_IN_MINUTE2)

    data_list = seDA.search_date_range(sdt, edt)
    seDA.close_session()
    return data_list
