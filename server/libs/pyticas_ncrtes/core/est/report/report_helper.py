# -*- coding: utf-8 -*-

import datetime

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

# def get_first_recovery_section(edata):
#     """
#     :type edata: pyticas_ncrtes.core.est.est_data.ESTData
#     :rtype: pyticas_ncrtes.core.etypes.NormalRatioSection
#     """
#     for threshold in edata.recovery_thresholds:
#         nrss = edata.results.get(threshold)
#         if nrss:
#             return nrss[0]
#     return None

# def get_last_recovery_section(edata, get_all=False):
#     """
#     :type edata: pyticas_ncrtes.core.est.est_data.ESTData
#     :rtype: pyticas_ncrtes.core.etypes.NormalRatioSection
#     """
#     if not get_all:
#         for threshold in edata.recovery_thresholds:
#             if threshold < 0.8:
#                 continue
#             nrss = edata.results.get(threshold)
#             if nrss:
#                 return nrss[-1]
#
#     for threshold in edata.recovery_thresholds:
#         nrss = edata.results.get(threshold)
#         if nrss:
#             return nrss[-1]
#
#     return None

def get_snow_start_time(edata, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: str
    """
    return _get_event_info(edata, 'snow_start_time', **kwargs)

def get_snow_end_time(edata, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: str
    """
    kwargs['pick_first'] = False
    return _get_event_info(edata, 'snow_end_time', **kwargs)

def get_reported_lane_lost_time(edata, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: str
    """
    kwargs['as_list'] = True
    return _get_event_info(edata, 'reported_lost_time', **kwargs)

def get_reported_lane_regain_time(edata, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: str
    """
    kwargs['as_list'] = True
    return _get_event_info(edata, 'reported_regain_time', **kwargs)

def get_weather_type(edata, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: str
    """
    return _get_event_info(edata, 'weather_type', **kwargs)

def get_precipitation(edata, **kwargs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: float
    """
    return _get_event_info(edata, 'precipitation', **kwargs)

def _get_event_info(edata, field_name, **kwargs):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type field_name: str
    :rtype: str
    """
    as_datetime = kwargs.get('as_datetime', False)
    as_list = kwargs.get('as_list', False)
    pick_first = kwargs.get('pick_first', True)

    attr = ''
    if edata.reported_events:
        if as_list:
            attr = []
            for rep in edata.reported_events:
                attr.append(getattr(rep, field_name, ''))
        else:
            for rep in edata.reported_events:
                attr = getattr(rep, field_name, '')
                if pick_first and attr:
                    break

    else:
        attr = getattr(edata.snow_event, field_name, '')

    if isinstance(attr, datetime.datetime) and not as_datetime:
        return attr.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(attr, list) and not as_datetime:
        return [ v.strftime('%Y-%m-%d %H:%M:%S') for v in attr ]
    else:
        return attr