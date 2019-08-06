# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import logging
import os
import sys
import traceback
import unittest

from pyticas import period as ph

from pyticas import ticas
from pyticas.config.mn import mn_cfg
from pyticas.infra import Infra
from pyticas.route import Route


class TestRoute(unittest.TestCase):

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
        #test_util.rm_dir(self.data_path)
        pass
    #
    # def test_crossover_route(self):
    #
    #     ih = self.infra.infra_helper
    #     rh = Route(self.infra, None)
    #     rh.route_data = rh.create_route_data('S1397', 'S1028')
    #     route = rh.route_data
    #     route.sub_routes[0].route_info.has_crossover = True
    #     route.sub_routes[0].route_info.crossover_from = 'EB'
    #     route.sub_routes[0].route_info.crossover_to = 'WB'
    #
    #     stations = [ rn for rn in route.sub_routes[0].route_info.rnodes if rn.is_station() ]
    #     orn_stations = [ rn for rn in rh.get_stations() ]
    #     print("")
    #     for (rn, orn) in zip(stations, orn_stations):
    #         print(rn.station_id, ' vs ', orn.station_id)
    #     print('Done', '*'*10)
    #
    # def test_get_rnodes_for_crossover_route(self):
    #
    #     ih = self.infra.infra_helper
    #     rh = Route(self.infra, None)
    #     rh.route_data = rh.create_route_data('S1397', 'S1028')
    #     route = rh.route_data
    #     route.sub_routes[0].route_info.has_crossover = True
    #     route.sub_routes[0].route_info.crossover_from = 'EB'
    #     route.sub_routes[0].route_info.crossover_to = 'WB'
    #
    #     rnodes = rh.get_rnodes()
    #     origin_rnodes = rh.get_rnodes(without_laneconfig=True)
    #     stations = rh.get_stations()
    #
    #     print("")
    #     for (orn, rn) in zip(origin_rnodes, rnodes):
    #         if not rn:
    #             str1 = '%10s, %10s, %15s' % ('None', 'None', 'None')
    #         elif rn.is_station():
    #             str1 = '%10s, %10s, %15s' % (rn.n_type, rn.name, rn.station_id)
    #         else:
    #             str1 = '%10s, %10s, %15s' % (rn.n_type, rn.name, rn.label)
    #
    #         if not orn:
    #             str2 = '%10s, %10s, %15s' % ('None', 'None', 'None')
    #         elif orn.is_station():
    #             str2 = '%10s, %10s, %15s' % (orn.n_type, orn.name, orn.station_id)
    #         else:
    #             str2 = '%10s, %10s, %15s' % (orn.n_type, orn.name, orn.label)
    #         print(str2, ' ||| ', str1)
    #     print('Done', '*'*10)
    #
    # def test_create_opposite_route(self):
    #
    #     ih = self.infra.infra_helper
    #     rh = Route(self.infra, None)
    #     #rh.route_config = rh.create_route_data('S1397', 'S1028')
    #     rh.route_data = rh.create_route_data('S1454', 'S1403')
    #     rnodes = rh.get_rnodes()
    #     o_route = rh.create_opposite_route()
    #     orh = Route(self.infra, o_route)
    #     o_rnodes = reversed(orh.get_rnodes())
    #
    #     print("")
    #     for (rn, orn) in zip(rnodes, o_rnodes):
    #         if rn.is_station():
    #             str1 = '%10s, %10s, %15s' % (rn.n_type, rn.name, rn.station_id)
    #         else:
    #             str1 = '%10s, %10s, %15s' % (rn.n_type, rn.name, rn.label)
    #
    #         if orn.is_station():
    #             str2 = '%10s, %10s, %15s' % (orn.n_type, orn.name, orn.station_id)
    #         else:
    #             str2 = '%10s, %10s, %15s' % (orn.n_type, orn.name, orn.label)
    #         print(str1, ' ||| ', str2)
    #
    #     print('Done', '*'*10)
    #
    # def test_wz_route(self):
    #     ih = self.infra.infra_helper
    #     rh = Route(self.infra, None)
    #     #rh.route_config = rh.create_route_data('S1397', 'S1028')
    #     rh.route_data = rh.create_route_data('S1454', 'S1403')
    #     #rh.route_data = rh.create_route_data('S870', 'S882') # WZ Case 01
    #
    #     wzLayout = wz.create_wz_layout(rh)
    #     filepath = os.path.join(self.infra.get_path('tmp', create=True), 'wz-01.xlsx')
    #     filepath2 = os.path.join(self.infra.get_path('tmp', create=True), 'wz-01 (2).xlsx')
    #     wz.write(filepath, wzLayout)
    #     wzLayout2 = xlsx.load_data(filepath)
    #     wz.write(filepath2, wzLayout2)
    #
    # def _test_wz_route2(self):
    #     ih = self.infra.infra_helper
    #     route = Route(self.infra, None)
    #     #rh.route_config = rh.create_route_data('S1397', 'S1028')
    #     #rh.route_data = rh.create_route_data('S1454', 'S1403')
    #     route.route_data = route.create_route_data('S870', 'S882') # WZ Case 01
    #     prd = ph.create_period((2013, 6, 18, 7, 0), (2013, 6, 18, 8, 0), 300)
    #
    #     wzLayout = wz.create_wz_layout(route)
    #     wz.set_closed_lanes(wzLayout, prd)
    #     filepath = os.path.join(self.infra.get_path('tmp', create=True), 'wz-01-filled.xlsx')
    #     wz.write(filepath, wzLayout)
    #
    #
    # def test_detector_check_for_lane_closed(self):
    #
    #     ih = self.infra.infra_helper
    #     rh = Route(self.infra, None)
    #     rh.route_data = rh.create_route_data('S179', 'S1080')
    #     route = rh.route_data
    #
    #     lane_close_from = 'Left'
    #     closed_lanes = 1
    #
    #     route.sub_routes[0].route_info.has_lane_close = True
    #     route.sub_routes[0].route_info.closed_lanes = closed_lanes
    #     route.sub_routes[0].route_info.lane_close_from = lane_close_from
    #
    #     stations = [ rn for rn in route.sub_routes[0].route_info.rnodes if rn.is_station() ]
    #     dc = rh.get_detector_checker()
    #
    #     print('')
    #     print('Lane Close Config : ', '{} lane(s) closed from {}'.format(closed_lanes, lane_close_from) )
    #
    #     for st in stations:
    #         print('{} ({} lane)'.format(st.station_id, st.lanes), [ (det.name, det.lane, 'T' if dc(det) else 'F') for det in st.detectors],  )
    #
    #     lane_close_from = 'Right'
    #     closed_lanes = 1
    #
    #     route.sub_routes[0].route_info.has_lane_close = True
    #     route.sub_routes[0].route_info.closed_lanes = closed_lanes
    #     route.sub_routes[0].route_info.lane_close_from = lane_close_from
    #
    #     stations = [ rn for rn in route.sub_routes[0].route_info.rnodes if rn.is_station() ]
    #     dc = rh.get_detector_checker()
    #
    #     print('')
    #     print('Lane Close Config : ', '{} lane(s) closed from {}'.format(closed_lanes, lane_close_from) )
    #     for st in stations:
    #         print('{} ({} lane)'.format(st.station_id, st.lanes), [ (det.name, det.lane, 'T' if dc(det) else 'F') for det in st.detectors],  )
    #
    # def test_detector_check_for_crossover(self):
    #
    #     ih = self.infra.infra_helper
    #     rh = Route(self.infra)
    #
    #     # I-35E NB
    #     rh.route_data = rh.create_route_data('S620', 'S626')
    #     route = rh.route_data
    #
    #     crossover_from = 'NB'
    #     crossover_to = 'SB'
    #     crossover_lane = 2
    #
    #     route.sub_routes[0].route_info.has_crossover = True
    #     route.sub_routes[0].route_info.crossover_from = crossover_from
    #     route.sub_routes[0].route_info.crossover_to = crossover_to
    #     route.sub_routes[0].route_info.crossover_lanes = crossover_lane
    #
    #     stations = rh.get_stations()
    #     dc = rh.get_detector_checker()
    #
    #     print('')
    #     print('Crossover Config : ', '{} lane(s) from {} to {}'.format(crossover_lane, crossover_from, crossover_to) )
    #     for st in stations:
    #         print('{} ({}, {} lane)'.format(st.station_id, st.corridor.dir, st.lanes), [ (det.name, det.lane, 'T' if dc(det) else 'F') for det in st.detectors] )
    #
    #     crossover_from = 'SB'
    #     crossover_to = 'NB'
    #     crossover_lane = 1
    #
    #     route.sub_routes[0].route_info.has_crossover = True
    #     route.sub_routes[0].route_info.crossover_from = crossover_from
    #     route.sub_routes[0].route_info.crossover_to = crossover_to
    #     route.sub_routes[0].route_info.crossover_lanes = crossover_lane
    #
    #
    #     stations = rh.get_stations()
    #     dc = rh.get_detector_checker()
    #
    #     print('')
    #     print('Crossover Config : ', '{} lane(s) from {} to {}'.format(crossover_lane, crossover_from, crossover_to) )
    #     for st in stations:
    #         print('{} ({}, {} lane)'.format(st.station_id, st.corridor.dir, st.lanes), [ (det.name, det.lane, 'T' if dc(det) else 'F') for det in st.detectors] )
    #
    # def test_detector_check_for_lane_shifted(self):
    #
    #     ih = self.infra.infra_helper
    #     rh = Route(self.infra, None)
    #     rh.route_data = rh.create_route_data('S179', 'S1080')
    #     route = rh.route_data
    #
    #     lane_shift_from = 'Left'
    #     shifted_lanes = 1
    #
    #     route.sub_routes[0].route_info.has_lane_shift= True
    #     route.sub_routes[0].route_info.shifted_lanes = shifted_lanes
    #     route.sub_routes[0].route_info.lane_shift_from = lane_shift_from
    #
    #     stations = [ rn for rn in route.sub_routes[0].route_info.rnodes if rn.is_station() ]
    #     dc = rh.get_detector_checker()
    #
    #     print('')
    #     print('Lane Shift Config : ', '{} lane(s) shifted from {}'.format(shifted_lanes, lane_shift_from) )
    #
    #     for st in stations:
    #         print('{} ({} lane)'.format(st.station_id, st.lanes), [ (det.name, det.lane, 'T' if dc(det) else 'F') for det in st.detectors] )
    #
    #     lane_shift_from = 'Right'
    #     shifted_lanes = 1
    #
    #     route.sub_routes[0].route_info.has_lane_shift= True
    #     route.sub_routes[0].route_info.shifted_lanes = shifted_lanes
    #     route.sub_routes[0].route_info.lane_shift_from = lane_shift_from
    #
    #     stations = [ rn for rn in route.sub_routes[0].route_info.rnodes if rn.is_station() ]
    #     dc = rh.get_detector_checker()
    #
    #     print('')
    #     print('Lane Shift Config : ', '{} lane(s) shifted from {}'.format(shifted_lanes, lane_shift_from) )
    #
    #     for st in stations:
    #         print('{} ({} lane)'.format(st.station_id, st.lanes), [ (det.name, det.lane, 'T' if dc(det) else 'F') for det in st.detectors] )
    #
    # def test_to_json(self):
    #     ih = self.infra.infra_helper
    #     rh = Route(self.infra, None)
    #     rh.route_data = rh.create_route_data('S179', 'S1080')
    #     route = rh.route_data
    #     from pyticas.tool import json
    #     print(json.dumps(route))

if __name__ == '__main__':
    unittest.main()
