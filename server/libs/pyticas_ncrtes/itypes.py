# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.itypes
======================

- data types used in communications with the client which are convertable to JSON type
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas.tool import json
from pyticas.ttypes import Serializable
from pyticas_ncrtes.db import model


class InfoBase(Serializable):
    _info_type_ = None
    _route_attrs_ = []
    _dt_attrs_ = []
    _json_attrs_ = []
    _enum_attrs_ = []
    _rel_attrs_ = {}

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
            rnodes = []
            for rnl in rnode_list:
                rnodes.extend(rnl)
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


class WinterSeasonInfo(InfoBase):
    def __init__(self):
        self.id = None
        """:type: int """
        self.name = None
        """:type: str """
        self.year = None
        """:type: int"""
        self.months = None
        """:type: str """

    def get_months(self):
        """

        :rtype: list[(int, int)]
        """
        yms = []
        for ym in self.months.split('-'):
            yms.append((int(ym[:4]), int(ym[4:])))
        return yms

    def set_months(self, months):
        """

        :type months: list[(int, int)]
        """
        self.year, self.months = WinterSeasonInfo.months_str(months)

    @classmethod
    def months_str(cls, months):
        years = ['%d%02d' % (y, m) for (y, m) in months]
        return int(years[0][:4]), '-'.join(sorted(years))

    def __str__(self):
        return ('<WinterSeasonInfo id=%d year=%d>'
                % (self.id, self.year))


class NormalDataInfo(InfoBase):
    _json_attrs_ = ['nsr_data']

    def __init__(self):
        self.id = None
        """:type: int """
        self.station_id = None
        """:type: str """
        self.winterseason_id = None
        """:type: int """
        self.data = None
        """:type: NSRData """


class NormalFunctionInfo(InfoBase):
    _json_attrs_ = ['func']

    def __init__(self):
        self.id = None
        """:type: int """
        self.station_id = None
        """:type: str """
        self.winterseason_id = None
        """:type: int """
        self.func = None
        """:type: pyticas_ncrtes.core.etypes.NSRFunction """


class SnowRouteGroupInfo(InfoBase):
    _info_type_ = 'snow route group'

    def __init__(self):
        self.id = None
        """:type: int """
        self.name = None
        """:type: str """
        self.region = None
        """:type: str """
        self.sub_region = None
        """:type: str """
        self.year = None
        """:type: int """
        self.description = None
        """:type: str """


class SnowRouteInfo(InfoBase):
    _info_type_ = 'snow route'
    _route_attrs_ = ['route1', 'route2']
    _rel_attrs_ = {'_snowroute_group': {'key': 'snowroute_group_id',
                                        'info_cls': SnowRouteGroupInfo,
                                        'model_cls': model.SnowRouteGroup}}

    def __init__(self):
        self.id = None
        """:type: int """
        self.name = None
        """:type: str """
        self.description = None
        """:type: str """
        self.route1 = None
        """:type: pyticas.ttypes.Route """
        self.route2 = None
        """:type: pyticas.ttypes.Route """
        self.snowroute_group_id = None
        """:type: int """
        self._snowroute_group = None
        """:type: SnowRouteGroupInfo """

    def __str__(self):
        return ('<SnowRouteInfo id=%d name="%s" year=%d snowroute_group_id="%s">'
                % (self.id, self.name, self._snowroute_group.year, self.snowroute_group_id))


class TargetStationInfo(InfoBase):
    _info_type_ = 'target station'
    _rel_attrs_ = {'_normal_function': {'key': 'normal_function_id',
                                        'info_cls': NormalFunctionInfo,
                                        'model_cls': model.NormalFunction},
                   '_snowroute': {'key': 'snowroute_id',
                                  'info_cls': SnowRouteInfo,
                                  'model_cls': model.SnowRoute},
                   '_winterseason': {'key': 'winterseason_id',
                                     'info_cls': WinterSeasonInfo,
                                     'model_cls': model.WinterSeason}}

    def __init__(self):
        self.id = None
        """:type: int """
        self.station_id = None
        """:type: str """
        self.winterseason_id = None
        """:type: int """
        self._winterseason = None
        """:type: WinterSeasonInfo"""
        self.snowroute_id = None
        """:type: int """
        self._snowroute = None
        """:type: SnowRouteInfo"""
        self.snowroute_name = None
        """:type: str """
        self.corridor_name = None
        """:type: str"""
        self.normal_function_id = None
        """:type: int """
        self._normal_function = None
        """:type: NormalFunctionInfo """

    def __str__(self):
        return '<TargetStationInfo id=%s station_id="%s" corridor_name="%s" winter_season_id=%s snow_route=%s' % (
            self.id, self.station_id, self.corridor_name, self.winterseason_id, self.snowroute_name
        )

class TargetLaneConfigInfo(InfoBase):
    _info_type_ = 'target lane config'
    _rel_attrs_ = {'_winterseason': {'key': 'winterseason_id',
                                     'info_cls': WinterSeasonInfo,
                                     'model_cls': model.WinterSeason}}

    def __init__(self):
        self.id = None
        """:type: int """
        self.corridor_name = None
        """:type: str"""
        self.station_id = None
        """:type: str """
        self.winterseason_id = None
        """:type: int """
        self._winterseason = None
        """:type: WinterSeasonInfo"""
        self.detectors = None
        """:type: str"""

    def __str__(self):
        return '<TargetLaneConfigInfo id=%d station_id="%s" corridor_name="%s"  detectors="%s" winter_season_id=%d ' % (
            self.id, self.station_id, self.corridor_name, self.detectors, self.winterseason_id
        )


class TargetStationManualInfo(InfoBase):
    def __init__(self):
        self.id = None
        """:type: int """
        self.corridor_name = None
        """:type: str """
        self.station_id = None
        """:type: str """


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


class BarelaneRegainTimeInfo(InfoBase):
    _info_type_ = 'barelane regain time'

    def __init__(self):
        self.truckroute_id = None
        """:type: str """
        self.snow_start_time = None  # format=%Y-%m-%d %H:%M
        """:type: str """
        self.snow_end_time = None
        """:type: str """
        self.lane_lost_time = None
        """:type: str """
        self.barelane_regain_time = None
        """:type: str """


class EstimationRequestInfo(InfoBase):
    _info_type_ = 'estimation request'

    def __init__(self):
        self.snow_start_time = None
        """:type: str """
        self.snow_end_time = None
        """:type: str """
        self.target_stations = None  # station ids
        """:type: list[str] """
        self.target_corridors = None  # corridor names
        """:type: list[str] """
        self.target_snow_routes = None  # snow route ids
        """:type: list[int] """
        self.barelane_regain_time_infos = None
        """:type: list[BarelaneRegainTimeInfo] """
