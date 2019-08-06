# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import unittest

from pyticas import period as ph
from pyticas import route
from pyticas import ticas
from pyticas.moe import moe
from pyticas.moe import moe_helper
from pyticas.moe import writer
from pyticas import rc
from .base import TestPyTICAS

class TestVMT(TestPyTICAS):

    def setUp(self):
        super().setUp()
        self.target_route = route.create_route('S870', 'S882')
        self.target_prd = ph.create_period((2015, 9, 1, 6, 0), (2015, 9, 1, 7, 0), 300)

    def test_moe_helper(self):
        data = moe.vmt(self.target_route, self.target_prd)
        #data = moe.add_virtual_rnodes(data, self.target_route)
        output_file = os.path.join(ticas.get_path('tmp', create=True), 'test-vmt.xlsx')
        print(output_file)
        writer.write(output_file, self.target_route, data, print_distance=True)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
