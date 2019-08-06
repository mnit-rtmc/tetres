# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import logging
import os
import sys
import traceback
import unittest
import pickle

from pyticas import ticas
from pyticas.config.mn import mn_cfg
from pyticas.infra import Infra


class TestInfraCls(unittest.TestCase):

    def setUp(self):
        self.metro_file = os.path.join(os.path.dirname(__file__), 'sample_metro_config', 'metro.xml')
        self.data_path = os.path.join(os.path.dirname(__file__), 'test_data_storage')
        logging.basicConfig(format='[%(asctime)s] (%(levelname)s) %(message)s', level=logging.INFO)
        try:
            ticas.initialize(self.data_path, mn_cfg)
        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)

    def tearDown(self):
        #test_util.rm_dir(self.data_path)
        pass

    def test_infra_load(self):
        infraObj = Infra.load_infra()
        pickled = pickle.dumps(infraObj)
        print('Size of Infra :', sys.getsizeof(pickled) / 1024 / 1024, 'MB')
        print(infraObj.get_corridor_names())
        print(dir(infraObj.get_rnode('S1095')))
        print(infraObj.get_detector('5409').station_id)
        print(dir(infraObj.get_meter('M169N16')))


if __name__ == '__main__':
    unittest.main()
