# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.ttypes import RNodeObject


def create_rnode(corr, rnode, RNODE_CACHE, STATION_RNODE_MAP):
    """

    :type corr: pyticas.ttypes.CorridorObject
    :type rnode: Element
    :type RNODE_CACHE: dict[str, RNodeObject]
    :type STATION_RNODE_MAP: dict[str, RNodeObject]
    :rtype: RNodeObject
    """

    rnodeKey = rnode.get('name')
    stationId = rnode.get('station_id', '')

    if stationId != '':
        STATION_RNODE_MAP[stationId] = rnodeKey

    rnodeObject = _create_rnode(corr, rnode)
    RNODE_CACHE[rnodeKey] = rnodeObject
    return rnodeObject

def _create_rnode(corr, rnode):
    """

    :type corr: pyticas.ttypes.CorridorObject
    :type rnode: xml.etree.ElementTree.Element
    :rtype: RNodeObject
    """
    n_type = rnode.get('n_type')
    if n_type == 'Station' and not rnode.get('station_id', None):
        n_type = ''

    return RNodeObject({
        'corridor' : corr,
        'name' : rnode.get('name'),
        'station_id' : rnode.get('station_id', ''),
        'n_type' : n_type,
        'transition' : rnode.get('transition', ''),
        'label' : rnode.get('label', ''),
        'lon' : float(rnode.get('lon', 0.0)),
        'lat' : float(rnode.get('lat', 0.0)),
        'lanes' : int(rnode.get('lanes', 0)),
        'shift' : int(rnode.get('shift', 0)),
        's_limit' : int(rnode.get('s_limit', 55)),
        'forks' : rnode.get('forks', ''),
        'active' : (rnode.get('active', 't') == 'f'),
        'up_rnode' : None,
        'down_rnode' : None,
        'up_station' : None,
        'down_station' : None,
        'up_entrance' : None,
        'down_entrance' : None,
        'up_exit' : None,
        'down_exit' : None,
        'detectors' : [],
        'meters' : []
    })

def add_detector(rnode, detector):
    """
    :type rnode: RNodeObject
    :type detector: pyticas.ttypes.DetectorObject
    """
    rnode.detectors.append(detector)

def add_meter(rnode, meter):
    """
    :type rnode: RNodeObject
    :type meter: pyticas.ttypes.MeterObject
    """
    rnode.meters.append(meter)

def fix_rnode_lanes(rnode):
    """
    :type rnode: RNodeObject
    """
    det_lanes = [ det.lane for det in rnode.detectors if det.lane ]

    if det_lanes:
        rnode.lanes = max(det_lanes)
