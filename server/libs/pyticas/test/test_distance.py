# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import unittest

from pyticas.tool import distance
from .base import TestPyTICAS


class TestDistance(TestPyTICAS):

    def test_calc_distance(self):
        profiles = [
            # Format : ( [loc1.lat, loc1.lon], [loc2.lat, loc2.lon], distance(loc1,loc2) )
            ([38.898556, -77.037852], [38.897147, -77.043934], 0.341)
        ]

        for prf in profiles:
            lat1, lon1 = prf[0]
            lat2, lon2 = prf[1]
            dist = prf[2]

            v = round(distance.distance_in_mile_with_coordinate(lat1, lon1, lat2, lon2), 3)
            self.assertEqual(v, dist)


if __name__ == '__main__':
    unittest.main()
