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

class TestRNodeInfo(unittest.TestCase):

    def setUp(self):
        self.metro_file = os.path.join(os.path.dirname(__file__), 'sample_metro_config', 'metro.xml')
        self.data_path = os.path.join(os.path.dirname(__file__), 'test_data_storage')
        logging.basicConfig(format='[%(asctime)s] (%(levelname)s) %(message)s', level=logging.INFO)
        try:
            ticas.initialize(self.data_path, mn_cfg)
            self.infra = Infra.load_infra_from_config_file(self.metro_file)
        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)

    def tearDown(self):
        #util.rm_dir(self.data_path)
        pass

    def test_nearby_station_in_opposite_direction(self):
        ih = self.infra.geo
        params = {
            'S872' : 'S903',
            'S1075' : 'S1088',
            'S1076' : 'S1088',
            'S1077' : 'S1086'
                  }
        for src, nearby in params.items():
            res = ih.find_nearby_station_in_opposite_direction(self.infra.get_rnode(src), d_limit=1)
            print('Check : ', src, ', expected=', nearby)
            for rn, dist in res:
                print(rn.station_id, ' : ', dist)
            print('*'*10)
            self.assertEqual(res[0][0].station_id, nearby)


if __name__ == '__main__':
    unittest.main()