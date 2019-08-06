# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import os
import unittest

from pyticas.debug.base import TestPyTICAS
from pyticas.rn import temp_detector_loader
from pyticas.tool import pygmaps


class TestTempDetLoader(TestPyTICAS):

    def test_load_temp_detectors(self):
        coordinate_based_file = os.path.join(self.data_path, 'temp_detectors', 'coordinate_based.csv')
        existing_detector_based_file = os.path.join(self.data_path, 'temp_detectors', 'existing_detector_based.csv')

        temp_detector_loader.import_coordinate_based(self.infra, coordinate_based_file)
        temp_detector_loader.import_existing_detector_based(self.infra, existing_detector_based_file)

        cases = [
            {'rnode': 'rnd_300011',
             'rnode_index': 5,
             'station_index': 5},

            {'rnode': 'rnd_300034',
             'rnode_index': 11,
             'station_index': 8},

            {'rnode': 'rnd_300084',
             'rnode_index': 4,
             'station_index': 1},

            {'rnode': 'rnd_300101',
             'rnode_index': 121,
             'station_index': 59},

            {'rnode': 'rnd_300120',
             'rnode_index': 58,
             'station_index': 32},

            {'rnode': 'rnd_300146',
             'rnode_index': 3,
             'station_index': 1},
        ]

        for case in cases:

            tmp_station = self.infra.get_rnode(case['rnode'])

            # for debug
            # print('=> ', tmp_station.station_id, tmp_station.corridor.rnodes.index(tmp_station))
            # print('=> ', tmp_station.station_id, tmp_station.corridor.stations.index(tmp_station))

            # checking manually to make `cases`
            # self._write_map(tmp_station, tmp_station.corridor.stations,
            #                 os.path.join(self.data_path, '%s-stations.html' % tmp_station.station_id))
            # self._write_map(tmp_station, tmp_station.corridor.rnodes,
            #                 os.path.join(self.data_path, '%s-rnodes.html' % tmp_station.station_id))

            self.assertEqual(case['rnode_index'], tmp_station.corridor.rnodes.index(tmp_station))
            self.assertEqual(case['station_index'], tmp_station.corridor.stations.index(tmp_station))

            # check up-down rnode/station/entrance/exit
            if tmp_station.down_rnode:
                self.assertEqual(tmp_station, tmp_station.down_rnode.up_rnode)
                self.assertEqual(tmp_station, tmp_station.down_rnode.up_station)
            if tmp_station.up_rnode:
                self.assertEqual(tmp_station, tmp_station.up_rnode.down_rnode)
                self.assertEqual(tmp_station, tmp_station.up_rnode.down_station)

            if tmp_station.down_station:
                self.assertEqual(tmp_station, tmp_station.down_station.up_station)
            if tmp_station.up_station:
                self.assertEqual(tmp_station, tmp_station.up_station.down_station)

            if tmp_station.down_entrance:
                self.assertEqual(tmp_station, tmp_station.down_entrance.up_station)
            if tmp_station.up_entrance:
                self.assertEqual(tmp_station, tmp_station.up_entrance.down_station)

            if tmp_station.down_exit:
                self.assertEqual(tmp_station, tmp_station.down_exit.up_station)
            if tmp_station.up_exit:
                self.assertEqual(tmp_station, tmp_station.up_exit.down_station)

    def _write_map(self, target_rnode, rnodes, file_path):
        """

        :type target_rnode: pyticas.ttypes.RNodeObject
        :type rnodes: list[pyticas.ttypes.RNodeObject]
        :type file_path: str
        :return:
        """
        init_lat = 44.974878
        init_lon = -93.233414

        mymap = pygmaps.maps(init_lat, init_lon, 10)

        for idx, rn in enumerate(rnodes):
            if rn.name == target_rnode.name:
                mymap.addpoint(target_rnode.lat, target_rnode.lon, "#FF0000",
                               '[%03d] Temp Station: %s' % (idx, target_rnode.station_id))
                continue
            mymap.addpoint(rn.lat, rn.lon, "#0000FF",
                           '[%03d] %s' % (idx, rn.station_id if rn.is_station() else rn.name))
        mymap.draw(file_path)

    def test_find_updn(self):
        cases = [{'corr': 'U.S.169 (NB)',
                  'expected_down': 'rnd_1557',
                  'expected_up': 'rnd_9',
                  'lat': 44.782978,
                  'lon': -93.430815,
                  'rnode_name': 'rnd_300011'},
                 {'corr': 'I-35 (NB)',
                  'expected_down': 'rnd_95021',
                  'expected_up': 'rnd_95210',
                  'lat': 44.646472,
                  'lon': -93.295386,
                  'rnode_name': 'rnd_300031'},
                 {'corr': 'I-35 (NB)',
                  'expected_down': 'rnd_95039',
                  'expected_up': 'rnd_95021',
                  'lat': 44.653025,
                  'lon': -93.29441,
                  'rnode_name': 'rnd_300032'},
                 {'corr': 'I-35 (NB)',
                  'expected_down': 'rnd_95027',
                  'expected_up': 'rnd_95023',
                  'lat': 44.658239,
                  'lon': -93.293567,
                  'rnode_name': 'rnd_300033'},
                 {'corr': 'I-35 (NB)',
                  'expected_down': 'rnd_95027',
                  'expected_up': 'rnd_95023',
                  'lat': 44.6603032,
                  'lon': -93.293565,
                  'rnode_name': 'rnd_300034'},
                 {'corr': 'I-35 (NB)',
                  'expected_down': 'rnd_1650',
                  'expected_up': 'rnd_95027',
                  'lat': 44.670277,
                  'lon': -93.293837,
                  'rnode_name': 'rnd_300035'},
                 {'corr': 'I-35 (NB)',
                  'expected_down': 'rnd_95025',
                  'expected_up': 'rnd_1650',
                  'lat': 44.674883,
                  'lon': -93.293475,
                  'rnode_name': 'rnd_300036'},
                 {'corr': 'I-35 (SB)',
                  'expected_down': 'rnd_95214',
                  'expected_up': 'rnd_95031',
                  'lat': 44.646472,
                  'lon': -93.295386,
                  'rnode_name': 'rnd_300067'},
                 {'corr': 'I-694 (EB)',
                  'expected_down': 'rnd_87061',
                  'expected_up': 'rnd_87059',
                  'lat': 45.069333,
                  'lon': -93.296957,
                  'rnode_name': 'rnd_300084'},
                 {'corr': 'I-694 (EB)',
                  'expected_down': 'rnd_87067',
                  'expected_up': 'rnd_87065',
                  'lat': 45.069402,
                  'lon': -93.288144,
                  'rnode_name': 'rnd_300085'},
                 {'corr': 'I-694 (WB)',
                  'expected_down': 'rnd_1813',
                  'expected_up': 'rnd_87199',
                  'lat': 45.069402,
                  'lon': -93.288144,
                  'rnode_name': 'rnd_300101'},
                 {'corr': 'I-35E (SB)',
                  'expected_down': 'rnd_85855',
                  'expected_up': 'rnd_85853',
                  'lat': 44.994065,
                  'lon': -93.090031,
                  'rnode_name': 'rnd_300120'},
                 {'corr': 'I-35E (SB)',
                  'expected_down': 'rnd_248',
                  'expected_up': 'rnd_85993',
                  'lat': 44.74091,
                  'lon': -93.28186,
                  'rnode_name': 'rnd_300134'},
                 {'corr': 'I-35E (NB)',
                  'expected_down': 'rnd_87575',
                  'expected_up': 'rnd_221',
                  'lat': 44.74091,
                  'lon': -93.28186,
                  'rnode_name': 'rnd_300146'}]

        for case in cases:
            up_rnode, dn_rnode = self.infra.geo.find_updown_rnodes(case['lat'], case['lon'],
                                                                   self.infra.get_corridor_by_name(case['corr']).rnodes)

            self.assertEqual(case['expected_up'], up_rnode.name)
            self.assertEqual(case['expected_down'], dn_rnode.name)

            # for debug
            #
            # if up_rnode and dn_rnode:
            #     print('=> corr=%s, station=%s, (%f, %f), up_rnode=(%s, %f, %f), down_rnode=(%s, %f, %f)' %
            #           (case['corr'], case['rnode_name'], case['lat'], case['lon'], up_rnode.name, up_rnode.lat,
            #            up_rnode.lon, dn_rnode.name,
            #            dn_rnode.lat, dn_rnode.lon))
            # elif up_rnode:
            #     print('=> corr=%s, station=%s, (%f, %f), up_rnode=(%s, %f, %f), down_rnode=None' %
            #           (case['corr'], case['rnode_name'], case['lat'], case['lon'], up_rnode.name, up_rnode.lat,
            #            up_rnode.lon))
            # elif dn_rnode:
            #     print('=> corr=%s, station=%s, (%f, %f), up_rnode=None, down_rnode=(%s, %f, %f)' %
            #           (case['corr'], case['rnode_name'], case['lat'], case['lon'], dn_rnode.name, dn_rnode.lat,
            #            dn_rnode.lon))
            # else:
            #     print('=> corr=%s, station=%s, (%f, %f), up_rnode=None, down_rnode=None' %
            #           (case['corr'], case['rnode_name'], case['lat'], case['lon']))


if __name__ == '__main__':
    unittest.main()
