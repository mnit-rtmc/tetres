# -*- coding: utf-8 -*-
from pyticas_tetres.db.tetres import model_yearly

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import enum

from functools import reduce
from pyticas.tool import json
from pyticas.ttypes import Serializable, PrecipIntens, PrecipType, SurfaceCondition
from pyticas_tetres.db.tetres import model


class InfoBase(Serializable):
    _info_type_ = None
    _route_attrs_ = []
    _dt_attrs_ = []
    _rel_attrs_ = {}
    _enum_attrs_ = []
    _json_attrs_ = []
    _lazy_json_attrs_ = []

    @classmethod
    def datetime2str(self, dt):
        """
        :type dt: datetime.datetime
        :rtype: str
        """
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def str2datetime(self, ds):
        """
        :type ds: str
        :rtype: datetime.datetime

        """
        return datetime.datetime.strptime(ds, '%Y-%m-%d %H:%M:%S')

    @classmethod
    def years_string(cls, syear, eyear):
        """
        :type syear: int
        :type eyear: int
        :rtype: str
        """
        return ','.join([str(y) for y in range(syear, eyear + 1)])

    @classmethod
    def corridor_string(cls, routes):
        """
        :type routes: list[pyticas.ttypes.Route]
        :return:
        """
        rnode_list = [r.rnodes for r in routes if r and r.rnodes]
        if len(rnode_list) == 1:
            rnodes = rnode_list[0]
        else:
            rnodes = reduce(lambda x, y: x + y, rnode_list)
        corrs = []
        for rn in rnodes:
            if rn.corridor.name not in corrs:
                corrs.append(rn.corridor.name)

        return ','.join(corrs)

    def get_dict(self):
        field_data = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if key in self._route_attrs_ or key in self._json_attrs_:
                value = json.dumps(value, only_name=True)
            field_data[key] = value
        return field_data

    def set_dict(self, dict_data):
        for key, value in dict_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return self.__str__()


class ConfigInfo(InfoBase):
    _info_type_ = 'config log'
    _dt_attrs_ = ['reg_date']

    def __init__(self):
        self.id = None
        """:type: int """
        self.name = None
        """:type: str """
        self.content = None
        """:type: str """

    def __str__(self):
        return ('<ConfigInfo id="%s" name="%s">' % (self.id, self.name))


class TTRouteInfo(InfoBase):
    _info_type_ = 'route'
    _route_attrs_ = ['route']

    def __init__(self, route=None):
        self.id = None
        """:type: int """
        self.name = None
        """:type: str """
        self.corridor = None
        """:type: str """
        self.description = None
        """:type: str """
        self.route = None
        """:type: pyticas.ttypes.Route """

        if route:
            self.set_route(route)

    def set_route(self, r):
        self.name = r.name
        self.corridor = r.rnodes[0].corridor.name
        self.description = r.desc
        self.route = r

    def corridors(self):
        """
        :rtype: list[pyticas.ttypes.CorridorObject]
        """
        if not self.route or not self.route.rnodes:
            return []
        else:
            res = []
            for rnode in self.route.rnodes:
                if rnode.corridor not in res:
                    res.append(rnode.corridor)
            return res

    def import_dict(self, d):
        self.name = d['name']
        self.description = d['description']
        self.corridor = d['corridor']
        self.route = d['route']

    def __str__(self):
        return '<TTRouteInfo id="%d" name="%s" corridor="%s">' % (
            self.id, self.name, self.corridor)


class SpecialEventInfo(InfoBase):
    _info_type_ = 'special event'
    _dt_attrs_ = ['start_time', 'end_time']

    def __init__(self):
        self.id = None
        """:type: int """
        self.name = None
        """:type: str """
        self.description = None
        """:type: str """
        self.years = None
        """:type: str """
        self.start_time = None
        """:type: str """
        self.end_time = None
        """:type: str """
        self.lat = None
        """:type: float """
        self.lon = None
        """:type: float """
        self.attendance = None
        """:type: int """

    def set_years(self):
        start_time = datetime.datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')
        self.years = self.years_string(start_time.year, end_time.year)

    def __str__(self):
        return '<SpecialEventInfo id="%d" name="%s" start_time="%s" end_time="%s" lat="%s" lon="%s" attendance="%s">' % (
            self.id, self.name, self.start_time, self.end_time, self.lat, self.lon, self.attendance)


class SnowRouteInfo(InfoBase):
    _info_type_ = 'snow route'
    _route_attrs_ = ['route1', 'route2']

    def __init__(self):
        self.id = None
        """:type: int """
        self.name = None
        """:type: str """
        self.description = None
        """:type: str """
        self.prj_id = None
        """:type: str """
        self.route1 = None
        """:type: pyticas.ttypes.Route """
        self.route2 = None
        """:type: pyticas.ttypes.Route """

    def __str__(self):
        return '<SnowRouteInfo id="%s">' % (self.id)


class SnowEventInfo(InfoBase):
    _info_type_ = 'snow event'
    _db_model_ = model.SnowEvent
    _dt_attrs_ = ['start_time', 'end_time']

    def __init__(self):
        self.id = None
        """:type: int """
        self.start_time = None
        """:type: str """
        self.end_time = None
        """:type: str """
        #
        # def set_duration_as_str(self, sdt, edt):
        #     """
        #     :type sdt: datetime.datetime
        #     :type edt: datetime.datetime
        #     """
        #     self.start_time = sdt.strftime('%Y-%m-%d %H:%M:%S')
        #     self.end_time = edt.strftime('%Y-%m-%d %H:%M:%S')
        #

    def __str__(self):
        return '<SnowEventInfo id="%s">' % (self.id)


class SnowManagementInfo(InfoBase):
    _info_type_ = 'snow management'
    _dt_attrs_ = ['lane_lost_time', 'lane_regain_time']
    _rel_attrs_ = {'_snowroute': {'key': 'sroute_id', 'info_cls': SnowRouteInfo, 'model_cls': model.SnowRoute},
                   '_snowevent': {'key': 'sevent_id', 'info_cls': SnowEventInfo, 'model_cls': model.SnowEvent}}

    def __init__(self):
        self.id = None
        """:type: int """
        self.sroute_id = None
        """:type: int """
        self.sevent_id = None
        """:type: int """
        self.lane_lost_time = None
        """:type: str """
        self.lane_regain_time = None
        """:type: str """
        self.duration = None
        """:type: float """
        self._snowroute = None
        """:type: SnowRouteInfo """
        self._snowevent = None
        """:type: SnowEventInfo """

    def __str__(self):
        return '<SnowManagementInfo id="%s">' % (self.id)


class WorkZoneGroupInfo(InfoBase):
    _info_type_ = 'work zone group'
    _db_model_ = model.WorkZoneGroup

    def __init__(self):
        self.id = None
        """:type: int """
        self.name = None
        """:type: str """
        self.description = None
        """:type: str """
        self.years = None
        """:type: str """
        self.corridors = None
        """:type: str """
        self.impact = None
        """:type: str """

    def __str__(self):
        return '<WorkZoneGroupInfo id="%s" name="%s">' % (self.id, self.name)


class RouteWiseMOEParametersInfo(InfoBase):
    _info_type_ = 'route wise moe parameters'
    _db_model_ = model.RouteWiseMOEParameters

    def __init__(self):
        self.id = None
        """:type: int """
        self.reference_tt_route_id = None
        """:type: int """
        self.moe_lane_capacity = None
        """:type: float """
        self.moe_critical_density = None
        """:type: float """
        self.moe_congestion_threshold_speed = None
        """:type: float """
        self.start_time = None
        """:type: str """
        self.end_time = None
        """:type: str """
        self.update_time = None
        """:type: str """

    def __str__(self):
        return '<Route Wise MOE Parameters id="%s" route_id="%s">' % (self.id, self.route_id)


class WorkZoneInfo(InfoBase):
    _info_type_ = 'work zone'
    _route_attrs_ = ['route1', 'route2']
    _dt_attrs_ = ['start_time', 'end_time']
    _rel_attrs_ = {'_wz_group': {'key': 'wz_group_id',
                                 'info_cls': WorkZoneGroupInfo,
                                 'model_cls': model.WorkZoneGroup}}

    def __init__(self):
        self.id = None
        """:type: int """
        self.wz_group_id = None
        """:type: int """
        self._wz_group = None
        """:type: WorkZoneGroupInfo """
        self.memo = None
        """:type: str """
        self.start_time = None
        """:type: str """
        self.end_time = None
        """:type: str """
        self.route1 = None
        """:type: pyticas.ttypes.Route """
        self.route2 = None
        """:type: pyticas.ttypes.Route """
        self.workzone_length = None
        """:type: float """

    def __str__(self):
        return '<WorkzoneInfo id="%d" wz_group_id="%d" start_time="%s" end_time="%s">' % (
            self.id, self.wz_group_id, self.start_time, self.end_time
        )


class WorkZoneFeatureInfo(InfoBase):
    _info_type_ = 'work feature'
    _rel_attrs_ = {'_workzone': {'key': 'wz_id', 'info_cls': WorkZoneInfo, 'model_cls': model.WorkZone}}

    def __init__(self):
        self.id = None
        """:type: int """
        self.wz_id = None
        """:type: int """
        self._workzone = None
        """:type: WorkZoneInfo """
        self.route_num = None
        """:type: int """
        self.closed_length = None
        """:type: int """
        self.closed_ramps = None
        """:type: int """
        self.has_shifted = None
        """:type: bool  """
        self.has_closed = None
        """:type: bool """
        self.use_opposing_lane = None
        """:type: bool """
        self.used_by_opposing_traffic = None
        """:type: bool """

    def __repr__(self):
        return '<WorkZoneFeatureInfo id="%d" wz_id="%d" route_num="%d" closed_length="%d" closed_ramps="%d" ' \
               'has_shifted="%d" has_closed="%d" use_opposing_lane="%d" used_by_opposing_traffic="%d">' % (
                   self.id, self.wz_id, self.route_num, self.closed_length, self.closed_ramps,
                   self.has_shifted, self.has_closed, self.use_opposing_lane, self.used_by_opposing_traffic)


class WorkZoneLaneConfigInfo(InfoBase):
    _info_type_ = 'work lane config'
    _rel_attrs_ = {'_workzone': {'key': 'wz_id', 'info_cls': WorkZoneInfo, 'model_cls': model.WorkZone}}

    def __init__(self):
        self.id = None
        """:type: int """
        self.wz_id = None
        """:type: int """
        self._workzone = None
        """:type: WorkZoneInfo """
        self.route_num = None
        """:type: int """
        self.origin_lanes = None
        """:type: int """
        self.open_lanes = None
        """:type: int """

    def __repr__(self):
        return '<WorkZoneLaneConfigInfo id="%d" wz_id="%d" route_num="%d" cfg="%d to %d">' % (
            self.id, self.wz_id, self.route_num, self.origin_lanes, self.open_lanes)


class IncidentTypeInfo(InfoBase):
    _info_type_ = 'incident type'

    def __init__(self):
        self.id = None
        """:type: int """
        self.eventtype = None
        """:type: str """
        self.eventtypecode = None
        """:type: str """
        self.eventsubtype = None
        """:type: str """
        self.eventsubtypecode = None
        """:type: str """
        self.classification = None
        """:type: str """
        self.iris_class = None
        """:type: str """
        self.iris_detail = None
        """:type: str """
        self.blocking = None
        """:type: bool """
        self.occupied = None
        """:type: bool """
        self.rollover = None
        """:type: bool """
        self.injury = None
        """:type: bool """
        self.fatal = None
        """:type: bool """
        self.cars_eventtype = None
        """:type: str """
        self.cars_eventtypecode = None
        """:type: str """

    def __str__(self):
        return '<IncidentTypeInfo id="%s" eventtype="%s" eventsubtype="%s">' % (
            self.id, self.eventtype, self.eventsubtype)


class IncidentInfo(InfoBase):
    _info_type_ = 'incident'
    _dt_attrs_ = ['cdts', 'udts', 'xdts']
    _rel_attrs_ = {'_incident_type': {'key': 'incident_type_id',
                                      'info_cls': IncidentTypeInfo,
                                      'model_cls': model.IncidentType}}

    def __init__(self):
        self.id = None
        """:type: int """
        self.corridor = None
        """:type: str """
        self.incident_type_id = None
        """:type: int """
        self._incident_type = None
        """:type: IncidentTypeInfo """
        self.cad_pkey = None
        """:type: int """
        self.iris_event_id = None
        """:type: int """
        self.iris_event_name = None
        """:type: int """

        self.cdts = None
        """:type: str """
        self.udts = None
        """:type: str """
        self.xdts = None
        """:type: str """
        self.lat = None
        """:type: float """
        self.lon = None
        """:type: float """

        self.road = None
        """:type: str """
        self.direction = None
        """:type: str """
        self.impact = None
        """:type: str """
        self.lane_type = None
        """:type: str """

        self.earea = None
        """:type: str """
        self.ecompl = None
        """:type: str """
        self.edirpre = None
        """:type: str """
        self.edirsuf = None
        """:type: str """
        self.efeanme = None
        """:type: str """
        self.efeatyp = None
        """:type: str """
        self.xstreet1 = None
        """:type: str """
        self.xstreet2 = None
        """:type: str """

    def __str__(self):
        return '<IncidentInfo id="%s" eventtype="%s" eventsubtype="%s" cdts="%s" udts="%s" xdts="%s" lat="%s" lon="%s">' % (
            self.id,
            self._incident_type.eventtype if self._incident_type else 'N/A',
            self._incident_type.eventsubtype if self._incident_type else 'N/A',
            self.cdts, self.udts, self.xdts,
            self.lat, self.lon)


class CADIncidentInfo(InfoBase):
    _info_type_ = 'CAD incident'
    _dt_attrs_ = ['cdts', 'udts', 'xdts']

    def __init__(self):
        self.id = None
        """:type: int """
        self.pkey = None
        """:type: int """
        self.eid = None
        """:type: int """
        self.openevent = None
        """:type: int """
        self.eventtype = None
        """:type: str """
        self.eventsubtype = None
        """:type: str """
        self.classification = None
        """:type: str """
        self.iris_class = None
        """:type: str """
        self.iris_detail = None
        """:type: str """
        self.cameranum = None
        """:type: int """
        self.cdts = None
        """:type: str """
        self.udts = None
        """:type: str """
        self.xdts = None
        """:type: str """
        self.lat = None
        """:type: float """
        self.lon = None
        """:type: float """
        self.xstreet1 = None
        """:type: str """
        self.xstreet2 = None
        """:type: str """
        self.location = None
        """:type: str """
        self.earea = None
        """:type: str """
        self.ecompl = None
        """:type: str """
        self.edirpre = None
        """:type: str """
        self.edirsuf = None
        """:type: str """
        self.efeanme = None
        """:type: str """
        self.efeatyp = None
        """:type: str """

    def __str__(self):
        return '<CADIncidentInfo pkey="%s" eid="%s" eventtype="%s" cdts="%s" udts="%s" xdts="%s" efeanme="%s" edirpre="%s" lat="%s" lon="%s">' % (
            self.pkey, self.eid, self.eventtype, self.cdts, self.udts, self.xdts, self.efeanme, self.edirpre, self.lat,
            self.lon
        )


class CADIncidentTypeInfo(InfoBase):
    _info_type_ = 'CAD incident type'

    def __init__(self):
        self.pkey = None
        """:type: int """
        self.eventtype = None
        """:type: str """
        self.eventtypecode = None
        """:type: str """
        self.eventsubtype = None
        """:type: str """
        self.eventsubtypecode = None
        """:type: str """
        self.classification = None
        """:type: str """
        self.iris_class = None
        """:type: str """
        self.iris_detail = None
        """:type: str """
        self.blocking = None
        """:type: bool """
        self.occupied = None
        """:type: bool """
        self.rollover = None
        """:type: bool """
        self.injury = None
        """:type: bool """
        self.fatal = None
        """:type: bool """
        self.cars_eventtype = None
        """:type: str """
        self.cars_eventtypecode = None
        """:type: str """

    def __str__(self):
        return '<CADIncidentTypeInfo pkey="%s" eventtype="%s" eventsubtype="%s">' % (
            self.pkey, self.eventtype, self.eventsubtype)


class IrisIncidentInfo(InfoBase):
    _info_type_ = 'iris'
    _dt_attrs_ = ['event_date']

    def __init__(self):
        self.id = None
        """:type: int """
        self.event_id = None
        """:type: int """
        self.name = None
        """:type: str """
        self.event_date = None
        """:type: str """
        self.description = None
        """:type: str """
        self.road = None
        """:type: str """
        self.direction = None
        """:type: str """
        self.impact = None
        """:type: str """
        self.cleared = None
        """:type: bool """
        self.confirmed = None
        """:type: bool """
        self.camera = None
        """:type: str """
        self.lane_type = None
        """:type: str """
        self.detail = None
        """:type: str """
        self.replaces = None
        """:type: str """
        self.lat = None
        """:type: float """
        self.lon = None
        """:type: float """

    def __str__(self):
        return '<IrisIncidentInfo event_id="%s" name="%s" event_date="%s" road="%s" direction="%s" impact="%s" lat="%s" lon="%s">' % (
            self.event_id, self.name, self.event_date, self.road, self.direction, self.impact, self.lat, self.lon
        )


class NoaaWeatherInfo(InfoBase):
    _info_type_ = 'noaa weather'
    _dt_attrs_ = ['dtime']

    def __init__(self, **kwargs):
        self.id = None
        """:type: int """
        self.usaf = None
        """:type: str """
        self.wban = None
        """:type: str """
        self.dtime = None
        """:type: str """
        self.precip = None
        """:type: float """
        self.precip_type = None
        """:type: str """
        self.precip_intensity = None
        """:type: str """
        self.precip_qc = None
        """:type: str """
        self.visibility = None
        """:type: float """
        self.visibility_qc = None
        """:type: str """
        self.obscuration = None
        """:type: str """
        self.descriptor = None
        """:type: str """
        self.air_temp = None
        """:type: float """
        self.air_temp_qc = None
        """:type: str """
        self.dew_point = None
        """:type: float """
        self.dew_point_qc = None
        """:type: str """
        self.relative_humidity = None
        """:type: float """
        self.wind_dir = None
        """:type: int """
        self.wind_dir_qc = None
        """:type: str """
        self.wind_speed = None
        """:type: float """
        self.wind_speed_qc = None
        """:type: str """
        self.wind_gust = None
        """:type: float """
        self.wind_gust_qc = None
        """:type: float """

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return '<NoaaWeatherInfo id="%s" usaf="%s" wban="%s" time="%s" precip="%s" precip_type="%s">' % (
            self.id, self.usaf, self.wban, self.dtime, self.precip, self.precip_type
        )


class WeatherInfo(InfoBase):
    _info_type_ = 'weather'
    _dt_attrs_ = ['dtime', 'pc_start_dtime', 'pc_end_dtime']
    _enum_attrs_ = {'pc_intens': PrecipIntens, 'pc_type': PrecipType, 'cond': SurfaceCondition}

    def __init__(self, **kwargs):
        self.id = None
        """:type: int """
        self.site_id = None
        """:type: str """
        self.dtime = None
        """:type: str """
        self.air_temp = None
        """:type: float """
        self.temp_alt = None
        """:type: float """
        self.temp_max = None
        """:type: float """
        self.temp_min = None
        """:type: float """
        self.dew_point = None
        """:type: str """
        self.rh = None
        """:type: int """
        self.pc_type = None
        """:type: pyticas.ttypes.PrecipType """
        self.pc_intens = None
        """:type: pyticas.ttypes.PrecipIntens """
        self.pc_rate = None
        """:type: int """
        self.pc_accum = None
        """:type: int """
        self.pc_accum_10min = None
        """:type: int """
        self.pc_start_dtime = None
        """:type: str """
        self.pc_end_dtime = None
        """:type: str """
        self.pc_past_1hour = None
        """:type: int """
        self.pc_past_3hours = None
        """:type: int """
        self.pc_past_6hours = None
        """:type: int """
        self.pc_past_12hours = None
        """:type: int """
        self.pc_past_24hours = None
        """:type: int """
        self.pc_time_since = None
        """:type: int """
        self.wet_build_temp = None
        """:type: int """
        self.vis_distance = None
        """:type: int """
        self.vis_situation = None
        """:type: int """
        self.barometric = None
        """:type: int """
        self.wnd_spd_avg = None
        """:type: int """
        self.wnd_spd_gust = None
        """:type: int """
        self.wnd_dir_avg = None
        """:type: int """
        self.wnd_dir_gust = None
        """:type: int """
        self.cond = None
        """:type: float """
        self.sf_temp = None
        """:type: int """
        self.frz_temp = None
        """:type: int """
        self.chem = None
        """:type: int """
        self.chem_pct = None
        """:type: int """
        self.depth = None
        """:type: int """
        self.ice_pct = None
        """:type: int """
        self.salinity = None
        """:type: int """
        self.conductivity = None
        """:type: int """
        self.blackice_signal = None
        """:type: int """
        self.error = None
        """:type: int """

        for k, v in kwargs.items():
            setattr(self, k, v)


class TravelTimeInfo(InfoBase):
    # faverolles 10/8/2019 [B]: HERE
    _info_type_ = 'travel time'
    _dt_attrs_ = ['time']

    def __init__(self):
        self.id = None
        """:type: int """
        self.route_id = None
        """:type: int """
        self.time = None
        """:type: str """
        self.tt = None
        """:type: float """
        self.vmt = None
        """:type: float """
        self.speed = None
        """:type: float """

        self.vht = None
        """:type: float """
        self.dvh = None
        """:type: float """
        self.lvmt = None
        """:type: float """
        self.sv = None
        """:type: float """

        self._weather = None
        """:type: NoaaWeatherInfo"""
        self._incidents = None
        """:type: list[IncidentInfo] """
        self._workzones = None
        """:type: list[WorkzoneInfo] """
        self._specialevents = None
        """:type: list[SpecialeventInfo] """
        self._snowmanagements = None
        """:type: list[SnowmanagementInfo] """

    def __str__(self):
        return '<TravelTimeInfo id="%s" route_id="%s" time="%s" tt="%s" vmt="%s" speed="%s">' % (
            self.id, self.route_id, self.time, self.tt, self.vmt, self.speed)
        # return f'<TravelTimeInfo id="{self.id:s}" route_id="{self.route_id:s}" time="{self.time:s}" ' \
        #        f'tt="{self.tt:s}" vmt="{self.vmt:s}" speed="{self.speed:s}"> ' \
        #        f'vht="{self.vht:s}" dvh="{self.dvh:s}" lvmt="{self.lvmt:s}" ' \
        #        f'cm="{self.cm:s}" cmh="{self.cmh:s}" sv="{self.sv:s}" ' \
        #        f'acceleration="{self.acceleration:s}" uvmt="{self.uvmt:s}">'


class TODReliabilityInfo(InfoBase):
    _info_type_ = 'tod reliability'
    _dt_attrs_ = ['time']

    def __init__(self):
        self.id = None
        """:type: int """
        self.route_id = None
        """:type: int """
        self._route = None
        """:type: TTRouteInfo """
        self.regime_type = None
        """:type: int """
        self.hour = None
        """:type: int """
        self.minute = None
        """:type: int """
        self.result = None
        """:type: str """

    def __str__(self):
        return '<TODReliabilityInfo id="%d" route_id="%d" regime_type="%d" time="%02d:%02d">' % (
            self.id, self.route_id, self.regime_type, self.hour, self.minute)


# class IncidentSeverity(TupleEnum):
#     K = ("Fatal", 180)
#     A = ("Incapacitating Injury", 90)
#     B = ("Non-incapacitating Injury", 45)
#     C = ("Possible Injury", 30)
#     N = ("Property Damage", 30)
#     UNKNOWN = ("Unknown", 30)
#
# class IncidentImpact(TupleEnum):
#     RC = ("Road Closed", 1)
#     LCS = ("2+ Lanes Closed", 2)
#     LC = ("Lane Closed", 3)
#     BL = ("Blocking", 4)
#     OS = ("On Shoulder", 5)
#     NB = ("Not Blocking", 6)
#     ROR = ("Ran Off Road", 7)
#     UNKNOWN = ("Unknown", 8)
#
# class IncidentType(TupleEnum):
#     C = ("Crash", 1)
#     DV = ("Disabled Vehicle", 2)
#     D = ("Debris", 3)
#     O = ("Other Incident", 4)


class TTExtInfo(InfoBase):

    def __init__(self, **kwargs):
        self.tt_id = None
        """:type: int """
        self._tt = None
        """:type: TravelTimeInfo """
        self.is_extended = False


class TTWeatherInfo(TTExtInfo):
    _info_type_ = 'tt-weather'
    _rel_attrs_ = {
        '_tt': {'key': 'tt_id', 'info_cls': TravelTimeInfo,
                'model_cls': lambda year: model_yearly.get_tt_table(int(year))},
        '_weather': {'key': 'weather_id', 'info_cls': NoaaWeatherInfo,
                     'model_cls': lambda year: model_yearly.get_noaa_table(int(year))}}

    def __init__(self, **kwargs):
        super(TTWeatherInfo, self).__init__()
        self.id = None
        """:type: int """
        self.tt_id = None
        """:type: int """
        self.weather_id = None
        """:type: int """
        self._tt = None
        """:type: TravelTimeInfo """
        self._weather = None
        """:type: NoaaWeatherInfo """

    def __str__(self):
        return '<TTWeatherInfo id="%d" tt_id="%d" weather_id="%d">' % (self.id, self.tt_id, self.weather_id)


class TTWorkzoneInfo(TTExtInfo):
    _info_type_ = 'tt-workzone'
    _rel_attrs_ = {
        '_tt': {'key': 'tt_id', 'info_cls': TravelTimeInfo,
                'model_cls': lambda year: model_yearly.get_tt_table(int(year))},
        '_workzone': {'key': 'workzone_id', 'info_cls': WorkZoneInfo, 'model_cls': model.WorkZone},
        # '_feature': {'key': 'feature_id', 'info_cls': WorkZoneFeatureInfo, 'model_cls': model.WorkZoneFeature},
        # '_laneconfig': {'key': 'laneconfig_id', 'info_cls': WorkZoneLaneConfigInfo, 'model_cls': model.WorkZoneLaneConfig},
    }

    def __init__(self, **kwargs):
        super().__init__()
        self.id = None
        """:type: int """
        self.tt_id = None
        """:type: int """
        self.workzone_id = None
        """:type: int """
        # self.feature_id = None
        # """:type: int """
        # self.laneconfig_id = None
        # """:type: int """
        self._tt = None
        """:type: TravelTimeInfo """
        self._workzone = None
        """:type: WorkZoneInfo """
        # self._feature = None
        # """:type: WorkZoneFeatureInfo """
        # self._laneconfig = None
        # """:type: WorkZoneLaneConfigInfo """
        self.loc_type = None
        """:type: int """
        self.distance = None
        """:type: float """
        self.off_distance = None
        """:type: float """
        # self.characteristics = None
        # """:type: str """

    def __str__(self):
        return '<TTWorkzoneInfo id="%d" tt_id="%d" workzone_id="%d" loc_type="%d" distance="%.2f" off_distance="%.2f>' % (
            self.id, self.tt_id, self.workzone_id, self.loc_type,
            self.distance, self.off_distance)


class TTIncidentInfo(TTExtInfo):
    _info_type_ = 'tt-incident'
    _rel_attrs_ = {
        '_tt': {'key': 'tt_id', 'info_cls': TravelTimeInfo,
                'model_cls': lambda year: model_yearly.get_tt_table(int(year))},
        '_incident': {'key': 'incident_id', 'info_cls': IncidentInfo, 'model_cls': model.Incident}}

    def __init__(self, **kwargs):
        super().__init__()
        self.id = None
        """:type: int """
        self.tt_id = None
        """:type: int """
        self.incident_id = None
        """:type: int """
        self._tt = None
        """:type: TravelTimeInfo """
        self._incident = None
        """:type: IncidentInfo """
        self.distance = None  # distance in mile from the upstream boundary of TTR route, negative value means incident is occure in upstream
        """:type: float """
        self.off_distance = None  # distance in mile from boundary of TTR route
        """:type: float """

    def get_incident(self):
        """
        :rtype: IncidentInfo
        """
        return self._incident

    def get_tt_info(self):
        """
        :rtype: TravelTimeInfo
        """
        return self._tt

    def __str__(self):
        return '<TTIncidentInfo id="%d" tt_id="%d" incident_id="%d" distance="%.2f" off_distance="%.2f">' % (
            self.id, self.tt_id, self.incident_id, self.distance, self.off_distance)


class TTSpecialeventInfo(TTExtInfo):
    _info_type_ = 'tt-specialevent'
    _rel_attrs_ = {
        '_tt': {'key': 'tt_id', 'info_cls': TravelTimeInfo,
                'model_cls': lambda year: model_yearly.get_tt_table(int(year))},
        '_specialevent': {'key': 'specialevent_id', 'info_cls': SpecialEventInfo, 'model_cls': model.Specialevent}}

    def __init__(self, **kwargs):
        super().__init__()
        self.id = None
        """:type: int """
        self.tt_id = None
        """:type: int """
        self.specialevent_id = None
        """:type: int """
        self._tt = None
        """:type: TravelTimeInfo """
        self._specialevent = None
        """:type: SpecialEventInfo """
        self.distance = None
        """:type: float """
        self.event_type = None
        """:type: str """

    def __str__(self):
        return '<TTSpecialEvent id="%d" tt_id="%d" specialevent_id="%d" distance="%d" event_type="%s">' % (
            self.id, self.tt_id, self.specialevent_id, self.distance, self.event_type)


class TTSnowManagementInfo(TTExtInfo):
    _info_type_ = 'tt-workzone'
    _rel_attrs_ = {
        '_tt': {'key': 'tt_id', 'info_cls': TravelTimeInfo,
                'model_cls': lambda year: model_yearly.get_tt_table(int(year))},
        '_snowmgmt': {'key': 'snowmgmt_id', 'info_cls': SnowManagementInfo, 'model_cls': model.SnowManagement}}

    def __init__(self, **kwargs):
        super().__init__()
        self.id = None
        """:type: int """
        self.tt_id = None
        """:type: int """
        self.snowmgmt_id = None
        """:type: int """
        self._tt = None
        """:type: TravelTimeInfo """
        self._snowmgmt = None
        """:type: SnowManagementInfo """
        self.loc_type = None
        """:type: int """
        self.distance = None
        """:type: float """
        self.off_distance = None
        """:type: float """
        self.road_status = None
        """:type: int """
        self.recovery_level = None
        """:type: int """

    def __str__(self):
        return '<TTSnowManagementInfo id="%s" tt_id="%d" snowmgmt_id="%d" loc_type="%d" distance="%.2f" off_distance="%.2f" road_status="%d">' % (
            self.id, self.tt_id, self.snowmgmt_id, self.loc_type,
            self.distance, self.off_distance, self.road_status)


class LOC_TYPE(enum.Enum):
    UP = 1
    UP_OVERLAPPED = 2
    INSIDE = 3
    DOWN = 4
    DOWN_OVERLAPPED = 5
    WRAP = 6

    @classmethod
    def get_by_value(cls, num):
        """
        :type num: int
        :rtype: LOC_TYPE
        """
        for name, member in LOC_TYPE.__members__.items():
            if member.value == num:
                return member
        return None


class WZCharacteristics(enum.Enum):
    USE_OPPOSING_LANE = 1
    USED_BY_OPPOSING_TRAFFICS = 2
    HAS_CLOSED_LANES = 3
    HAS_SHIFTED_LANES = 4
    HAS_CLOSED_RAMPS = 5


# used in user-client
class EstimationRequestInfo(InfoBase):
    _info_type_ = 'estimation request info'

    def __init__(self, route=None):
        self.travel_time_route = None
        """:type: pyticas_tetres.ttypes.TTRouteInfo """
        self.start_date = None
        """:type: str """
        self.end_date = None
        """:type: str """
        self.start_time = None
        """:type: str """
        self.end_time = None
        """:type: str """
        self.weekdays = None
        """:type: pyticas_tetres.ttypes.WeekdayConditionInfo """
        self.except_holiday = None
        """:type: bool """
        self.estmation_mode = None
        """:type: pyticas_tetres.ttypes.ReliabilityEstimationModeInfo """
        self.operating_conditions = None
        """:type: list[pyticas_tetres.ttypes.OperatingConditionsInfo] """
        self.oc_param = None
        """:type: pyticas_tetres.ttypes.OperatingConditionParamInfo """
        self.write_spreadsheets = None
        """:type: bool """
        self.write_graph_images = None
        """:type: bool """

        # faverolles 1/22/2020: Added for selectable parameter in Admin Client
        self.write_moe_spreadsheet = None
        """:type: bool """

        self._dbsession = None
        """:type: sqlalchemy.orm.Session """

    def add_start_time_offset(self, offset=0):
        start_time_object_with_offset = datetime.datetime.strptime(self.start_time, '%H:%M:%S') + datetime.timedelta(
            minutes=offset)
        self.start_time = start_time_object_with_offset.strftime('%H:%M:%S')

    def get_start_date(self):
        return self._get_date(self.start_date)

    def get_end_date(self):
        return self._get_date(self.end_date)

    def get_start_time(self, offset=None):
        return self._get_time(self.start_time, offset=offset)

    def get_end_time(self):
        return self._get_time(self.end_time)

    def _get_date(self, dts):
        """

        :type dts: str
        :rtype: datetime.date
        """
        if not dts:
            return None
        return datetime.datetime.strptime(dts, '%Y-%m-%d').date()

    def _get_time(self, dts, offset=None):
        """

        :type dts: str
        :rtype: datetime.time
        """
        if not dts:
            return None
        if not offset:
            return datetime.datetime.strptime(dts, '%H:%M:%S').time()
        else:
            return (datetime.datetime.strptime(dts, '%H:%M:%S') + datetime.timedelta(minutes=offset)).time()

    def __str__(self):
        return '<EstimationRequestInfo route_id="%s" start_date="%s" end_date="%s" start_time="%s" end_time="%s">' % (
            self.travel_time_route.id if self.travel_time_route else 'N/A',
            self.start_date, self.end_date,
            self.start_time, self.end_time)


class ReliabilityEstimationModeInfo(InfoBase):
    _info_type_ = 'reliability estimation mode'

    def __init__(self):
        self.mode_daily = None
        """:type: bool """
        self.mode_tod = None
        """:type: bool """
        self.mode_whole = None
        """:type: bool """

    def __str__(self):
        return '<ReliabilityEstimationModeInfo mode_daily="%s" mode_tod="%s" mode_whole="%s">' % (
            self.mode_daily, self.mode_tod, self.mode_whole)


class WeekdayConditionInfo(InfoBase):
    _info_type_ = 'weekdays'

    def __init__(self):
        self.sunday = None
        """:type: bool """
        self.monday = None
        """:type: bool """
        self.tuesday = None
        """:type: bool """
        self.wednesday = None
        """:type: bool """
        self.thursday = None
        """:type: bool """
        self.friday = None
        """:type: bool """
        self.saturday = None
        """:type: bool """

    def get_weekdays(self):
        """
        :type weekdays: pyticas_tetres.ttypes.WeekdayConditionInfo
        :rtype: list[int]
        """
        weekday_numbers = []
        if (self.sunday): weekday_numbers.append(6)
        if (self.monday): weekday_numbers.append(0)
        if (self.tuesday): weekday_numbers.append(1)
        if (self.wednesday): weekday_numbers.append(2)
        if (self.thursday): weekday_numbers.append(3)
        if (self.friday): weekday_numbers.append(4)
        if (self.saturday): weekday_numbers.append(5)
        return weekday_numbers

    def __str__(self):
        return '<WeekdayConditionInfo sunday-moday="%s">' % (
            [self.sunday, self.monday, self.tuesday, self.wednesday, self.thursday, self.friday, self.saturday])


class OperatingConditionsInfo(InfoBase):
    _info_type_ = 'operating conditions'

    def __init__(self):
        self.name = None
        """:type: str """
        self.desc = None
        """:type: str """
        self.weather_conditions = None
        """:type: list[WeatherConditionInfo] """
        self.incident_conditions = None
        """:type: list[IncidentConditionInfo] """
        self.workzone_conditions = None
        """:type: list[WorkzoneConditionInfo] """
        self.specialevent_conditions = None
        """:type: list[SpecialeventConditionInfo] """
        self.snowmanagement_conditions = None
        """:type: list[SnowmanagementConditionInfo] """

    def __str__(self):
        return '<OperatingConditionsInfo name="%s" desc="%s">' % (self.name, self.desc)


class WeatherConditionInfo(InfoBase):
    _info_type_ = 'weather condition'

    def __init__(self):
        self.type = None
        """:type: str """
        self.intensity = None
        """:type: str """

    def __str__(self):
        return ('<WeatherConditionInfo type="%s" intensity="%s">'
                % (self.type, self.intensity))


class IncidentConditionInfo(InfoBase):
    _info_type_ = 'incident condition'

    def __init__(self):
        self.type = None
        """:type: str """
        self.impact = None
        """:type: str """
        self.severity = None
        """:type: str """

    def __str__(self):
        return ('<IncidentConditionInfo type="%s" impact="%s" severity="%s">'
                % (self.type, self.impact, self.severity))


class WorkzoneConditionInfo(InfoBase):
    _info_type_ = 'workzone condition'

    def __init__(self):
        self.relative_location = None
        """:type: str """
        self.impact = None
        """:type: str """
        self.workzone_length = None
        """:type: str """

    def __str__(self):
        return ('<WorkzoneConditionInfo relative_location="%s" impact="%s">'
                % (self.relative_location, self.impact))


class SpecialeventConditionInfo(InfoBase):
    _info_type_ = 'special event condition'

    def __init__(self):
        self.distance = None
        """:type: str """
        self.event_size = None
        """:type: str """
        self.event_time = None
        """:type: str """


class SnowmanagementConditionInfo(InfoBase):
    _info_type_ = 'snow management condition'

    def __init__(self):
        self.road_condition = None
        """:type: str """

    def __str__(self):
        return '<SnowmanagementConditionInfo road_condition="%s">' % self.road_condition


class ActionLogInfo(InfoBase):
    _info_type_ = 'action log'
    _dt_attrs_ = ['reg_date', 'handled_date', 'status_updated_date']

    def __init__(self):
        self.id = None
        """:type: int """
        self.action_type = None
        """:type: str """
        self.target_datatype = None
        """:type: str """
        self.target_table = None
        """:type: str """
        self.target_id = None
        """:type: int """
        self.handled = None
        """:type: bool """
        self.handled_date = None
        """:type: str """
        self.status = None
        """:type: str """
        self.status_updated_date = None
        """:type: str """
        self.reason = None
        """:type: str """
        self.user_ip = None
        """:type: str """
        self.data_desc = None
        """:type: str """
        self.reg_date = None
        """:type: str """

    def __str__(self):
        return ('<ActionLogInfo id="%s" action_type="%s" target_datatype="%s" target_table="%s" target_id="%s" '
                'handled="%s" handled_date="%s" status="%s" status_update_date="%s" user_ip="%s" reg_date="%s">' % (
                    self.id,
                    self.action_type,
                    self.target_datatype,
                    self.target_table,
                    self.target_id,
                    self.handled,
                    self.handled_date,
                    self.status,
                    self.status_updated_date,
                    self.user_ip,
                    self.reg_date))


class SystemConfigInfo(InfoBase):
    _info_type_ = 'system config'

    def __init__(self):
        self.data_archive_start_year = None
        """:type: int """
        self.daily_job_start_time = None
        """:type: str """
        self.daily_job_offset_days = None
        """:type: int """
        self.weekly_job_start_day = None
        """:type: str """
        self.weekly_job_start_time = None
        """:type: str """
        self.monthly_job_start_date = None
        """:type: int """
        self.monthly_job_start_time = None
        """:type: str """
        self.incident_downstream_distance_limit = None
        """:type: float """
        self.incident_upstream_distance_limit = None
        """:type: float """
        self.workzone_downstream_distance_limit = None
        """:type: float """
        self.workzone_upstream_distance_limit = None
        """:type: float """
        self.specialevent_arrival_window = None
        """:type: int """
        self.specialevent_departure_window1 = None
        """:type: int """
        self.specialevent_departure_window2 = None
        """:type: int """

        # faverolles 1/12/2020: Adding AdminClient MOE Config Parameters
        self.moe_critical_density = None
        """:type: float """
        self.moe_lane_capacity = None
        """:type: float """
        self.moe_congestion_threshold_speed = None
        """:type: float """

    def __str__(self):
        return '<SystemConfigInfo>'


class OperatingConditionParamInfo(InfoBase):
    _info_type_ = 'operating condition param'

    def __init__(self):
        self.incident_downstream_distance_limit = None
        """:type: float """
        self.incident_upstream_distance_limit = None
        """:type: float """
        self.incident_keep_in_minute = None
        """:type: int """
        self.workzone_downstream_distance_limit = None
        """:type: float """
        self.workzone_upstream_distance_limit = None
        """:type: float """
        self.workzone_length_short_from = None
        """:type: float """
        self.workzone_length_short_to = None
        """:type: float """
        self.workzone_length_medium_from = None
        """:type: float """
        self.workzone_length_medium_to = None
        """:type: float """
        self.workzone_length_long_from = None
        """:type: float """
        self.workzone_length_long_to = None
        """:type: float """
        self.specialevent_size_small_from = None
        """:type: int """
        self.specialevent_size_small_to = None
        """:type: int """
        self.specialevent_size_medium_from = None
        """:type: int """
        self.specialevent_size_medium_to = None
        """:type: int """
        self.specialevent_size_large_from = None
        """:type: int """
        self.specialevent_size_large_to = None
        """:type: int """
        self.specialevent_distance_near_from = None
        """:type: float """
        self.specialevent_distance_near_to = None
        """:type: float """
        self.specialevent_distance_middle_from = None
        """:type: float """
        self.specialevent_distance_middle_to = None
        """:type: float """
        self.specialevent_distance_far_from = None
        """:type: float """
        self.specialevent_distance_far_to = None
        """:type: float """

    def __str__(self):
        return '<OperatingConditionParamInfo>'
