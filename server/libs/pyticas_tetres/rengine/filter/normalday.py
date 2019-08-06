# -*- coding: utf-8 -*-

from pyticas_tetres.rengine.filter.ftypes import ExtFilterGroup
from pyticas_tetres.rengine.filter import incident, workzone, weather, specialevent, snowmanagement

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def explicit_normalday_filter(**kwargs):
    """
    :rtype: ExtFilterGroup
    """
    return ExtFilterGroup([
        weather.normal_explicit(),
        incident.no_incident(distance_limit=kwargs.get('incident_distance_limit', None), **kwargs),
        workzone.no_workzone(distance_limit=kwargs.get('workzone_distance_limit', None), **kwargs),
        specialevent.no_specialevent(distance_limit=kwargs.get('specialevent_distance_limit', None), **kwargs),
        snowmanagement.no_snowmanagement(distance_limit=kwargs.get('snowmanagement_distance_limit', None), **kwargs),
    ], **kwargs)


def implicit_normalday_filter(**kwargs):
    """
    :rtype: ExtFilterGroup
    """
    return ExtFilterGroup([
        weather.normal_implicit(),
        incident.no_incident(distance_limit=kwargs.get('incident_distance_limit', None), **kwargs),
        workzone.no_workzone(distance_limit=kwargs.get('workzone_distance_limit', None), **kwargs),
        specialevent.no_specialevent(distance_limit=kwargs.get('specialevent_distance_limit', None), **kwargs),
        snowmanagement.no_snowmanagement(distance_limit=kwargs.get('snowmanagement_distance_limit', None), **kwargs),
    ], **kwargs)
