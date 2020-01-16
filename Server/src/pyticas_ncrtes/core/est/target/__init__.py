# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas_ncrtes.core.est.target import lane
from pyticas_ncrtes.core.est.target import station

# function alias
get_target_detectors = lane.get_target_detectors
get_detector_checker = lane.get_detector_checker
get_target_stations = station.get_target_stations