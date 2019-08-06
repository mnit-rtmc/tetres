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

class TestMOE(TestPyTICAS):

    def setUp(self):
        super().setUp()
        self.target_route = route.create_route('S870', 'S882')
        self.target_prd = ph.create_period((2015, 9, 1, 6, 0), (2015, 9, 1, 7, 0), 300)

    def test_moe_helper(self):
        data = moe.speed(self.target_route, self.target_prd)
        data = moe.add_virtual_rnodes(data, self.target_route)
        output_file = os.path.join(ticas.get_path('tmp', create=True), 'test-eval.xlsx')

        self.target_route.cfg = rc.route_config.create_route_config(self.target_route.rnodes)

        #rc.route_config.remove_virtual_nodesets(self.target_route.cfg)

        writer.write(output_file, self.target_route, data, print_distance=True)
        self.assertTrue(True)

    def test_moe_with_route_config(self):

        input_file = os.path.join(ticas.get_path('tmp', create=True), 'test-eval.xlsx')
        output_file = os.path.join(ticas.get_path('tmp', create=True), 'test-eval-2.xlsx')

        r = rc.loader.load(input_file)
        data = moe.speed(r, self.target_prd)

        writer.write(output_file, r, data)
        self.assertTrue(True)

    #
    # def test_spatial_avg_imputation(self):
    #     test_data = [
    #         [55, 50, 55, 50, 55, 60, 75],
    #         [55, 50, 55, -1, 55, 60, 75],
    #         [55, -1, 55, -1, -1, 60, 75],
    #         [55, 20, 55, 30, 55, 60, 75],
    #     ]
    #
    #     expected_data = [
    #         [55, 50, 55, 50, 55, 60, 75],
    #         [55, 50, 55, 40, 55, 60, 75],
    #         [55, 35, 55, 35, 55.0, 60, 75],
    #         [55, 20, 55, 30, 55, 60, 75],
    #     ]
    #
    #     from pyticas.moe.imputation import spatial_avg
    #
    #     imp_data = spatial_avg.imputation(test_data)
    #
    #     self.assertEqual(imp_data, expected_data)
    #
    # def test_tt(self):
    #     route = Route(self.infra)
    #     route_data = route.create_route_data('S870', 'S1504')
    #     prd = ph.create_period((2015, 10, 5, 6, 0), (2015, 10, 5, 9, 0), 30)
    #
    #     res = moe.estimate_travel_time(route, prd)
    #     writer.write(os.path.join(self.data_path, 'tt-S870-S1504.xlsx'), res)
    #
    # def test_crossover_route(self):
    #     route_name = 'WZ I-35E NB (split to TH77)'
    #     route = Route(self.infra)
    #     route.load_route_data(route_name)
    #     prd = ph.create_period((2015, 10, 5, 6, 0), (2015, 10, 5, 9, 0), 30)
    #     res = moe.estimate_travel_time(route, prd)
    #     writer.write(os.path.join(self.data_path, 'tt-crossover.xlsx'), res)
    #
    # def test_eval(self):
    #
    #     route = Route()
    #     route.create_route_data('S301', 'S323')
    #
    #     prd = ph.create_period((2015, 9, 9, 6, 0), (2015, 9, 9, 8, 0), 300)
    #     prd2 = ph.create_period((2015, 9, 10, 6, 0), (2015, 9, 10, 8, 0), 300)
    #
    #     if 1:
    #         print('Speed ==============')
    #         res = moe.estimate_speed(route, prd)
    #         res = moe.add_virtual_rnodes(res)
    #         for rd in res:
    #             # if not rd.station_id: continue
    #             print((rd.station_id, rd.data))
    #
    #         res = moe.estimate_travel_time(route, prd)
    #         print('TT ===================')
    #         for rd in res:
    #             # if not rd.station_id: continue
    #             print((rd.station_id, rd.data))
    #
    #     res = moe.estimate_speed(route, prd)
    #     writer.write(os.path.join(self.data_path, 'speed.xlsx'), res)
    #
    #     # TODO : fix how to make virtual rnode data for total flow
    #     res = moe.estimate_total_flow(route, prd)
    #     res = moe_helper.add_virtual_rnodes(res)
    #     writer.write(os.path.join(self.data_path, 'tq.xlsx'), res)
    #
    #     res = moe.estimate_travel_time(route, prd)
    #     writer.write(os.path.join(self.data_path, 'tt.xlsx'), res)
    #
    #     res = moe_helper.remove_virtual_rnodes(res)
    #     writer.write(os.path.join(self.data_path, 'tt-no-vrn.xlsx'), res)
    #
    #     res = moe.estimate_vmt(route, prd)
    #     writer.write(os.path.join(self.data_path, 'vmt.xlsx'), res)
    #
    #     res = moe.estimate_vht(route, prd)
    #     writer.write(os.path.join(self.data_path, 'vht.xlsx'), res)
    #
    #     res = moe.estimate_dvh(route, prd)
    #     writer.write(os.path.join(self.data_path, 'dvh.xlsx'), res)
    #
    #     res = moe.estimate_lvmt(route, prd)
    #     writer.write(os.path.join(self.data_path, 'lvmt.xlsx'), res)
    #
    #     res = moe.estimate_acceleration(route, prd)
    #     writer.write(os.path.join(self.data_path, 'accel.xlsx'), res)
    #
    # def _compare_data(self, d1, d2):
    #     if len(d1) != len(d2):
    #         return False
    #
    #     for idx in range(len(d1)):
    #         if abs(d1[idx] - d2[idx]) > 0.1:
    #             return False
    #
    #     return True
    #

if __name__ == '__main__':
    unittest.main()
