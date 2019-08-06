# -*- coding: utf-8 -*-
from pyticas_ncrtes.core.nsrf.target import lane
from pyticas_ncrtes.da.normal_func import NormalFunctionDataAccess
from pyticas_ncrtes.da.snowroute import SnowRouteDataAccess
from pyticas_ncrtes.da.target_lane_config import TargetLaneConfigDataAccess
from pyticas_ncrtes.da.winter_season import WinterSeasonDataAccess

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas_ncrtes import api_urls, ncrtes, itypes
from pyticas_ncrtes.api_base import NCRTESApi
from pyticas_ncrtes.core.month import get_normal_months_from_year
from pyticas_ncrtes.core.nsrf import cache as nsr_cache
from pyticas_ncrtes.core.nsrf import nsr_func
from pyticas_ncrtes.da.target_station import TargetStationDataAccess
from pyticas_ncrtes.protocol import json2ts
from pyticas_server import protocol as prot


def register_api(app):
    ncrtes_api = NCRTESApi(app, 'ts', json2ts, TargetStationDataAccess, {
        # 'delete': (api_urls.TS_DELETE, ['POST']),
        'years': (api_urls.TS_YEARS, ['GET']),
    })
    ncrtes_api.register()

    def _find_snow_route(station_id, snow_routes):
        """

        :type station_id: str
        :type snow_routes: list[itypes.SnowRouteInfo]
        :rtype:
        """
        for snow_route in snow_routes:
            if station_id in [ rn.station_id for rn in snow_route.route1.rnodes + snow_route.route1.rnodes ]:
                return snow_route
        return None

    def _find_target_station_info(station_id, ts_list):
        """

        :type station_id: str
        :type ts_list: list[itypes.TargetStationInfo]
        :rtype: itypes.TargetStationInfo
        """
        for tsi in ts_list:
            if tsi.station_id == station_id:
                return tsi
        return None

    def _find_target_lane_info(station_id, tlc_list):
        """

        :type station_id: str
        :type tlc_list: list[itypes.TargetLaneConfigInfo]
        :rtype: itypes.TargetLaneConfigInfo
        """
        for tlci in tlc_list:
            if tlci.station_id == station_id:
                return tlci
        return None

    @app.route(api_urls.TS_LIST, methods=['POST'])
    def ncrtes_ts_list():
        try:
            year = int(request.form.get('year'))
            corridor_name = request.form.get('corridor_name')
            months = get_normal_months_from_year(year)
            wsDA = WinterSeasonDataAccess()
            wsi = wsDA.get_by_year(year)
            if not wsi:
                wsi = itypes.WinterSeasonInfo()
                wsi.set_months(months)
                wsi.name = 'WinterSeason %s-%s' % (months[0][0], months[-1][0])
                wsDA.insert(wsi, autocommit=True)
            wsDA.close()

            tsDA = TargetStationDataAccess()
            ts_list = tsDA.list_by_corridor_name(year, corridor_name)
            tsDA.close()

            snrDA = SnowRouteDataAccess()
            snow_routes = snrDA.list_by_year(year)
            snrDA.close()

            tlcDA = TargetLaneConfigDataAccess()
            tlc_list = tlcDA.list_by_corridor_name(year, corridor_name)
            tlcDA.close()

            # sort (from upstream to downstream)
            infra = ncrtes.get_infra()
            corr = infra.get_corridor_by_name(corridor_name)

            res = []
            for idx, st in enumerate(corr.stations):
                tsi = _find_target_station_info(st.station_id, ts_list)
                tlci = _find_target_lane_info(st.station_id, tlc_list)
                if not tsi:
                    snow_route = _find_snow_route(st.station_id, snow_routes)
                    print(idx, st.station_id)
                    tsi = itypes.TargetStationInfo()
                    tsi.winterseason_id = wsi.id if wsi else None
                    tsi.station_id = st.station_id
                    tsi.snowroute_id = snow_route.id if snow_route else None
                    tsi.snowroute_name = snow_route._snowroute_group.name if snow_route else None
                    tsi.corridor_name = st.corridor.name
                    tsi.detectors = tlci.detectors if tlci else ','.join([ det.name for det in lane.get_target_detectors(st) ])
                    tsi.normal_function_id = None
                    res.append(tsi)
                else:
                    print(idx, st.station_id)
                    tsi.detectors = tlci.detectors if tlci else ','.join([ det.name for det in lane.get_target_detectors(st) ])
                    res.append(tsi)

            res = [ v for v in res if v.detectors ]

        except Exception as ex:
            return prot.response_error('exception occured when retrieving data')

        return prot.response_success({'list': res})


    @app.route(api_urls.TS_UPDATE, methods=['POST'])
    def ncrtes_ts_update():
        year = int(request.form.get('year'))
        station_id = request.form.get('station_id')
        detectors = request.form.get('detectors')

        infra = ncrtes.get_infra()
        str_detectors = str(detectors)

        if not year:
            return prot.response_fail('Year Info must be entered.')

        if not station_id:
            return prot.response_fail('Station Info must be entered.')

        if not detectors:
            return prot.response_fail('Detectors must be entered.')

        station = infra.get_rnode(station_id)
        if not station:
            return prot.response_fail('Station %s does not exists.' % station_id)

        station_detectors = [ det.name for det in station.detectors ]
        detectors = [x.strip() for x in detectors.split(',')]
        for det_name in detectors:
            det = infra.get_detector(det_name)
            if not det:
                return prot.response_fail('Detector %s does not exists.' % det_name)
            if det.name not in station_detectors:
                return prot.response_fail('Detector %s does not exists on the station.' % det_name)

        wsDA = WinterSeasonDataAccess()
        wsi = wsDA.get_by_year(year)
        if not wsi:
            months = get_normal_months_from_year(year)
            wsi = itypes.WinterSeasonInfo()
            wsi.set_months(months)
            wsi.name = 'WinterSeason %s-%s' % (months[0][0], months[-1][0])
            wsDA.insert(wsi, autocommit=True)
        wsDA.close()

        tsDA = TargetStationDataAccess()
        ex_tsi = tsDA.get_by_station_id(year, station_id)
        tsDA.close()

        tlcDA = TargetLaneConfigDataAccess()
        ex_tlci = tlcDA.get_by_station_id(year, station_id)
        if not ex_tlci:
            ex_tlci = itypes.TargetLaneConfigInfo()
            ex_tlci.winterseason_id = wsi.id
            ex_tlci.station_id = station_id
            ex_tlci.detectors = ''
            ex_tlci.corridor_name = station.corridor.name
            model = tlcDA.insert(ex_tlci, autocommit=True)
            ex_tlci.id = model.id

        # update normal function
        if ex_tsi and ex_tlci.detectors != str_detectors:
            target_station = infra.get_rnode(ex_tlci.station_id)
            valid_detectors = [infra.get_detector(det_name) for det_name in detectors]
            normal_months = get_normal_months_from_year(year)
            nf, nfi = None, None
            try:
                nf, nfi = _update_normal_function(target_station, normal_months, valid_detectors)
            except Exception as ex:
                from pyticas.tool import tb
                tb.traceback(ex)

        # query to update database
        ex_tlci.detectors = ','.join(detectors)
        updated = tlcDA.update(ex_tlci.id, ex_tlci.get_dict(), autocommit=True)

        tlcDA.close()
        if updated:
            return prot.response_success(obj=ex_tlci.id)
        else:
            return prot.response_fail("fail to update (id={})".format(ex_tlci.id))


def _update_normal_function(target_station, normal_months, valid_detectors):
    """ get normal function and data using cache

    :type target_station: pyticas.ttypes.RNodeObject
    :type normal_months: list[(int, int)]
    :type valid_detectors: list[pyticas.ttypes.DetectorObject]
    :rtype: (pyticas_ncrtes.core.etypes.NSRFunction, pyticas_ncrtes.itypes.NormalFunctionInfo)
    """

    # delete cached file
    nsr_cache.clear_data(target_station.station_id, normal_months)

    dc = lambda det: det in valid_detectors
    nf = nsr_func.make(target_station, normal_months, dc=dc, valid_detectors=valid_detectors)
    if nf:
        # nfi = nsr_cache.dumps_function(nf, normal_months)
        ws = WinterSeasonDataAccess()
        wsi = ws.get_by_months(normal_months)
        if not wsi:
            wsi = itypes.WinterSeasonInfo()
            wsi.set_months(normal_months)
            wsi.name = 'WinterSeason %s-%s' % (normal_months[0][0], normal_months[-1][0])
            ws.insert(wsi, autocommit=True)

        da = NormalFunctionDataAccess()
        nfi = da.get_by_station(wsi.id, target_station.station_id)
        if not nfi:
            nfi = itypes.NormalFunctionInfo()
            nfi.station_id = target_station.station_id
            nfi.winterseason_id = wsi.id
            nfi.func = nf
            da.insert(nfi, autocommit=True)
        else:
            nfi.func = nf
            da.commit()

        #da.insert(nfi, autocommit=True)
        #print('normalfunction-inserted : ', nfi.id)

        ws.close()
        da.close()

        return nf, nfi
    else:
        return None, None
