# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import sqlite3
import datetime

from pyticas import cfg
from pyticas.tool import distance
from pyticas.ttypes import RWISData, TupleEnum, Period
from pyticas.ttypes import SurfaceCondition, PrecipType, RWISSiteInfo

# TODO: update this setup
RWIS_DBS = {}
""":type: dict[int, RWISLocalDB] """

FIELD_DICT = {
    # <field name in DB> : <field name in RWISData>
    'dtime': 'DateTime',
    'sf_status': ('SfStatus', SurfaceCondition.find_by_value),
    'sf_temp': 'SfTemp',
    'pc_rate': 'PrecipRate',
    'pc_start_dtime': 'StartTime',
    'pc_end_dtime': 'EndTime',
    'pc_accum': 'PrecipAccumulation',
    'pc_type': ('PrecipType', PrecipType.find_by_value),
    'pc_past_3hours': '3hr Accum',
    'pc_past_6hours': '6hr Accum',
    'pc_past_12hours': '12hr Accum',
    'pc_past_24hours': '24hr Accum',
    'rh': 'RH',
    'wnd_dir_avg': ('WindDirection', lambda degree: list(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])[int(round(((degree % 360.0) / 45)))]),
    'wnd_spd_avg': 'AvgWindSpeed',
}

def find_nearby_sites(s_lat, s_lon):
    """ return RWIS site list order by distance (from nearest)

    :type s_lat: float
    :type s_lon: float
    :return: RWIS site list
    :rtype: list[RWISSiteInfo]
    """
    sites = []
    for gr in cfg.RWIS_SITE_INFO:
        for st in gr['sites']:
            d = distance.distance_in_mile_with_coordinate(s_lat, s_lon, st['lat'], st['lon'])
            sites.append(RWISSiteInfo({'group_id': gr['id'],
                                       'group_name': gr['name'],
                                       'site_id': st['id'],
                                       'site_name': st['name'],
                                       'lat': st['lat'],
                                       'lon': st['lon'],
                                       'distance_to_target': d}))

    return sorted(sites, key=lambda s: s.distance_to_target)


def get_site_by_id(site_id):
    """ return site information

    :type site_id: str
    :rtype: RWISSiteInfo
    """
    for gr in cfg.RWIS_SITE_INFO:
        for st in gr['sites']:
            if st['id'] == site_id:
                return RWISSiteInfo({'group_id': gr['id'],
                                     'group_name': gr['name'],
                                     'site_id': st['id'],
                                     'site_name': st['name'],
                                     'lat': st['lat'],
                                     'lon': st['lon']})
    return None


def get_all_rwis_sites():
    """ return site information

    :rtype: list[RWISSiteInfo]
    """
    sites = []
    for gr in cfg.RWIS_SITE_INFO:
        for st in gr['sites']:
            sites.append(RWISSiteInfo({'group_id': gr['id'],
                                       'group_name': gr['name'],
                                       'site_id': st['id'],
                                       'site_name': st['name'],
                                       'lat': st['lat'],
                                       'lon': st['lon']}))
    return sites


def get_weather(site, prd, sen_id=0):
    periods = split_period(prd)
    for p in periods:
        if p.start_date.year not in RWIS_DBS.keys():
            return None
    total_wd = None
    for p in periods:
        db = RWIS_DBS.get(p.start_date.year)
        wd = db.get_weather(site, p, sen_id)

        if not wd:
            return None

        if not total_wd:
            total_wd = wd
        else:
            total_wd = total_wd + wd

    return total_wd

def split_period(prd):
    """

    :type prd: pyticas.ttypes.Period
    :return:
    """
    if prd.start_date.year == prd.end_date.year:
        return [prd]

    periods = []
    s_date = prd.start_date
    while s_date.year < prd.end_date.year:
        next_date = datetime.datetime(s_date.year+1, 1, 1, 0, 0)
        periods.append(Period(s_date, next_date, prd.interval))
        s_date = next_date
    periods.append(Period(s_date, prd.end_date, prd.interval))
    return periods

def load_dbs(rwis_db_dir):
    for f in os.listdir(rwis_db_dir):
        if not f.endswith('sqlite3'):
            continue
        year = int(f[5:9])
        db = RWISLocalDB(os.path.join(rwis_db_dir, f))
        RWIS_DBS[year] = db

class RWISLocalDB(object):
    def __init__(self, dbfile):
        self.conn = sqlite3.connect(dbfile)

        def _dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.conn.row_factory = _dict_factory

    def get_weather(self, site, prd, sen_id=0):
        """

        :type site: pyticas.ttypes.RWISSiteInfo
        :type prd: pyticas.ttypes.Period
        :type sen_id: int
        :return:
        """
        sdt, edt, interval = prd.start_date, prd.end_date, prd.interval

        sql = ''.join(['SELECT s.dtime, s.temp as sf_temp, s.cond as sf_status',
                       ', a.pc_rate, a.pc_start_dtime, a.pc_end_dtime, a.pc_accum, a.pc_type',
                       ', a.pc_past_3hours, a.pc_past_6hours, a.pc_past_12hours, a.pc_past_24hours',
                       ', a.rh, a.wnd_dir_avg, a.wnd_spd_avg',
                       ' FROM surface as s ',
                       ' LEFT JOIN atmospheric as a ON s.site_id = a.site_id and s.dtime = a.dtime',
                       ' WHERE s.site_id=%d AND s.sen_id = %d AND s.dtime >= "%s" and s.dtime <= "%s"' % (
                           site.site_id, sen_id, sdt, edt)])

        cur = self.conn.cursor()
        cur.execute(sql)
        return self._to_rwis_data(cur, prd)

    def _to_rwis_data(self, cur, prd):
        fields = [v if isinstance(v, str) else v[0] for k, v in FIELD_DICT.items()]
        wd = RWISData(fields, [])
        for row in cur.fetchall():
            for k, v in FIELD_DICT.items():
                if isinstance(v, str):
                    wd.data[v].append(row[k])
                else:
                    if row[k] == None:
                        wd.data[v[0]].append(row[k])
                    else:
                        ret = v[1](row[k])
                        if isinstance(ret, TupleEnum):
                            wd.data[v[0]].append(ret.get_text())
                        else:
                            wd.data[v[0]].append(ret)

        wd.formating()
        wd.set_period(prd)
        return wd