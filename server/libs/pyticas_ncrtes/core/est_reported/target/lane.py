# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

def get_target_detectors(target_station, target_lane=2):
    """ return detector list to be used in collecting normal-day data

    :type target_station: pyticas.ttypes.RNodeObject
    :rtype: list[pyticas.ttypes.DetectorObject]
    """
    # in some stations
    # lane1 detector is missing
    lane1_det = _lane1_detector(target_station)
    if not lane1_det:
        return []

    # if lane 1 is auxiliary lane
    # then use lane 3
    if target_lane == 2 and lane1_det.is_auxiliary_lane():
        target_lane = 3 if target_station.lanes > 2 else -1

    if target_lane < 0:
        return []

    for det in target_station.detectors:
        if (det.lane == target_lane
                and not det.is_HOVT_lane()
                and not det.is_velocity_lane()
                and not det.is_temporary()):
            return [det]
    return []


def get_detector_checker(target_station):
    """ return detector-checker function

    :type target_station: pyticas.ttypes.RNodeObject
    :rtype: (function, list[pyticas.ttypes.DetectorObject])
    """

    valid_detectors = get_target_detectors(target_station)

    if not valid_detectors:
        return False, False

    def dc(det):
        """ check detector is in valid detectors
        :type det: pyticas.ttypes.DetectorObject
        :rtype: bool
        """
        return det in valid_detectors

    return dc, valid_detectors


def detectors_without_HOVT(target_station):
    """ this function is to test station data

    :type target_station: pyticas.ttypes.RNodeObject
    :rtype: list[pyticas.ttypes.DetectorObject]
    """
    # in some stations
    # lane1 detector is missing
    return [ det for det in target_station.detectors if not det.is_HOVT_lane() ]


def _lane1_detector(target_station):
    """ return lane-1 detector

    :type target_station: pyticas.ttypes.RNodeObject
    :rtype: pyticas.ttypes.DetectorObject
    """
    for det in target_station.detectors:
        if det.lane == 1 and not det.is_velocity_lane() and not det.is_temporary():
            return det
    return None