# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.cfg import INCIDENT_DOWNSTREAM_DISTANCE_LIMIT, INCIDENT_UPSTREAM_DISTANCE_LIMIT
from pyticas_tetres.da.tt_incident import TTIncidentDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine.helper import incident as ihelper
from pyticas_tetres.rengine.helper import loc
from pyticas_tetres.util.noop_context import nonop_with


def categorize(ttri, prd, ttdata, **kwargs):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type prd: pyticas.ttypes.Period
    :type ttdata: list[pyticas_tetres.ttypes.TravelTimeInfo]
    :rtype: int
    """
    lock = kwargs.get('lock', nonop_with())

    given_incidents = kwargs.get('incidents', None)
    all_incidents = given_incidents or ihelper.find_incidents(ttri.corridors()[0], prd)

    route_length = ttri.route.length()
    incd_locations = []
    for incd in all_incidents:
        distance = loc.location_by_coordinate(ttri.route, incd.lat, incd.lon)
        if distance != False:
            if distance < -INCIDENT_UPSTREAM_DISTANCE_LIMIT or distance > route_length + INCIDENT_DOWNSTREAM_DISTANCE_LIMIT:
                continue
            off_distance = distance if distance < 0 else max(0, distance - route_length)
            incd_locations.append((distance, off_distance, incd))

    year = prd.start_date.year
    ttincident_da = TTIncidentDataAccess(year)

    # avoid to save duplicated data
    with lock:
        is_deleted = ttincident_da.delete_range(ttri.id, prd.start_date, prd.end_date,
                                                item_ids=[v.id for v in all_incidents])
        if not is_deleted or not ttincident_da.commit():
            ttincident_da.rollback()
            ttincident_da.close_session()
            getLogger(__name__).warning('! incident.categorize(): fail to delete existing data')
            return -1

    dict_data = []
    for idx, tti in enumerate(ttdata):
        incds = _find_incident(incd_locations, tti.str2datetime(tti.time))
        for (dist, off_dist, incd) in incds:
            dict_data.append({
                'tt_id': tti.id,
                'incident_id': incd.id,
                'distance': dist,
                'off_distance': off_dist
            })

    if dict_data:
        with lock:
            inserted_ids = ttincident_da.bulk_insert(dict_data)
            if not inserted_ids or not ttincident_da.commit():
                ttincident_da.rollback()
                ttincident_da.close_session()
                getLogger(__name__).warning('! incident.categorize(): fail to insert categorization data')
                return -1

    ttincident_da.close_session()
    return len(dict_data)


def _find_incident(incidents, dt):
    """
    :type incidents: list[(float, float, pyticas_tetres.ttypes.IncidentInfo)]
    :type dt: datetime.datetime
    :rtype: list[(float, float, pyticas_tetres.ttypes.IncidentInfo)]
    """
    incds = []
    for idx, (distance, off_distance, incd) in enumerate(incidents):
        xdts = incd.xdts if incd.xdts else incd.udts
        if not xdts:
            continue
        if incd.str2datetime(incd.cdts) <= dt <= incd.str2datetime(xdts):
            incds.append((distance, off_distance, incd))
    return incds
