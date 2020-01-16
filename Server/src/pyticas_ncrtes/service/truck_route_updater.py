# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.service.truck_route_updater
===========================================

- link target station and truck route information in database

"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.infra import Infra
from pyticas_ncrtes.logger import getLogger


def target_station_and_snowroute_info(year):
    infra = Infra.get_infra()

    logger = getLogger(__name__)
    logger.info('>>> updating relations between target station and truck route')

    from pyticas_ncrtes.da.snowroute import SnowRouteDataAccess
    from pyticas_ncrtes.da.target_station import TargetStationDataAccess

    snrDA = SnowRouteDataAccess()
    tsDA = TargetStationDataAccess()

    snow_routes = snrDA.list_by_year(year)
    target_stations = tsDA.list_by_year(year, as_model=True)

    for tidx, ts in enumerate(target_stations):
        rnode = infra.get_rnode(ts.station_id)
        if not rnode:
            continue

        for snri in snow_routes:
            if rnode in snri.route1.rnodes or rnode in snri.route2.rnodes:
                ts.snowroute_id = snri.id
                ts.snowroute_name = snri._snowroute_group.name
                if tidx and tidx % 100:
                    snrDA.commit()

    snrDA.commit()
    snrDA.close()
    tsDA.close()

    logger.info('<<< end of updating relations between target station and truck route')
