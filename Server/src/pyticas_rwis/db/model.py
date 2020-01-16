# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from sqlalchemy import Column, Integer, VARCHAR, Float
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Index, UniqueConstraint

Base = declarative_base()


class Atmospheric(Base):
    __tablename__ = 'atmospheric'
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, nullable=False)
    dtime = Column(DateTime, nullable=False)
    temp = Column(Float, nullable=True)
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
    wet_build_temp = Column(Float, nullable=True)
    vis_distance = Column(Integer, nullable=True)
    vis_situation = Column(Integer, nullable=True)
    barometric = Column(Integer, nullable=True)
    wnd_spd_avg = Column(Integer, nullable=True)
    wnd_spd_gust = Column(Integer, nullable=True)
    wnd_dir_avg = Column(Integer, nullable=True)
    wnd_dir_gust = Column(Integer, nullable=True)


Index('AtmoLookUpIndex1', Atmospheric.site_id, Atmospheric.dtime)
UniqueConstraint(Atmospheric.site_id, Atmospheric.dtime, name='AtmoUniqueIndex1')


class Surface(Base):
    __tablename__ = 'surface'
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, nullable=False)
    sen_id = Column(Integer, nullable=False)
    dtime = Column(DateTime, nullable=False)
    cond = Column(Integer, nullable=True)
    temp = Column(Integer, nullable=True)
    frz_temp = Column(Integer, nullable=True)
    chem = Column(Integer, nullable=True)
    chem_pct = Column(Integer, nullable=True)
    depth = Column(Integer, nullable=True)
    ice_pct = Column(Integer, nullable=True)
    salinity = Column(Integer, nullable=True)
    conductivity = Column(Integer, nullable=True)
    blackice_signal = Column(Integer, nullable=True)
    error = Column(Integer, nullable=True)


Index('SurfaceLookUpIndex1', Surface.site_id, Surface.sen_id, Surface.dtime)
UniqueConstraint(Surface.site_id, Surface.sen_id, Surface.dtime, name='SurfaceUniqueIndex1')