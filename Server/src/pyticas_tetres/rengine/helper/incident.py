# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

def find_incidents(corr, prd):
    """

    :type corr: pyticas.ttypes.CorridorObject
    :type prd: pyticas.ttypes.Period
    :rtype: list[pyticas_tetres.ttypes.IncidentInfo]
    """
    from pyticas_tetres.da import incident

    da_incident = incident.IncidentDataAccess()

    route_name = corr.route.replace('I-', '')
    route_name = route_name.replace('T.H.', '')
    route_name = route_name.replace('U.S.', '')

    idata_list = da_incident.list(sdate=prd.start_date, edate=prd.end_date,
                             corridor=route_name, direction=corr.dir)
    da_incident.close_session()
    return idata_list
