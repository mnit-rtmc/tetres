# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.ttypes import MeterObject


def create_meter(rnode, meter, METER_CACHE):
    """

    :type rnode: pyticas.ttypes.RNodeObject
    :type meter: xml.etree.ElementTree.Element
    :type METER_CACHE: dict[str, MeterObject]
    :return: MeterObject
    """
    meterKey = meter.get('name')
    meterObject = MeterObject({
        'rnode' : rnode,
        'name' : meter.get('name'),
        'label' : rnode.label,
        'storage' : int(meter.get('storage', 0)),
        'max_wait' : int(meter.get('max_wait', 0)),
        'lon' : float(meter.get('lon', 0.0)),
        'lat' : float(meter.get('lat', 0.0)),
        'queue' : _find_detectors('Q', rnode.detectors),
        'green' : _find_detectors('G', rnode.detectors),
        'merge' : _find_detectors('M', rnode.detectors),
        'bypass' : _find_detectors('B', rnode.detectors),
        'passage' : _find_detectors('P', rnode.detectors)
    })
    METER_CACHE[meterKey] = meterObject
    return meterObject

def _find_detectors(det_type, detectors):
    dets = []
    for det in detectors:
        if det_type == 'G' and det.is_green_lane():
            dets.append(det)
        elif det_type == 'M' and det.is_merge_lane():
            dets.append(det)
        elif det_type == 'B' and det.is_bypass_lane():
            dets.append(det)
        elif det_type == 'P' and det.is_passage_lane():
            dets.append(det)
        elif det_type == 'Q' and det.is_queue_lane():
            dets.append(det)
    return dets