# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import unittest

from .base import TestPyTICAS
from pyticas.tool import pygmaps

class TestCamInfo(TestPyTICAS):
    def test_cam_info(self):
        """ test cam location
        """
        cases = [
            {'camera' : 'C008', 'up_station' : 'S601', 'dn_station' : 'S602'},
            {'camera' : 'C865', 'up_station' : 'S1361', 'dn_station' : 'S1058'},
            {'camera' : 'C505', 'up_station' : 'S814', 'dn_station' : 'S927'},
            {'camera' : 'C425', 'up_station' : 'S478', 'dn_station' : 'S192'},
            {'camera' : 'C1714', 'up_station' : 'S1104', 'dn_station' : None},
            {'camera' : 'C920', 'up_station' : 'S291', 'dn_station' : None},
            {'camera' : 'C122', 'up_station' : None, 'dn_station' : 'S301'},

        ]
        for case in cases:
            cam = self.infra.get_camera(case['camera'])

            # for debug
            #
            # self._write_map(cam, cam.corridor.stations,
            #                 os.path.join(self.data_path, '%s-stations.html' % cam.name))

            self.assertEqual(cam.up_station, self.infra.get_rnode(case['up_station']))
            self.assertEqual(cam.down_station, self.infra.get_rnode(case['dn_station']))



    def _write_map(self, target_cam, rnodes, file_path):
        """

        :type target_cam: pyticas.ttypes.CameraObject
        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :type file_path: str
        :return:
        """
        init_lat = 44.974878
        init_lon = -93.233414

        mymap = pygmaps.maps(init_lat, init_lon, 10)
        mymap.addpoint(target_cam.lat, target_cam.lon, "#FF0000",
                       'Camera : %s' % (target_cam.name))
        for idx, rn in enumerate(rnodes):
            if rn.name == target_cam.name:
                continue
            mymap.addpoint(rn.lat, rn.lon, "#0000FF",
                           '[%03d] %s' % (idx, rn.station_id if rn.is_station() else rn.name))
        mymap.draw(file_path)

if __name__ == '__main__':
    unittest.main()

