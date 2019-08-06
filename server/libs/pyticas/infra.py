# -*- coding: utf-8 -*-
from pyticas.ttypes import RNodeObject

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os

from pyticas import cfg
from pyticas import ticas
from pyticas.dr.det_reader import DetectorDataReader
from pyticas.dr.rnode_reader import RNodeDataReader
from pyticas.rn import infra_loader
from pyticas.rn import geo
from pyticas.tool import util


class Infra(object):
    """ Class to access `Roadway Network Information` such as corridor, station, detector, meter ..

    **Multiple Instances of `Infra`**

        Roadway network information(RNI) is obtained from `metro_config.xml.gz` of `IRIS` server.
        This file is updated according to geometry changes in the freeway network.
        However, the config file before updated cannot be accessed currently
        When the config file is loaded, the downloaded XML file is saved to `data/metro/`
        in name of configuration date, i.e. 2016-02-20.xml
        Then, RNI can be loaded with the given configuration date through `Infra.get_infra("2016-02-20")`
        If, configuration date is not provided, it will load_data the most recent RNI.

        - class methods
            - get_infra()
            - get_cfg_dates()
            - load_infra()
            - load_infra_from_config_file()
            - initialize()
            - get_path()


    **Access to Roadway Network Information**

        - get_corridors()
        - get_corridor_names()
        - get_corridor()
        - get_corridor_by_name()
        - get_rnode()
        - get_detector()
        - get_camera()
        - get_dms()
        - get_meter()


    **Traffic Data Reader**

        - `rdr`
            - get_volume()
            - get_speed()
            - get_density()
            - get_total_flow()
            - get_average_flow()
            - get_speed()
            - get_occupancy()
            - get_scan()

        - `ddr`
            - get_volume()
            - get_speed()
            - get_density()
            - get_total_flow()
            - get_average_flow()
            - get_speed()
            - get_occupancy()
            - get_scan()

    """
    INFRA_POOL = {}

    def __init__(self, metro_info):

        self.cfg_date = ''
        """ :tyhpe: str """

        self.corridors = {}
        """ :type: dict[str, pyticas.ttypes.CorridorObject] """

        self.rnodes = {}
        """ :type: dict[str, pyticas.ttypes.RNodeObject] """

        self.station_rnode_map = {}
        """
        :param: dict[station_id, rnode_name]
        :type: dict[str, str]
        """

        self.detectors = {}
        """ :type: dict[str, pyticas.ttypes.DetectorObject] """

        self.meters = {}
        """ :type: dict[str, pyticas.ttypes.MeterObject] """

        self.cameras = {}
        """ :type: dict[str, pyticas.ttypes.CameraObject] """

        self.corridor_camera_map = {}
        """
        :param: dict[corridor_name, list[camera_id]]
        :type: dict[str, list[str]]
        """

        self.dmss = {}
        """ :type: dict[str, pyticas.ttypes.DMSObject] """

        self.corridor_dms_map = {}
        """
        :param: dict[corridor_name, list[dms_id]]
        :type: dict[str, list[str]]
        """

        self.ddr = DetectorDataReader()
        """ :type: DetectorDataReader """

        self.rdr = RNodeDataReader(self.ddr)
        """ :type: RNodeDataReader """

        self.geo = geo.Geo(self)
        """:type: Geo """

        # set value from passed dictionary
        for k, v in metro_info.items():
            setattr(self, k, v)

        self.geo.update_corridor_connections()


    @classmethod
    def initialize(cls, data_path, cfg_profile=None):
        ticas.initialize(data_path, cfg_profile)

    @classmethod
    def get_path(cls, sub_dir, **kwargs):
        return ticas.get_path(sub_dir, **kwargs)

    @classmethod
    def get_infra(cls, cfg_date='', **kwargs):
        """
        :type cfg_date: str
        :type kwargs: dict
        :rtype: Infra
        """
        if not cfg_date and Infra.INFRA_POOL:
            recent_metro = sorted(Infra.INFRA_POOL)[-1]
            return Infra.INFRA_POOL.get(recent_metro)
        return Infra.INFRA_POOL.get(cfg_date, Infra.load_infra(cfg_date, **kwargs))

    @classmethod
    def get_cfg_dates(cls):
        return [str(f).split('.')[0] for f in os.listdir(Infra.get_path('metro'))]

    @classmethod
    def load_infra(cls, cfg_date='', **kwargs):
        if cfg_date in Infra.INFRA_POOL:
            return Infra.INFRA_POOL.get(cfg_date)

        metro_info = infra_loader.load_metro(cfg_date, **kwargs)
        if not metro_info:
            raise Exception('Fail to load_data metro network information')
        infraObject = Infra(metro_info)
        Infra.INFRA_POOL[infraObject.cfg_date] = infraObject
        return infraObject

    @classmethod
    def load_infra_from_config_file(cls, file_path):
        if not os.path.exists(file_path):
            raise Exception('Metro config file does not exists')
        metro_info = infra_loader.load_metro_from_file(file_path)
        if not metro_info:
            raise Exception('Fail to load_data metro network information')
        infraObject = Infra(metro_info)
        Infra.INFRA_POOL[infraObject.cfg_date] = infraObject
        return infraObject

    def get_corridors(self):
        """ return all corridor objects

        :return: corridor objects
        :rtype: list[pyticas.ttypes.CorridorObject]
        """
        return sorted(self.corridors.values(), key=lambda corr:corr.name)

    def get_corridor_names(self):
        """ return all corridor names

        :return: corridor names
        :rtype: list[str]
        """
        return sorted(self.corridors.keys())

    def get_corridor(self, route, direction=''):
        """ find corridor by route and direction and return corridor object

        :param route: route of corridor (e.g. I-35, I-94)
        :type route: str

        :param direction: direction (e.g. EB, WB, SB, NB)
        :type direction: str

        :return: corridor object
        :rtype: CorridorObject
        """
        if not direction:
            return self.get_corridor_by_name(route)
        return self.corridors.get('{0} ({1})'.format(route, direction), None)

    def get_corridor_by_name(self, corr_name):
        """ find corridor by name and return corridor object

        :param corr_name: corridor name
        :type corr_name: str

        :return: corridor object
        :rtype: pyticas.ttypes.CorridorObject

        Notice::
            corr_name must be 'route (dir)' format
        """
        return self.corridors.get(corr_name, None)

    def get_rnode(self, rn):
        """ find rnode object from rnode object cache

        :param rn: rnode name or station name
        :type rn: str
        :return: rnode object
        :rtype: pyticas.ttypes.RNodeObject
        """
        if isinstance(rn, str):
            return self.rnodes.get(self.station_rnode_map.get(rn, rn), None)
        elif hasattr(rn, '_obj_type_') and rn._obj_type_ == 'RNODE':
            return rn
        elif isinstance(rn, RNodeObject):
            return rn

        return None

    def get_detector(self, det):
        """ return detector

        :type det: str
        :rtype: pyticas.ttypes.DetectorObject
        """
        if isinstance(det, str):
            return self.detectors.get(det, None)
        elif hasattr(det, '_obj_type_') and det._obj_type == 'DETECTOR':
            return det

        return None

    def get_camera(self, cam):
        """ find camera object by name

        :param cam: camera name
        :type cam: str
        :rtype: CameraObject
        """
        if isinstance(cam, str):
            return self.cameras.get(cam, None)
        elif hasattr(cam, '_obj_type_') and cam._obj_type == 'CAMERA':
            return cam

        return None

    def get_dms(self, dms):
        """ find DMS object by name

        :param dms: DMS name
        :type dms: str
        :rtype: pyticas.ttypes.DMSObject
        """
        if isinstance(dms, str):
            dms_name = dms.split('_')[0]
            return self.dmss.get(dms_name, None)
        elif hasattr(dms, '_obj_type_') and dms._obj_type == 'DMS':
            return dms

        return None

    def get_meter(self, met):
        """ find meter object by name

        :type met: str
        :return: meter object
        """
        if isinstance(met, str):
            return self.meters.get(met, None)
        elif hasattr(met, '_obj_type_') and met._obj_type == 'METER':
            return met

        return None

    def confidence(self, data, **kwargs):
        if not any(data):
            return 0
        return len([d for d in data if d != kwargs.get('missing_value', cfg.MISSING_VALUE)]) / float(len(data)) * 100

    def is_missing(self, data, **kwargs):
        return self.confidence(data, **kwargs) < kwargs.get('threshold', cfg.MISSING_THRESHOLD)
