# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from sqlalchemy import and_

from pyticas import cfg
from pyticas.tool import distance
from pyticas.ttypes import TupleEnum, RWISSiteInfo, RWISData, RWISDataRow
from pyticas import time as rwis_time
from pyticas_rwis.db import conn
from pyticas_rwis.db.model import Atmospheric, Surface

#
# SF_FIELD_DICT = {
#     # <field name in DB> : <field name in ScanWebData>
#     'dtime': ('DateTime', lambda dtt: dtt.strftime("%Y-%m-%d %H:%M:%S")),
#     'cond': ('SfStatus', SurfaceCondition.find_by_value),
#     'temp': 'SfTemp',
# }
#
# ATM_FIELD_DICT = {
#     # <field name in DB> : <field name in ScanWebData>
#     'pc_rate': 'PrecipRate',
#     'pc_intens': ('PrecipIntens', PrecipIntens.find_by_value),
#     'pc_start_dtime': ('StartTime', lambda dtt: dtt.strftime("%Y-%m-%d %H:%M:%S")),
#     'pc_end_dtime': ('EndTime', lambda dtt: dtt.strftime("%Y-%m-%d %H:%M:%S")),
#     'pc_accum': 'PrecipAccumulation',
#     'pc_type': ('PrecipType', PrecipType.find_by_value),
#     'pc_past_3hours': '3hr Accum',
#     'pc_past_6hours': '6hr Accum',
#     'pc_past_12hours': '12hr Accum',
#     'pc_past_24hours': '24hr Accum',
#     'rh': 'RH',
#     'wnd_dir_avg': ('WindDirection', lambda degree: list(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])[
#         int(round(((degree % 360.0) / 45)))]),
#     'wnd_spd_avg': 'AvgWindSpeed',
# }


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


def get_weather(site_id, prd, sen_id=0):
    """

    :type site_id: int
    :type prd: pyticas.ttypes.Period
    :type sen_id: int
    :rtype: list[RWISDataRow]
    """
    sdt, edt = prd.start_date, prd.end_date

    sdt = sdt - datetime.timedelta(seconds=600)
    edt = edt + datetime.timedelta(seconds=600)

    sdt = rwis_time.GMT(sdt)
    edt = rwis_time.GMT(edt)

    session = conn.get_session()

    qry = (session.query(Surface, Atmospheric).join(Atmospheric, and_(Surface.site_id == Atmospheric.site_id,
                                                                          Surface.dtime == Atmospheric.dtime))
        .filter(Surface.site_id == site_id)
        .filter(Surface.sen_id == sen_id)
        .filter(Surface.dtime >= sdt)
        .filter(Surface.dtime <= edt))

    session.close()

    #start_time = time.time()
    res = qry.all()
    #print(qry)
    #print("--- query : %s seconds ---" % (time.time() - start_time))

    # fields = [v if isinstance(v, str) else v[0] for k, v in SF_FIELD_DICT.items()]
    # fields += [v if isinstance(v, str) else v[0] for k, v in ATM_FIELD_DICT.items()]
    #
    wd = RWISData(prd)
    # start_time = time.time()
    for idx, (surface, atm) in enumerate(res):
        row = RWISDataRow(atm, surface)
        wd.add_data(row)

    wd.set_period()

    # for d in wd.data:
    #     for k, v in d.__dict__.items():
    #         print('{}={}, '.format(k, v), end='')
    #     print('')
    return wd


def _set_data(wd, field_dict, db_obj):
    for k, v in field_dict.items():
        value = getattr(db_obj, k)
        if isinstance(v, str):
            wd.data[v].append(value)
        else:
            if value == None:
                wd.data[v[0]].append(value)
            else:
                ret = v[1](value)
                if isinstance(ret, TupleEnum):
                    wd.data[v[0]].append(ret.get_text())
                else:
                    wd.data[v[0]].append(ret)

if __name__ == '__main__':
    from pyticas.infra import Infra
    from pyticas.ttypes import Period
    RWIS_DB_INFO = {
        'engine': 'postgresql',
        'host': '131.212.105.85',
        'port': 5432,
        'db_name': 'rwis',
        'user': 'postgres',
        'passwd': 'natsrl@207'
    }
    conn.connect(RWIS_DB_INFO)
    Infra.initialize('D:/TICAS-NG/data')
    Infra.get_infra()
    prd = Period('2012-01-02 07:00:00', '2012-01-02 08:00:00', 300)
    site = get_site_by_id(330009)
    wd = get_weather(site.site_id, prd)

# from pyticas.infra import Infra
#
# Infra.initialize('./data')
# Infra.get_infra()
#
# prd = Period(datetime.datetime(2013, 5, 2, 23, 50, 0), datetime.datetime(2013, 5, 3, 1, 0, 0), 600)
# start_time = time.time()
# wd = get_weather(330045, prd)
# print("--- retreiving data : %s seconds ---" % (time.time() - start_time))
# for idx, dt in enumerate(wd.data['DateTime']):
#     print(dt, wd.data['SfTemp'][idx])
# print(wd.get_data_string())
#
# rwis2010 = RWISLocalDB('D:\\RWIS-2010.sqlite3')
# wd = rwis2010.search(330045, Period(datetime.datetime(2010, 7, 1, 6, 0, 0), datetime.datetime(2010, 7, 1, 7, 0, 0), 30),
#                      0)
# print(wd.get_data_string())

# from pyticas.dr import rwis
# from pyticas.ttypes import Period
#
# prd = Period(datetime.datetime(2016, 3, 22, 6, 0, 0), datetime.datetime(2016, 3, 22, 7, 0, 0), 30)
# site = rwis.get_site_by_id(330085)
# wd2 = rwis.get_weather(site, prd, reader=rwis.RWIS_READER.SCANWEB_HTML, nocache=True)
# if wd2:
#     print(wd2.get_data_string())
# else:
#     print('no data from scanweb')
