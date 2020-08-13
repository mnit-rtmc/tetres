# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, VARCHAR, Float, Text
from sqlalchemy import DateTime, Boolean, CHAR, UnicodeText, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False, unique=True)
    content = Column(UnicodeText, nullable=True)

    def get_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content
        }

    def __repr__(self):
        return '<Config id="%s" name="%s">' % (self.id, self.name)


class TTRoute(Base):
    __tablename__ = 'route'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    description = Column(Text, nullable=True)
    corridor = Column(VARCHAR(20), nullable=False)
    route = Column(UnicodeText, nullable=False)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return '<TTRoute id="%s" name="%s">' % (self.id, self.name)


class WorkZoneGroup(Base):
    __tablename__ = 'workzone_group'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    _wzs = relationship("WorkZone")
    name = Column(VARCHAR(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    corridors = Column(VARCHAR(255), nullable=True)
    years = Column(VARCHAR(255), nullable=True)
    impact = Column(Text, nullable=True)

    def __repr__(self):
        return '<WorkZoneGroup id="%s" name="%s">' % (self.id, self.name)


class RouteWiseMOEParameters(Base):
    __tablename__ = 'route_wise_moe_parameters'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    reference_tt_route_id = Column(Integer, ForeignKey('route.id', ondelete='CASCADE'), nullable=False, index=True)
    reference_tt_route = relationship(TTRoute)
    moe_lane_capacity = Column(Float, nullable=False)
    moe_critical_density = Column(Float, nullable=False)
    moe_congestion_threshold_speed = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    update_time = Column(DateTime, nullable=False)

    def __repr__(self):
        return '<Route Wise MOE Parameters id="%s" route_id="%s">' % (self.id, self.route_id)


class WorkZone(Base):
    __tablename__ = 'workzone'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    wz_group_id = Column(Integer, ForeignKey('workzone_group.id', ondelete='CASCADE'), nullable=False, index=True)
    _wz_group = relationship("WorkZoneGroup", backref=backref('workzones'))
    _features = relationship('WorkZoneFeature')
    _laneconfigs = relationship('WorkZoneLaneConfig')
    memo = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    route1 = Column(UnicodeText, nullable=False)
    route2 = Column(UnicodeText, nullable=False)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    workzone_length = Column(Float, nullable=True)

    def __repr__(self):
        return '<WorkZone id="%s" wz_group="%s">' % (self.id, self._wz_group.name)


class WorkZoneFeature(Base):
    __tablename__ = 'workzone_feature'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    wz_id = Column(Integer, ForeignKey('workzone.id', ondelete='CASCADE'), nullable=False, index=True)
    route_num = Column(Integer, nullable=False)
    closed_length = Column(Float, nullable=False)
    closed_ramps = Column(Integer, nullable=False)
    has_shifted = Column(Boolean, nullable=False)
    has_closed = Column(Boolean, nullable=False)
    use_opposing_lane = Column(Boolean, nullable=False)
    used_by_opposing_traffic = Column(Boolean, nullable=False)

    def __repr__(self):
        return '<WorkZoneFeature id="%s" wz_id="%s" route_num="%s" closed_length="%s" closed_ramps="%s" ' \
               'has_shifted="%s" has_closed="%s" use_opposing_lane="%s" used_by_opposing_traffic="%s">' % (
                   self.id, self.wz_id, self.route_num, self.closed_length, self.closed_ramps,
                   self.has_shifted, self.has_closed, self.use_opposing_lane, self.used_by_opposing_traffic)


class WorkZoneLaneConfig(Base):
    __tablename__ = 'workzone_lncfg'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    wz_id = Column(Integer, ForeignKey('workzone.id', ondelete='CASCADE'), nullable=False, index=True)
    route_num = Column(Integer, nullable=False)
    origin_lanes = Column(Integer, nullable=False)
    open_lanes = Column(Integer, nullable=False)

    def __repr__(self):
        return '<WorkZoneLaneConfig id="%s" wz_id="%s" route_num="%s" cfg="%s to %s">' % (
            self.id, self.wz_id, self.route_num, self.origin_lanes, self.open_lanes)


class Specialevent(Base):
    __tablename__ = 'specialevent'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    years = Column(VARCHAR(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    attendance = Column(Integer, nullable=True)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    __table_args__ = (UniqueConstraint('name', 'start_time', 'end_time', name='_specialevent_uc'),)

    def __repr__(self):
        return '<Specialevent: {}>'.format(self.id)


class SnowManagement(Base):
    __tablename__ = 'snowmgmt'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    sroute_id = Column(Integer, ForeignKey('snowroute.id', ondelete='CASCADE'), nullable=False, index=True)
    sevent_id = Column(Integer, ForeignKey('snowevent.id', ondelete='CASCADE'), nullable=False, index=True)
    _snowroute = relationship("SnowRoute", backref=backref('snowmgmts'))
    _snowevent = relationship("SnowEvent", backref=backref('snowmgmts'))
    lane_lost_time = Column(DateTime, nullable=False)
    lane_regain_time = Column(DateTime, nullable=False)
    duration = Column(Float, nullable=False)  # in hour
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return '<SnowManagement id=%d>' % self.id


class SnowRoute(Base):
    __tablename__ = 'snowroute'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(VARCHAR(100), nullable=False)
    description = Column(Text, nullable=True)
    prj_id = Column(VARCHAR(20), nullable=True)
    route1 = Column(UnicodeText, nullable=False)
    route2 = Column(UnicodeText, nullable=False)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    _sr_snowmgmts = relationship("SnowManagement")

    def __repr__(self):
        return '<SnowRoute id=%s name="%s">' % (self.id, self.name)


class SnowEvent(Base):
    __tablename__ = 'snowevent'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    _se_snowmgmts = relationship("SnowManagement")

    def __repr__(self):
        return '<SnowEvent id=%s start="%s" end="%s">' % (self.id, self.start_time, self.end_time)


class IncidentType(Base):
    __tablename__ = 'incident_type'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    eventtype = Column(String(255), nullable=False)
    eventsubtype = Column(String(255), nullable=True)
    eventtypecode = Column(String(50), nullable=False)
    eventsubtypecode = Column(String(50), nullable=True)
    classification = Column(String(50), nullable=True)
    iris_class = Column(String(50), nullable=True)
    iris_detail = Column(String(50), nullable=True)
    blocking = Column(Boolean, nullable=True)
    occupied = Column(Boolean, nullable=True)
    rollover = Column(Boolean, nullable=True)
    injury = Column(Boolean, nullable=True)
    fatal = Column(Boolean, nullable=True)
    cars_eventtype = Column(VARCHAR(255), nullable=True)
    cars_eventtypecode = Column(VARCHAR(50), nullable=True)

    def __repr__(self):
        return '<IncidentType id="%s" eventtype="%s" eventsubtype="%s">' % (self.id, self.eventtype, self.eventsubtype)


class Incident(Base):
    __tablename__ = 'incident'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    incident_type_id = Column(Integer, ForeignKey('incident_type.id'), nullable=False)
    _incident_type = relationship("IncidentType")
    cad_pkey = Column(Integer, unique=True, nullable=False)
    iris_event_id = Column(Integer, nullable=True)
    iris_event_name = Column(VARCHAR(16), nullable=True)

    cdts = Column(DateTime, nullable=True)
    udts = Column(DateTime, nullable=True)
    xdts = Column(DateTime, nullable=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)

    road = Column(VARCHAR(20), nullable=True)
    direction = Column(VARCHAR(4), nullable=True)
    impact = Column(VARCHAR(20), nullable=True)
    lane_type = Column(VARCHAR(12), nullable=True)

    earea = Column(VARCHAR(3), nullable=True)
    ecompl = Column(VARCHAR(60), nullable=True)
    edirpre = Column(CHAR(20), nullable=True)
    edirsuf = Column(CHAR(20), nullable=True)
    efeanme = Column(VARCHAR(35), nullable=True)
    efeatyp = Column(VARCHAR(30), nullable=True)
    xstreet1 = Column(VARCHAR(40), nullable=True)
    xstreet2 = Column(VARCHAR(40), nullable=True)

    def __repr__(self):
        return '<Incident id="%s" cad_pkey="%s" iris_event_id="%s" cdts="%s" udts="%s" xdts="%s" ' \
               'eventtype="%s" eventsubtype="%s" lat="%s" lon="%s">' % (
                   self.id,
                   self.cad_pkey,
                   self.iris_event_id,
                   self.cdts,
                   self.udts,
                   self.xdts,
                   self._incident_type.eventtype if self._incident_type else None,
                   self._incident_type.eventsubtype if self._incident_type else None,
                   self.lat, self.lon)


class TODReliability(Base):
    __tablename__ = 'tod_results'
    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey('route.id', ondelete='CASCADE'), nullable=False, index=True)
    route = relationship(TTRoute, backref=backref('tod_reliabilites'))
    regime_type = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    minute = Column(Integer, nullable=False)
    result = Column(Text, nullable=False)

    def __repr__(self):
        return '<TODReliability id="%s" route_id="%s" regime_type="%s" hour="%s" minute="%s">' % (
            self.id,
            self.route_id,
            self.regime_type,
            self.hour,
            self.minute)


class ActionLog(Base):
    __tablename__ = 'action_log'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    action_type = Column(VARCHAR(10), nullable=False)
    target_datatype = Column(VARCHAR(255), nullable=True)
    target_table = Column(VARCHAR(255), nullable=True)
    target_id = Column(Integer, nullable=True)
    data_desc = Column(VARCHAR(255), nullable=True)
    handled = Column(Boolean, nullable=False, default=False)
    handled_date = Column(DateTime, nullable=True)
    status = Column(VARCHAR(50), nullable=True)
    status_updated_date = Column(DateTime, nullable=True)
    reason = Column(VARCHAR(255), nullable=True)
    user_ip = Column(VARCHAR(15), nullable=True)
    reg_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    processed_start_date = Column(DateTime, nullable=True)
    processed_end_date = Column(DateTime, nullable=True)

    def __repr__(self):
        return ('<ActionLog id="%s" action_type="%s" target_datatype="%s" target_table="%s" target_id="%s" '
                'data="%s" handled="%s" handled_date="%s" status="%s" status_updated_date="%s" reason="%s" user_ip="%s" reg_date="%s">' % (
                    self.id,
                    self.action_type,
                    self.target_datatype,
                    self.target_table,
                    self.target_id,
                    self.data_desc,
                    self.handled,
                    self.status,
                    self.status_updated_date,
                    self.reason,
                    self.user_ip,
                    self.handled_date,
                    self.reg_date))


# this class is for type reference in IDE (TravelTime model is declared in model_yearly.py)
class TravelTime(object):
    # faverolles 10/8/2019 NOTE: MOE

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey('route.id'), nullable=False)
    route = relationship("TTRoute")
    time = Column(DateTime, nullable=False)
    tt = Column(Float, nullable=False)
    vmt = Column(Float, nullable=True)
    vht = Column(Float, nullable=True)
    dvh = Column(Float, nullable=True)
    lvmt = Column(Float, nullable=True)
    uvmt = Column(Float, nullable=True)
    cm = Column(Float, nullable=True)
    cmh = Column(Float, nullable=True)
    acceleration = Column(Float, nullable=True)
    meta_data = Column(UnicodeText, nullable=True)

    inc_severity = Column(Integer, nullable=True)
    inc_impact = Column(Integer, nullable=True)
    inc_type = Column(Integer, nullable=True)
    precip_type = Column(Integer, nullable=True)
    precip_rate = Column(Integer, nullable=True)
    wz = Column(Integer, nullable=True)
    snowmgmt = Column(Integer, nullable=True)
    _tt_weathers = relationship('TTWeather', lazy='joined', cascade='all, delete')
    _tt_incidents = relationship('TTIncident', lazy='joined', cascade='all, delete')
    _tt_workzones = relationship('TTWorkzone', lazy='joined', cascade='all, delete')
    _tt_specialevents = relationship('TTSpecialevent', lazy='joined', cascade='all, delete')
    _tt_snowmanagements = relationship('TTSnowmgmt', lazy='joined', cascade='all, delete')
    UniqueConstraint('usaf', 'wban', 'dtime', name='_noaa_uc')

    def __repr__(self):
        return '<TravelTime id=%s route="%s:%s" tt="%s">' % (self.id, self.route.id, self.route.name, self.tt)


# this class is for type reference in IDE (This model is declared in model_yearly.py)
class Noaa(object):
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    usaf = Column(VARCHAR(6), nullable=False)
    wban = Column(VARCHAR(5), nullable=False)
    dtime = Column(DateTime, nullable=False)
    precip = Column(Float, nullable=True)
    precip_type = Column(VARCHAR(4), nullable=True)
    precip_intensity = Column(VARCHAR(4), nullable=True)
    relative_humidity = Column(Float, nullable=True)
    precip_qc = Column(VARCHAR(4), nullable=True)
    visibility = Column(Float, nullable=True)
    visibility_qc = Column(VARCHAR(4), nullable=True)
    obscuration = Column(VARCHAR(4), nullable=True)
    descriptor = Column(VARCHAR(4), nullable=True)
    air_temp = Column(Float, nullable=True)
    air_temp_qc = Column(VARCHAR(4), nullable=True)
    dew_point = Column(Float, nullable=True)
    dew_point_qc = Column(VARCHAR(4), nullable=True)
    wind_dir = Column(Integer, nullable=True)
    wind_dir_qc = Column(VARCHAR(4), nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_speed_qc = Column(VARCHAR(4), nullable=True)
    wind_gust = Column(Float, nullable=True)
    wind_gust_qc = Column(VARCHAR(4), nullable=True)


class TTExtModel(object):
    def __init__(self, **kwargs):
        self.tt_id = None
        """:type: int """
        self._tt = None
        """:type: TravelTime """
        self.is_extended = False


# this class is for type reference in IDE (This model is declared in model_yearly.py)
class TTWeather(TTExtModel):
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    tt_id = Column(Integer, primary_key=True)
    _tt = relationship(TravelTime)
    weather_id = Column(Integer, ForeignKey(Noaa.id), primary_key=True)
    _weather = relationship(Noaa)


# this class is for type reference in IDE (This model is declared in model_yearly.py)
class TTIncident(TTExtModel):
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    tt_id = Column(Integer, primary_key=True)
    _tt = relationship(TravelTime)
    incident_id = Column(Integer, ForeignKey(Incident.id), primary_key=True)
    _incident = relationship(Incident)
    distance = Column(Float, nullable=True)
    off_distance = Column(Float, nullable=True)


# this class is for type reference in IDE (This model is declared in model_yearly.py)
class TTWorkzone(TTExtModel):
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    tt_id = Column(Integer, primary_key=True)
    _tt = relationship(TravelTime)
    workzone_id = Column(Integer, ForeignKey(WorkZone.id), primary_key=True)
    _workzone = relationship(WorkZone)
    loc_type = Column(Integer, nullable=True)
    distance = Column(Float, nullable=True)
    off_distance = Column(Float, nullable=True)


# this class is for type reference in IDE (This model is declared in model_yearly.py)
class TTSpecialevent(TTExtModel):
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    tt_id = Column(Integer, primary_key=True)
    _tt = relationship(TravelTime)
    specialevent_id = Column(Integer, ForeignKey(Specialevent.id), primary_key=True)
    _specialevent = relationship(Specialevent)
    distance = Column(Float, nullable=False)
    event_type = Column(CHAR, nullable=False)


# this class is for type reference in IDE (This model is declared in model_yearly.py)
class TTSnowmgmt(TTExtModel):
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    tt_id = Column(Integer, primary_key=True)
    _tt = relationship(TravelTime)
    snowmgmt_id = Column(Integer, ForeignKey(SnowManagement.id), primary_key=True)
    _snowmgmt = relationship(SnowManagement)
    loc_type = Column(Integer, nullable=True)
    distance = Column(Float, nullable=True)
    off_distance = Column(Float, nullable=True)
    road_status = Column(Integer, nullable=True)
    recovery_level = Column(Integer, nullable=True)


# this class is for type reference in IDE (This model is declared in model_yearly.py)
class Weather(object):
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    site_id = Column(VARCHAR(10))
    sen_id = Column(Integer, nullable=False)
    dtime = Column(DateTime, nullable=False)
    air_temp = Column(Float, nullable=True)
    temp_alt = Column(Float, nullable=True)
    temp_max = Column(Float, nullable=True)
    temp_min = Column(Float, nullable=True)
    dew_point = Column(VARCHAR(20), nullable=True)
    rh = Column(Integer, nullable=True)
    pc_type = Column(Integer, nullable=True)
    pc_intens = Column(Integer, nullable=True)
    pc_rate = Column(Integer, nullable=True)
    pc_accum = Column(Integer, nullable=True)
    pc_accum_10min = Column(Integer, nullable=True)
    pc_start_dtime = Column(DateTime, nullable=True)
    pc_end_dtime = Column(DateTime, nullable=True)
    pc_past_1hour = Column(Integer, nullable=True)
    pc_past_3hours = Column(Integer, nullable=True)
    pc_past_6hours = Column(Integer, nullable=True)
    pc_past_12hours = Column(Integer, nullable=True)
    pc_past_24hours = Column(Integer, nullable=True)
    pc_time_since = Column(Integer, nullable=True)
    wet_build_temp = Column(Integer, nullable=True)
    vis_distance = Column(Integer, nullable=True)
    vis_situation = Column(Integer, nullable=True)
    barometric = Column(Integer, nullable=True)
    wnd_spd_avg = Column(Integer, nullable=True)
    wnd_spd_gust = Column(Integer, nullable=True)
    wnd_dir_avg = Column(VARCHAR(2), nullable=True)
    wnd_dir_gust = Column(VARCHAR(2), nullable=True)
    cond = Column(Integer, nullable=True)
    sf_temp = Column(Integer, nullable=True)
    frz_temp = Column(Integer, nullable=True)
    chem = Column(Integer, nullable=True)
    chem_pct = Column(Integer, nullable=True)
    depth = Column(Integer, nullable=True)
    ice_pct = Column(Integer, nullable=True)
    salinity = Column(Integer, nullable=True)
    conductivity = Column(Integer, nullable=True)
    blackice_signal = Column(Integer, nullable=True)
    error = Column(Integer, nullable=True)
