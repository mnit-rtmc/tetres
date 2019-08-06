# -*- coding: utf-8 -*-

import datetime

from pyticas_tetres.da.snowmgmt import SnowMgmtDataAccess

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def find_snowmgmts(prd):
    """

    :type prd: pyticas.ttypes.Period
    :rtype: list[pyticas_tetres.ttypes.SnowManagementInfo]
    """
    snmDA = SnowMgmtDataAccess()
    data_list = snmDA.list_by_period(prd.start_date, prd.end_date)
    snmDA.close_session()
    return data_list
