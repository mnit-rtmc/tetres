# -*- coding: utf-8 -*-
import math

from pyticas_noaa.isd import isdtypes
from pyticas_tetres import ttypes

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

def write_operating_condition_info_sheet(eparam, wb):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type wb: xlsxwriter.Workbook
    """
    ws = wb.add_worksheet('Operating Coditions (OC)')

    ws.write_row(0, 0, ['Index', 'Name', 'Description'])
    for idx, ef in enumerate(eparam.operating_conditions):
        ws.write_row(idx+1, 0, [idx, ef.name, ef.desc])


def write_whole_data_sheet(eparam, ext_filter_groups, wb):
    """

    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type ext_filter_groups: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    """
    for idx, ef in enumerate(ext_filter_groups):
        ws = wb.add_worksheet('data (OC=%d)' % idx)
        ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
        ws.write_row(1, 0, ['', '', '', '',
                            'weather', '', '', '', '',
                            'incident', '', '', '', '', '', '',
                            'workzone', '', '', '', '',
                            'special-event', '', '', '',
                            'snow-management'
                            ])

        ws.write_row(2, 0, ['time', 'tt', 'speed', 'vmt',
                            'usaf', 'wban', 'precip_type', 'precip', 'precip_intensity', # weather
                            'type', 'impact', 'cdts', 'udts', 'xdts', 'distance', 'off_distance', # incident
                            'name', 'lane_config', 'closed_length', 'location', 'off_distance', # workzone
                            'name', 'distance', 'attendance', 'type', # special event
                            'truck_route', 'road_status', 'location', 'off_distance'
                            ])

        for idx, extdata in enumerate(ef.whole_data):
            dts = extdata.tti.time.strftime('%Y-%m-%d %H:%M')
            tt = extdata.tti.tt if extdata.tti.tt != math.inf and extdata.tti.tt and extdata.tti.tt > 0 else ''
            u = extdata.tti.speed if extdata.tti.speed != math.inf and extdata.tti.speed and extdata.tti.speed > 0 else ''
            vmt = extdata.tti.vmt if extdata.tti.vmt != math.inf and extdata.tti.vmt and extdata.tti.vmt > 0 else ''

            ws.write_row(idx + 3, 0, [dts, tt, u, vmt]
                         + get_weather_values(extdata)
                         + get_incident_values(extdata)
                         + get_workzone_values(extdata)
                         + get_specialevent_values(extdata)
                         + get_snowmangement_values(extdata)
                         )


def get_weather_values(extdata):
    """

    :type extdata: pyticas_tetres.rengine.filter.ftypes.ExtData
    :rtype: list[str]
    """
    try:
        return [
            extdata.weather._weather.usaf,
            extdata.weather._weather.wban,
            _get_precip_type(extdata),
            extdata.weather._weather.precip,
            isdtypes.INTENSITY_TYPES.get(int(extdata.weather._weather.precip_intensity), '') if extdata.weather._weather.precip_intensity else '',
        ]
    except Exception as ex:
        print('error occured: ', ex)
        print('precip_type:', extdata.weather._weather.precip_type)
        return []

def _get_precip_type(extdata):
    if not extdata or not extdata.weather or not extdata.weather._weather or not extdata.weather._weather.precip:
        return ''
    if extdata.weather._weather.precip_type.isdigit():
        return isdtypes.PRECIP_TYPES.get(int(extdata.weather._weather.precip_type), '')
    return extdata.weather._weather.precip_type


def get_incident_values(extdata):
    """
    :type extdata: pyticas_tetres.ttypes.ExtData
    :rtype: list[str]
    """
    itypes, impacts, cdtss, udtss, xdtss, dists, off_dists = [], [], [], [], [], [], []
    for incd in extdata.incidents:
        itype = incd._incident._incident_type.eventtype
        impact = incd._incident.impact
        cdts = dt2str(incd._incident.cdts)
        udts = dt2str(incd._incident.udts)
        xdts = dt2str(incd._incident.xdts)
        dist = float2str(incd.distance)
        off_dist = float2str(incd.off_distance)

        itypes.append(itype or '')
        impacts.append(impact or '')
        cdtss.append(cdts or '')
        udtss.append(udts or '')
        xdtss.append(xdts or '')
        dists.append(dist or '')
        off_dists.append(off_dist or '')

    return ['|'.join(itypes),
            '|'.join(impacts),
            '|'.join(cdtss),
            '|'.join(udtss),
            '|'.join(xdtss),
            '|'.join(dists),
            '|'.join(off_dists)]


def get_workzone_values(extdata):
    """
    :type extdata: pyticas_tetres.ttypes.ExtData
    :rtype: list[str]
    """
    names, lane_cfgs, closed_lengths, off_dists, locs = [], [], [], [], []
    for tt_wz in extdata.workzones:
        name = tt_wz._workzone._wz_group.name
        _lane_cfg = list(set([ '%s to %s' % (f.origin_lanes, f.open_lanes) for f in tt_wz._workzone._laneconfigs ]))
        lane_cfg = ','.join(_lane_cfg)
        _closed_length = list(set([ '%.2f' % f.closed_length for f in tt_wz._workzone._features ]))
        closed_length = ','.join(_closed_length)
        off_dist = float2str(tt_wz.off_distance)
        loc = ttypes.LOC_TYPE.get_by_value(tt_wz.loc_type).name if tt_wz.loc_type else ''

        names.append(name or '')
        lane_cfgs.append(lane_cfg or '')
        closed_lengths.append(closed_length or '')
        locs.append(loc or '')
        off_dists.append(off_dist or '')

    return ['|'.join(names),
            '|'.join(lane_cfgs),
            '|'.join(closed_lengths),
            '|'.join(locs),
            '|'.join(off_dists),
            ]


def get_specialevent_values(extdata):
    """
    :type extdata: pyticas_tetres.ttypes.ExtData
    :rtype: list[str]
    """
    names, dists, event_types, attendances = [], [], [], []
    for se in extdata.specialevents:
        name = se._specialevent.name
        dist = float2str(se.distance)
        event_type = se.event_type
        attendance = int2str(se._specialevent.attendance)

        names.append(name or '')
        dists.append(dist or '')
        attendances.append(attendance or '')
        event_types.append(event_type or '')

    return ['|'.join(names),
            '|'.join(dists),
            '|'.join(attendances),
            '|'.join(event_types)]


def get_snowmangement_values(extdata):
    """
    :type extdata: pyticas_tetres.ttypes.ExtData
    :rtype: list[str]
    """
    truck_route_ids, off_dists, road_statuss, locs = [], [], [], []
    for sm in extdata.snowmanagements:
        truck_route_id = sm._snowmgmt._snowroute.prj_id
        road_status = sm.road_status
        loc = ttypes.LOC_TYPE.get_by_value(sm.loc_type).name if sm.loc_type else ''
        off_dist = float2str(sm.off_distance)

        road_status = 'Lost' if road_status < 0 else 'Regained'

        truck_route_ids.append(truck_route_id or '')
        road_statuss.append(road_status or '')
        locs.append(loc or '')
        off_dists.append(off_dist or '')

    return ['|'.join(truck_route_ids),
            '|'.join(road_statuss),
            '|'.join(locs),
            '|'.join(off_dists)
            ]


def _get_item(a_result, field_name, **kwargs):
    """
    :type a_result: dict
    :type field_name: str
    :rtype: Union(str, float, int)
    """
    missing_value = kwargs.get('missing_value', '')
    attrs = []
    if ':' in field_name:
        attrs = [ int(attr) if attr.isdigit() else attr for attr in field_name.split(':') ]
    else:
        attrs = [field_name]

    obj = a_result
    for attr_name in attrs:
        try:
            obj = obj.get(attr_name, missing_value)
        except Exception as ex:
            print('a_result: ', a_result)
            print('field_name: ', field_name)
            print('attrs: ', attrs)
            raise ex
    return obj

def get_result_list(a_result, col_names=None, fields=None, **kwargs):
    """
    :type a_result: dict
    :rtype: list[str], list[str]
    """
    if not a_result:
        return [], []

    if not col_names or not fields:
        fields, col_names = get_indice_names()

    data = [ _get_item(a_result, cn, **kwargs) for cn in fields ]

    return col_names, data

def get_indice_names():
    field = [
        'avg_tt',
        'count',
        'tt_by_ffs',
        'congested_avg_tt',
        'congested_count',
        'percentile_tts:80',
        'percentile_tts:85',
        'percentile_tts:90',
        'percentile_tts:95',
        'buffer_index:80',
        'buffer_index:85',
        'buffer_index:90',
        'buffer_index:95',
        'planning_time_index:80',
        'planning_time_index:85',
        'planning_time_index:90',
        'planning_time_index:95',
        'tt_rate',
        'travel_time_rate:80',
        'travel_time_rate:85',
        'travel_time_rate:90',
        'travel_time_rate:95',
        'travel_time_index',
        'lottr',
        'semi_variance',
        'semi_variance_count',
        'on_time_arrival',
        'on_time_arrival_count',
        'misery_index',
    ]
    col_names = [
        'Avg TT',
        'Data Count',
        'Free-Flow TT using Speed Limit',
        'Congested Avg. TT',
        'Congested Data Count',
        '80th %-ile TT',
        '85th %-ile TT',
        '90th %-ile TT',
        '95th %-ile TT',
        'Buffer Index (80th %-ile)',
        'Buffer Index (85th %-ile)',
        'Buffer Index (90th %-ile)',
        'Buffer Index (95th %-ile)',
        'Planning Time Index (80th %-ile)',
        'Planning Time Index (85th %-ile)',
        'Planning Time Index (90th %-ile)',
        'Planning Time Index (95th %-ile)',
        'Travel Time Rate(Avg Travel Time) (minute/mile)',
        'Travel Time Rate (80th %-ile)',
        'Travel Time Rate (85th %-ile)',
        'Travel Time Rate (90th %-ile)',
        'Travel Time Rate (95th %-ile)',
        'Travel Time Index',
        'Level of Travel Time Reliability',
        'Semi-Variance',
        'Semi-Variance Data Count',
        'On-Time Arrival',
        'On-Time Arrival Data Count',
        'Misery Index'
    ]
    return field, col_names


def get_indice_names_for_byindices():
    field = [
        'avg_tt',
        'congested_avg_tt',
        'percentile_tts:80',
        'percentile_tts:85',
        'percentile_tts:90',
        'percentile_tts:95',
        'buffer_index:80',
        'buffer_index:85',
        'buffer_index:90',
        'buffer_index:95',
        'planning_time_index:80',
        'planning_time_index:85',
        'planning_time_index:90',
        'planning_time_index:95',
        'tt_rate',
        'travel_time_rate:80',
        'travel_time_rate:85',
        'travel_time_rate:90',
        'travel_time_rate:95',
        'travel_time_index',
        'lottr',
        'semi_variance',
        'on_time_arrival',
        'misery_index',
    ]
    col_names = [
        'Avg TT',
        'Congested Avg. TT',
        '80th %-ile TT',
        '85th %-ile TT',
        '90th %-ile TT',
        '95th %-ile TT',
        'Buffer Index (80th %-ile)',
        'Buffer Index (85th %-ile)',
        'Buffer Index (90th %-ile)',
        'Buffer Index (95th %-ile)',
        'Planning Time Index (80th %-ile)',
        'Planning Time Index (85th %-ile)',
        'Planning Time Index (90th %-ile)',
        'Planning Time Index (95th %-ile)',
        'Travel Time Rate (Avg Travel Time)(minute/mile)',
        'Travel Time Rate (80th %-ile)',
        'Travel Time Rate (85th %-ile)',
        'Travel Time Rate (90th %-ile)',
        'Travel Time Rate (95th %-ile)',
        'Travel Time Index',
        'Level of Travel Time Reliability',
        'Semi-Variance',
        'On-Time Arrival',
        'Misery Index'
    ]
    sheet_names = [
        'AvgTT',
        'CongestedAvgTT',
        '80th%-ile TT',
        '85th%-ile TT',
        '90th%-ile TT',
        '95th%-ile TT',
        'BufferIndex(80%)',
        'BufferIndex(85%)',
        'BufferIndex(90%)',
        'BufferIndex(95%)',
        'PlanningTimeIndex(80%)',
        'PlanningTimeIndex(85%)',
        'PlanningTimeIndex(90%)',
        'PlanningTimeIndex(95%)',
        'TT-Rate(AvgTravelTime)',
        'TravelTimeRate(80%)',
        'TravelTimeRate(85%)',
        'TravelTimeRate(90%)',
        'TravelTimeRate(95%)',
        'TravelTimeIndex',
        'LevelOfTTR',
        'Semi-Variance',
        'On-TimeArrival',
        'MiseryIndex'
    ]
    return field, col_names, sheet_names


def dt2str(dt):
    """
    :type dt: datetime.datetime
    :rtype: str
    """
    if not dt:
        return ''
    return dt.strftime('%Y-%m-%d %H:%M')

def float2str(num):
    """
    :type num: float
    :rtype: str
    """
    if not num:
        return ''
    return '%.2f' % num

def int2str(num):
    """
    :type num: int
    :rtype: str
    """
    if not num:
        return ''
    return '%d' % num
