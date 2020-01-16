# -*- coding: utf-8 -*-
import math

from pyticas import cfg

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def feet_to_mile(feet):
    """ convert feet to mile
    """
    return float(feet) / 5280


def mile_to_feet(mile):
    return mile * 5280


def distance_in_feet(rnode1, rnode2):
    return distance_in_mile(rnode1, rnode2) * 5280


def distance_in_mile(rnode1, rnode2):
    return distance_in_mile_with_coordinate(rnode1.lat, rnode1.lon, rnode2.lat, rnode2.lon)


def distance_in_mile_with_coordinate(lat1, lon1, lat2, lon2):
    lon1 = _deg2rad(lon1)
    lon2 = _deg2rad(lon2)
    lat1 = _deg2rad(lat1)
    lat2 = _deg2rad(lat2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.pow(math.sin(dlat / 2), 2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(dlon / 2), 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return c * cfg.RADIUS_IN_EARTH_FOR_MILE


def _deg2rad(deg):
    return float(deg) * math.pi / 180.0


def calculate_distance(e1, e2, n1, n2):
    return math.sqrt(((e1 - e2) * (e1 - e2) + (n1 - n2) * (n1 - n2)) / 1609 * 5280)
