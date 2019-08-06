# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import sys
import traceback
import unittest

from pyticas import ticas
from pyticas.config.mn import mn_cfg
from pyticas.test import util


class TestT(unittest.TestCase):

    def setUp(self):
        self.metro_file = os.path.join(os.path.dirname(__file__), 'sample_metro_config', 'metro.xml')
        self.data_path = os.path.join(os.path.dirname(__file__), 'test_data_storage')
        try:
            ticas.initialize(self.data_path, mn_cfg)
            ticas.load_metro(self.metro_file)
        except Exception as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)

    def tearDown(self):
        util.rm_dir(self.data_path)

    def test_something(self):
        pass
    
if __name__ == '__main__':
    unittest.main()