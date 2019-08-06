# -*- coding: utf-8 -*-
"""
Operating Condition (OC) Helper module
"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.rengine.filter import (weather, incident, workzone, specialevent, snowmanagement)
from pyticas_tetres.rengine.filter.ftypes import Or_, And_

NO_CONDITION = 'No'
ANY_CONDITION = 'Any'

WEATHER_TYPE_DRY = 'Dry'
WEATHER_TYPE_DRIZZLE = 'Drizzle'
WEATHER_TYPE_RAIN = 'Rain'
WEATHER_TYPE_SNOW = 'Snow'
WEATHER_TYPES = [WEATHER_TYPE_DRY, WEATHER_TYPE_DRIZZLE, WEATHER_TYPE_RAIN, WEATHER_TYPE_SNOW]
WEATHER_NO_FUNCTION = weather.normal_implicit
WEATHER_ANY_FUNCTION = weather.has_weather_implicit
WEATHER_TYPE_FUNCTIONS = {
    WEATHER_TYPE_DRY: weather.normal_implicit,
    WEATHER_TYPE_DRIZZLE: weather.type_drizzle,
    WEATHER_TYPE_RAIN: weather.type_rain,
    WEATHER_TYPE_SNOW: weather.type_snow,
}

WEATHER_INTENSITY_LIGHT = 'Light'
WEATHER_INTENSITY_MODERATE = 'Moderate'
WEATHER_INTENSITY_HEAVY = 'Heavy'
WEATHER_INTENSITIES = [WEATHER_INTENSITY_LIGHT, WEATHER_INTENSITY_MODERATE, WEATHER_INTENSITY_HEAVY]
WEATHER_INTENSITY_FUNCTIONS = {
    WEATHER_INTENSITY_LIGHT: weather.intensity_moderate,
    WEATHER_INTENSITY_MODERATE: weather.intensity_moderate,
    WEATHER_INTENSITY_HEAVY: weather.intensity_heavy
}

ITYPES = []
""":type: list[pyticas_tetres.ttypes.IncidentTypeInfo] """
INCIDENT_NO_FUNCTION = incident.no_incident
INCIDENT_ANY_FUNCTION = incident.has_incident
INCIDENT_TYPE_HAZARD = 'Hazard'
INCIDENT_TYPE_ROADWORK = 'Roadwork'
INCIDENT_TYPE_STALL = 'Stall'
INCIDENT_TYPE_CRASH = 'Crash'
INCIDENT_TYPES = [INCIDENT_TYPE_HAZARD, INCIDENT_TYPE_ROADWORK, INCIDENT_TYPE_STALL, INCIDENT_TYPE_CRASH]
INCIDENT_TYPE_FUNCTIONS = {
    INCIDENT_TYPE_HAZARD: incident.iris_type_hazard,
    INCIDENT_TYPE_ROADWORK: incident.iris_type_roadwork,
    INCIDENT_TYPE_STALL: incident.iris_type_stall,
    INCIDENT_TYPE_CRASH: incident.iris_type_crash,
}

INCIDENT_IMPACT_ROAD_CLOSED = 'Road Closed'
INCIDENT_IMPACT_2PLUS_LANE_CLOSED = '2+ Lane Closed'
INCIDENT_IMPACT_1LANE_CLOSED = '1 Lane Closed'
INCIDENT_IMPACT_NOT_BLOCKING = 'Not Blocking'
INCIDENT_IMPACT_ONLY_ON_SHOULDER = 'Only on Shoulder'
INCIDENT_IMPACTS = [INCIDENT_IMPACT_ROAD_CLOSED, INCIDENT_IMPACT_2PLUS_LANE_CLOSED,
                    INCIDENT_IMPACT_1LANE_CLOSED, INCIDENT_IMPACT_NOT_BLOCKING, INCIDENT_IMPACT_ONLY_ON_SHOULDER]
INCIDENT_IMPACT_FUNCTIONS = {
    INCIDENT_IMPACT_ROAD_CLOSED: None,  # TODO
    INCIDENT_IMPACT_2PLUS_LANE_CLOSED: incident.impact_two_plus_lane_closed,
    INCIDENT_IMPACT_1LANE_CLOSED: incident.impact_lane_closed,
    INCIDENT_IMPACT_NOT_BLOCKING: incident.impact_not_blocking,
    INCIDENT_IMPACT_ONLY_ON_SHOULDER: None,  # TODO
}

INCIDENT_SEVERITY_FATAL = 'Fatal'
INCIDENT_SEVERITY_SERIOUS_INSURY = 'Serious Injury'
INCIDENT_SEVERITY_PERSONAL_INSURY = 'Personal Injury'
INCIDENT_SEVERITY_PROPERTY_DEMAGE = 'Property Damage'
INCIDENT_SEVERITIES = [INCIDENT_SEVERITY_FATAL, INCIDENT_SEVERITY_SERIOUS_INSURY,
                       INCIDENT_SEVERITY_PERSONAL_INSURY, INCIDENT_SEVERITY_PROPERTY_DEMAGE]
INCIDENT_SEVERITY_FUNCTIONS = {
    INCIDENT_SEVERITY_FATAL: incident.severity_fatal,
    INCIDENT_SEVERITY_SERIOUS_INSURY: incident.severity_injury_serious,
    INCIDENT_SEVERITY_PERSONAL_INSURY: incident.severity_injury_personal,
    INCIDENT_SEVERITY_PROPERTY_DEMAGE: incident.severity_property_damage,
}

WORKZONE_NO_FUNCTION = workzone.no_workzone
WORKZONE_ANY_FUNCTION = workzone.has_workzone
WORKZONE_LANE_CONFIGS = []
WORKZONE_LANE_CONFIG_FUNCTIONS = {}


def wz_laneconfig_decorator(from_lane, to_lane):
    def func():
        return workzone.lane_config(from_lane, to_lane)

    return func


def wz_length_decorator(min_length, max_length):
    def func(**kwargs):
        return workzone.closed_length(min_length, max_length, **kwargs)

    return func


for from_lane in range(2, 6):
    for to_lane in range(1, from_lane):
        key = '%d to %d' % (from_lane, to_lane)
        WORKZONE_LANE_CONFIGS.append(key)
        WORKZONE_LANE_CONFIG_FUNCTIONS[key] = wz_laneconfig_decorator(from_lane, to_lane)

WORKZONE_CLOSED_LENGTH_SHORT = 'Short'
WORKZONE_CLOSED_LENGTH_MEDIUM = 'Medium'
WORKZONE_CLOSED_LENGTH_LONG = 'Long'
WORKZONE_CLOSED_LENGTHS = [WORKZONE_CLOSED_LENGTH_SHORT, WORKZONE_CLOSED_LENGTH_MEDIUM, WORKZONE_CLOSED_LENGTH_LONG]

WORKZONE_LOCATION_UPSTREAM = 'Upstream'
WORKZONE_LOCATION_OVERLAPPED = 'Overlapped'
WORKZONE_LOCATION_DOWNSTREAM = 'Downstream'
WORKZONE_LOCATIONS = [WORKZONE_LOCATION_UPSTREAM, WORKZONE_LOCATION_OVERLAPPED, WORKZONE_LOCATION_DOWNSTREAM]
WORKZONE_LOCATION_FUNCTIONS = {
    WORKZONE_LOCATION_UPSTREAM: workzone.loc_upstream,
    WORKZONE_LOCATION_OVERLAPPED: workzone.loc_overlapped,
    WORKZONE_LOCATION_DOWNSTREAM: workzone.loc_downstream,
}

SPECIALEVENT_NO_FUNCTION = specialevent.no_specialevent
SPECIALEVENT_ANY_FUNCTION = specialevent.has_specialevent

SPECIALEVENT_DISTANCE_NEAR = 'Near'
SPECIALEVENT_DISTANCE_MIDDLE = 'Middle'
SPECIALEVENT_DISTANCE_FAR = 'Far'


def se_distance_decorator(min_length, max_length):
    def func():
        return specialevent.distance(min_length, max_length)

    return func


SPECIALEVENT_EVENT_SIZE_SMALL = 'Small'
SPECIALEVENT_EVENT_SIZE_MEDIUM = 'Medium'
SPECIALEVENT_EVENT_SIZE_LARGE = 'Large'
SPECIALEVENT_EVENT_SIZES = [
    SPECIALEVENT_EVENT_SIZE_SMALL, SPECIALEVENT_EVENT_SIZE_MEDIUM, SPECIALEVENT_EVENT_SIZE_LARGE
]

def se_event_size_decorator(min_attendance, max_attendance):
    def func():
        return specialevent.attendance(min_attendance, max_attendance)

    return func

SPECIALEVENT_EVENT_TIME_BEFORE = 'Before'
SPECIALEVENT_EVENT_TIME_DURING_AFTER = 'During-After'
SPECIALEVENT_EVENT_TIMES = [SPECIALEVENT_EVENT_TIME_BEFORE, SPECIALEVENT_EVENT_TIME_DURING_AFTER]
SPECIALEVENT_EVENT_TIME_FUNCTIONS = {
    SPECIALEVENT_EVENT_TIME_BEFORE: specialevent.type_arrival,
    SPECIALEVENT_EVENT_TIME_DURING_AFTER: specialevent.type_departure
}
SNOWMANAGEMENT_NO_FUNCTION = snowmanagement.no_snowmanagement
SNOWMANAGEMENT_ANY_FUNCTION = snowmanagement.has_snowmanagement


def get_weather_filter(filter_list, op_param):
    """

    Properties of WeatherFilterInfo
    --------------------------------
    - type : Dry, Drizzle, Rain, Snow
    - intensity : Light, Moderate, Heavy


    :type filter_list: list[pyticas_tetres.ttypes.WeatherConditionInfo]
    :type op_param: pyticas_tetres.ttypes.OperatingConditionParamInfo
    :rtype: pyticas_tetres.rengine.filter.ftypes.IExtFilter
    """
    if not filter_list:
        return None
    funcs = []
    for finfo in filter_list:
        if finfo.type == NO_CONDITION:
            funcs.append(WEATHER_NO_FUNCTION())
            continue
        if finfo.type == ANY_CONDITION:
            funcs.append(WEATHER_ANY_FUNCTION())
            continue
        if finfo.type not in WEATHER_TYPES:
            continue
        if (not _check_field(finfo.type, WEATHER_TYPES)
                or not _check_field(finfo.intensity, WEATHER_INTENSITIES)):
            continue
        and_funcs = []
        if WEATHER_TYPE_FUNCTIONS.get(finfo.type, None):
            and_funcs.append(WEATHER_TYPE_FUNCTIONS[finfo.type]())
        if WEATHER_INTENSITY_FUNCTIONS.get(finfo.intensity, None):
            and_funcs.append(WEATHER_INTENSITY_FUNCTIONS[finfo.intensity]())
        ext_filter = And_(*and_funcs)
        funcs.append(ext_filter)
    return Or_(*funcs)


def get_incident_filter(filter_list, op_param):
    """
     
    :type filter_list: list[pyticas_tetres.ttypes.IncidentConditionInfo]
    :type op_param: pyticas_tetres.ttypes.OperatingConditionParamInfo
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    if not filter_list:
        return None

    keep_result_in_minute = op_param.incident_keep_in_minute
    downstream_distance_limit = op_param.incident_downstream_distance_limit
    upstream_distance_limit = op_param.incident_upstream_distance_limit

    args = {'downstream_distance_limit' : downstream_distance_limit,
            'upstream_distance_limit' : upstream_distance_limit,
            'keep_result_in_minute' : keep_result_in_minute}

    funcs = []
    for finfo in filter_list:
        if finfo.type == NO_CONDITION:
            funcs.append(INCIDENT_NO_FUNCTION(downstream_distance_limit=downstream_distance_limit, upstream_distance_limit=upstream_distance_limit))
            continue
        if finfo.type == ANY_CONDITION:
            funcs.append(INCIDENT_ANY_FUNCTION(**args))
            continue
        if (not _check_field(finfo.type, INCIDENT_TYPES)
                or not _check_field(finfo.impact, INCIDENT_IMPACTS)
                or not _check_field(finfo.severity, INCIDENT_SEVERITIES)):
            continue
        and_funcs = []
        if INCIDENT_TYPE_FUNCTIONS.get(finfo.type, None):
            and_funcs.append(INCIDENT_TYPE_FUNCTIONS[finfo.type](**args))
        if INCIDENT_IMPACT_FUNCTIONS.get(finfo.impact, None):
            and_funcs.append(INCIDENT_IMPACT_FUNCTIONS[finfo.impact](**args))
        if INCIDENT_SEVERITY_FUNCTIONS.get(finfo.severity, None):
            and_funcs.append(INCIDENT_SEVERITY_FUNCTIONS[finfo.severity](**args))
        ext_filter = And_(*and_funcs)
        funcs.append(ext_filter)
    return Or_(*funcs)


def get_workzone_filter(filter_list, op_param):
    """
     
    :type filter_list: list[pyticas_tetres.ttypes.WorkzoneConditionInfo]
    :type op_param: pyticas_tetres.ttypes.OperatingConditionParamInfo
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    if not filter_list:
        return None

    downstream_distance_limit = op_param.workzone_downstream_distance_limit
    upstream_distance_limit = op_param.workzone_upstream_distance_limit

    args = {'downstream_distance_limit' : downstream_distance_limit,
            'upstream_distance_limit' : upstream_distance_limit}

    wz_length_short = (op_param.workzone_length_short_from, op_param.workzone_length_short_to)
    wz_length_medium = (op_param.workzone_length_medium_from, op_param.workzone_length_medium_to)
    wz_length_long = (op_param.workzone_length_long_from, op_param.workzone_length_long_to)

    WORKZONE_CLOSED_LENGTH_FUNCTIONS = {
        WORKZONE_CLOSED_LENGTH_SHORT: wz_length_decorator(*wz_length_short),
        WORKZONE_CLOSED_LENGTH_MEDIUM: wz_length_decorator(*wz_length_medium),
        WORKZONE_CLOSED_LENGTH_LONG: wz_length_decorator(*wz_length_long),
    }

    funcs = []
    for finfo in filter_list:
        if finfo.lane_config == NO_CONDITION:
            funcs.append(WORKZONE_NO_FUNCTION(**args))
            continue
        if finfo.lane_config == ANY_CONDITION:
            funcs.append(WORKZONE_ANY_FUNCTION(**args))
            continue
        if (not _check_field(finfo.lane_config, WORKZONE_LANE_CONFIGS)
                or not _check_field(finfo.lane_closed_length, WORKZONE_CLOSED_LENGTHS)
                or not _check_field(finfo.relative_location, WORKZONE_LOCATIONS)):
            continue
        and_funcs = []
        if WORKZONE_LANE_CONFIG_FUNCTIONS.get(finfo.lane_config, None):
            and_funcs.append(WORKZONE_LANE_CONFIG_FUNCTIONS[finfo.lane_config](*args))
        if WORKZONE_CLOSED_LENGTH_FUNCTIONS.get(finfo.lane_closed_length, None):
            and_funcs.append(WORKZONE_CLOSED_LENGTH_FUNCTIONS[finfo.lane_closed_length](*args))
        if WORKZONE_LOCATION_FUNCTIONS.get(finfo.relative_location, None):
            and_funcs.append(WORKZONE_LOCATION_FUNCTIONS[finfo.relative_location](*args))
        ext_filter = And_(*and_funcs)
        funcs.append(ext_filter)
    return Or_(*funcs)


def get_specialevent_filter(filter_list, op_param):
    """
     
    :type filter_list: list[pyticas_tetres.ttypes.SpecialeventConditionInfo]
    :type op_param: pyticas_tetres.ttypes.OperatingConditionParamInfo
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    if not filter_list:
        return None

    se_distance_near = (op_param.specialevent_distance_near_from, op_param.specialevent_distance_near_to)
    se_distance_middle = (op_param.specialevent_distance_middle_from, op_param.specialevent_distance_middle_to)
    se_distance_far = (op_param.specialevent_distance_far_from, op_param.specialevent_distance_far_to)

    se_size_small = (op_param.specialevent_size_small_from, op_param.specialevent_size_small_to)
    se_size_medium = (op_param.specialevent_size_medium_from, op_param.specialevent_size_medium_to)
    se_size_large = (op_param.specialevent_size_large_from, op_param.specialevent_size_large_to)

    SPECIALEVENT_DISTANCE_FUNCTIONS = {
        SPECIALEVENT_DISTANCE_NEAR: se_distance_decorator(*se_distance_near),
        SPECIALEVENT_DISTANCE_MIDDLE: se_distance_decorator(*se_distance_middle),
        SPECIALEVENT_DISTANCE_FAR: se_distance_decorator(*se_distance_far),
    }

    SPECIALEVENT_EVENT_SIZE_FUNCTIONS = {
        SPECIALEVENT_EVENT_SIZE_SMALL: se_event_size_decorator(*se_size_small),
        SPECIALEVENT_EVENT_SIZE_MEDIUM: se_event_size_decorator(*se_size_medium),
        SPECIALEVENT_EVENT_SIZE_LARGE: se_event_size_decorator(*se_size_large)
    }

    funcs = []
    for finfo in filter_list:
        if finfo.event_size == NO_CONDITION:
            funcs.append(SPECIALEVENT_NO_FUNCTION())
            continue
        if finfo.event_size == ANY_CONDITION:
            funcs.append(SPECIALEVENT_ANY_FUNCTION())
            continue
        if (not _check_field(finfo.event_size, SPECIALEVENT_EVENT_SIZES)
                or not _check_field(finfo.event_time, SPECIALEVENT_EVENT_TIMES)):
            continue
        and_funcs = []
        if SPECIALEVENT_DISTANCE_FUNCTIONS.get(finfo.distance, None):
            and_funcs.append(SPECIALEVENT_DISTANCE_FUNCTIONS[finfo.distance]())
        if SPECIALEVENT_EVENT_SIZE_FUNCTIONS.get(finfo.event_size, None):
            and_funcs.append(SPECIALEVENT_EVENT_SIZE_FUNCTIONS[finfo.event_size]())
        if SPECIALEVENT_EVENT_TIME_FUNCTIONS.get(finfo.event_time, None):
            and_funcs.append(SPECIALEVENT_EVENT_TIME_FUNCTIONS[finfo.event_time]())
        ext_filter = And_(*and_funcs)
        funcs.append(ext_filter)
    return Or_(*funcs)


def get_snowmanagement_filter(filter_list, op_param):
    """
     
    :type filter_list: list[pyticas_tetres.ttypes.SnowmanagementConditionInfo]
    :type op_param: pyticas_tetres.ttypes.OperatingConditionParamInfo
    :rtype: pyticas_tetres.rengine.filter.ftypes.ExtFilter
    """
    if not filter_list:
        return None

    for finfo in filter_list:
        if finfo.road_condition == NO_CONDITION:
            return SNOWMANAGEMENT_NO_FUNCTION()
        if finfo.road_condition == ANY_CONDITION:
            return SNOWMANAGEMENT_ANY_FUNCTION()
    return None


def _check_field(fname, container):
    return (not fname or fname in container)
