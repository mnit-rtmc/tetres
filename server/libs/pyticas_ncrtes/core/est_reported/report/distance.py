# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.tool import distance as distutil

def accumulated_distances(stations):
    miles = 0.0
    prevRn = None
    mile_points_map = {}
    mile_points_keys = {}
    for rnode in stations:
        if prevRn != None:
            m = distutil.distance_in_mile(prevRn, rnode)
            miles += m
        while str(miles) in mile_points_keys:
            miles += 0.0000001
        mile_points_map[rnode.station_id] = round(miles, 1)
        mile_points_keys[str(miles)] = rnode
        prevRn = rnode
    return mile_points_map