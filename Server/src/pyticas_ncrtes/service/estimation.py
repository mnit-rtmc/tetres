# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.service.estimation
==================================

- main script to estimate NCRT
- it is called by API request handler (pyticas_ncrtes.api.estimation)
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import os
import time
from queue import Queue

from pyticas.tool import tb, timeutil
from pyticas.ttypes import Period
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import est
from pyticas_ncrtes.core import etypes
from pyticas_ncrtes.core import setting
from pyticas_ncrtes.core.est import phase, section
from pyticas_ncrtes.core.est import ncrt_sectionwide
from pyticas_ncrtes.core.month import get_normal_months_from_period
from pyticas_ncrtes.core.month import get_normal_months_from_year
from pyticas_ncrtes.core.nsrf import target
from pyticas_ncrtes.da.normal_func import NormalFunctionDataAccess
from pyticas_ncrtes.da.snowroute import SnowRouteDataAccess
from pyticas_ncrtes.da.snowroute_group import SnowRouteGroupDataAccess
from pyticas_ncrtes.da.target_station import TargetStationDataAccess
from pyticas_ncrtes.itypes import TargetStationInfo
from pyticas_ncrtes.logger import getLogger
from pyticas_ncrtes.service import normalday


def estimate(request_param, msg_queue=None, **kwargs):
    """

    :type request_param: pyticas_ncrtes.itypes.EstimationRequestInfo
    :type msg_queue: queue.Queue
    :rtype: list[pyticas_ncrtes.est.etypes.SnowData]
    """

    logger = getLogger(__name__)

    from_station = kwargs.get('from_station', None)
    to_station = kwargs.get('to_station', None)
    for_normalday = kwargs.get('normalday', None)
    nd_offset = kwargs.get('nd_offset', 2)

    stime = time.time()

    infra = ncrtes.get_infra()
    msg_queue = msg_queue or Queue()

    logger.info('@@@ NCRT estimation process start')

    # prepare reported events
    reported_events = _reported_events(request_param)

    # prepare time period and route information
    year = _get_year(request_param.snow_start_time)
    snow_routes, snri_list = _snow_routes(year)
    prd = _snow_event(request_param)

    origin_prd = prd.clone()

    # make station groups by corridor or snow route
    # to run by the the group
    logger.info('year : %d' % year)
    est_groups = _est_groups(year, request_param, snow_routes, snri_list, from_station, to_station)

    if not est_groups:
        logger.info('! No target stations to estimate')
        return False

    # run estimation process for each station group
    logger.debug('!estimate > run estimation process for each station group')

    for case_name, stations in est_groups.items():

        msg_queue.put('Case : %s ' % case_name)
        logger.debug(' > start : %s' % case_name)

        # iterate target stations to prepare ESTData list
        edata_list, tsi_list, sidx_list = _prepare_est_data(stations,
                                                            prd=prd,
                                                            year=year,
                                                            reported_events=reported_events,
                                                            snow_routes=snow_routes,
                                                            msg_queue=msg_queue,
                                                            from_station=from_station,
                                                            to_station=to_station,
                                                            for_normalday=for_normalday,
                                                            origin_prd=origin_prd,
                                                            nd_offset=nd_offset)

        # logger.debug(' > finding NCRT by u')
        # for edata in edata_list:
        #     ncrt_by_u.estimate(edata)
        # logger.debug('end...')
        # return

        logger.debug(' > creating sections')
        sections = section.sections(edata_list)

        logger.debug(' > finding interested points')
        # determine u-k change points by snowing
        # bysnowing.find(edata_list, sections)

        logger.debug(' > start estimating')
        for idx, edata in enumerate(edata_list):
            # Run estimation process
            # logger.debug(' ==> %s' % edata.target_station.station_id)
            est.estimate(sidx_list[idx], tsi_list[idx], edata)

        # adjust NCRT of individual stations
        logger.debug(' > sectionwide adjust NCRTs')

        # TODO: enable this...
        ncrt_sectionwide.adjust_ncrts(edata_list, sections)

        # remove single-station section without NCRT (type1)
        edata_list, sections = ncrt_sectionwide.remove_section_with_single_station(edata_list, sections)

        # determine NCRT (type2) using section-wide data
        # logger.debug(' > sectionwide alternatives')
        # ncrt_sectionwide.determine(edata_list, sections)

        # determine phase change points
        logger.debug(' > phase change points')
        for idx, edata in enumerate(edata_list):
            try:
                phase.determine(edata)
            except Exception as ex:
                tb.traceback(ex)
                continue

        output_path = os.path.join(infra.get_path('ncrtes', create=True), 'whole_data',
                                   prd.start_date.strftime('%Y-%m-%d'), case_name)
        est.report(case_name, edata_list, output_path)

        etime = time.time()

        logger.info(
            '@@@ End of NCRT estimation process (elapsed time=%s)' % timeutil.human_time(seconds=(etime - stime)))


def _prepare_est_data(stations, **kwargs):
    """

    :type stations: list[pyticas_ncrtes.itypes.TargetStationInfo]
    :type kwargs:
    :rtype: (list[pyticas_ncrtes.core.etypes.ESTData], list[pyticas_ncrtes.itypes.TargetStationInfo], list[int])
    """

    case_name = kwargs.get('case_name', None)
    reported_events = kwargs.get('reported_events', None)
    msg_queue = kwargs.get('msg_queue', None)
    from_station = kwargs.get('from_station', None)
    to_station = kwargs.get('to_station', None)
    for_normalday = kwargs.get('for_normalday', None)
    origin_prd = kwargs.get('origin_prd', None)
    nd_offset = kwargs.get('nd_offset', None)
    snow_routes = kwargs.get('snow_routes', None)
    prd = kwargs.get('prd', None)
    year = kwargs.get('year', None)

    logger = getLogger(__name__)
    infra = ncrtes.get_infra()

    sidx_list, tsi_list, edata_list = [], [], []
    msg_queue.put('Case : %s ' % case_name)
    logger.debug(' > start : %s' % case_name)

    # for test
    f_found = False
    f_to_found = False

    # iterate target stations to prepare ESTData list
    for sidx, tsi in enumerate(stations):

        if f_to_found:
            break

        # for test
        if from_station:
            if tsi.station_id == from_station:
                f_found = True
            if not f_found:
                continue

        # target station object
        station = infra.get_rnode(tsi.station_id)

        if not station.is_normal_station() or not station.detectors:
            continue

        # for test
        if to_station and tsi.station_id == to_station:
            f_to_found = True

        # for test
        if for_normalday:
            prd = normalday.get_normal_period(station, origin_prd, nd_offset)
            reported_events = {}

        msg_queue.put('  - Station : %s ' % tsi.station_id)
        logger.debug('   - Station : %s' % tsi.station_id)

        try:
            # Normal Average UK Function
            if tsi._normal_function:
                nf = tsi._normal_function.func
            else:
                nf = None

            edata = est.prepare_data(tsi, station, year,
                                     prd.start_date, prd.end_date,
                                     snow_routes, reported_events, nf)

        except Exception as ex:
            logger.debug(tb.traceback(ex, f_print=False))
            continue

        if not edata:
            continue

        edata_list.append(edata)
        tsi_list.append(tsi)
        sidx_list.append(sidx)

    return edata_list, tsi_list, sidx_list


def _output_path(prd, corr_name):
    infra = ncrtes.get_infra()

    output_path = os.path.join(infra.get_path('ncrtes', create=True), 'wetnormal', '%s - %s' % (
        prd.start_date.strftime('%Y-%m-%d'), corr_name))

    # output_path = os.path.join(infra.get_path(setting.OUTPUT_DIR, create=True), 'output',
    #                            datetime.datetime.now().strftime('%Y%m%d %H%M%S'))

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path


def _est_groups(year, request_param, snow_routes, snri_list, from_station=None, to_station=None):
    """

    :type year: int
    :type request_param: pyticas_ncrtes.itypes.EstimationRequestInfo
    :type snow_routes: list[etypes.SnowRoute]
    :type snri_list: list[pyticas_ncrtes.itypes.SnowRouteInfo]
    :rtype: dict[str, list[pyticas_ncrtes.itypes.TargetStationInfo]]
    """
    infra = ncrtes.get_infra()
    logger = getLogger(__name__)

    tsDA = TargetStationDataAccess()
    nfDA = NormalFunctionDataAccess()

    # make station groups by corridor or snow route
    est_groups = {}
    TS_CACHE = {}

    if hasattr(request_param, 'target_stations') and request_param.target_stations:

        target_stations = [tsDA.get_by_station_id(year, st) for st in request_param.target_stations]
        est_groups['user-defined'] = [tsi for tsi in target_stations if tsi]

    elif request_param.target_corridors:

        logger.debug('!estimate > prepare station list for each corridor')

        for corr_name in request_param.target_corridors:

            # TODO: for test
            if 'I-94(EB)' == corr_name:
                from_station = 'S1115'
                to_station = 'S1051'
            elif 'I-94(WB)' == corr_name:
                from_station = 'S1058'
                to_station = 'S1111'

            logger.debug(' -> %s' % corr_name)

            tsis = tsDA.list_by_corridor_name(year, corr_name)
            if not tsis:
                logger.debug('!!! no target stations for %s' % corr_name)
                continue

            # TODO: for test
            f_found, f_to_found = False, False
            _tsis = []
            for tsi in tsis:

                if f_to_found:
                    break

                # for test
                if from_station:
                    if tsi.station_id == from_station:
                        f_found = True
                    if not f_found:
                        continue

                if to_station and tsi.station_id == to_station:
                    f_to_found = True

                _tsis.append(tsi)

            if from_station:
                tsis = _tsis
            ###############

            corr = infra.get_corridor_by_name(corr_name)
            st_indices = {st.station_id: idx for idx, st in enumerate(corr.stations)}
            stsis = sorted(tsis, key=lambda tsi: st_indices[tsi.station_id])

            if from_station:
                sidx = st_indices.get(from_station, None)
                eidx = st_indices.get(to_station, None)
                if sidx and eidx:
                    stsis = [tsi for tsi in stsis if
                             st_indices[tsi.station_id] >= sidx or st_indices[tsi.station_id] <= sidx]

            # remove `station`s in curve
            candidates = target.station.get_target_stations(corr_name)
            candidate_stations = [st for st in candidates]
            candidate_station_ids = [st.station_id for st in candidates]

            _group = [tsi for tsi in stsis if tsi.snowroute_name and tsi.station_id in candidate_station_ids]
            _group_st_ids = [tsi.station_id for tsi in _group if tsi._normal_function]

            res = []
            for st in candidate_stations:

                # no target station
                if st.station_id not in _group_st_ids:
                    tsi = TargetStationInfo()
                    tsi.station_id = st.station_id
                    tsi.detectors = ','.join([det.name for det in target.get_target_detectors(st)])

                    snri = _find_snow_route(st, snri_list)
                    if snri:
                        tsi.snowroute_name = snri.name
                        tsi.snowroute_id = snri.id

                    nfi = nfDA.get_by_station(year, st.station_id)
                    if nfi:
                        tsi.normal_function_id = nfi.id
                        tsi._normal_function = nfi
                        res.append(tsi)
                else:
                    # target station
                    _sts = [tsi for tsi in stsis if tsi.station_id == st.station_id]
                    res.append(_sts[0])

            est_groups[corr_name] = res


    elif request_param.target_snow_routes:
        logger.debug('!estimate > prepare station list for each snow route')
        for snow_route_id in request_param.target_snow_routes:
            logger.debug(' -> snow_route.id=%d' % snow_route_id)
            snri, target_stations1, target_stations2 = _get_stations_from_snowrouteinfos(year, snow_route_id, snri_list,
                                                                                         tsDA, TS_CACHE)

            if not snri:
                logger.warn('Cannot find snow-route information')
                continue
            if not target_stations1:
                logger.debug('!!! no target stations for route1 of snowroute.id=%d' % snow_route_id)
            else:
                est_groups['%d-route1' % snri.id] = target_stations1

            if not target_stations2:
                logger.debug('!!! no target stations for route2 of snowroute.id=%d' % snow_route_id)
            else:
                est_groups['%d-route2' % snri.id] = target_stations2

    tsDA.close()

    # Remove the target stations having normal-function adjusted from other target station
    # for k in est_groups.keys():
    #     est_groups[k] = [ tsi for tsi in est_groups[k] if not tsi._normal_function or not tsi._normal_function.adjusted_from]

    for k in est_groups.keys():
        est_groups[k] = [tsi for tsi in est_groups[k] if tsi.snowroute_id]

    return est_groups


def _reported_events(request_param):
    """
    
    :type request_param: pyticas_ncrtes.itypes.EstimationRequestInfo
    :rtype: dict[str, list[ReportedEvent]]
    """
    logger = getLogger(__name__)
    reported_events = {}
    if hasattr(request_param, 'barelane_regain_time_infos') and request_param.barelane_regain_time_infos:
        for brt in request_param.barelane_regain_time_infos:
            # logger.debug(' > truck_id=%s, start=%s, end=%s, lost=%s, regain=%s' % (
            #     brt.truckroute_id,
            #     brt.snow_start_time,
            #     brt.snow_end_time,
            #     brt.lane_lost_time,
            #     brt.barelane_regain_time
            # ))
            reported = etypes.ReportedEvent(brt.truckroute_id,
                                            brt.snow_start_time,
                                            brt.snow_end_time,
                                            brt.lane_lost_time,
                                            brt.barelane_regain_time)
            rbtlist = reported_events.get(brt.truckroute_id, [])
            rbtlist.append(reported)
            reported_events[brt.truckroute_id] = rbtlist

    return reported_events


def _snow_event(request_param):
    """
    
    :type request_param: pyticas_ncrtes.itypes.EstimationRequestInfo
    :rtype: pyticas.ttypes.Period
    """
    rep_snow_start_time = _to_dt(request_param.snow_start_time)
    rep_snow_end_time = _to_dt(request_param.snow_end_time)
    prd = Period(rep_snow_start_time, rep_snow_end_time, setting.DATA_INTERVAL)
    return prd


def _to_dt(tstr):
    """
    
    :type tstr: str 
    :rtype: datetime.datetime 
    """
    dt = None
    if '-' in tstr:
        dt = datetime.datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')
    else:
        dt = datetime.datetime.strptime(tstr, '%m/%d/%Y %H:%M')
        try:
            dt = datetime.datetime.strptime(tstr, '%m/%d/%Y %H:%M')
        except Exception as ex:
            print('Exception parsing datetime time : %s' % str(ex))
            pass
    return dt


def _snow_routes(year):
    """
    
    :type year: int 
    :rtype: list[SnowRoute], list[from pyticas_ncrtes.itypes.SnowRouteInfo]
    """
    logger = getLogger(__name__)
    da_snrg = SnowRouteGroupDataAccess()
    da_snr = SnowRouteDataAccess()
    snrgi_list = da_snrg.search([('year', year)], group_by='name')
    snri_list = []
    for snrgi in snrgi_list:
        _snri_list = da_snr.search([('snowroute_group_id', snrgi.id)])
        if _snri_list:
            snri_list.extend(_snri_list)

    snow_routes = []
    for snri in snri_list:
        # logger.debug(' > snow route : %s, %s, %s, %s' % (
        #     snri.id, snri._snowroute_group.region, snri._snowroute_group.sub_region, snri._snowroute_group.name
        # ))
        sr1 = etypes.SnowRoute(snri._snowroute_group.region,
                               snri._snowroute_group.sub_region,
                               snri._snowroute_group.name,
                               '',
                               snri.route1.corridors()[0].route,
                               snri.route1.corridors()[0].dir,
                               snri.route1.get_stations()[0].station_id,
                               snri.route1.get_stations()[-1].station_id,
                               snri.name,
                               snri.description)

        sr2 = etypes.SnowRoute(snri._snowroute_group.region,
                               snri._snowroute_group.sub_region,
                               snri._snowroute_group.name,
                               '',
                               snri.route2.corridors()[0].route,
                               snri.route2.corridors()[0].dir,
                               snri.route2.get_stations()[0].station_id,
                               snri.route2.get_stations()[-1].station_id,
                               snri.name,
                               snri.description)

        # logger.debug('   - %s' % sr1)
        # logger.debug('   - %s' % sr2)
        snow_routes.append(sr1)
        snow_routes.append(sr2)

    return snow_routes, snri_list


def _find_snow_route(station, snri_list):
    """

    :type station: pyticas.ttypes.RNodeObject
    :type snri_list: list[pyticas_ncrtes.itypes.SnowRouteInfo]
    :rtype: pyticas_ncrtes.itypes.SnowRouteInfo
    """
    for snri in snri_list:
        if station in snri.route1.rnodes or station in snri.route2.rnodes:
            return snri
    return None


def _get_year(start_date):
    """

    :type start_date: str or datetime.datetime
    :return:
    """
    if isinstance(start_date, str):
        dt = _to_dt(start_date)
    else:
        dt = start_date

    today = datetime.datetime.now()
    if dt.year == today.year:
        if dt.month < 6:
            return dt.year - 2
        else:
            return dt.year - 1

    if dt.month >= 6:
        return dt.year
    else:
        return dt.year - 1


def _get_stations_from_snowrouteinfos(year, snow_route_id, snri_list, tsDA, TS_CACHE):
    """
    :type year: int
    :type snow_route_id: int
    :type snri_list: list[pyticas_ncrtes.itypes.SnowRouteInfo]
    :type tsDA: pyticas_ncrtes.da.target_station.TargetStationDataAccess
    :type TS_CACHE: dict
    :rtype: (pyticas_ncrtes.itypes.SnowRouteInfo, list[pyticas_ncrtes.itypes.TargetStationInfo], list[pyticas_ncrtes.itypes.TargetStationInfo])
    """
    for snri in snri_list:
        if snow_route_id == snri.id:
            corr_name1 = snri.route1.corridors()[0].name
            corr_name2 = snri.route2.corridors()[0].name

            tsis1 = TS_CACHE.get(corr_name1, tsDA.list_by_corridor_name(year, corr_name1))
            if corr_name1 not in TS_CACHE:
                TS_CACHE[corr_name1] = tsis1

            tsis2 = TS_CACHE.get(corr_name2, tsDA.list_by_corridor_name(year, corr_name1))
            if corr_name2 not in TS_CACHE:
                TS_CACHE[corr_name2] = tsis2

            target_stations1 = []
            target_stations2 = []

            for st in snri.route1.rnodes:
                for tsi in tsis1:
                    if st.station_id == tsi.station_id:
                        target_stations1.append(tsi)
                        break

            for st in snri.route2.rnodes:
                for tsi in tsis2:
                    if st.station_id == tsi.station_id:
                        target_stations2.append(tsi)
                        break

            return (snri, target_stations1, target_stations2)

    return (None, None, None)


def sheet_writer(wb, sheet, results, r, n_data, rows_before_data, rows_after_data, **kwargs):
    """
    :type wb: Workbook
    :type sheet: xlsxwriter.workbook.Worksheet
    :type results: list[pyticas.ttypes.RNodeData]
    :type r: pyticas.ttypes.Route
    :type n_data: int
    :type rows_before_data: int
    :type rows_after_data: int
    """
    tcol = len(results) + 1
    sheet.write_string(0, tcol, 'Average')

    for tidx in range(n_data):
        all_row_data = [rnd.data[tidx] for ridx, rnd in enumerate(results) if rnd.data[tidx] > 0]
        row = tidx + rows_before_data
        if any(all_row_data):
            avg = sum(all_row_data) / len(all_row_data)
            sheet.write(row, tcol, avg)
        else:
            sheet.write(row, tcol, -1)
