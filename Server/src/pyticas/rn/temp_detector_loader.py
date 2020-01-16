# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import csv
import math

from pyticas.logger import getDefaultLogger
from pyticas.ttypes import DetectorObject, RNodeObject
from pyticas.tool.distance import distance_in_mile_with_coordinate

temp_station_base_rnode_id = 300000
temp_station_rnode_count = 0
temp_station_base_id = 30000
temp_station_count = 0
errors = []

def import_existing_detector_based(infra, file_path):
    """

    :type infra: pyticas.infra.Infra
    :type file_path: str
    :return:
    """
    with open(file_path, 'r') as csvfile:
        cr = csv.reader(csvfile, delimiter=',', quotechar='|')
        r = -1
        for row in cr:
            r += 1
            if not r:
                continue
            tmp_det_name = row[0]
            ex_det_name = row[1]
            ex_tmp_det = infra.get_detector(tmp_det_name)

            if ex_tmp_det:
                pass

            ex_det = infra.get_detector(ex_det_name)
            if ex_det:
                _create_detector_existing_detector_based(infra, tmp_det_name, ex_det)


def _create_detector_existing_detector_based(infra, tmp_det_name, ex_det):
    """

    :type infra: pyticas.infra.Infra
    :type tmp_det_name: str
    :type ex_det: pyticas.ttypes.DetectorObject
    :return:
    """

    detKey = tmp_det_name
    if infra.detectors.get(detKey):
        return

    detObject = DetectorObject({
        'rnode': ex_det.rnode,
        'name': tmp_det_name,
        'label': ex_det.label,
        'category': ex_det.category,
        'lane': ex_det.lane,
        'shift': ex_det.shift,
        'field': None,
        'abandoned': False,
        'controller': None,
    })

    infra.detectors[detObject.name] = detObject
    ex_det.rnode.detectors.append(detObject.name)


def import_coordinate_based(infra, file_path):
    """

    :type infra: pyticas.infra.Infra
    :type file_path: str
    :return:
    """
    with open(file_path, 'r') as csvfile:
        cr = csv.reader(csvfile, delimiter=',', quotechar='|')
        r = -1
        for row in cr:
            r += 1
            if not r:
                continue
            corridor_name = row[0]
            direction = row[1]
            station_name = row[2]
            lat = float(row[3])
            lon = float(row[4])
            dets = []

            corridor = infra.get_corridor(corridor_name, direction)
            for idx in range(5, len(row)):
                if any(row[idx]):
                    det = infra.get_detector(row[idx])
                    if det:
                        continue
                    dets.append(row[idx])

            if dets:
                _create_rnode_coordinate_based(infra, corridor, lat, lon, dets, station_name)


def _create_rnode_coordinate_based(infra, corridor, lat, lon, dets, station_name=''):
    """

    :type infra: pyticas.infra.Infra
    :type corridor: pyticas.ttypes.CorridorObject
    :type lat: float
    :type lon: float
    :type dets: list[str]
    :type station_name: str
    :return:
    """
    global temp_station_base_rnode_id, temp_station_rnode_count, temp_station_base_id, temp_station_count

    if station_name and infra.get_rnode(station_name):
        _add_detector_to_existing_station(infra, station_name, dets)
        return

    sid = temp_station_base_id + temp_station_count
    station_name = 'ST{0}'.format(sid)
    should_create_rnode = True
    temp_station_count += 1

    rid = temp_station_base_rnode_id + temp_station_rnode_count
    temp_station_rnode_count += 1
    rnd_name = 'rnd_{0}'.format(rid)

    up_station, dn_station = infra.geo.find_updown_rnodes(lat, lon, corridor.stations)
    if not up_station and not dn_station:
        return

    s_limit = up_station.s_limit if up_station else dn_station.s_limit

    rnodeObject = RNodeObject({
        'corridor': corridor,
        'name': rnd_name,
        'station_id': station_name,
        'n_type': 'Station',
        'transition': '',
        'label': '',
        'lon': lon,
        'lat': lat,
        'lanes': len(dets),
        'shift': 0,
        's_limit': s_limit,
        'forks': '',
        'active': True,
        'up_rnode': None,
        'down_rnode': None,
        'up_station': None,
        'down_station': None,
        'up_entrance': None,
        'down_entrance': None,
        'up_exit': None,
        'down_exit': None,
        'detectors': [infra.get_detector(det) for det in dets],
        'meters': []
    })

    infra.rnodes[rnodeObject.name] = rnodeObject
    infra.station_rnode_map[station_name] = rnodeObject.name

    for idx in range(len(dets)):
        lane = idx + 1
        tmp_det_name = dets[idx]
        if infra.get_detector(tmp_det_name):
            continue
        detObject = DetectorObject({
            'rnode': rnodeObject,
            'name': tmp_det_name,
            'label': '%sN%d' % (rnodeObject.label.replace(' ', ''), lane),
            'category': '',
            'lane': lane,
            'shift': 0,
            'field': None,
            'abandoned': False,
            'controller': None,
        })
        infra.detectors[tmp_det_name] = detObject

    rnodeObject.detectors = [infra.get_detector(det) for det in dets]
    _add_station_to_corridor(infra, corridor, rnodeObject)

    return rnodeObject


def _add_detector_to_existing_station(infra, station_id, dets):
    """

    :type infra:
    :type station_id:
    :type dets:
    :return:
    """
    rnode = infra.get_rnode(station_id)
    if not rnode:
        raise Exception('Not existing station : ' + station_id)

    for idx in range(len(dets)):
        detObject = DetectorObject({
            'rnode': rnode,
            'name': dets[idx],
            'label': '%sN%d' % (rnode.label.replace(' ', ''), idx + 1),
            'category': '',
            'lane': idx + 1,
            'shift': 0,
            'field': None,
            'abandoned': False,
            'controller': None,
        })

        rnode.detectors.append(detObject.name)
        infra.detectors[dets[idx]] = detObject


def _add_station_to_corridor(infra, corr, rnode):
    """ add rnode to CorridorObject according to rnode type

    :type infra:pyticas.infra.Infra
    :type corr: CorridorObject
    :type rnode: pyticas.ttypes.RNodeObject
    """

    def _insert(target_node, up_rnode, dn_rnode, rnodes, location='down'):
        """

        :type target_node: pyticas.ttypes.RNodeObject
        :type up_rnode: pyticas.ttypes.RNodeObject
        :type dn_rnode: pyticas.ttypes.RNodeObject
        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :type location: str
        :return:
        """
        if up_rnode:
            ref_rnode = up_rnode
            location = 'down'
        else:
            ref_rnode = dn_rnode
            location = 'up'

        if not up_rnode and not dn_rnode:
            raise ValueError('Up or Down RNodeObject must exists')

        insert_point = rnodes.index(ref_rnode)
        if location == 'down':
            rnodes.insert(insert_point + 1, target_node)
        else:
            rnodes.insert(insert_point, target_node)

    up_rnode, dn_rnode = infra.geo.find_updown_rnodes(rnode.lat, rnode.lon, corr.rnodes)

    if not up_rnode and not dn_rnode:
        raise ValueError('Cannot find location of temporary station (%f, %f)' % (rnode.lat, rnode.lon))

    try:
        _insert(rnode, up_rnode, dn_rnode, corr.rnodes)
    except ValueError:
        errors.append({
            'type' : 'rnode',
            'rnode_name' : rnode.name,
            'lat' : rnode.lat,
            'lon' : rnode.lon,
            'corr' : rnode.corridor.name,
            'expected_up' : '',
            'expected_down' : ''
        })
        print('=> rnode : ', rnode.name, rnode.corridor.name, rnode.lat, rnode.lon)


    up_station, dn_station = infra.geo.find_updown_rnodes(rnode.lat, rnode.lon, corr.stations, d_limit=10)

    try:
        _insert(rnode, up_station, dn_station, corr.stations)
    except ValueError:
        errors.append({
            'type' : 'station',
            'rnode_name' : rnode.name,
            'lat' : rnode.lat,
            'lon' : rnode.lon,
            'corr' : rnode.corridor.name,
            'expected_up' : '',
            'expected_down' : ''
        })
        print('=> station : ', rnode.name, rnode.corridor.name, rnode.lat, rnode.lon)

    corr.station_rnode[rnode.station_id] = rnode
    corr.rnode_station[rnode.name] = rnode

