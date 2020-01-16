# -*- coding: utf-8 -*-

import datetime

from pyticas import period
from pyticas.tool import tb
from pyticas_tetres import cfg
from pyticas_tetres.da import tt, tt_workzone, tt_snowmgmt
from pyticas_tetres.da import tt_specialevent, tt_incident, tt_weather, wz_feature, wz_laneconfig
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine.filter.ftypes import ExtData
from pyticas_tetres.rengine.helper import wz_feature as wz_feature_helper

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def extract_tt(ttri, start_date, end_date, start_time, end_time, filters, **kwargs):
    """
    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type start_date: datetime.date
    :type end_date: datetime.date
    :type start_time: datetime.time
    :type end_time: datetime.time
    :type filters: list[pyticas_tetres.rengine.filter.ExtFilterGroup]
    """
    daily_periods = period.create_periods(start_date, end_date, datetime.time(0, 0, 0), datetime.time(23, 59, 59),
                                          cfg.TT_DATA_INTERVAL, **kwargs)
    extract_tt_by_periods(ttri, daily_periods, start_time, end_time, filters)


def extract_tt_by_periods(ttri, periods, start_time, end_time, filters):
    """

    **important**
    each period must be whole day time period

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type periods: list[pyticas.ttypes.Period]
    :type filters: list[pyticas_tetres.rengine.filter.ExtFilterGroup]
    """
    logger = getLogger(__name__)
    # sess = conn.get_session()
    das = {}
    all_wz_features = {}
    all_wz_laneconfigs = {}

    # collecting daily data
    for prd in periods:
        logger.debug('>>>> retrieving data for %s' % prd.get_date_string())
        year = prd.start_date.year
        sdate = prd.start_date
        edate = prd.end_date
        if year not in das:
            da_tt = tt.TravelTimeDataAccess(year)
            da_tt_wz = tt_workzone.TTWorkZoneDataAccess(year)
            da_tt_wz_feature = wz_feature.WZFeatureDataAccess()
            da_tt_wz_lncfg = wz_laneconfig.WZLaneConfigDataAccess()
            da_tt_weather = tt_weather.TTWeatherDataAccess(year)
            da_tt_snowmgmt = tt_snowmgmt.TTSnowManagementDataAccess(year)
            da_tt_incident = tt_incident.TTIncidentDataAccess(year)
            da_tt_specialevent = tt_specialevent.TTSpecialeventDataAccess(year)
            das[year] = (
                da_tt, da_tt_wz, da_tt_wz_feature, da_tt_wz_lncfg, da_tt_weather, da_tt_snowmgmt, da_tt_incident,
                da_tt_specialevent)

        (da_tt, da_tt_wz, da_tt_wz_feature, da_tt_wz_lncfg, da_tt_weather, da_tt_snowmgmt, da_tt_incident,
         da_tt_specialevent) = das[year]

        # traveltimes = da_tt.list_by_period(ttri.id, self.prd)
        weathers = da_tt_weather.list(ttri.id, sdate, edate, as_model=True)
        """:type: list[pyticas_tetres.ttrms_types.WeatherInfo] """
        workzones = da_tt_wz.list(ttri.id, sdate, edate, as_model=True)
        """:type: list[pyticas_tetres.ttrms_types.WorkZoneInfo] """
        incidents = da_tt_incident.list(ttri.id, sdate, edate, as_model=True)
        """:type: list[pyticas_tetres.ttrms_types.IncidentInfo] """
        snowmgmts = da_tt_snowmgmt.list(ttri.id, sdate, edate, as_model=True)
        """:type: list[pyticas_tetres.ttrms_types.SnowManagementInfo] """
        specialevents = da_tt_specialevent.list(ttri.id, sdate, edate, as_model=True)
        """:type: list[pyticas_tetres.ttrms_types.SpecialEventInfo] """
        traveltimes = da_tt.list_by_period(ttri.id, prd)
        """:type: list[pyticas_tetres.ttrms_types.TravelTimeInfo] """

        if not any(weathers):
            logger.debug('>>>> end of retrieving data for %s (no weather data)' % prd.get_date_string())
            continue

        extras = {
            'weathers': {_tt.id: [] for _tt in traveltimes},
            'workzones': {_tt.id: [] for _tt in traveltimes},
            'incidents': {_tt.id: [] for _tt in traveltimes},
            'specialevents': {_tt.id: [] for _tt in traveltimes},
            'snowmgmts': {_tt.id: [] for _tt in traveltimes},
        }
        """:type: dict[str, dict[int, list]]"""

        _put_to_bucket(ttri, weathers, extras['weathers'], da_tt_weather, year, all_wz_features, all_wz_laneconfigs, das)
        _put_to_bucket(ttri, workzones, extras['workzones'], da_tt_wz, year, all_wz_features, all_wz_laneconfigs, das)
        _put_to_bucket(ttri, incidents, extras['incidents'], da_tt_incident, year, all_wz_features, all_wz_laneconfigs, das)
        _put_to_bucket(ttri, snowmgmts, extras['snowmgmts'], da_tt_snowmgmt, year, all_wz_features, all_wz_laneconfigs, das)
        _put_to_bucket(ttri, specialevents, extras['specialevents'], da_tt_specialevent, year, all_wz_features, all_wz_laneconfigs, das)

        for tti in traveltimes:
            _tt_weathers = extras['weathers'][tti.id]
            extdata = ExtData(tti,
                              _tt_weathers[0] if _tt_weathers else None,
                              extras['incidents'][tti.id],
                              extras['workzones'][tti.id],
                              extras['specialevents'][tti.id],
                              extras['snowmgmts'][tti.id])

            if start_time <= tti.str2datetime(tti.time).time() <= end_time:
                for ef in filters:
                    try:
                        ef.check(extdata)
                    except Exception as ex:
                        tb.traceback(ex)
                        logger.debug('>>>> end of retrieving data for %s (error occured 1)' % prd.get_date_string())
                        continue
            else:
                for ef in filters:
                    try:
                        ef.check_outofrange(extdata)
                    except Exception as ex:
                        tb.traceback(ex)
                        logger.debug('>>>> end of retrieving data for %s (error occured 2)' % prd.get_date_string())
                        continue

        del extras
        logger.debug('>>>> end of retrieving data for %s' % prd.get_date_string())

    # sess.close()

def _put_to_bucket(ttri, extdata_list, extras_slot, da, year, all_wz_features, all_wz_laneconfigs, das):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type extdata_list: list[object]
    :type extras_slot: dict
    :type da: object
    :type year: int
    :return:
    """
    (da_tt, da_tt_wz, da_tt_wz_feature, da_tt_wz_lncfg, da_tt_weather, da_tt_snowmgmt, da_tt_incident,
     da_tt_specialevent) = das[year]
    for v in extdata_list:
        if hasattr(v, 'workzone_id') and hasattr(v, '_workzone'):
            if v.workzone_id not in all_wz_features:
                _features = da_tt_wz_feature.list(v.workzone_id)
                _lncfgs = da_tt_wz_lncfg.list(v.workzone_id)
                features, lncfgs = wz_feature_helper.get_wz_feature(v._workzone, _features, _lncfgs, ttri.corridor)
                all_wz_features[v.workzone_id] = features
                all_wz_laneconfigs[v.workzone_id] = lncfgs
            else:
                features = all_wz_features[v.workzone_id]
                lncfgs = all_wz_laneconfigs[v.workzone_id]

            # TODO: Laneconfig must be updated to one data set
            setattr(v, 'features', features if features else None)
            setattr(v, 'laneconfigs', lncfgs if lncfgs else None)

        bucket = extras_slot.get(v.tt_id, [])
        bucket.append(da.da_base.to_info(v, none_route=True))
        extras_slot[v.tt_id] = bucket