# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_ncrtes.api import target_station_identification, api_info
from pyticas_ncrtes.api import snowroute, snowroute_group, estimation
from pyticas_ncrtes.api import target_station, target_station_manual

handlers = [ target_station_identification,
             api_info,
             snowroute,
             snowroute_group,
             estimation,
             target_station,
             target_station_manual,
             ]