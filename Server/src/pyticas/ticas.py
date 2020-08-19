# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os

from pyticas import cfg, logger
from pyticas.ttypes import TrafficType


class TICASObj(object):
    def __init__(self):
        self.initialized = False
        self.data_path = None

    def initialize(self, data_path, cfg_profile=None):
        if not data_path:
            raise Exception('data_path is required')

        if self.initialized:
            return
        self.data_path = os.path.abspath(data_path)

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        default_dirs = ['db', 'metro', 'route', 'cache', 'log', 'map', 'tetres']
        for dn in default_dirs:
            dir_path = os.path.join(self.data_path, dn)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
        cache_dir = os.path.join(self.data_path, "cache")
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        det_directory = os.path.join(cache_dir, "det")
        if not os.path.exists(det_directory):
            os.makedirs(det_directory)
        tetres_filters_directory = os.path.join(self.data_path, "tetres", "filters")
        if not os.path.exists(tetres_filters_directory):
            os.makedirs(tetres_filters_directory)
        tetres_route_groups_directory = os.path.join(self.data_path, "tetres", "route-groups")
        if not os.path.exists(tetres_route_groups_directory):
            os.makedirs(tetres_route_groups_directory)
        if cfg_profile:
            if not hasattr(cfg_profile, 'setup') or not callable(getattr(cfg_profile, 'setup')):
                raise Exception('cfg_profile must have callable "setup()" function')
            cfg_profile.setup()
        else:
            from pyticas.config.mn import mn_cfg
            mn_cfg.setup()

        self._set_traffictype(cfg.SAMPLES_PER_DAY)
        self.initialized = True
        logger.updateLoggerPaths(self.get_path('log'))

    def get_path(self, subdir, **kwargs):
        """ return data path

        if data root path is '/data' and get_path('cache') called,
        it returns '/data/cache'

        :rtype: str
        """
        self._check_initialized()

        if subdir.startswith('/') or '..' in subdir:
            raise Exception('Invalid subdir parameter : %s' % subdir)

        if subdir:
            target_path = os.path.join(self.data_path, subdir)
        else:
            target_path = self.data_path

        if kwargs.get('create', False):
            if not os.path.exists(target_path):
                os.makedirs(target_path)

        return target_path

    def _check_initialized(self):
        if not self.initialized:
            raise Exception('"TICASObj.initialize()" must be called before using pyticas')

    def _set_traffictype(self, samples_per_day):
        TrafficType.occupancy = TrafficType("occupancy", ".o30", 2, samples_per_day, "density_with_station",
                                            "avg_in_rnode")
        TrafficType.density = TrafficType("density", ".c30", 2, samples_per_day, "density_with_station", "avg_in_rnode")

        TrafficType.flow = TrafficType("flow", "", 0, samples_per_day, "flow", "sum_in_rnode")
        TrafficType.flow_average = TrafficType("flow", "", 0, samples_per_day, "flow", "avg_in_rnode")

        TrafficType.travel_time = TrafficType("travel_time", "", None, None, None, None)
        TrafficType.vmt = TrafficType("vmt", "", None, None, None, None)
        TrafficType.accel = TrafficType("acceleration", "", None, None, None, None)
        TrafficType.speed = TrafficType("speed", "", 0, samples_per_day, "average", "avg_in_rnode")


        TrafficType.scan = TrafficType("scan", ".c30", 2, samples_per_day, "average", "avg_in_rnode")
        TrafficType.speed_wavetronics = TrafficType("speed_wavetronics", ".s30", 1, samples_per_day, "average",
                                                    "avg_in_rnode")
        TrafficType.volume = TrafficType("volume", ".v30", 1, samples_per_day, "cumulative", "sum_in_rnode")


_TICAS_ = TICASObj()


def initialize(data_path, cfg_profile=None):
    _TICAS_.initialize(data_path, cfg_profile)


def is_initialized():
    return _TICAS_.initialized


def check_initialized():
    _TICAS_._check_initialized()


def get_path(subdir, **kwargs):
    return _TICAS_.get_path(subdir, **kwargs)
