# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.ttypes import DetectorObject

def create_detector(rnode, station_id, det, DETECTOR_CACHE):
    """

    :type rnode: pyticas.ttypes.RNodeObject
    :type station_id: str
    :type det: xml.etree.ElementTree.Element
    :type DETECTOR_CACHE: dict[str, DetectorObject]
    :rtype: DetectorObject
    """
    detKey = det.get('name')
    detObject = DetectorObject({
        'rnode' : rnode,
        'name' : det.get('name'),
        'label' : det.get('label', ''),
        'category' : det.get('category', ''),
        'lane' : int(det.get('lane', 0)),
        'shift' : int(det.get('shift', 0)),
        'field' : float(det.get('field', 22.0)),
        'abandoned' : det.get('abandoned', 'f') == 't',
        'controller' : det.get('controller', '')
    })
    DETECTOR_CACHE[detKey] = detObject
    return detObject

