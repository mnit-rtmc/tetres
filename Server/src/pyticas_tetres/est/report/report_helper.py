# -*- coding: utf-8 -*-
import json
import math
import traceback
from typing import List

import xlsxwriter
from pyticas.moe.mods.cm import calculate_cm_dynamically
from pyticas.moe.mods.cmh import calculate_cmh_dynamically
from pyticas.moe.mods.lvmt import calculate_lvmt_dynamically
from pyticas.moe.mods.uvmt import calculate_uvmt_dynamically

from pyticas_noaa.isd import isdtypes
from pyticas_tetres import ttypes
from pyticas_tetres.cfg import TT_DATA_INTERVAL
from pyticas_tetres.rengine.filter.ftypes import ExtFilterGroup
from pyticas_tetres.util.systemconfig import get_system_config_info

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def write_operating_condition_info_sheet(eparam, wb):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type wb: xlsxwriter.Workbook
    """

    ws = wb.add_worksheet('Operating Coditions (OC)')

    ws.write_row(0, 0, ['Index', 'Name', 'Description'])
    for idx, ef in enumerate(eparam.operating_conditions):
        ws.write_row(idx + 1, 0, [idx, ef.name, ef.desc])


def write_moe_per_route_sheets(est_req_info: ttypes.EstimationRequestInfo,
                               ext_filter_groups: List[ExtFilterGroup],
                               cm_work_book: xlsxwriter.Workbook,
                               cmh_work_book: xlsxwriter.Workbook,
                               sv_work_book: xlsxwriter.Workbook) -> None:
    # faverolles 1/22/2020 TODO: Confirm Working

    from pyticas import period
    from pyticas.moe import writer
    from colorama import Fore
    from pyticas.moe.mods import cm, cmh, sv

    print(f"{Fore.LIGHTGREEN_EX}Calculating and Writing Spreadsheets for CM, CMH, and SV...")

    route_name = est_req_info.travel_time_route.name
    start_date_time = f"{est_req_info.get_start_date().strftime('%Y-%m-%d')} " \
                      f"{est_req_info.get_start_time().strftime('%H:%M:%S')}"
    end_date_time = f"{est_req_info.get_end_date().strftime('%Y-%m-%d')} " \
                    f"{est_req_info.get_end_time().strftime('%H:%M:%S')}"

    print(f"{Fore.CYAN}[{Fore.LIGHTMAGENTA_EX}{route_name}{Fore.CYAN}] "
          f"[{Fore.LIGHTMAGENTA_EX}{start_date_time}{Fore.CYAN}] "
          f"[{Fore.LIGHTMAGENTA_EX}{end_date_time}{Fore.CYAN}]")

    try:
        route = est_req_info.travel_time_route.route
        prd = period.create_period_from_string(start_date_time, end_date_time, 300)

        try:
            print(f"{Fore.LIGHTGREEN_EX}Calculating CM...")
            res_cm = cm.run(route, prd)
            writer.write_cm(None, _route=route, results=res_cm, work_book=cm_work_book)
        except Exception as e:
            print(f"{Fore.RED} Fail calculate or write cm {e}")
            traceback.print_exc()
            print(f"{Fore.RED} End Traceback")

        print(f"{Fore.LIGHTBLUE_EX}Done Calculating CM")

        try:
            print(f"{Fore.LIGHTGREEN_EX}Calculating CMH...")
            res_cmh = cmh.run(route, prd)
            writer.write_cmh(None, _route=route, results=res_cmh, work_book=cmh_work_book)
        except Exception as e:
            print(f"{Fore.RED} Fail calculate or write cmh {e}")
            traceback.print_exc()
            print(f"{Fore.RED} End Traceback")

        print(f"{Fore.LIGHTBLUE_EX}Done Calculating CMH")

        try:
            print(f"{Fore.LIGHTGREEN_EX}Calculating SV...")
            res_sv = sv.run(route, prd)
            writer.write_sv(None, _route=route, results=res_sv, work_book=sv_work_book)
        except Exception as e:
            print(f"{Fore.RED} Fail calculate or write sv {e}")
            traceback.print_exc()
            print(f"{Fore.RED} End Traceback")

        print(f"{Fore.LIGHTBLUE_EX}Done Calculating SV")

    except Exception as e:
        print(f"{Fore.RED} Fail to load route name or create period {e}")


def write_moe_data_sheet(eparam, ext_filter_groups, wb):
    # faverolles 10/12/2019:
    #   Created function to write moe data to spreadsheet
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type ext_filter_groups: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    """

    def clean(v):
        return v if v != math.inf and v and v > 0 else ''

    def cleanMOE(v):
        return v if v != math.inf and v and v >= 0 else ''

    for idx, ef in enumerate(ext_filter_groups):
        ws = wb.add_worksheet('MOE Data (OC=%d)' % idx)
        ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
        ws.write_row(1, 0, [
            '', '', '', '',
            'moe-values', '', '', '',
            '', '', '', '', '',
            'Speed Variation', '', '', '', '',
            'MOE Parameters', '', '',
            'weather', '', '', '', '',
            'incident', '', '', '', '', '', '',
            'workzone', '', '', '', '',
            'special-event', '', '', '',
            'snow-management'

        ])

        ws.write_row(2, 0, [
            'time', 'tt', 'speed', 'vmt',
            'vht', 'dvh', 'lvmt', 'uvmt',
            'cm', 'cmh', 'acceleration', 'number_of_vehicles_entered', 'number_of_vehicles_exited',
            'speed_average', 'speed_variance', 'speed_max_u', 'speed_min_u', 'speed_difference',
            'moe_lane_capacity', 'moe_critical_density', 'moe_congestion_threshold_speed',
            'usaf', 'wban', 'precip_type', 'precip', 'precip_intensity',  # weather
            'type', 'impact', 'cdts', 'udts', 'xdts', 'distance', 'off_distance',  # incident
            'name', 'lane_config', 'closed_length', 'location', 'off_distance',  # workzone
            'name', 'distance', 'attendance', 'type',  # special event
            'truck_route', 'road_status', 'location', 'off_distance'

        ])

        for idx, extdata in enumerate(ef.whole_data):
            x = extdata.tti
            dts = x.time.strftime('%Y-%m-%d %H:%M')
            try:
                meta_data = json.loads(x.meta_data)
            except Exception as e:
                print("Meta data not found, MOE value is not pre-calculated for the route: {}, for "
                      "the time period: {}. Error: {}".format(x, dts, e))
                meta_data = {}
            # interval = TT_DATA_INTERVAL
            moe_lane_capacity = cleanMOE(meta_data.get("moe_lane_capacity", 0))
            moe_critical_density = cleanMOE(meta_data.get("moe_critical_density", 0))
            moe_congestion_threshold_speed = cleanMOE(meta_data.get("moe_congestion_threshold_speed", 0))
            # lvmt = cleanMOE(calculate_lvmt_dynamically(meta_data, interval, moe_critical_density, moe_lane_capacity))
            # uvmt = cleanMOE(calculate_uvmt_dynamically(meta_data, interval, moe_critical_density, moe_lane_capacity))
            # cm = cleanMOE(calculate_cm_dynamically(meta_data, moe_congestion_threshold_speed))
            # cmh = cleanMOE(calculate_cmh_dynamically(meta_data, interval, moe_congestion_threshold_speed))
            speed_average = cleanMOE(meta_data.get("speed_average", 0))
            speed_variance = cleanMOE(meta_data.get("speed_variance", 0))
            speed_max_u = cleanMOE(meta_data.get("speed_max_u", 0))
            speed_min_u = cleanMOE(meta_data.get("speed_min_u", 0))
            speed_difference = cleanMOE(meta_data.get("speed_difference", 0))
            number_of_vehicles_entered = cleanMOE(meta_data.get("number_of_vehicles_entered", 0))
            number_of_vehicles_exited = cleanMOE(meta_data.get("number_of_vehicles_exited", 0))
            try:
                acceleration = "->".join([str(i) for i in meta_data.get("accelerations")])
            except:
                acceleration = ""
            ws.write_row(idx + 3, 0, [
                dts, clean(x.tt), clean(x.speed), clean(x.vmt),
                cleanMOE(x.vht), cleanMOE(x.dvh), cleanMOE(x.lvmt), cleanMOE(x.uvmt),
                cleanMOE(x.cm), cleanMOE(x.cmh), acceleration, number_of_vehicles_entered, number_of_vehicles_exited,
                speed_average, speed_variance, speed_max_u, speed_min_u, speed_difference,
                moe_lane_capacity, moe_critical_density, moe_congestion_threshold_speed,
            ]
                         + get_weather_values(extdata)
                         + get_incident_values(extdata)
                         + get_workzone_values(extdata)
                         + get_specialevent_values(extdata)
                         + get_snowmangement_values(extdata)
                         )


def write_moe_data_sheet_daily(eparam, ext_filter_groups, wb, daily):
    # faverolles 10/12/2019 TODO:
    #   Created function to write moe data to spreadsheet
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type ext_filter_groups: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type wb:xlsxwriter.Workbook
    :type daily: list[(list[dict], list[datetime.date])]
    :type results: list[(list[dict], list[datetime.date])]
    """

    # for idx, ef in enumerate(eparam.operating_conditions):
    #     ws = wb.add_worksheet('daily (OC=%d)' % idx)
    #     daily_results, dates = daily[idx]
    #     if not daily_results:
    #         continue
    #
    #     row = 0
    #     is_head_written = False
    #     for didx, a_result in enumerate(daily_results):
    #         head, result_row = report_helper.get_result_list(a_result, missing_value=MISSING_VALUE)
    #         if not is_head_written:
    #             _, head = report_helper.get_indice_names()
    #             is_head_written = True
    #             ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
    #             ws.write_row(1, 0, ['Date'] + head)
    #             if not row:
    #                 row += 2
    #         ws.write_row(row, 0, [dates[didx].strftime('%Y-%m-%d')] + result_row)
    #         row += 1
    #
    # def clean(v):
    #     return v if v != math.inf and v and v > 0 else ''
    #
    # def cleanMOE(v):
    #     return v if v != math.inf and v and v >= 0 else ''
    #
    # for idx, ef in enumerate(ext_filter_groups):
    #     ws = wb.add_worksheet('MOE Data (OC=%d)' % idx)
    #     ws.write_row(0, 0, ['Operating Condition:', eparam.operating_conditions[idx].name])
    #     ws.write_row(1, 0, [
    #         '', '', '', '',
    #         'moe-values', '', '', '', '',
    #     ])
    #
    #     ws.write_row(2, 0, [
    #         'time', 'tt', 'speed', 'vmt',
    #         'vht', 'dvh', 'lvmt', 'sv',
    #     ])
    #
    #     for idx, extdata in enumerate(ef.whole_data):
    #         x = extdata.tti
    #         dts = x.time.strftime('%Y-%m-%d %H:%M')
    #         ws.write_row(idx + 3, 0, [
    #             dts, clean(x.tt), clean(x.speed), clean(x.vmt),
    #             cleanMOE(x.vht), cleanMOE(x.dvh), cleanMOE(x.lvmt), cleanMOE(x.sv)]
    #                      + get_weather_values(extdata)
    #                      + get_incident_values(extdata)
    #                      + get_workzone_values(extdata)
    #                      + get_specialevent_values(extdata)
    #                      + get_snowmangement_values(extdata))


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
                            'usaf', 'wban', 'precip_type', 'precip', 'precip_intensity',  # weather
                            'type', 'impact', 'cdts', 'udts', 'xdts', 'distance', 'off_distance',  # incident
                            'name', 'lane_config', 'closed_length', 'location', 'off_distance',  # workzone
                            'name', 'distance', 'attendance', 'type',  # special event
                            'truck_route', 'road_status', 'location', 'off_distance'
                            ])

        for idx, extdata in enumerate(ef.whole_data):
            dts = extdata.tti.time.strftime('%Y-%m-%d %H:%M')
            tt = extdata.tti.tt if extdata.tti.tt != math.inf and extdata.tti.tt and extdata.tti.tt > 0 else ''
            u = extdata.tti.speed if extdata.tti.speed != math.inf and extdata.tti.speed and extdata.tti.speed > 0 else ''
            vmt = extdata.tti.vmt if extdata.tti.vmt != math.inf and extdata.tti.vmt and extdata.tti.vmt > 0 else ''

            ws.write_row(
                idx + 3, 0,
                [dts, tt, u, vmt]
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
            isdtypes.INTENSITY_TYPES.get(int(extdata.weather._weather.precip_intensity),
                                         '') if extdata.weather._weather.precip_intensity else '',
        ]
    except Exception as ex:
        return ["", "", "", "", ""]


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
        try:
            _lane_cfg = list(set(['%s to %s' % (f.origin_lanes, f.open_lanes) for f in tt_wz._workzone._laneconfigs]))
        except Exception as e:
            _lane_cfg = list()
        lane_cfg = ','.join(_lane_cfg)
        try:
            _closed_length = list(set(['%.2f' % f.closed_length for f in tt_wz._workzone._features]))
        except Exception as e:
            _closed_length = list()
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
        attrs = [int(attr) if attr.isdigit() else attr for attr in field_name.split(':')]
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

    data = [_get_item(a_result, cn, **kwargs) for cn in fields]

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
