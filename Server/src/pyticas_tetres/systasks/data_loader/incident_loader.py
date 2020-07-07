# -*- coding: utf-8 -*-
import datetime
import time
from collections import defaultdict

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import distance as distutil, timeutil
from pyticas_tetres.da import incident, incident_type, incident_cad, incident_type_cad, incident_iris
from pyticas_tetres.logger import getLogger
from pyticas_tetres.ttypes import IncidentTypeInfo

DISTANCE_THRESHOLD_FOR_SAME_EVENT = 1  # 0.5mile
TIMEDIFF_THRESHOLD_FOR_SAME_EVENT = 30  # 30 minute


def import_all_corridor(start_date, end_date, **kwargs):
    """

    :type start_date: datetime.datetime
    :type end_date: datetime.datetime
    :rtype: (int, bool)
    """
    logger = getLogger(__name__)
    da_incident = incident.IncidentDataAccess()
    logger.debug('delete all existing data')

    is_deleted = da_incident.delete_range_all(start_date, end_date)
    if not is_deleted or not da_incident.commit():
        da_incident.rollback()
        da_incident.close_session()
        return 0, True

    logger.debug('end of delete all existing data')
    event_types = sync_incident_types_to_CAD()

    logger.debug('loading iris data')
    da_iris = incident_iris.IrisIncidentDataAccess()  # read only
    iris_data_list = da_iris.list(sdate=start_date, edate=end_date)
    da_iris.close_session()

    iris_data_bucket = defaultdict(list)
    for idata in iris_data_list:
        evt_date = idata.str2datetime(idata.event_date).date().strftime('%Y-%m-%d')
        iris_data_bucket[evt_date].append(idata)
    logger.debug('end of loading iris data : %d' % len(iris_data_list))

    iris_data_cache = {}
    window_size = 100000
    data_list = []
    logger.debug('loading CAD data and inserting to DB')
    stime = time.time()

    n_inserted = 0
    da_cad = incident_cad.IncidentDataAccess()  # read only
    for item in da_cad.list_as_generator(sdate=start_date, edate=end_date, window_size=window_size):
        if not item.lat or not item.lon:
            continue
        if item.str2datetime(item.cdts) < start_date:
            continue
        # stime = time.time()
        # logger.debug('- finding iris data : %s' % item)
        if item.eid in iris_data_cache:
            iris_data = iris_data_cache[item.eid]
        else:
            iris_data = _find_iris_data(iris_data_bucket, item)
            iris_data_cache[item.eid] = iris_data
        # logger.debug('- end of finding iris data (elapsed time=%s)' % (timeutil.human_time(seconds=(time.time() - stime))))
        # iris_data = None

        # logger.debug('- finding event type')
        et = _find_event_type(item.eventtype, item.eventsubtype, event_types)
        # logger.debug('- end of finding event type')

        ii = dict(
            cad_pkey=item.pkey,
            cdts=_date_time(item.cdts),
            udts=_date_time(item.udts),
            xdts=_date_time(item.xdts),
            earea=item.earea,
            ecompl=item.ecompl,
            edirpre=item.edirpre,
            edirsuf=item.edirsuf,
            efeanme=item.efeanme,
            efeatyp=item.efeatyp,
            xstreet1=item.xstreet1,
            xstreet2=item.xstreet2,
            lat=item.lat,
            lon=item.lon,
            iris_event_id=iris_data.event_id if iris_data else None,
            iris_event_name=iris_data.name if iris_data else None,
            road=iris_data.road if iris_data else None,
            direction=iris_data.direction if iris_data else None,
            impact=iris_data.impact if iris_data else None,
            lane_type=iris_data.lane_type if iris_data else None,
            incident_type_id=et.id
        )

        data_list.append(ii)

        if len(data_list) >= window_size:
            inserted_ids = da_incident.bulk_insert(data_list, print_exception=True)
            if not inserted_ids or not da_incident.commit(print_exception=True):
                logger.warning('=> exception occured when saving data (1)')
                da_incident.rollback()
                da_incident.close_session()
                da_cad.close_session()
                return n_inserted, True
            else:
                n_inserted += len(data_list)
                data_list = []

    da_cad.close_session()

    if data_list:
        logger.debug('=> save data (bulk mode) : %d' % len(data_list))
        inserted_ids = da_incident.bulk_insert(data_list, print_exception=True)
        if not inserted_ids or not da_incident.commit(print_exception=True):
            logger.warning('=> exception occured when saving data (2)')
            da_incident.rollback()
            da_incident.close_session()
            return n_inserted, True
        else:
            n_inserted += len(data_list)

    logger.debug('end of loading CAD data and inserting to DB (elapsed time=%s)' % timeutil.human_time(
        seconds=(time.time() - stime)))
    logger.debug(' : %d incident data has been loaded (has_error=%s)' % (n_inserted, False))

    da_incident.close_session()

    return n_inserted, False


def _find_iris_data(iris_data_bucket, cad_incident_info):
    """

    :type iris_data_bucket: dict[str, list[pyticas_tetres.ttypes.IrisIncidentInfo]]
    :type cad_incident_info: pyticas_tetres.ttypes.CADIncidentInfo
    :rtype: pyticas_tetres.ttypes.IrisIncidentInfo
    """
    evt_date = cad_incident_info.str2datetime(cad_incident_info.cdts).strftime('%Y-%m-%d')
    iris_data_list = iris_data_bucket.get(evt_date, [])
    if not iris_data_list:
        return None

    for iris_data in iris_data_list:
        try:
            iris_description = iris_data.description
            iris_classification = iris_description.split()[1]
        except:
            iris_classification = ""
        cad_classification = cad_incident_info.iris_class
        if cad_classification and iris_classification:
            if str(cad_classification).lower() != str(iris_classification).lower():
                continue
        distance = distutil.distance_in_mile_with_coordinate(iris_data.lat, iris_data.lon, cad_incident_info.lat,
                                                             cad_incident_info.lon)
        if distance > DISTANCE_THRESHOLD_FOR_SAME_EVENT:
            continue

        timediff = iris_data.str2datetime(iris_data.event_date) - cad_incident_info.str2datetime(cad_incident_info.cdts)
        if (timediff.seconds / 60 < TIMEDIFF_THRESHOLD_FOR_SAME_EVENT):
            return iris_data
    return None


def _date_time(date_string):
    return datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S') if date_string else None


def sync_incident_types_to_CAD():
    """
    :rtype: list[pyticas_tetres.ttypes.IncidentTypeInfo]
    """
    logger = getLogger(__name__)

    da_type = incident_type.IncidentTypeDataAccess()
    da_type_cad = incident_type_cad.IncidentTypeDataAccess()

    # load_data incident types
    event_types = da_type.list()

    pk = da_type.da_base.get_next_pk()

    # incident type sync to CAD database
    logger.debug('incident type synchronization with CAD database')
    for et_cad in da_type_cad.list():
        et = _find_event_type(et_cad.eventtype, et_cad.eventsubtype, event_types)
        # logger.debug('  - type : %s (%s)' % (et_cad, et))
        if not et:
            it = IncidentTypeInfo()
            for k, v in et_cad.__dict__.items():
                setattr(it, k, v)
            it.id = pk
            pk += 1
            cloned_it = it.clone()
            event_types.append(cloned_it)

            # logger.debug('    -> add incident type : %s ' % it)
            inserted_item = da_type.insert(it)
            if not inserted_item:
                logger.warning('  - cannot insert incident type : %s' % et)

    if not da_type.commit():
        logger.warning(' !! commit error')

    logger.debug('end of incident type synchronization with CAD database')

    da_type.close_session()
    da_type_cad.close_session()

    return event_types


def _find_event_type(eventtype, eventsubtype, event_types):
    """

    :type eventtype: str
    :type eventsubtype: str
    :type event_types: list[IncidentTypeInfo]
    :rtype: IncidentTypeInfo
    """
    for et in event_types:
        if et.eventtype == eventtype and et.eventsubtype == eventsubtype:
            return et
    return None

# faverolles 12/27/2019: removed half finished function
# def import_all_corridor_one_by_one(start_date, end_date):
#     """
#
#     :type start_date: datetime.datetime
#     :type end_date: datetime.datetime
#     :rtype: list[dict]
#     """
#     da_incident = incident.IncidentDataAccess()
#     da_cad = incident_cad.IncidentDataAccess()
#     da_iris = incident_iris.IrisIncidentDataAccess()
#
#     res = []
#     logger = getLogger(__name__)
#     logger.debug('start to import incident data from CAD database during %s - %s' % (start_date, end_date))
#     for corr in tetres.get_infra().get_corridors():
#         if 'CD' in corr.name or 'RTMC' in corr.name or 'All' in corr.name or not corr.dir:
#             continue
#         logger.debug('load_data incident data of %s' % corr.name)
#         inserted_count = import_corridor_data(corr, start_date, end_date, das=(da_incident, da_cad, da_iris))
#         res.append({'corridor': corr.name, 'inserted': inserted_count})
#
#     da_incident.close()
#     da_cad.close()
#     da_iris.close()
#     return res


# def import_corridor_data(corr, start_date, end_date, **kwargs):
#     """
#     :type corr: pyticas.ttypes.CorridorObject
#     :type start_date: datetime.datetime
#     :type end_date: datetime.datetime
#     :return:
#     """
#     das = kwargs.get('das', None)
#
#     logger = getLogger(__name__)
#     if not das:
#         da_incident = incident.IncidentDataAccess()
#         da_cad = incident_cad.IncidentDataAccess()
#         da_iris = incident_iris.IrisIncidentDataAccess()
#     else:
#         (da_incident, da_cad, da_iris) = das
#
#     da_incident.delete_range(corr.route, corr.dir, start_date, end_date)
#
#     event_types = sync_incident_types_to_CAD()
#
#     cnt = 0
#     route_name = corr.route.replace('I-', '')
#     route_name = route_name.replace('T.H.', '')
#     route_name = route_name.replace('U.S.', '')
#
#     iris_data_list = da_iris.list(sdate=start_date, edate=end_date, corridor=corr.route, direction=corr.dir)
#     iris_data_cache = {}
#
#     data_list = []
#     for item in da_cad.list_as_generator(sdate=start_date, edate=end_date, corridor=route_name, direction=corr.dir, window_size=10000):
#
#         if item.eid in iris_data_cache:
#             iris_data = iris_data_cache[item.eid]
#         else:
#             iris_data = _find_iris_data(iris_data_list, item)
#             iris_data_cache[item.eid] = iris_data
#
#         et = _find_event_type(item.eventtype, item.eventsubtype, event_types)
#
#         ii = model.Incident(
#             cad_pkey=item.pkey,
#             cdts=item.cdts,
#             udts=item.udts,
#             xdts=item.xdts,
#             earea=item.earea,
#             ecompl=item.ecompl,
#             edirpre=item.edirpre,
#             edirsuf=item.edirsuf,
#             efeanme=item.efeanme,
#             efeatyp=item.efeatyp,
#             xstreet1=item.xstreet1,
#             xstreet2=item.xstreet2,
#             lat=item.lat,
#             lon=item.lon,
#
#             iris_event_id=iris_data.event_id if iris_data else None,
#             iris_event_name=iris_data.name if iris_data else None,
#             road=iris_data.road if iris_data else None,
#             direction=iris_data.direction if iris_data else None,
#             impact=iris_data.impact if iris_data else None,
#             lane_type=iris_data.lane_type if iris_data else None,
#
#             incident_type_id=et.id
#         )
#         if cnt % 1000 == 0:
#             logger.debug('-> create iris data : %d : %s' % (cnt, ii))
#
#         data_list.append(ii)
#         cnt += 1
#
#         if len(data_list) > 10000:
#             try:
#                 logger.debug('=> save data (bulk mode) : %d' % len(data_list))
#                 da_incident.da_base.session.bulk_save_objects(data_list)
#                 da_incident.da_base.session.commit()
#                 data_list = []
#             except Exception as ex:
#                 da_incident.rollback()
#                 return 0
#
#     if data_list:
#         try:
#             logger.debug('=> save data (bulk mode) : %d' % len(data_list))
#             da_incident.da_base.session.bulk_save_objects(data_list)
#             da_incident.da_base.session.commit()
#             data_list = []
#         except Exception as ex:
#             da_incident.rollback()
#             return 0
#
#     logger.debug(' : %d incident data has been loaded for %s' % (cnt, corr.name))
#
#     if not das:
#         da_incident.close()
#         da_cad.close()
#         da_iris.close()
#
#     return cnt
