# -*- coding: utf-8 -*-
import datetime
import os
import re
import sys
from collections import defaultdict, OrderedDict
from enum import Enum

from pyticas import cfg
from pyticas.logger import getDefaultLogger
from pyticas.time import GMT2Local
from pyticas.tool import json
from pyticas.tool import distance as distutil

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


###############################
# Base Types
###############################
class Serializable(object):
    def serialize(self):
        d = {'__class__': self.__class__.__name__,
             '__module__': self.__module__,
             }
        d.update(self.__dict__)
        return d

    def clone(self):
        try:
            return json.loads(json.dumps(self, only_name=False))
        except Exception:
            logger = getDefaultLogger(__name__)
            logger.error('Fail to cloning object : %s' % self.__repr__(), exc_info=True)
            return None

    @classmethod
    def unserialize(cls, kwargs):
        obj = cls.__new__(cls)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        return obj


class TupleEnum(Enum):
    def get_name(self):
        return self.name

    def get_text(self):
        return self.value[1]

    def get_value(self):
        return self.value[0]

    def get_description(self):
        if len(self.value) >= 3:
            return self.value[2]
        else:
            return self.value[1]

    @classmethod
    def find_by_value(cls, value):
        for k, v in cls.__dict__.items():
            if hasattr(v, 'get_value') and v.get_value() == value:
                return v
        return None

    @classmethod
    def find_by_text(cls, value):
        for k, v in cls.__dict__.items():
            if hasattr(v, 'get_text') and v.get_text() == value:
                return v
        return None


###############################
# Roadway Network Elements
###############################
class InfraObject(object):
    _obj_type_ = 'InfraObject'

    def __init__(self):
        self.name = 'noname'
        self.infra_cfg_date = ''

    def serialize(self):
        return {'name': self.name,
                '_obj_type_': self._obj_type_}

    def serialize_name(self):
        return self.name


class CorridorObject(InfraObject):
    """ object representing corridor

    Attributes::

        - name (str): corridor name (e.g. I-35 (NB))
        - route (str): route of corridor (e.g. I-35)
        - dir (str): direction (e.g. NB, EB, SB, WB)
        - rnodes (list[RNodeObject]): list of rnodes in the corridor
        - stations (list[RNodeObject]): list of stations in the corridor
        - station_rnode (dict[str, RNodeObject]): dictionary to map station name and rnode name (e.g. station_rnode['S100'] => RNodeObject)
        - rnode_station (dict[str, RNodeObject]): dictionary to map rnode name and station name (e.g. rnode_station['rnd_1234'] => RNodeObject)
        - entrances (list[RNodeObject]): list of entrances in the corridor
        - exits (list[RNodeObject]): list of exits in the corridor
        - intersections (list[RNodeObject]): list of intersections in the corridor
        - dmss (list[DMSObject]): list of DMSs in the corridor
        - cameras (list[CameraObject]): list of cameras in the corridor
        - interchanges (list[RNodeObject]): list of interchanges in the corridor
        - accesses (list[RNodeObject]): list of access in the corridor
    """

    _obj_type_ = 'CORRIDOR'

    def __init__(self, attrs):

        super().__init__()

        self.name = None
        """ :type: str """

        self.route = None
        """ :type: str """

        self.dir = None
        """ :type: str """

        self.rnodes = None
        """ :type: list[RNodeObject] """

        self.stations = None
        """ :type: list[RNodeObject] """

        self.station_rnode = None
        """ :type: dict[str, RNodeObject] """

        self.rnode_station = None
        """ :type: dict[str, RNodeObject] """

        self.entrances = []
        """ :type: list[RNodeObject] """

        self.exits = []
        """ :type: list[RNodeObject] """

        self.intersections = []
        """ :type: list[RNodeObject] """

        self.dmss = []
        """ :type: list[DMSObject] """

        self.cameras = []
        """ :type: list[CameraObject] """

        self.interchanges = []
        """ :type: list[RNodeObject] """

        self.accesses = []
        """ :type: list[RNodeObject] """

        for key, value in attrs.items():
            setattr(self, key, value)

    @classmethod
    def corr_key(cls, route, direction):
        """ make corridor name by combining route and direction

        :param route: route of corridor (e.g. I-35, I-94)
        :type route: str

        :param direction: direction (e.g. EB, WB, SB, NB)
        :type direction: str

        :return: corridor name with direction
        :rtype: str

        """
        if direction:
            return '{0} ({1})'.format(route, direction)
        else:
            return route

    def is_CD(self):
        return self.route.endswith('CD')

    def is_Rev(self):
        return 'Rev' in self.route

    def is_RTMC(self):
        return 'RTMC' in self.route

    def __str__(self):
        return '<CorridorObject route="%s" dir="%s">' % (self.route, self.dir)


class RNodeObject(InfraObject):
    """ object representing RNode

    Attributes::
        - corridor (CorridorObject):  the corridor that the rnode is located on
        - name (str): rnode name
        - station_id (str): station id of the rnode if it exists
        - n_type (str): node type e.g. Station, Entrance, Exit, Intersection, Interchange, Access
        - transition (str): transition of the ramp e.g. Leg, Loop, CD
        - label (str): label of the rnode
        - lon (float): longitude of the rnode
        - lat (float): latitude of the rnode
        - lanes (int): number of lanes of the rnode
        - shift (int): lane shift offset value
        - s_limit (int): speed limit
        - forks (list[str]): connected rnodes in the other corridor, ACCESS and INTERCHANGE have multiple forks
        - up_rnode (RNodeObject): rnode in the upstream of the rnode
        - down_rnode (RNodeObject): rnode in the downstream of the rnode
        - up_station (RNodeObject): station in the upstream of the rnode
        - down_station (RNodeObject): station in the downstream of the rnode
        - up_entrance (RNodeObject): entrance in the upstream of the rnode
        - down_entrance (RNodeObject): entrance in the downstream of the rnode
        - up_exit (RNodeObject): exit in the upstream of the rnode
        - down_exit (RNodeObject): exit in the downstream of the rnode
        - up_dmss (list[DMSObject]): DMSs in the upstream of the rnode
        - down_dmss (list[DMSObject]): DMSs in the downstream of the rnode
        - up_camera (CameraObject): camera in the upstream of the rnode
        - down_camera (CameraObject): camera in the downstream of the rnode
        - detectors (list[DetectorObject]): list of the detectors in the rnode
        - meters (list[MeterObject]): list of the meters in the rnode
        - active (bool): is it currently active?
    """

    _obj_type_ = 'RNODE'

    def __init__(self, attrs):

        super().__init__()

        self.corridor = None
        """:type: CorridorObject """

        self.name = None
        """:type: str """

        self.station_id = None
        """:type: str """

        self.n_type = None
        """:type: str """

        self.transition = None
        """:type: str """

        self.label = None
        """:type: str """

        self.lon = None
        """:type: float """

        self.lat = None
        """:type: float """

        self.lanes = None
        """:type: int """

        self.shift = None
        """:type: int """

        self.s_limit = None
        """:type: int """

        self.forks = []
        """:type: list[str] """

        self.up_rnode = None
        """:type: RNodeObject """

        self.down_rnode = None
        """:type: RNodeObject """

        self.up_station = None
        """:type: RNodeObject """

        self.down_station = None
        """:type: RNodeObject """

        self.up_entrance = None
        """:type: RNodeObject """

        self.down_entrance = None
        """:type: RNodeObject """

        self.up_exit = None
        """:type: RNodeObject """

        self.down_exit = None
        """:type: RNodeObject """

        self.up_dmss = []
        """:type: list[DMSObject] """

        self.down_dmss = []
        """:type: list[DMSObject] """

        self.up_camera = []
        """:type: list[CameraObject] """

        self.down_camera = []
        """:type: list[CameraObject] """

        self.detectors = None
        """:type: list[DetectorObject] """

        self.meters = []
        """:type: list[MeterObject] """

        self.active = True
        """:type: bool """

        self.connected_to = {}
        """:type: dict[str, RNodeObject] """

        self.connected_from = {}
        """:type: dict[str, RNodeObject] """

        for key, value in attrs.items():
            setattr(self, key, value)

        if self.forks:
            self.forks = self.forks.split(' ')
        else:
            self.forks = []

    def get_detectors(self, det_checker=None):
        return [det for det in self.detectors if not det_checker or det_checker(det)]

    def get_green_detectors(self, det_checker=None):
        return self._get_ramp_detectors('G', det_checker)

    def get_queue_detectors(self, det_checker=None):
        return self._get_ramp_detectors('Q', det_checker)

    def get_bypass_detectors(self, det_checker=None):
        return self._get_ramp_detectors('B', det_checker)

    def get_passage_detectors(self, det_checker=None):
        return self._get_ramp_detectors('P', det_checker)

    def get_merge_detectors(self, det_checker=None):
        return self._get_ramp_detectors('M', det_checker)

    def _get_ramp_detectors(self, category, det_checker=None):
        return [det for det in self.get_detectors(det_checker) if category == det.category]

    def is_rnode(self):
        return True

    def is_station(self):
        return (not self.n_type or self.n_type == 'Station') and any(self.station_id)

    def is_available_station(self):
        return self.is_station() and self.active and self.station_id != ''

    def is_exit(self):
        return self.n_type == 'Exit'

    def is_CD_exit(self):
        return self.n_type == 'Exit' and (self.transition == 'CD' or ('CD' in self.label and self.forks))

    def is_CD_entrance(self):
        return self.n_type == 'Entrance' and self.transition == 'CD'

    def is_access(self):
        return self.n_type == 'Access'

    def is_entrance(self):
        return self.n_type == 'Entrance'

    def is_ramp(self):
        return self.is_entrance() or self.is_exit()

    def is_intersection(self):
        return self.n_type == 'Intersection'

    def is_interchange(self):
        return self.n_type == 'Interchange'

    def is_wavetronics(self):
        if self.station_id != '':
            m = re.findall(r'([STQ]+)(\d+)', self.station_id)
            if m:
                station_id_num = int(m[0][1])
                if int(station_id_num / 100) * 100 / 100 == 17:
                    return True
        return False

    def is_radar_station(self):
        if self.station_id != '':
            m = re.findall(r'([STQ]+)(\d+)', self.station_id)
            if m:
                station_id_num = int(m[0][1])
                if int(station_id_num / 100) * 100 / 100 == 18:
                    return True
        return False

    def is_temp_station(self):
        if self.station_id != '':
            m = re.findall(r'([STQ]+)(\d+)', self.station_id)
            if m:
                prefix = m[0][0]
                if prefix != 'S':
                    return True

        return False

    def is_velocity(self):
        for det in self.detectors:
            if not det.is_velocity_lane():
                return False
        return True

    def is_abandoned(self):
        for det in self.detectors:
            if not det.is_abandoned():
                return False
        return True

    def is_normal_station(self):
        if not self.is_station():
            return False
        for fn in [self.is_temp_station, self.is_wavetronics, self.is_radar_station, self.is_velocity]:
            if fn():
                return False
        return True

    def get_lanes(self, **kwargs):
        without_category = kwargs.get('without', [])
        lanes = self.lanes
        for det in self.detectors:
            if det.category in without_category:
                lanes -= 1
        return lanes

    def has_lane(self, category):
        for det in self.detectors:
            if det.category == category:
                return True
        return False

    def has_meter(self):
        return any(self.meters)

    def __str__(self):
        return '<RNodeObject name="%s" n_type="%s" station_id="%s" label="%s">' % (
            self.name, self.n_type, self.station_id, self.label)


class DetectorObject(InfraObject):
    """ object representing detector

    Attributes::

        - name (str): detector name
        - rnode_name (str): name of rnode that containing the detector
        - station_id (str): station id of rnode that containing the detector
        - label (str): label of detector
        - category (str): lane type of detector (e.g. 'A', 'M', 'B', 'Q'...)
        - lane (int): lane which detector is located on
        - field (float): field length of detector
        - abandoned (bool): true if it is abandoned
        - controller (str): controller name that the detector is connected
        - shift (int): lane shift offset value

    """

    _obj_type_ = 'DETECTOR'

    def __init__(self, attrs):

        super().__init__()

        self.name = None
        """ :type: str """

        self.rnode = None
        """ :type: RNodeObject """

        self.label = None
        """ :type: str """

        self.category = None
        """ :type: str """

        self.lane = None
        """ :type: int """

        self.field = None
        """ :type: float """

        self.abandoned = None
        """ :type: bool """

        self.controller = None
        """ :type: str """

        self.shift = None
        """ :type: int """

        for key, value in attrs.items():
            setattr(self, key, value)

    @classmethod
    def confidence(cls, data, missing_data=-1):
        if not data:
            return 0
        return len([d for d in data if d != missing_data]) / float(len(data)) * 100

    @classmethod
    def is_missing(cls, data, missing_data=-1):
        return DetectorObject.confidence(data, missing_data) < 80

    def get_field_length(self):
        if self.field == None or self.field < 0:
            return 20
        else:
            return float(self.field)

    def is_wavetronics(self):
        if self.rnode.station_id:
            m = re.findall(r'([STQ]+)(\d+)', self.rnode.station_id)
            prefix = m[0][0]
            station_id = int(m[0][1])
            if station_id / 100 == 17: return True
            if prefix != 'S': return True  # prefix 'S' is origin station
        return False

    def is_abandoned(self):
        return self.abandoned

    def is_temporary(self):
        return self.name[0] == 'T'

    def lane_type(self):
        LaneType = {'': 'Mainline',
                    'A': 'Auxiliary',
                    'CD': 'CD',
                    'R': 'Reversible',
                    'M': 'Merge',
                    'Q': 'Queue',
                    'X': 'Exit',
                    'B': 'Bypass',
                    'P': 'Passage',
                    'V': 'Velocity',
                    'O': 'Omnibus',
                    'G': 'Green',
                    'Y': 'Wrongway',
                    'H': 'HOV',
                    'HT': 'HOT',
                    'D': 'Shoulder'
                    }
        return LaneType.get(self.category, 'None')

    def is_mainline(self):
        return ('' == self.category)

    def is_auxiliary_lane(self):
        return ('A' == self.category)

    def is_HOVT_lane(self):
        return self.is_HOV_lane() or self.is_HOT_lane()

    def is_HOV_lane(self):
        return ('H' == self.category)

    def is_HOT_lane(self):
        return ('HT' == self.category)

    def is_velocity_lane(self):
        return ('V' == self.category)

    def is_omnibus_lane(self):
        return ('O' == self.category)

    def is_merge_lane(self):
        return ('M' == self.category)

    def is_green_lane(self):
        return ('G' == self.category)

    def is_passage_lane(self):
        return ('P' == self.category)

    def is_queue_lane(self):
        return ('Q' == self.category)

    def is_bypass_lane(self):
        return ('B' == self.category)

    def is_CD_lane(self):
        return ('CD' == self.category)

    def is_exit_lane(self):
        return ('X' == self.category)

    def is_wrongway_lane(self):
        return ('Y' == self.category)

    def is_shoulder_lane(self):
        return ('D' == self.category)

    def __str__(self):
        return '<DetectorObject name="%s" lane="%d" category="%s" label="%s">' % (
            self.name, self.lane, self.category, self.label)


class CameraObject(InfraObject):
    """ object representing camera

    Attributes::

        - corridor_name (str): corridor name that the camera is located on
        - name (str): camera name
        - description (str): camera description
        - label (str): label
        - lon (float): longitude
        - lat (float): latitude
        - distance_from_first_station (float): distance from the first station of the corridor
        - up_station (str): upstream station name
        - down_station (str): downstream station name
    """

    _obj_type_ = 'CAMERA'

    def __init__(self, attrs):
        super().__init__()

        self.corridor = None
        """ :type: CorridorObject """

        self.name = None
        """ :type: str """

        self.label = None
        """ :type: str """

        self.description = None
        """ :type: str """

        self.lon = None
        """ :type: float """

        self.lat = None
        """ :type: float """

        self.distance_from_first_station = None
        """ :type: float """

        self.up_station = None
        """ :type: RNodeObject """

        self.down_station = None
        """ :type: RNodeObject """

        for key, value in attrs.items():
            setattr(self, key, value)

    def __str__(self):
        return '<CameraObject name="%s" corridor="%s" label="%s">' % (
            self.name, self.corridor.name, self.label)


class DMSObject(InfraObject):
    """ object representing DMS

    Attributes::

        - corridor_name (str): name of the corridor that the DMS is located on
        - name (str): DMS name
        - description (str): description of the DMS
        - label (str): label of the DMS
        - lon (float): longitude of the DMS
        - lat (float): latitude of the DMS
        - width_pixel (int): width pixel of the DMS
        - height_pixel (int): height pixel of the DMS
        - distance_from_first_station (float): distance from the first station in the same corridor
        - up_station (RNodeObject): the first station object from the DMS to upstream
        - down_station (RNodeObject): the first station object from the DMS to downstream
        - dms_list (list[str]): DMS name list (DMS Object consists of multiple DMS such as L35WS55_1, L35WS55_2, L35WS55_3 ..)
    """

    _obj_type_ = 'DMS'

    def __init__(self, attrs):
        super().__init__()

        self.corridor = None
        """: type: CorridorObject """

        self.name = None
        """: type: str """

        self.description = None
        """: type: str """

        self.label = None
        """: type: str """

        self.lon = None
        """: type: float """

        self.lat = None
        """: type: float """

        self.width_pixels = None
        """: type: int """

        self.height_pixels = None
        """: type: int """

        self.distance_from_first_station = None
        """: type: float """

        self.up_station = None
        """: type: RNodeObject """

        self.down_station = None
        """: type: RNodeObject """

        self.dms_list = []
        """: type: list[str] """

        for key, value in attrs.items():
            setattr(self, key, value)

    def __str__(self):
        return '<DMSObject name="%s" corridor="%s" label="%s">' % (
            self.name, self.corridor.name, self.label)


class MeterObject(InfraObject):
    """ object representing Meter

    Attributes::

        - rnode_name (str): name of the rnode that the Meter is located on
        - name (str): Meter name
        - label (str): label of the Meter
        - storage (int): storage of the ramp
        - max_wait (int): max wait time
        - lon (float): longitude of the Meter
        - lat (float): latitude of the Meter
        - queue (list[DetectorObject]): detector object list that type is queue
        - green (list[DetectorObject]): detector object list that type is green
        - merge (list[DetectorObject]): detector object list that type is merge
        - bypass (list[DetectorObject]): detector object list that type is bypass
        - passage (list[DetectorObject]): detector object list that type is passage
    """

    _obj_type_ = 'METER'

    def __init__(self, attrs):
        super().__init__()

        self.rnode = None
        """ :type: RNodeObject """

        self.name = None
        """ :type: str """

        self.label = None
        """ :type: str """

        self.storage = None
        """ :type: int """

        self.max_wait = None
        """ :type: int """

        self.lon = None
        """ :type: float """

        self.lat = None
        """ :type: float """

        self.queue = None
        """ :type: list[DetectorObject] """

        self.green = None
        """ :type: list[DetectorObject] """

        self.merge = None
        """ :type: list[DetectorObject] """

        self.bypass = None
        """ :type: list[DetectorObject] """

        self.passage = None
        """ :type: list[DetectorObject] """

        for key, value in attrs.items():
            setattr(self, key, value)
            #
            # def get_detectors_data(self, dets, prd, traffic_type, aggr_type='max'):
            #     """ return total volume of passage detector
            #
            #     @type dets: detector name or object, list
            #     @type prd: period.Period
            #     @type traffic_type: traffictype.TrafficType
            #     @type aggr_type: aggregation method. it can be 'avg' or 'max' or 'min' or 'sum', string
            #     """
            #     if traffic_type.is_speed(): dataMethod = dr.get_speed
            #     elif traffic_type.is_volume(): dataMethod = dr.get_volume
            #     elif traffic_type.is_density(): dataMethod = dr.get_density
            #     elif traffic_type.is_flow(): dataMethod = dr.get_flow
            #     elif traffic_type.is_occupancy(): dataMethod = dr.get_occupancy
            #     elif traffic_type.is_scan(): dataMethod = dr.get_scan
            #     else: return None
            #
            #     if any(dets):
            #         dataList = []
            #         for d in dets:
            #             dataList.append(dataMethod(d, prd))
            #
            #         aggData = []
            #         nCount = len(dets)
            #         for didx in range(len(dataList[0])):
            #             total = 0
            #             minValue = sys.maxsize
            #             maxValue = -1 * sys.maxsize
            #             for detIdx in range(nCount):
            #                 o = dataList[detIdx][didx]
            #                 if minValue > o: minValue = o
            #                 if maxValue < o: maxValue = o
            #                 total += o
            #             avg = total / nCount if total > 0 else 0
            #             if aggr_type == 'avg': aggData.append(avg)
            #             elif aggr_type == 'min': aggData.append((minValue if minValue != sys.maxsize else -1))
            #             elif aggr_type == 'max': aggData.append(max(maxValue, -1))
            #             elif aggr_type == 'sum': aggData.append(total)
            #
            #         del dataList
            #
            #         return aggData
            #
            #     return None

    def __str__(self):
        return '<MeterObject name="%s" rnode="%s" label="%s">' % (
            self.name, self.rnode.name, self.label)


###############################
# Route and Period
###############################
class Period(Serializable):
    def __init__(self, start_date, end_date, interval=30):
        """
        :type start_date: str
        :type start_date: datetime.datetime
        :type end_date: str
        :type end_date: datetime.datetime
        :type interval: int
        """
        if isinstance(start_date, str):
            self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        else:
            self.start_date = start_date

        if isinstance(end_date, str):
            self.end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        else:
            self.end_date = end_date

        self.interval = interval

    def days(self):
        """ return number of dates

        :rtype: int
        """
        return len(self.get_dates())

    def years(self):
        """ return year list

        :rtype: list[int]
        """
        years = []
        for dt in self.get_dates():
            if dt.year not in years:
                years.append(dt.year)
        return years

    def get_period_string(self):
        return '%s ~ %s [interval=%d]' % (
            self.start_date.strftime("%Y-%m-%d %H:%M:%S"),
            self.end_date.strftime("%Y-%m-%d %H:%M:%S"),
            self.interval)

    def get_date_string(self):
        """
        :rtype: str
        """
        if self.days() == 1:
            return self.start_date.strftime("%Y-%m-%d")
        else:
            return '{} ~ {}'.format(self.start_date.strftime("%Y-%m-%d"),
                                    self.end_date.strftime("%Y-%m-%d"))

    def get_timeline(self, **kwargs):
        """ return timeline as list
        :rtype: list[datetime.datetime]
        """
        as_datetime = kwargs.get('as_datetime', False)
        with_date = kwargs.get('with_date', False)
        without_date = kwargs.get('without_date', False)
        if as_datetime:
            return self._get_timeline(as_datetime=True)
        elif without_date:
            return self._get_timeline(with_date=False, as_datetime=False)
        elif self.days() > 1:
            return self._get_timeline(with_date=True, as_datetime=False)
        else:
            return self._get_timeline(with_date=with_date, as_datetime=False)

    def _get_timeline(self, with_date=False, as_datetime=False):
        """ return timeline with date as list

        :rtype: list[datetime.datetime]
        """
        sdate = self.start_date
        """:type: datetime.datetime """

        ret = []
        while (sdate < self.end_date):
            sdate = sdate + datetime.timedelta(0, self.interval)
            if sdate > self.end_date:
                break
            if as_datetime:
                ret.append(sdate)
            else:
                if with_date:
                    ret.append(sdate.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    ret.append(sdate.strftime("%H:%M:%S"))
        return ret

    def get_dates(self):
        """ return date list

        :rtype: list[datetime.datetime]
        """
        sdate = self.start_date
        """:type: datetime.datetime """
        ret = []
        while (sdate.date() <= self.end_date.date()):
            ret.append(sdate.date())
            sdate = sdate + datetime.timedelta(days=1)
        return ret

    def extend_start_hour(self, extHour):
        """
        :type extHour: int
        """
        self.start_date = self.start_date - datetime.timedelta(0, extHour * 3600)
        return self

    def extend_end_hour(self, extHour):
        """
        :type extHour: int
        """
        self.end_date = self.end_date + datetime.timedelta(0, extHour * 3600)
        return self

    def shrink(self, sidx, eidx):
        """

        :type prd: Period
        :param sidx: start index
        :type sidx: int
        :param eidx: end index
        :type eidx: int
        """
        date_cursor = self.start_date
        idx = 0
        start_date = None
        end_date = None
        while (date_cursor <= self.end_date):
            if idx == sidx:
                start_date = date_cursor
            if idx == eidx:
                end_date = date_cursor
                break
            idx += 1
            date_cursor = date_cursor + datetime.timedelta(0, self.interval)

        self.start_date = start_date
        self.end_date = end_date
        return self

    def clone(self):
        """
        :rtype: Period
        """
        return super().clone()

    def __str__(self):
        """ return period string e.g. 20150901060000-20150901100030-30

        :rtype: str
        """
        return '<Period start_date="%s" end_date="%s" interval="%d">' % (
            self.start_date.strftime("%Y-%m-%d %H:%M:%S"),
            self.end_date.strftime("%Y-%m-%d %H:%M:%S"),
            self.interval)

    def __repr__(self):
        """ return period string e.g. 20150901060000-20150901100030-30

        :rtype: str
        """
        return self.__str__()


class Route(Serializable):
    def __init__(self, name='NoName', desc=''):
        """
        :type name: str
        :type desc: str
        """
        self.name = name
        """:type: str """

        self.desc = desc
        """:type: str """

        self.infra_cfg_date = None
        """:type: str """

        self.rnodes = list()
        """:type: list[pyticas.ttypes.RNodeObject] """

        self.cfg = None
        """:type: pyticas.ttypes.RouteConfig """

    # @property
    # def route_config(self):
    #     return self.cfg
    #
    # @route_config.setter
    # def route_config(self, v):
    #     self.cfg = v

    def get_rnodes(self):
        if not self.cfg:
            return self.rnodes

        stations = []
        for idx, node_set in enumerate(self.cfg.node_sets):
            crossover_lanes = node_set.node1.node_config.co_lanes
            od_lanes = node_set.node2.node_config.od_lanes

            if not crossover_lanes and not od_lanes:
                if node_set.node1.rnode:
                    stations.append(node_set.node1.rnode)
            else:
                if node_set.node2.rnode:
                    stations.append(node_set.node2.rnode)
        return stations

    def get_stations(self):
        return [st for st in self.get_rnodes() if st.is_station()]

    def get_detector_checker(self):

        if not self.cfg:
            return lambda det: True

        def find_nodeset(rn):
            """

            :type rn: RNodeObject
            :rtype: (RouteConfigNodeSet, RouteConfigNode)
            """
            for idx, node_set in enumerate(self.cfg.node_sets):
                if node_set.node1.rnode == rn:
                    return node_set, node_set.node1
                elif node_set.node2.rnode == rn:
                    return node_set, node_set.node2
            return None, None

        def checker(det):
            """

            :type det: DetectorObject
            :rtype: bool
            """
            node_set, node = find_nodeset(det.rnode)
            if not node_set:
                return False

            if node_set.node1.rnode == det.rnode:
                node1 = node_set.node1
                lanes1 = [n for n in range(1, node1.lanes + 1)]
                open_lanes = list(set(lanes1)
                                  - set(node1.node_config.closed_lanes)
                                  - set(node1.node_config.shifted_lanes)
                                  - set(node1.node_config.od_lanes))
                return det.lane in open_lanes

            elif node_set.node2.rnode == det.rnode:
                node2 = node_set.node2
                lanes2 = [n for n in range(1, node2.lanes + 1)]
                open_lanes = list(set(lanes2)
                                  - set(node2.node_config.closed_lanes)
                                  - set(node2.node_config.shifted_lanes))

                return det.lane in open_lanes and det.lane in node2.node_config.od_lanes

        return checker

    def corridors(self):
        """
        :rtype: list[pyticas.ttypes.CorridorObject]
        """
        corrs = []
        for rn in self.rnodes:
            if rn.corridor not in corrs:
                corrs.append(rn.corridor)
        return corrs

    def length(self):
        miles = 0.0
        for ridx in range(1, len(self.rnodes)):
            m = distutil.distance_in_mile(self.rnodes[ridx-1], self.rnodes[ridx])
            miles += m
        return miles

    def clone(self):
        """
        :rtype: Route
        """
        return super().clone()

    def is_same_route(self, other):
        """
        :type other: Route
        :rtype: bool
        """
        if other.rnodes != self.rnodes:
            return False

        has_cfg1 = (self.cfg != None)
        has_cfg2 = (other.cfg != None)
        if has_cfg1 != has_cfg2:
            return False

        if not has_cfg1:
            return True

        cfg_json1 = json.dumps(self.cfg)
        cfg_json2 = json.dumps(other.cfg)
        return cfg_json1 == cfg_json2


    def __str__(self):
        return '<Route name="%s" description="%s" corridor="%s" rnodes="%s ~ %s>' % (
            self.name,
            self.desc,
            ', '.join([ corr.name for corr in self.corridors() ]),
            self.rnodes[0].name,
            self.rnodes[-1].name
        )


class RouteConfig(Serializable):
    def __init__(self):
        self.infra_cfg_date = None
        """:type: str """

        self.node_sets = []
        """:type: list[RouteConfigNodeSet] """

    def add_node(self, rn, orn):
        """
        :type rn: RNodeObject
        :type orn: RNodeObject
        """
        self.node_sets.append(RouteConfigNodeSet(rn, orn))

    def add_nodes(self, rns, orns):
        """
        :type rns: list[RNodeObject]
        :type orns: list[RNodeObject]
        """
        for (rn, orn) in zip(rns, orns):
            self.add_node(rn, orn)

    def clone(self):
        """
        :rtype: RouteConfig
        """
        return super().clone()

class RouteConfigNodeSet(Serializable):
    def __init__(self, rn, orn, mp=0, ad=0, ln1=0, ln2=0):
        """
        :param rn: rnode for a direction
        :type rn: pyticas.ttypes.RNodeObject
        :param orn: rnode for the other direction
        :type orn: pyticas.ttypes.RNodeObject
        :type mp: float
        :type ad: float
        :type ln: int
        """
        self.node1 = RouteConfigNode(rn, ln1)
        """:type: RouteConfigNode """

        self.node2 = RouteConfigNode(orn, ln2)
        """:type: RouteConfigNode """

        self.mile_point = mp
        self.acc_distance = ad

    def is_virtual(self):
        return self.node1.is_virtual() and self.node2.is_virtual()


class RouteConfigNode(Serializable):
    def __init__(self, rn, ln=0):
        """
        :param rn: rnode for a direction
        :type rn: pyticas.ttypes.RNodeObject
        :type mp: float
        :type ad: float
        :type ln: int
        """
        self.rnode = rn
        """:type: pyticas.ttypes.RNodeObject """

        self.corridor = rn.corridor if rn else None
        """:type: pyticas.ttypes.CorridorObject """

        self.lanes = ln
        """:type: int """

        self.node_config = RouteConfigInfo()
        """:type: RouteConfigInfo """

    def get_name(self):
        if self.is_station():
            return self.rnode.station_id
        elif self.is_entrance():
            return 'E:%s(%s)' % (self.rnode.label, self.rnode.name)
        elif self.is_exit():
            return 'X:%s(%s)' % (self.rnode.label, self.rnode.name)
        else:
            return 'Virtual'

    def is_station(self):
        return (self.rnode and self.rnode.is_station())

    def is_entrance(self):
        return (self.rnode and self.rnode.is_entrance())

    def is_exit(self):
        return (self.rnode and self.rnode.is_exit())

    def is_ramp(self):
        return self.is_entrance() or self.is_exit()

    def is_virtual(self):
        return not self.rnode


class RouteConfigInfo(Serializable):
    """
        Members:
            - orn: rnode name in the opposite direction
            - ramp_opened: 1 if ramp is opened, -1 if ramp is closed, 0 if it is not ramp
            - closed_lanes: list of closed lanes
                        e.g. [1, 2] => lane 1 and lane 2 are closed
            - od_lanes: list of lanes occupied by opposite direction
                        e.g. [1, 2] => opposing traffic use lane 1 and 2
            - co_lanes: list of lanes that cross over to opposite direction
                        e.g. [1, 2] => lane 1 and lane 2 of the opposite direction are used by the direction of this node
            - shifted_lanes: list of closed lanes
                        e.g. [1, 2] => lane 1 and lane 2 are shifted
            - shift_dirs: shifting directions i.e. 'R' or 'L'
                        e.g. {1 : 'L' } => lane 1 is shifted to left side
    """

    def __init__(self):
        self.ramp_opened = 0
        """:type: int """

        self.lane_types = []
        """:type: list[str] """

        self.closed_lanes = []
        """:type: list[int] """

        self.od_lanes = []
        """:type: list[int] """

        self.co_lanes = []
        """:type: list[int] """

        self.shifted_lanes = []
        """:type: list[int] """

        self.shift_dirs = {}
        """:type: dict[int, str] """


######################################
# For Traffic Data Reader
#####################################
""" RNode Data

    - RNodeData class contains not only traffic data but also additional information
      such as traffic type, detector names, missing lanes and lane-by-lane data
"""


class RNodeData(Serializable):
    def __init__(self, rnode, prd, traffic_type):
        """
        :type rnode: pyticas.ttypes.RNodeObject
        :type prd: Period
        :type traffic_type: pyticas.ttypes.TrafficType
        """
        self.rnode = rnode

        if isinstance(rnode, RNodeObject):
            self.rnode_name = rnode.name
            self.station_id = rnode.station_id
            self.speed_limit = rnode.s_limit
        else:
            self.rnode_name = ''
            self.station_id = ''
            self.speed_limit = ''

        self.prd = prd
        """:type: Period """
        self.traffic_type = traffic_type
        """:type: TrafficType """
        self.data = [cfg.MISSING_VALUE] * len(prd.get_timeline())
        """:type: list[float] """
        self.detector_names = []
        """:type: list[str] """
        self.detectors = []
        """:type: list[DetectorObject] """
        self.dup_detector_names = []
        """:type: list[str] """
        self.detector_data = {}
        self.lanes = None
        """:type: list[int] """
        self.missing_lanes = []
        """:type: list[int] """

    def __str__(self):
        return '<RNodeData type="%s" info="%s" period="%s">' % (
            self.traffic_type.name, self.get_title(), self.prd.get_period_string())

    def __repr__(self):
        return self.__str__()

    # def clone(self):
    #     rd = RNodeData(self.rnode, self.prd.clone(), self.traffic_type)
    #     rd.data = list(self.data)
    #     rd.detector_names = list(self.detector_names)
    #     rd.dup_detector_names = list(self.dup_detector_names)
    #     rd.detector_data = dict(self.detector_data)
    #     rd.lanes = self.lanes
    #     rd.missing_lanes = list(self.missing_lanes)
    #     return rd

    def get_title(self, **kwargs):
        # is it virtual station
        if not self.rnode_name:
            return '-'

        if self.rnode.is_entrance():
            return '<Entrance> {} ({})'.format(self.rnode.label, self.rnode.name)
        elif self.rnode.is_exit():
            return '<Exit> {} ({})'.format(self.rnode.label, self.rnode.name)

        if kwargs.get('no_lane_info', False):
            return '{} ({})'.format(self.rnode.label,
                                    self.rnode.station_id if self.rnode.station_id else self.rnode.name)
        else:
            if not kwargs.get('print_type', False):
                return '{} ({}) {}/{} lanes'.format(self.rnode.label,
                                                    self.rnode.station_id if self.rnode.station_id else self.rnode.name,
                                                    self.lanes, self.rnode.lanes)
            else:
                return '<Station> {} ({}) {}/{} lanes'.format(self.rnode.label,
                                                              self.rnode.station_id if self.rnode.station_id else self.rnode.name,
                                                              self.lanes, self.rnode.lanes)


    def set_data(self, dets, data, **kwargs):
        """ set detector list and data (called by pyticas.dr.rnode_reader)

        :type dets: list[pyticas.ttypes.DetectorObject]
        :type data: list[list[float]]
        :type kwargs: dict
        """
        if not data: return

        missing_value = kwargs.get('missing_value', cfg.MISSING_VALUE)

        not_missing_lanes = [det.lane for idx, det in enumerate(dets) if
                             not DetectorObject.is_missing(data[idx], missing_value)]
        missing_lanes = [det.lane for idx, det in enumerate(dets) if
                         DetectorObject.is_missing(data[idx], missing_value) and det.lane not in not_missing_lanes]

        # when both original and temporary detector have data
        # remove the detector having small value
        dup_dets = self._duplicated_lane_dets(dets, data) if self.rnode and self.rnode.is_station() else []

        # make rnode data
        n_total_valid = 0
        n_dets = len(dets) - len(dup_dets)
        rnode_data = []

        lengths = [ len(data[i]) for i in range(len(data)) ]
        max_length = max(lengths)
        for i in range(max_length):
            row = [data[j][i] for j, det in enumerate(dets) if det not in dup_dets and lengths[j] > i and data[j][i] >= 0]
            n_valid = len(row)
            n_total_valid += n_valid
            v = self.traffic_type.gathering_method(sum(row), n_valid) if n_valid > 0 else missing_value
            rnode_data.append(v)

        self.data = self._set_interval(rnode_data, self.traffic_type, self.prd.interval)
        self.detector_data = {det.name: self._set_interval(data[idx], self.traffic_type, self.prd.interval)
                              for idx, det in enumerate(dets)}
        self.detector_names = [det.name for det in dets]
        self.detectors = dets
        self.dup_detector_names = [det.name for det in dup_dets]
        self.lanes = n_dets
        self.missing_lanes = missing_lanes

    def _duplicated_lane_dets(self, dets, data):
        """

        :type dets: list[pyticas.ttypes.DetectorObject]
        :type data: list[list[float]]
        :rtype list[pyticas.ttypes.DetectorObject]
        """
        to_remove_dets = []
        dets_by_lane = defaultdict(list)
        for idx, det in enumerate(dets):
            dets_by_lane[det.lane].append(idx)

        for dets_in_a_lane in dets_by_lane.values():
            if len(dets_in_a_lane) == 1: continue

            to_remove_idx = []
            origin_det_idx = -1
            prev_avg_value = -1 * sys.maxsize
            prev_idx = -1
            for idx in dets_in_a_lane:
                if not dets[idx].is_temporary():
                    origin_det_idx = idx
                if DetectorObject.is_missing(data[idx]):
                    to_remove_idx.append(idx)
                    continue
                avg_value = sum(data[idx]) / len(data[idx])
                if avg_value > prev_avg_value:
                    if prev_idx > 0:
                        to_remove_idx.append(prev_idx)
                    prev_avg_value = avg_value
                    prev_idx = idx
                else:
                    to_remove_idx.append(idx)
            if len(to_remove_idx) == len(dets_in_a_lane) and origin_det_idx in to_remove_idx:
                to_remove_idx.remove(origin_det_idx)
            to_remove_dets += [dets[idx] for idx in to_remove_idx]

        return to_remove_dets

    def _set_interval(self, data, traffic_type, interval):
        """

        :type data: list[float]
        :type traffic_type: TrafficType
        :type interval: int
        :return:
        """
        if interval == cfg.DETECTOR_DATA_INTERVAL:
            return data

        ret = []
        freq = interval // cfg.DETECTOR_DATA_INTERVAL
        for i in range(0, len(data), freq):
            dataSum = 0.0
            validCount = 0
            nextItv = len(data) if (i + freq) > len(data) else (i + freq)
            for j in range(i, nextItv):
                v = data[j]
                if v >= 0:
                    dataSum += v
                    validCount += 1
                    # elif traffic_type.interval_function_name == "density_with_station":
                    #     validCount += 1

            if validCount > 0 and dataSum >= 0:
                ret.append(traffic_type.interval_function(dataSum, validCount, freq))
            else:
                ret.append(cfg.MISSING_VALUE)

        return ret


class TrafficType(Serializable):
    volume = None
    """:type: TrafficType """

    occupancy = None
    """:type: TrafficType """

    scan = None
    """:type: TrafficType """

    density = None
    """:type: TrafficType """

    speed = None
    """:type: TrafficType """

    speed_wavetronics = None
    """:type: TrafficType """

    flow = None
    """:type: TrafficType """

    flow_average = None
    """:type: TrafficType """

    travel_time = None
    """:type: TrafficType """

    vmt = None
    """:type: TrafficType """

    accel = None
    """:type: TrafficType """

    def __init__(self, name, extension, sample_size, samples_per_day, interval_function, rnode_gathering_detector_data):
        self.name = name
        self.extension = extension
        self.sample_size = sample_size
        self.samples_per_day = samples_per_day
        self.funcs = {
            'average': lambda sum_of_data, valid_count, freq: sum_of_data / valid_count,
            'density_with_station': lambda sum_of_data, valid_count, freq: sum_of_data / valid_count,
            'cumulative': lambda sum_of_data, valid_count, freq: sum_of_data,
            'flow': lambda sum_of_data, valid_count, freq: sum_of_data / freq,
            'sum_in_rnode': lambda sum_of_data, valid_count: sum_of_data,
            'avg_in_rnode': lambda sum_of_data, valid_count: sum_of_data / valid_count,
        }
        self.interval_function = self.funcs.get(interval_function)
        self.interval_function_name = interval_function
        self.gathering_method = self.funcs.get(rnode_gathering_detector_data)
        self.gathering_method_name = rnode_gathering_detector_data

    def is_volume(self): return self.name == 'volume'

    def is_occupancy(self): return self.name == 'occupancy'

    def is_scan(self): return self.name == 'scan'

    def is_density(self): return self.name == 'density'

    def is_speed(self): return self.name == 'speed'

    def is_microwave_speed(self): return self.name == 'speed_microwave'

    def is_flow(self): return self.name == 'flow'

    def __str__(self):
        return '<TrafficType name="%s" extension="%s" sample_size="%d" samples_per_day="%d">' % (
            self.name, self.extension, self.sample_size, self.samples_per_day)

    def __repr__(self):
        return self.__str__()


#################################
# RWIS
#################################
class RWISSiteInfo(object):
    def __init__(self, data=None):
        self.group_id = None
        self.group_name = None
        self.site_id = None
        self.site_name = None
        self.lat = None
        self.lon = None
        self.distance_to_target = None
        if data:
            for k, v in data.items():
                setattr(self, k, v)

    def __str__(self):
        return '<RWISSiteInfo site_id="%s" site_name="%s" group_id="%s" group_name="%s" lat="%s" lon="%s">' % (
            self.site_id, self.site_name, self.group_id, self.group_name, self.lat, self.lon)


class ScanWebData(Serializable):
    _DATA_INTERVAL_ = 300
    _DATA_RANGE_LIMIT_ = 600

    def __init__(self, fields, datalist):
        self.data = {}
        self.fields = list(set(fields))
        for fidx, field in enumerate(fields):
            self.data[field] = [row[fidx] for dix, row in enumerate(datalist)]

        self.formating()

    def formating(self):
        datefields = ['DateTime', 'StartTime', 'EndTime']
        for fidx, field in enumerate(self.fields):
            self._sanit_general(self.data[field])
            if field in datefields:
                self._sanit_datefield(self.data[field])
                continue
            if self._check_number(self.data[field]):
                self._sanit_number(self.data[field])

    def _check_number(self, datalist):
        for didx, data in enumerate(datalist):
            if not data:
                continue
            if not isinstance(data, str):
                return True
            converted = ''.join([i for i in data if i.isdigit() or i == '.'])
            if converted:
                return True
            else:
                return False
        return False

    def _sanit_general(self, datalist):
        for didx, data in enumerate(datalist):
            if data in ['-', 'None', '']:
                datalist[didx] = None

    def _sanit_datefield(self, datalist):
        for didx, data in enumerate(datalist):
            if not data:
                continue
            if '/' in data:
                try:
                    dtt = datetime.datetime.strptime(data, '%m/%d/%Y %H:%M')
                except:
                    dtt = datetime.datetime.strptime(data, '%m/%d/%Y %H:%M:%S')

                datalist[didx] = dtt.strftime('%Y-%m-%d %H:%M:%S')

    def _sanit_number(self, datalist):
        for didx, data in enumerate(datalist):
            if not data or not isinstance(data, str):
                continue
            dstr = ''.join(i for i in data if i.isdigit() or i == '.')
            if dstr:
                datalist[didx] = float(dstr) if '.' in dstr else int(dstr)
            else:
                datalist[didx] = None

    def get_data_string(self):
        strs = []
        strs.append('# Weather Data')
        for field in self.fields:
            row = ', '.join(["'%s'" % d if isinstance(d, str) else "%s" % str(d) for d in self.data[field]])
            strs.append('  - %s : [%s]' % (field, row))
        return os.linesep.join(strs)

    def get_datetimes(self):
        times = self.data.get('DateTime', None)
        if not times:
            return None
        if '/' in times[0]:
            return [datetime.datetime.strptime(t, '%m/%d/%Y %H:%M') if t else None for t in times]
        else:
            return [datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S') if t else None for t in times]

    def get_surface_statuses(self):
        """ return surface status list

        SFCond Meanings::

            Com Init                 :    Data not yet available
            Com Fail                 :    Communications down
            No Report (2)            :    No report from sensor
            Dry (3)                  :    No moisture on pavement
            Wet (4)                  :    Moisture on pavement
            Chemical Wet (5)         :    Moisture mixed with anti-icer
            Snow/Ice Warning (6)     :    Freezing on pavement
            Damp (7)                 :    Absorbsion
            Damp (8)                 :    Absorbsion
            Damp (9)                 :    Condensation on pavement
            Frost (10)               :    Freezing condensation
            Damp (11)                :    Absorb. (Dew)
            Frost (12)               :    Freezing condensation
            Snow/Ice Warn (13)       :    Freezing on pavement
            Com Rest (14)            :    Communication restored
            No Report                :    No report from sensor
            Dry                      :    No moisture on pavement
            Wet                      :    Moisture on pavement
            Snow/Ice Watch           :    Potential freeze condition
            Chemical Wet             :    Mositure mixed with anti-icer
            Slush                    :    Slush
            Snow/Ice Warning         :    Freeze conditions
            Damp                     :    Damp
            Frost                    :    Frost
            Wet Below Freezing       :    Moisture detected below freezing
            Wet Above Freezing       :    Moisture detected above freezing
            Black Ice Warning        :    Possible ice condition due to fog
            No Report                :    No report from sensor
            Dry                      :    Dry
            Wet                      :    Wet
            Snow/Ice Watch           :    Potential freeze condition
            Chemical Wet             :    Mositure mixed with anti-icer
            Snow/Ice Warning         :    Freeze conditions
            Damp                     :    Damp
            Frost                    :    Frost
            Wet Below Freezing       :    Moisture detected below freezing
            Wet Above Freezing       :    Moisture detected above freezing
            Black Ice Warning        :    Possible ice condition due to fog
            Other                    :    ESS Surface Status code,Other (0).
            Error                    :    ESS Surface Status code,Error (1).
            Dry                      :    ESS Surface Status code,Dry().
            Trace Moisture           :    ESS Surface Status code,Trace Moisture().
            Wet                      :    ESS Surface Status code,Wet().
            Chemically Wet           :    ESS Surface Status code,Chemically Wet().
            Ice Warning              :    ESS Surface Status code,Ice Warning().
            Ice Watch                :    ESS Surface Status code,Ice Watch().
            Snow Warning             :    ESS Surface Status code,Snow Warning().
            Snow Watch               :    ESS Surface Status code,Snow Watch().
            Absorption               :    ESS Surface Status code,Absorption().
            Dew                      :    ESS Surface Status code,Dew().
            Frost                    :    ESS Surface Status code,Frost().
            Absorption at Dewpoint   :    ESS Surface Status code,Absorption at Dewpoin().
        """
        return self.data.get('SfStatus', None)

    def get_precip_types(self):
        """ return precipitation type list

        PCType Meanings::

            None            :    No precipitation
            Yes             :    Precip occurring
            Rain            :    Rain occurring
            Snow            :    Snow occurring
            Mixed           :    Mixed precip
            Upper           :    Upper
            Lower           :    Lower
            Both            :    Both
            Light           :    Light precip
            Light Freezing  :    Light freezing rain
            Freezing Rain   :    Freezing rain
            Sleet           :    Ice pellets or sleet detected
            Hail            :    Hail detected
            Lens Dirty      :    Lens needs cleaning
            No  Com         :    No Com
            Fault           :    Sensor fault
            Initialized     :    Initialized
            Other           :    (Ess) Some other type of Precip occurring
            Unidentified    :    (Ess) Some unidentified type of Precip occurring
            Unknown         :    (Ess) It is not known if Precip is occurring
            Frozen          :    (Ess) Some type of frozen Precip occurring,sleet or freezing rain.
            No Data (251)   :    No Data (251)
            No Data (252)   :    No Data (252)
            No Data (253)   :    No Data (253)
            No Data (254)   :    No Data (254)
            No Data         :    No Data
        """
        return self.data.get('PrecipType', None)

    def get_precip_accumulations(self):
        """ returns accumulated precipitation list in 'inch' (1 inch = 2.54 cm)
        :rtype: list[float]
        """
        return self.data.get('PrecipAccumulation', None)

    def get_precip_accumulations_3h(self):
        """ returns 3h accumulated precipitation list in 'inch' (1 inch = 2.54 cm)

        :rtype: list[float]
        """
        return self.data.get('3hr Accum', None)

    def get_precip_accumulations_6h(self):
        """ returns 6h accumulated precipitation list in 'inch' (1 inch = 2.54 cm)

        :rtype: list[float]
        """
        return self.data.get('6hr Accum', None)

    def get_precip_accumulations_24h(self):
        """ returns 24h accumulated precipitation list in 'inch' (1 inch = 2.54 cm)

        :rtype: list[float]
        """
        return self.data.get('24hr Accum', None)

    def get_precip_start_time(self):
        """ returns precipitation start times

        :rtype: list[datetime.datetime]
        """
        times = self.data.get('StartTime', None)
        if not times:
            return None
        return [datetime.datetime.strptime(t, '%m/%d/%Y %H:%M') if t else None for t in times]

    def get_precip_end_time(self):
        """ returns precipitation end times

        :rtype: list[datetime.datetime]
        """
        times = self.data.get('EndTime', None)
        if not times:
            return None
        return [datetime.datetime.strptime(t, '%m/%d/%Y %H:%M') if t else None for t in times]

    def get_precip_rates(self):
        """ returns precipitation rate list in 'iph' (1 inch = 2.54 cm)

        :rtype: list[float]
        """
        return self.data.get('PrecipRate', None)

    def get_surface_temperatures(self):
        """ returns surface temperature list in 'F'

        :rtype: list[float]
        """
        return self.data.get('SfTemp', None)

    def get_air_temperatures(self):
        """ returns air temperature list in 'F'

        :rtype: list[float]
        """
        return self.data.get('AirTemp', None)

    def get_wind_speeds(self):
        """ returns wind speed list in 'mph'

        :rtype: list[float]
        """
        return self.data.get('AvgWindSpeed', None)

    def get_wind_directions(self):
        """ returns wind direction list in 'mph'

        Wind Direction Data::

            E, W, S, N, NE, NW, SE, SW

        :rtype: list[str]
        """
        return self.data.get('WindDirection', None)

    def get_dewpoints(self):
        """ returns dew point temperaturelist in 'F'

        :rtype: list[float]
        """
        return self.data.get('Dewpoint', None)

    def get_humidities(self):
        """ return surface_status

        :rtype: list
        """
        return self.data.get('RH', None)

    def is_dry(self, rate_threshold=0.8):
        """ is road surface status dry?

        Options::

            default 'dry_threshold' is 0.8

        :param kwargs: optional parameters ('weather_data', 'dry_threshold')
        :return: True if surface is dry else False
        :rtype: bool
        """
        surface_status = self.get_surface_statuses()
        dry_status = [sf for sf in surface_status if sf.lower() == 'dry']

        if not dry_status or not surface_status or len(dry_status) / len(surface_status) < rate_threshold:
            return False
        else:
            return True

    def is_rain(self, rate_threshold=0.8):
        """ is road surface status rainy?

        Options::

            default 'rate_threshold' is 0.8

        :param kwargs: optional parameters ('weather_data', 'dry_threshold')
        :return: True if surface is dry else False
        :rtype: bool
        """
        surface_status = self.get_surface_statuses()
        rain_status = [sf for sf in surface_status if self._contains(['wet', 'rain'], sf.lower(), ['freezing']) ]
        if not rain_status or not surface_status or len(rain_status) / len(surface_status) < rate_threshold:
            return False
        else:
            return True

    def is_snow(self, rate_threshold=0.8):
        """ is road surface status rainy?

        Options::

            default 'rate_threshold' is 0.8

        :param kwargs: optional parameters ('weather_data', 'dry_threshold')
        :return: True if surface is dry else False
        :rtype: bool
        """
        surface_status = self.get_surface_statuses()
        snow_status = [sf for sf in surface_status if self._contains(['snow', 'slush', 'ice', 'chemical wet', 'freezing'], sf.lower()) ]
        if not snow_status or not surface_status or len(snow_status) / len(surface_status) < rate_threshold:
            return False
        else:
            return True


    def set_period(self, prd):
        """ make list of json from csv list

        :type wd: ScanWebData
        :type prd: pyticas.ttypes.Period
        """
        dtimes = self.get_datetimes()
        s_date, e_date = prd.start_date, prd.end_date

        def _find_row(dtimes, t_date, start_row):
            start_row = max(start_row - 3, 0)
            for idx in range(start_row, len(dtimes)):
                dtt = dtimes[idx]
                if dtt >= t_date:
                    return max(idx - 1, 0)
                # if dtt == t_date:
                #     return idx
            return 0 if t_date < dtimes[0] else len(dtimes) - 1

        new_data = {}
        datelist = []
        prev_row = row = 0
        while s_date < e_date:
            row = _find_row(dtimes, s_date, prev_row)
            s_date = s_date + datetime.timedelta(seconds=self._DATA_INTERVAL_)
            datelist.append(s_date.strftime("%Y-%m-%d %H:%M:%S"))
            dt = s_date - dtimes[row] if s_date >= dtimes[row] else dtimes[row] - s_date
            for field in self.fields:
                datalist = new_data.get(field, [])
                if dt.seconds > self._DATA_RANGE_LIMIT_:  # 10 min
                    datalist.append(None)
                else:
                    datalist.append(self.data[field][row])

                new_data[field] = datalist
            prev_row = row

        new_data['DateTime'] = datelist
        self.data = new_data

    def _contains(self, arr, target_str, except_arr=None):
        """

        :type arr: list[str]
        :type target_str: str
        :type except_arr: list[str]
        :rtype:
        """
        for v in arr:
            if v in target_str and (not except_arr or not self._contains(except_arr, target_str)):
                return True
        return False

    def __add__(self, other_wd):
        rwis_data = ScanWebData(self.fields, [])
        for fidx, field in enumerate(other_wd.fields):
            rwis_data.data[field] = self.data[field] + other_wd.data[field]
        return rwis_data


class WeatherSensorData(object):
    """ class to contain weather information and get status easily """
    _weather_types = {0: 'Dry', 1: 'Rain', 2: 'Rain&Snow', 3: 'Snow', 4: 'Hailstone', -1: 'Error'}

    def __init__(self, types, rains):
        """

        :type types: int
        :type rains: float
        """
        if not types or not rains:
            self.code = -1
            self.name = self._weather_types[-1]
            types = []
            rains = []

        n_acc = 0.0
        n_total_rain_fall = 0.0
        n_rain_fall = 0.0
        n_data = len(types)

        wtypes = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, -1: 0}

        for idx in range(n_data):
            t = types[idx]
            r = rains[idx]
            wtypes[t] += 1
            if t != -1:
                n_acc += 1
            if t > 0:
                n_total_rain_fall += r
                n_rain_fall += 1

        self.code = max(wtypes, key=wtypes.get) if types else -1
        self.name = self._weather_types[self.code]
        self.accuracy = (n_acc / n_data * 100) if types else -1
        self.avg_rain_fall = (n_total_rain_fall / n_rain_fall) if types and n_rain_fall > 0 else 0;
        self.total_rain_fall = n_total_rain_fall
        self.n_dry = wtypes.get(0)
        self.n_data = n_data
        self.dry_rate = (self.n_dry / float(self.n_data)) if types else -1
        self.types = types
        self.rains = rains

    def type_to_str(self, type_code):
        """
        :type type_code: int
        :rtype: str
        """
        return self._weather_types.get(type_code, 'None')

    def get_code(self):
        return self.type_to_str(self.code)

    def is_dry(self, **kwargs):
        dry_rate_threshold = kwargs.get('threshold', 0.8)
        return (self.get_dry_rate() >= dry_rate_threshold)

    def is_rain(self):
        return self.code == 1

    def is_mixed(self):
        return self.code == 2

    def is_snow(self):
        return self.code == 3

    def is_hailstone(self):
        return self.code == 4

    def is_error(self):
        return self.code == -1

    def get_dry_rate(self):
        return self.dry_rate

    def get_avg_rain_fall(self):
        return self.avg_rain_fall

    def get_total_rain_fall(self):
        return self.total_rain_fall

    def get_accuracy(self):
        return self.accuracy

    def __str__(self):
        return '<WeatherSensorData : name={}, accuracy={}, avg_rain_fall={}>'.format(self.name, self.accuracy,
                                                                                     self.avg_rain_fall)


class SurfaceCondition(TupleEnum):
    COM_INIT = (0, "Com Init", "Data not yet available")
    COM_FAIL = (1, "Com Fail", "Communications down")
    NO_REPORT_2 = (2, "No Report (2)", "No report from sensor")
    DRY_3 = (3, "Dry (3)", "No moisture on pavement")
    WET_4 = (4, "Wet (4)", "Moisture on pavement")
    CHEMICAL_WET_5 = (5, "Chemical Wet (5)", "Moisture mixed with anti-icer")
    SNOW_ICE_WARNING_6 = (6, "Snow/Ice Warning (6)", "Freezing on pavement")
    DAMP_7 = (7, "Damp (7)", "Absorbsion")
    DAMP_8 = (8, "Damp (8)", "Absorbsion")
    DAMP_9 = (9, "Damp (9)", "Condensation on pavement")
    FROST_10 = (10, "Frost (10)", "Freezing condensation")
    DAMP_11 = (11, "Damp (11)", "Absorb. (Dew)")
    FROST_12 = (12, "Frost (12)", "Freezing condensation")
    SNOW_ICE_WARN_13 = (13, "Snow/Ice Warn (13)", "Freezing on pavement")
    COM_REST_14 = (14, "Com Rest (14)", "Communication restored")
    NO_REPORT = (32, "No Report", "No report from sensor")
    DRY = (33, "Dry", "No moisture on pavement")
    WET = (34, "Wet", "Moisture on pavement")
    SNOW_ICE_WATCH = (35, "Snow/Ice Watch", "Potential freeze condition")
    CHEMICAL_WET = (36, "Chemical Wet", "Mositure mixed with anti-icer")
    SLUSH = (37, "Slush", "Slush")
    SNOW_ICE_WARNING = (38, "Snow/Ice Warning", "Freeze conditions")
    DAMP = (39, "Damp", "Damp")
    FROST = (40, "Frost", "Frost")
    WET_BELOW_FREEZING = (41, "Wet Below Freezing", "Moisture detected below freezing")
    WET_ABOVE_FREEZING = (42, "Wet Above Freezing", "Moisture detected above freezing")
    BLACK_ICE_WARNING = (43, "Black Ice Warning", "Possible ice condition due to fog")
    NO_REPORT_33 = (52, "No Report", "No report from sensor")
    DRY_33 = (53, "Dry", "No moisture on pavement")
    WET_33 = (54, "Wet", "Moisture on pavement")
    SNOW_ICE_WATCH_33 = (55, "Snow/Ice Watch", "Potential freeze condition")
    CHEMICAL_WET_33 = (56, "Chemical Wet", "Mositure mixed with anti-icer")
    SLUSH_33 = (57, "Slush", "Slush")
    SNOW_ICE_WARNING_33 = (58, "Snow/Ice Warning", "Freeze conditions")
    DAMP_33 = (59, "Damp", "Damp")
    FROST_33 = (60, "Frost", "Frost")
    WET_BELOW_FREEZING_33 = (61, "Wet Below Freezing", "Moisture detected below freezing")
    WET_ABOVE_FREEZING_33 = (62, "Wet Above Freezing", "Moisture detected above freezing")
    BLACK_ICE_WARNING_33 = (63, "Black Ice Warning", "Possible ice condition due to fog")
    OTHER = (101, "Other", "ESS Surface Status code,Other (0).")
    ERROR = (102, "Error", "ESS Surface Status code,Error (1).")
    DRY_ESS = (103, "Dry", "ESS Surface Status code,Dry().")
    TRACE_MOISTURE = (104, "Trace Moisture", "ESS Surface Status code,Trace Moisture().")
    WET_ESS = (105, "Wet", "ESS Surface Status code,Wet().")
    CHEMICALLY_WET_ESS = (106, "Chemically Wet", "ESS Surface Status code,Chemically Wet().")
    ICE_WARNING_ESS = (107, "Ice Warning", "ESS Surface Status code,Ice Warning().")
    ICE_WATCH_ESS = (108, "Ice Watch", "ESS Surface Status code,Ice Watch().")
    SNOW_WARNING_ESS = (109, "Snow Warning", "ESS Surface Status code,Snow Warning().")
    SNOW_WATCH_ESS = (110, "Snow Watch", "ESS Surface Status code,Snow Watch().")
    ABSORPTION_ESS = (111, "Absorption", "ESS Surface Status code,Absorption().")
    DEW_ESS = (112, "Dew", "ESS Surface Status code,Dew().")
    FROST_ESS = (113, "Frost", "ESS Surface Status code,Frost().")
    ABSORPTION_AT_DEWPOINT_ESS = (114, "Absorption at Dewpoint", "ESS Surface Status code,Absorption at Dewpoin().")
    NULL1 = (251, "null", "null")
    NULL2 = (252, "null", "null")
    NULL3 = (253, "null", "null")
    NULL4 = (254, "null", "null")
    NULL5 = (255, "null", "null")


class PrecipType(TupleEnum):
    NONE = (0, "None", "NO precipitation")
    YES = (1, "Yes", "PRECIP occurring")
    RAIN = (2, "Rain", "RAIN occurring")
    SNOW = (3, "Snow", "SNOW occurring")
    MIXED = (4, "Mixed", "MIXED precip")
    UPPER = (5, "Upper", "UPPER")
    LOWER = (6, "Lower", "LOWER")
    BOTH = (7, "Both", "BOTH")
    LIGHT = (8, "Light", "LIGHT Precip")
    LIGHT_FREEZING = (9, "Light Freezing", "Light Freezing rain")
    FREEZING_RAIN = (10, "Freezing Rain", "Freezing rain")
    SLEET = (11, "Sleet", "ICE pellets or sleet detected")
    HAIL = (12, "Hail", "HAIL detected")
    LENS_DIRTY = (28, "Lens Dirty", "LENS needs cleaning")
    NO_COM = (29, "NO Com", "No Com")
    FAULT = (30, "Fault", "SENSOR Fault")
    INITIALIZED = (31, "Initialized", "INITIALIZED")
    OTHER = (41, "Other", "(ESS) Some other type of Precip occurring")
    UNIDENTIFIED = (42, "Unidentified", "(ESS) Some unidentified type of Precip occurring")
    UNKNOWN = (43, "Unknown", "(ESS) It is not known if Precip is occurring")
    FROZEN = (44, "Frozen", "(ESS) Some type of frozen Precip occurring,sleet or freezing rain.")
    NO_DATA_0 = (255, "NO Data", "No Data")
    NO_DATA_1 = (251, "NO Data 1", "No Data (251)")
    NO_DATA_2 = (252, "NO Data 2", "No Data (252)")
    NO_DATA_3 = (253, "NO Data 3", "No Data (253)")
    NO_DATA_4 = (254, "NO Data 4", "No Data (254)")


class PrecipIntens(TupleEnum):
    NONE = (0, "None", "No Intensity")
    RESERVED = (1, "Reserved", "Reserved")
    LIGHT = (2, "Light", "Light")
    MODERATE = (3, "Moderate", "Moderate")
    HEAVY = (4, "Heavy", "Heavy")
    RESERVED_1 = (5, "Reserved_1", "Reserved_1")
    RESERVED_2 = (6, "Reserved_2", "Reserved_2")
    INITIALIZED = (7, "Initialized", "Initialized")
    SLIGHT = (10, "Slight", "(Ess)  Slight precipitation is occurring.")
    OTHER = (11, "Other", "(Ess) Other")
    UNKNOWN = (12, "Unknown", "(Ess) intensity is not known")
    NO_DATA_251 = (251, "No Data (251)", "No Data (251)")
    NO_DATA_252 = (252, "No Data (252)", "No Data (252)")
    NO_DATA_253 = (253, "No Data (253)", "No Data (253)")
    NO_DATA_254 = (254, "No Data (254)", "No Data (254)")
    NO_DATA = (255, "No Data", "No Data")


#
#
# class SfType(TupleEnum):
#     ABSORPTION = (0, "Absorption")
#     ABSORPTION_AT_DEWPOINT = (1, "Absorption at Dewpoint")
#     BLACK_ICE_WARNING = (2, "Black Ice Warning")
#     CHEMICAL_WET = (3, "Chemical Wet")
#     CHEMICALLY_WET = (4, "Chemically Wet")
#     COM_FAIL = (5, "Com Fail")
#     COM_INIT = (6, "Com Init")
#     COM_REST = (7, "Com Rest")
#     DAMP = (8, "Damp")
#     DEW = (9, "Dew")
#     DRY = (10, "Dry")
#     ERROR = (11, "Error")
#     FROST = (12, "Frost")
#     ICE_WARNING = (13, "Ice Warning")
#     ICE_WATCH = (14, "Ice Watch")
#     NO_REPORT = (15, "No Report")
#     OTHER = (16, "Other")
#     SLUSH = (17, "Slush")
#     SNOW_ICE_WARNING = (18, "Snow/Ice Warning")
#     SNOW_ICE_WATCH = (19, "Snow/Ice Watch")
#     SNOW_WARNING = (20, "Snow Warning")
#     SNOW_WATCH = (21, "Snow Watch")
#     TRACE_MOISTURE = (22, "Trace Moisture")
#     WET = (23, "Wet")
#     WET_ABOVE_FREEZING = (24, "Wet Above Freezing")
#     WET_BELOW_FREEZING = (25, "Wet Below Freezing")
#
#
# class PCType(TupleEnum):
#     BOTH = (0, "Both")
#     FAULT = (1, "Fault")
#     FREEZING_RAIN = (2, "Freezing Rain")
#     FROZEN = (3, "Frozen")
#     HAIL = (4, "Hail")
#     INITIALIZED = (5, "Initialized")
#     LENS_DIRTY = (6, "Lens Dirty")
#     LIGHT = (7, "Light")
#     LIGHT_FREEZING = (8, "Light Freezing")
#     LOWER = (9, "Lower")
#     MIXED = (10, "Mixed")
#     NO_COM = (11, "No Com")
#     NO_DATA = (12, "No Data")
#     NONE = (13, "None")
#     OTHER = (14, "Other")
#     RAIN = (15, "Rain")
#     SLEET = (16, "Sleet")
#     SNOW = (17, "Snow")
#     UNIDENTIFIED = (18, "Unidentified")
#     UNKNOW = (19, "Unknown")
#     UPPER = (20, "Upper")
#     YES = (21, "Yes")

#
# class WindDirection(TupleEnum):
#     E = (0, "E")
#     W = (1, "W")
#     S = (2, "S")
#     N = (3, "N")
#     NE = (4, "NE")
#     NW = (5, "NW")
#     SE = (6, "SE")
#     SW = (7, "SW")

class RWISData(Serializable):
    _DATA_INTERVAL_ = 300
    _DATA_RANGE_LIMIT_ = 600

    def __init__(self, prd):
        """
        :type prd: pyticas.ttypes.Period
        """
        self.prd = prd
        self.data = []
        """:type: list[RWISDataRow] """

    def add_data(self, row):
        self.data.append(row)

    def get_datetimes(self):
        return [drow.dtime for drow in self.data]

    def set_period(self):
        """ make list of json from csv list

        :type wd: RWISData
        :type prd: pyticas.ttypes.Period
        """
        dtimes = self.get_datetimes()
        s_date, e_date = self.prd.start_date, self.prd.end_date

        def _find_row(dtimes, t_date, start_row):
            start_row = max(start_row - 3, 0)
            for idx in range(start_row, len(dtimes)):
                dtt = dtimes[idx]
                if dtt > t_date:
                    return max(idx - 1, 0)
                if dtt == t_date:
                    return idx
            return 0 if t_date < dtimes[0] else len(dtimes) - 1

        new_data = []
        datelist = []
        prev_row = row = 0
        while s_date < e_date:
            s_date = s_date + datetime.timedelta(seconds=self._DATA_INTERVAL_)
            row = _find_row(dtimes, s_date, prev_row)
            datelist.append(s_date.strftime("%Y-%m-%d %H:%M:%S"))
            dt = s_date - dtimes[row] if s_date >= dtimes[row] else dtimes[row] - s_date
            nd = self.data[row].clone()
            nd.dtime = s_date
            if dt.seconds > self._DATA_RANGE_LIMIT_:  # 10 min
                new_data.append(None)
            else:
                new_data.append(nd)

            prev_row = row
        self.data = new_data

        # def get_json_data2(self):
        #
        #     if not self.data:
        #         return []
        #
        #     keys = [ k for k, v in self.data[0].__dict__.items() ]
        #     json_data = {}
        #     for key in keys:
        #         json_data[key] = []
        #         for row in self.data:
        #             v = getattr(row, key)
        #             vtoset = v
        #             if isinstance(v, datetime.datetime) or isinstance(v, TupleEnum):
        #                 vtoset = str(v)
        #             json_data[key].append(vtoset)
        #
        #     return json_data


class RWISDataRow(Serializable):

    def __init__(self, atModelData, sfModelData):
        """

        :type atModelData: pyticas_rwis.db.model.Atmospheric
        :type sfModelData: pyticas_rwis.db.model.Surface
        :return:
        """

        # original data info  in DB
        # - time : GMT
        # - temp : 1/100 degrees celsius
        # - distance : meter
        # - speed : kilometers / hour
        # - water level : millimeters
        # - precip rate : 0.025 millimeters / hour
        # - precip accumulation : 0.025 millimeters
        # - chemical factor : 0 <= CF <= 95
        # - surface condition : in code (integer), defined pyticas_rwis.types.SurfaceCondition
        # - precipitation type : in code (integer), defined pyticas_rwis.types.PrecipitationType
        # - visual situation : in code (integer)
        # - visual situation : in code (integer)

        self.atm_id = None
        self.site_id = None
        self.dtime = None
        self.air_temp = None
        self.temp_alt = None
        self.temp_max = None
        self.temp_min = None
        self.dew_point = None
        self.rh = None
        self.pc_type = None
        self.pc_intens = None
        self.pc_rate = None
        self.pc_accum = None
        self.pc_accum_10min = None
        self.pc_start_dtime = None
        self.pc_end_dtime = None
        self.pc_past_1hour = None
        self.pc_past_3hours = None
        self.pc_past_6hours = None
        self.pc_past_12hours = None
        self.pc_past_24hours = None
        self.pc_time_since = None
        self.wet_build_temp = None
        self.vis_distance = None
        self.vis_situation = None
        self.barometric = None  # origin: millibar
        self.wnd_spd_avg = None
        self.wnd_spd_gust = None
        self.wnd_dir_avg = None
        self.wnd_dir_gust = None

        self.sf_id = None
        self.sen_id = None
        self.cond = None
        self.sf_temp = None
        self.frz_temp = None
        self.chem = None
        self.chem_pct = None
        self.depth = None
        self.ice_pct = None
        self.salinity = None
        self.conductivity = None
        self.blackice_signal = None
        self.error = None

        for key, value in atModelData.__dict__.items():
            if key.startswith('_') or key == 'id':
                continue
            if key == 'temp':
                key = 'air_temp'
            setattr(self, key, value)

        for key, value in sfModelData.__dict__.items():
            if key.startswith('_') or key == 'id':
                continue
            if key == 'temp':
                key = 'sf_temp'
            setattr(self, key, value)

        self.atm_id = atModelData.id
        self.sf_id = sfModelData.id

        self._convert_units()

    def _convert_units(self):
        temps = ['air_temp', 'temp_alt', 'temp_min', 'temp_max', 'sf_temp', 'frz_temp', 'wet_build_temp', 'dew_point']
        times = ['dtime', 'pc_start_dtime', 'pc_end_dtime']
        distances = ['vis_distance']
        water_levels = ['pc_past_1hour', 'pc_past_3hours', 'pc_past_6hours', 'pc_past_12hours', 'pc_past_24hours']
        depths = ['depth']
        wnd_dirs = ['wnd_dir_avg', 'wnd_dir_gust']
        rates = ['ice_pct', 'chem_pct', 'chem']
        grams = ['salinity']

        def _convert_attrs(attrs, convert_function):
            for att_name in attrs:
                v = getattr(self, att_name)
                if v == None:
                    continue
                elif v == '':
                    setattr(self, att_name)
                    continue

                setattr(self, att_name, convert_function(v))
                setattr(self, att_name + '_origin', v)

        # `0.01 C` to `F`
        _convert_attrs(temps, lambda v: (float(v) / 100 * 1.8 + 32) if abs(float(v)) < 10000 else None)

        # `GMT` to local time (time zone defined in `cfg`)
        _convert_attrs(times, GMT2Local)

        # `mm` to `inch`
        _convert_attrs(water_levels, lambda v: v * 0.039370)

        # wind direction angle to string
        _convert_attrs(wnd_dirs, lambda degree: list(["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"])[
            int(round(((degree % 360.0) / 45)))])

        # rates (0 < r < 100)
        _convert_attrs(rates, lambda v: v if 0 <= v <= 100 else None)

        # depth ( `0.1 mm` to `inch`)
        _convert_attrs(depths, lambda v: (float(v) / 10 * 0.039370) if float(v) < 32766 else None)

        # distances ( `meter` to `ft`)
        _convert_attrs(distances, lambda v: (float(v) * 3.28084) if float(v) < 32766 else None)

        # weight ( `g` to `once`)
        _convert_attrs(grams, lambda v: (float(v) * 0.035274) if float(v) < 65534 else None)

        self.pc_intens = PrecipIntens.find_by_value(self.pc_intens)
        self.pc_type = PrecipType.find_by_value(self.pc_type)
        self.cond = SurfaceCondition.find_by_value(self.cond)


class AttrDict(dict):
    """
    **Example**
        ad = AttrDict({'name': 'Chongmyung Park'}, email='chongmyung.park@gmail.com', country='South Korea')
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def extract(self, names):
        if isinstance(names, list):
            return ( self.__dict__.get(k, None) for k in names )
        else:
            return self.__dict__.get(names, None)

    def __add__(self, other):
        if isinstance(other, AttrDict):
            _other = other.__dict__
        elif isinstance(other, dict):
            _other = other
        else:
            raise Exception('Unsupport type')
        adict = dict(self.__dict__)
        adict.update(_other)
        return adict

    def __setitem__(self, key, value):
        super(AttrDict, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delitem__(self, key):
        super(AttrDict, self).__delitem__(key)
        del self.__dict__[key]

