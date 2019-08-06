# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import logging
import os
import sys
import traceback
import unittest

from pyticas import ticas
from pyticas.config.mn import mn_cfg
from pyticas.infra import Infra
from pyticas.tool import pygmaps
from pyticas.ttypes import CameraObject
from .base import TestPyTICAS

class TestCamInfo(TestPyTICAS):

    def test_cam_info(self):
        """ test rnode information
        """
        cam = self.infra.get_camera('C008')
        self._write_cam_map(cam, os.path.join(self.data_path, 'cam_map_C008.html'))

    def _write_cam_map(self, cam, file_path):
        """

        :type cam: CameraObject
        :type file_path: str
        :return:
        """
        init_lat = 44.974878
        init_lon = -93.233414

        corr = self.infra.get_corridor_by_name(cam.corridor.name)
        mymap = pygmaps.maps(init_lat, init_lon, 10)
        print(cam.__dict__)
        mymap.addpoint(cam.lat, cam.lon, "#0000FF",
                       'Camera: {}<br/>UpStation: {}<br/>DownStation: {}'.format(cam.name, cam.up_station, cam.down_station))

        for rn in corr.rnodes:
            rn = self.infra.get_rnode(rn)
            coord = (rn.lat, rn.lon)
            mymap.addpoint(coord[0], coord[1], "#FF0000",
                           'Name: {}<br/>StationID: {}<br/>Label: {}<br/>UpCam: {}<br/>DownCam: {}'.format(rn.name, rn.station_id, rn.label, rn.up_camera, rn.down_camera))
        mymap.draw(file_path)

if __name__ == '__main__':
    unittest.main()