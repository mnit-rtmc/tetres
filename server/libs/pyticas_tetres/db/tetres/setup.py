# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_tetres.db import __DB_VERSION__
from pyticas_tetres.logger import getLogger


def initialize_database():
    logger = getLogger(__name__)
    logger.info('    - initialize database : add default data')

    from pyticas_tetres.db.tetres import conn

    conn.engine.execute("INSERT INTO config (name, content) VALUES ('version', '{}')".format(__DB_VERSION__))

    #conn.engine.execute("TRUNCATE incident_type")
    # conn.engine.execute("INSERT INTO incident_type (eventtype, eventtypecode, eventsubtype, eventsubtypecode) VALUES ('FATALITY CRASH', '1054', 'VEHICLE VS ANIMAL', 'ANIMAL')")
    # conn.engine.execute("INSERT INTO incident_type (eventtype, eventtypecode, eventsubtype, eventsubtypecode) VALUES ('FATALITY CRASH2', '10542', 'VEHICLE VS ANIMAL2', 'ANIMAL2')")

    # insert test data
    # logger.info('    - initialize database : add test data')
    # test_data()

def test_data():
    import datetime
    from pyticas import route
    from pyticas_tetres.ttypes import WorkZoneInfo, WorkZoneGroupInfo, TTRouteInfo, SpecialEventInfo
    from pyticas_tetres.da.wz import WorkZoneDataAccess
    from pyticas_tetres.da.wz_group import WZGroupDataAccess
    from pyticas_tetres.da.specialevent import SpecialEventDataAccess
    from pyticas_tetres.da.route import TTRouteDataAccess

    # route data
    r1 = route.create_route('S38', 'S40', name='Route I-35W NB') # I-35W NB
    r2 = route.create_route('S186', 'S188', name='Route I-494 WB') # I-494 WB
    r3 = route.create_route('S428', 'S430', name='Route US-169 NB') # US169 NB

    ri1 = TTRouteInfo(r1)
    ri2 = TTRouteInfo(r2)
    ri3 = TTRouteInfo(r3)

    dsRoute = TTRouteDataAccess()
    dsWZ = WorkZoneDataAccess(session=dsRoute.da_base.session)
    dsWZGroup = WZGroupDataAccess(session=dsRoute.da_base.session)
    dsSE = SpecialEventDataAccess(session=dsRoute.da_base.session)

    rm = dsRoute.insert(ri1)
    rm = dsRoute.insert(ri2)
    rm = dsRoute.insert(ri3)

    # workzone data
    def _wzg(idx, r1, r2, y1, y2):
        wgi = WorkZoneGroupInfo()
        wgi.name = 'test wz group %d' % idx
        wgi.desc = 'test is test wz group %d' % idx
        wgi.years  = WorkZoneGroupInfo.years_string(y1, y2)
        wgi.corridors = WorkZoneGroupInfo.corridor_string([r1, r2])
        return wgi

    def _wzi(idx, r1, r2, y1, y2, wgid):
        wi = WorkZoneInfo()
        wi.wz_group_id = wgid
        wi.route1 = r1
        wi.route2 = r2
        wi.memo = 'memo of test wz %d' % idx
        sdt = datetime.datetime(y1, 3, 2, 1, 0, 0)
        edt = datetime.datetime(y2, 7, 2, 1, 0, 0)
        wi.start_time = sdt.strftime('%Y-%m-%d %H:%M:%S')
        wi.end_time = edt.strftime('%Y-%m-%d %H:%M:%S')
        wi.years = WorkZoneInfo.years_string(y1, y2)
        return wi

    r1 = route.create_route('S38', 'S40', name='Route I-35W NB') # I-35W NB
    r2 = route.opposite_route(r1)
    r3 = route.create_route('S186', 'S188', name='Route I-494 WB') # I-494 WB
    r4 = route.opposite_route(r3)

    wgi1 = _wzg(1, r1, r2, 2012, 2012)
    wgi2 = _wzg(2, r3, r4, 2012, 2013)
    wgi3 = _wzg(3, r1, r2, 2014, 2016)

    ac = True
    wgm1 = dsWZGroup.insert(wgi1)
    wgm2 = dsWZGroup.insert(wgi2)
    wgm3 = dsWZGroup.insert(wgi3)

    wi1 = _wzi(1, r1, r2, 2012, 2012, wgm1.id)
    wi2 = _wzi(2, r3, r4, 2012, 2013, wgm2.id)
    wi3 = _wzi(3, r1, r2, 2014, 2016, wgm3.id)

    wm1 = dsWZ.insert(wi1)
    wm2 = dsWZ.insert(wi2)
    wm3 = dsWZ.insert(wi3)

    # special event data
    def _sei(idx, y1, m1, d1, y2, m2, d2, att):
        sei = SpecialEventInfo()
        sei.name = 'test se %d' % idx
        sei.description = 'test is test se %d' % idx

        sdt = datetime.datetime(y1, m1, d1, 1, 0, 0)
        edt = datetime.datetime(y2, m2, d2, 1, 0, 0)
        sei.start_time = sei.datetime2str(sdt)
        sei.end_time = sei.datetime2str(edt)
        sei.set_years()
        sei.attendance = att
        sei.lon = -93.331893
        sei.lat = 44.970797
        return sei

    se1 = _sei(1, 2014, 3, 1, 2014, 3, 2, 1000)
    se2 = _sei(2, 2012, 4, 1, 2012, 4, 2, 20000)
    se3 = _sei(3, 2016, 5, 1, 2016, 5, 2, 300)

    sem1 = dsSE.insert(se1)
    sem2 = dsSE.insert(se2)
    sem3 = dsSE.insert(se3)

    dsWZ.close_session()
    dsSE.close_session()
    dsRoute.close_session()