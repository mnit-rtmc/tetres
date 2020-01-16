# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import tb
from pyticas_tetres.da.route import TTRouteDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine import traveltime_info

def run(target_date):
    """

    :type target_date: datetime.datetime
    :return:
    """
    ttr_route_da = TTRouteDataAccess()
    route_list = ttr_route_da.list()
    ttr_route_da.close_session()

    for ttri in route_list:
        try:
            traveltime_info.calculate_TOD_reliabilities(ttri.id, target_date)
        except Exception as ex:
            tb.traceback(ex)
            getLogger(__name__).warning('Fail to calculate TOD reliabilities for route=%d' % ttri.id)


