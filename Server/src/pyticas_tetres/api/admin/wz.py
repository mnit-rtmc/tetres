# -*- coding: utf-8 -*-
"""
wz.py
~~~~~~~~~~~~~~

this module handles the request from `operating-condition data input > workzone tab` of `admin client`

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas import rc
from pyticas import route
from pyticas.ttypes import Route
from pyticas_server import protocol as prot
from pyticas_server.util import json2route
from pyticas_tetres import api_urls_admin
from pyticas_tetres.admin_auth import requires_auth
from pyticas_tetres.api_base import TeTRESApi
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.da.wz import WorkZoneDataAccess
from pyticas_tetres.da.wz_feature import WZFeatureDataAccess
from pyticas_tetres.da.wz_group import WZGroupDataAccess
from pyticas_tetres.da.wz_laneconfig import WZLaneConfigDataAccess
from pyticas_tetres.protocol import json2wzi
from pyticas_tetres.rengine.helper import wz as wz_helper
from pyticas_tetres.ttypes import WorkZoneInfo, WZCharacteristics
from pyticas.tool import distance as distance_util


def register_api(app):
    tetres_api = TeTRESApi(app, ActionLogDataAccess.DT_WORKZONE, json2wzi, WorkZoneDataAccess, {
        'delete': (api_urls_admin.WZ_DELETE, ['POST']),
    }, requires_auth=True)
    tetres_api.register()

    @app.route(api_urls_admin.WZ_LIST, methods=['POST'])
    @requires_auth
    def tetres_workzone_list():
        wzgroup_id = request.form.get('wzgroup_id')

        wzDA = WorkZoneDataAccess()
        wz_list = wzDA.search([('wz_group_id', wzgroup_id)])
        wzDA.close_session()

        return prot.response_success({'list': wz_list})

    @app.route(api_urls_admin.WZ_LIST_ALL, methods=['GET'])
    @requires_auth
    def tetres_workzone_list_all():
        wzDA = WorkZoneDataAccess()
        wz_list = wzDA.list()
        wzDA.close_session()
        return prot.response_success({'list': wz_list})

    @app.route(api_urls_admin.WZ_INSERT, methods=['POST'])
    @requires_auth
    def tetres_workzone_insert():
        wz_json = request.form.get('data', None)
        route_json = request.form.get('route', None)

        wzi = json2wzi(wz_json)
        if route_json:
            return _wz_insert_from_route(wzi, route_json)

        return _wz_insert_from_wz(wzi)

    @app.route(api_urls_admin.WZ_UPDATE, methods=['POST'])
    @requires_auth
    def tetres_workzone_update():
        wz_id = request.form.get('id')
        wz_json = request.form.get('data')

        wzDA = WorkZoneDataAccess()

        exWZObj = wzDA.get_by_id(wz_id)
        if not exWZObj:
            wzDA.close_session()
            return prot.response_invalid_request()

        info = json2wzi(wz_json)
        route2 = route.opposite_route(info.route1)
        cfg2 = info.route1.cfg.clone()
        rc.route_config.reverse(cfg2)
        route2.cfg = cfg2
        info.route2 = route2
        info.route1.name = 'route1 - %s' % info.route1.rnodes[0].corridor.name
        info.route1.desc = ''
        info.route2.name = 'route2 - %s' % info.route2.rnodes[0].corridor.name
        info.route2.desc = ''

        if not isinstance(info.route2, Route):
            wzDA.close_session()
            return prot.response_fail('fail to load_data route configuration file')

        wzgDA = WZGroupDataAccess(session=wzDA.get_session())
        try:
            info.workzone_length = route_length(info.route1)
        except:
            pass

        is_updated = wzDA.update(wz_id, info.get_dict())
        if not is_updated or not wzDA.commit():
            wzDA.rollback()
            wzDA.close_session()
            return prot.response_fail('fail to update database (1)')

        is_updated = wzgDA.update_years(exWZObj.wz_group_id)
        if not is_updated or not wzgDA.commit():
            wzgDA.rollback()
            wzgDA.close_session()
            return prot.response_fail('fail to update database (2)')

        updatedWZObj = wzDA.get_by_id(wz_id)

        # commented out this part since currently we couldn't collect work zone feature and lane config data
        # inserted = _wz_insert_feature(updatedWZObj)
        # if not inserted:
        #     wzDA.close_session()
        #     return prot.response_fail('fail to update database (3)')

        # commit here
        # if not wzDA.commit():
        #     return prot.response_fail('fail to update database (4)')

        tetres_api.add_actionlog(ActionLogDataAccess.UPDATE,
                                 wzDA.get_tablename(),
                                 wz_id,
                                 ActionLogDataAccess.data_description(ActionLogDataAccess.DT_WORKZONE, updatedWZObj),
                                 handled=_should_be_set_as_handled(exWZObj, updatedWZObj),
                                 dbsession=wzDA.get_session())

        wzDA.close_session()

        return prot.response_success(wz_id)

    def _should_be_set_as_handled(exObj, newObj):
        """

        :type exObj: pyticas_tetres.ttypes.WorkZoneInfo
        :type newObj: pyticas_tetres.ttypes.WorkZoneInfo
        :rtype:
        """
        if (exObj.start_time != newObj.start_time
            or exObj.end_time != newObj.end_time):
            return False

        return (exObj.route1.is_same_route(newObj.route1) and exObj.route2.is_same_route(newObj.route2))

    def route_length(route):
        starting_r_node = route.rnodes[0]
        ending_r_node = route.rnodes[-1]
        distance = distance_util.distance_in_mile_with_coordinate(starting_r_node.lat, starting_r_node.lon,
                                                                  ending_r_node.lat,
                                                                  ending_r_node.lon)
        return distance

    def _wz_insert_from_wz(wzi):
        """
        :type wzi: WorkZoneInfo
        """
        if not isinstance(wzi, WorkZoneInfo) or not wzi.route1 or not wzi.route2:
            return prot.response_invalid_request()

        wzDA = WorkZoneDataAccess()

        wzi.route1.name = 'route1 - %s' % wzi.route1.rnodes[0].corridor.name
        wzi.route1.desc = ''
        wzi.route2.name = 'route2 - %s' % wzi.route2.rnodes[0].corridor.name
        wzi.route2.desc = ''
        # wzi.id = wzDA.da_base.get_next_pk()
        try:
            wzi.workzone_length = route_length(wzi.route1)
        except:
            pass

        wzm = wzDA.insert(wzi)
        if wzm is False or not wzDA.commit():
            return prot.response_fail('fail to save workzone route data (1)')

        wzi.id = wzm.id

        inserted_id = wzi.id

        tetres_api.add_actionlog(ActionLogDataAccess.INSERT,
                                 wzDA.get_tablename(),
                                 inserted_id,
                                 ActionLogDataAccess.data_description(ActionLogDataAccess.DT_WORKZONE, wzi),
                                 handled=False,
                                 dbsession=wzDA.get_session())

        wzDA.close_session()
        return prot.response_success(obj=inserted_id)

    def _wz_insert_from_route(wzi, route_json):
        """
        :type wzi: WorkZoneInfo
        :type route_json: str
        """
        route1 = json2route(route_json)
        route2 = route.opposite_route(route1)
        if not isinstance(route2, Route):
            return prot.response_fail('fail to load_data route configuration file')
        cfg2 = route1.cfg.clone()
        route2.cfg = rc.route_config.reverse(cfg2)
        wzi.route1 = route1
        wzi.route2 = route2
        return _wz_insert_from_wz(wzi)

    def _wz_insert_feature(wzi):
        """
        :type wzi: WorkZoneInfo
        """
        wz_id = wzi.id

        wzfDA = WZFeatureDataAccess()
        wzlDA = WZLaneConfigDataAccess()

        (wz_length1, _features1, _lncfgs1, n_closed_ramps1) = wz_helper.features(wzi, 1)
        (wz_length2, _features2, _lncfgs2, n_closed_ramps2) = wz_helper.features(wzi, 2)

        wzf_list = wzfDA.list(wz_id)
        if wzf_list:
            is_deleted = wzfDA.delete_items([wzfi.id for wzfi in wzf_list])
            if not is_deleted or not wzfDA.commit():
                wzfDA.rollback()
                wzfDA.close_session()
                wzlDA.close_session()
                return False

        wzl_list = wzlDA.list(wz_id)
        if wzl_list:
            is_deleted = wzlDA.delete_items([wzli.id for wzli in wzl_list])
            if not is_deleted or not wzlDA.commit():
                wzlDA.rollback()
                wzlDA.close_session()
                wzfDA.close_session()
                return False

        wzli_data = _wzli_data(wz_id, 1, _lncfgs1) + _wzli_data(wz_id, 2, _lncfgs2)
        wzfi_data = [_wzfi_data(wz_id, 1, wz_length1, _features1, n_closed_ramps1),
                     _wzfi_data(wz_id, 2, wz_length2, _features2, n_closed_ramps2)]

        if wzli_data:
            inserted_ids = wzlDA.bulk_insert(wzli_data)
            if not inserted_ids or not wzlDA.commit():
                wzlDA.rollback()
                wzlDA.close_session()
                wzfDA.rollback()
                wzfDA.close_session()
                return False

        if wzfi_data:
            inserted_ids = wzfDA.bulk_insert(wzfi_data)
            if not inserted_ids or not wzfDA.commit():
                wzlDA.rollback()
                wzlDA.close_session()
                wzfDA.rollback()
                wzfDA.close_session()
                return False

        wzlDA.close_session()
        wzfDA.close_session()

        return True

    def _wzfi_data(wz_id, route_num, wz_length, features, n_closed_ramps):
        return {'wz_id': wz_id,
                'route_num': route_num,
                'closed_length': wz_length,
                'closed_ramps': n_closed_ramps,
                'use_opposing_lane': WZCharacteristics.USE_OPPOSING_LANE in features,
                'used_by_opposing_traffic': WZCharacteristics.USED_BY_OPPOSING_TRAFFICS in features,
                'has_closed': WZCharacteristics.HAS_CLOSED_LANES in features,
                'has_shifted': WZCharacteristics.HAS_SHIFTED_LANES in features,
                }

    def _wzli_data(wz_id, route_num, lncfgs):
        return [{'wz_id': wz_id,
                 'route_num': route_num,
                 'origin_lanes': origin_lanes,
                 'open_lanes': open_lanes} for idx, (origin_lanes, open_lanes) in enumerate(lncfgs)]
