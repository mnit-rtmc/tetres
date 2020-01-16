# -*- coding: utf-8 -*-
from pyticas import route
from pyticas.rn import geo
from pyticas.tool import distance
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def sections_old(edata_list):
    """

    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :rtype: list[list[pyticas_ncrtes.core.etypes.ESTData]]
    """
    section_configs = [
        ('S911', 'S1601'),
        ('S33', 'S44'),
        ('S34', 'S49'),
        ('S50', 'S51'),
        ('S52', 'S63'),
        ('S565', 'S572'),
        ('S573', 'S659'),
        ('S664', 'S666'),
        ('S667', 'S1863'),
        ('S671', 'S1561')]

    routes = [route.create_route(srn, ern, '', '') for (srn, ern) in section_configs]

    station_to_routes = {}
    for ridx, r in enumerate(routes):
        for st in r.get_stations():
            station_to_routes[st.station_id] = ridx

    sections = [[] for _ in range(len(routes))]

    for edata in edata_list:
        ridx = station_to_routes.get(edata.target_station.station_id, None)
        if ridx is None:
            continue
        sections[ridx].append(edata)

    return sections


def sections(edata_list):
    """

    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :rtype: list[list[pyticas_ncrtes.core.etypes.ESTData]]
    """
    logger = getLogger(__name__)
    snow_route_data = stations_in_same_truck_route(edata_list)
    res = []
    for idx, edatas in enumerate(snow_route_data):
        # print('# snow_route=%d' % idx)
        _sections = _divide_section(edatas)
        _final_sections = _sections
        # _final_sections = []
        # for sidx, s in enumerate(_sections):
        #     _sub_sections = _divide_section_by_length(s)
        #     _final_sections.extend(_sub_sections)

        res.extend(_final_sections)
        # for sidx, s in enumerate(_final_sections):
        #     print('!! divide=%d' % sidx)
        #     for edata in s:
        #         print('  > ', edata.snow_route.id, ' : ', edata.target_station, ' : ', edata.target_station.lanes, edata.target_station)

    for sidx, s in enumerate(res):
        logger.debug('!! section=%d' % sidx)
        for edata in s:
            logger.debug('  > truck_route=%s, station=%s lanes=%s, s_limit=%s label=%s ' %
                         (edata.snow_route.id, edata.target_station.station_id,
                          edata.target_station.lanes, edata.target_station.s_limit,
                          edata.target_station.label))

    # raise Exception('Here~~~')

    return res

def _divide_section(edata_list):
    """

    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :rtype: list[list[pyticas_ncrtes.core.etypes.ESTData]]
    """
    up_station, dn_station = edata_list[0].target_station, edata_list[-1].target_station
    if up_station == dn_station:
        return [edata_list]

    s_sections, sts = [], []

    prev_s_limit = edata_list[0].target_station.s_limit

    st_to_edata = {}
    for edata in edata_list:
        st_to_edata[edata.target_station.station_id] = edata

    cur_rnode = up_station

    while cur_rnode.down_rnode:

        if (cur_rnode.connected_from
            or (cur_rnode.is_normal_station() and cur_rnode.s_limit != prev_s_limit)):

            if sts:
                s_sections.append(sts)

            sts = []

        if not cur_rnode.is_normal_station():
            cur_rnode = cur_rnode.down_rnode
            continue

        if cur_rnode.station_id in st_to_edata:
            sts.append(st_to_edata[cur_rnode.station_id])

        prev_s_limit = cur_rnode.s_limit

        cur_rnode = cur_rnode.down_rnode

        if cur_rnode.station_id == dn_station.station_id:
            break

    if sts:
        s_sections.append(sts)

    return s_sections


def _divide_section_by_length(edata_list):
    """

    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :rtype: list[list[pyticas_ncrtes.core.etypes.ESTData]]
    """
    dth = 5
    up_station, dn_station = edata_list[0].target_station, edata_list[-1].target_station
    corr = edata_list[0].target_station.corridor
    distmap = geo.get_mile_point_map(corr.stations)
    dist = distmap[dn_station.name] - distmap[up_station.name]

    if dist < dth:
        return [edata_list]

    half_dist = dist / 2
    sts1, sts2 = [], []
    for edata in edata_list:
        d = distmap[edata.target_station.name] - distmap[up_station.name]
        if d < half_dist:
            sts1.append(edata)
        else:
            sts2.append(edata)

    return [sts1, sts2]


def stations_in_same_truck_route(edata_list):
    """

    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :rtype: list[list[pyticas_ncrtes.core.etypes.ESTData]]
    """
    res, stations, prev_id = [], [], None

    for edata in edata_list:

        if not edata.snow_route:
            continue

        snow_route_id = edata.snow_route.id

        if not prev_id or snow_route_id != prev_id:
            if stations:
                res.append(stations)
                stations = []

        prev_id = snow_route_id
        stations.append(edata)

    if stations:
        res.append(stations)

    return res

