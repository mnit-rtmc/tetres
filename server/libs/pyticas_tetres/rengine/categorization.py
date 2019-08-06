# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.da.tt import TravelTimeDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine.cats import weather, incident, snowmgmt, specialevent, workzone


def categorize(ttri, prd, **kwargs):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type prd: pyticas.ttypes.Period
    :rtype: dict
    """
    tt_da = TravelTimeDataAccess(prd.start_date.year)
    tt_data_list = tt_da.list_by_period(ttri.id, prd)
    tt_da.close_session()

    n_data = len(tt_data_list)
    res = {
        'route_id': ttri.id,
        'duration': prd.get_period_string(),
        'tt_counts': n_data,
        'has_error': False,
        'inserted': {}
    }

    if not tt_data_list:
        getLogger(__name__).warning(
            '!categorization.categorize(): no data (%s, %s)' % (ttri.name, prd.get_period_string()))
        res['has_error'] = True
        return res

    categorizers = kwargs.get('categorizers', [weather, workzone, specialevent, snowmgmt, incident])
    for categorizer in categorizers:
        n_inserted = categorizer.categorize(ttri, prd, tt_data_list, **kwargs)
        res['inserted'][categorizer.__name__] = n_inserted
        if n_inserted < 0:
            res['has_error'] = True

    return res
