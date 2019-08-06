# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import unittest

from .base import TestPyTICAS
from pyticas.tool import pygmaps

class TestDMSInfo(TestPyTICAS):
    def test_dms_info(self):
        """ test dms location
        """

        dms1 = self.infra.get_dms('L35WN47_1')
        dms2 = self.infra.get_dms('L35WN47_2')
        self.assertIsNotNone(dms1)
        self.assertIsNotNone(dms2)
        self.assertEqual(dms1, dms2)

        cases = [
            {'dms' : 'L52N11', 'up_station' : 'S1178', 'dn_station' : None},
            {'dms' : 'V212E03', 'up_station' : None, 'dn_station' : 'S1379'},
            {'dms' : 'V100N01', 'up_station' : None, 'dn_station' : 'S375'},
            {'dms' : 'L35WN47', 'up_station' : 'S57', 'dn_station' : 'S58'},
            {'dms' : 'L35WN43', 'up_station' : 'S1705', 'dn_station' : 'S53'},
            {'dms' : 'V494E07', 'up_station' : 'S196', 'dn_station' : 'S197'},
        ]
        for case in cases:
            dms = self.infra.get_dms(case['dms'])
            if not dms:
                print("No DMS : ", case['dms'])
                continue

            if not dms.corridor:
                print("No Corridor : ", dms.name)
                continue
            # for debug
            #
            self._write_map(dms, dms.corridor.stations,
                            os.path.join(self.data_path, '%s-stations.html' % dms.name))

            self.assertEqual(dms.up_station, self.infra.get_rnode(case['up_station']))
            self.assertEqual(dms.down_station, self.infra.get_rnode(case['dn_station']))



    def _write_map(self, target_dms, rnodes, file_path):
        """

        :type target_dms: pyticas.ttypes.DMSObject
        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :type file_path: str
        :return:
        """
        init_lat = 44.974878
        init_lon = -93.233414

        mymap = pygmaps.maps(init_lat, init_lon, 10)
        mymap.addpoint(target_dms.lat, target_dms.lon, "#FF0000",
                       'DMS : %s' % (target_dms.name))
        for idx, rn in enumerate(rnodes):
            if rn.name == target_dms.name:
                continue
            mymap.addpoint(rn.lat, rn.lon, "#0000FF",
                           '[%03d] %s' % (idx, rn.station_id if rn.is_station() else rn.name))
        mymap.draw(file_path)

if __name__ == '__main__':
    unittest.main()

