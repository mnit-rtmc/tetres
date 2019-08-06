# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import unittest
import traceback
import os
import sys
import logging

from pyticas import ticas
from pyticas.infra import Infra
from .base import TestPyTICAS

class TestRNodeInfo(TestPyTICAS):

    def test_rnode_info(self):
        """ test rnode information
        """

        """
        # Station 916 XML config

          <r_node name='rnd_88713' station_id='S916' label='Crystal Lake Rd' lon='-93.28301' lat='44.72992' lanes='3' shift='7' s_limit='70'>
            <detector name='3882' label='35/CrystlS1' lane='1' field='26.7' controller='ctl_60997'/>
            <detector name='T852' label='35/CrystlS1' lane='1'/>
            <detector name='3883' label='35/CrystlS2' lane='2' field='34.0' controller='ctl_60997'/>
            <detector name='T853' label='35/CrystlS2' lane='2'/>
            <detector name='3884' label='35/CrystlS3' lane='3' field='26.0' controller='ctl_60997'/>
            <detector name='T854' label='35/CrystlS3' lane='3'/>
          </r_node>
        """

        station = self.infra.get_rnode('S916')

        self.assertEqual(station.station_id, 'S916')
        self.assertEqual(station.lanes, 3)
        self.assertEqual(station.name, 'rnd_88713')
        self.assertEqual(station.label, 'Crystal Lake Rd')
        self.assertEqual(station.lon, -93.28301)
        self.assertEqual(station.lat, 44.72992)
        self.assertEqual(station.shift, 7)
        self.assertEqual(station.s_limit, 70)

        #self.assertEqual([ det.name for det in station.detectors], ['3882', 'T852', '3883', 'T853', '3884', 'T854'])
        self.assertEqual([ det.name for det in station.detectors], ['3882', '3883', '3884'])

        self.assertEqual(station.up_station.name, 'rnd_95427') # S1590
        self.assertEqual(station.down_station.name, 'rnd_88719') # S1097

        self.assertEqual(station.up_exit.name, 'rnd_94601')
        self.assertEqual(station.up_rnode.name, 'rnd_89593')
        self.assertEqual(station.up_entrance.name, 'rnd_89593')

        self.assertEqual(station.down_exit.name, 'rnd_88717')
        self.assertEqual(station.down_rnode.name, 'rnd_88715')
        self.assertEqual(station.down_entrance.name, 'rnd_88715')

        """
        # most downstream station of I-35 SB
          <r_node name='rnd_95214' station_id='S1584' label='210th St' lon='-93.29629' lat='44.64498' lanes='2' shift='6' s_limit='70'>
            <detector name='7034' label='35/210StS1' lane='1' field='25.5' controller='35-81.84'/>
            <detector name='T816' label='35/210StS1' lane='1'/>
            <detector name='7035' label='35/210StS2' lane='2' field='38.0' controller='35-81.84'/>
            <detector name='T817' label='35/210StS2' lane='2'/>
          </r_node>
        """
        station = self.infra.get_rnode('S1584')
        self.assertEqual(station.up_station.name, 'rnd_95019') # S1583
        self.assertEqual(station.down_station, None)

        self.assertEqual(station.up_exit.name, 'rnd_95031')
        self.assertEqual(station.up_rnode.name, 'rnd_95031')
        self.assertEqual(station.up_entrance.name, 'rnd_95043')

        self.assertEqual(station.down_exit, None)
        self.assertEqual(station.down_rnode.name, 'rnd_95766')
        self.assertEqual(station.down_entrance.name, 'rnd_95766')

        """
        # most upstream station of I-35 SB
          <r_node name='rnd_94573' station_id='S1520' label='Co Rd 22' lon='-93.00482' lat='45.33666' lanes='2' shift='6' s_limit='70'>
            <detector name='6660' label='35/CR22S1' lane='1' field='30.4' controller='ctl_0014'/>
            <detector name='6661' label='35/CR22S2' lane='2' field='24.5' controller='ctl_0014'/>
          </r_node>
        """
        station = self.infra.get_rnode('S1520')
        self.assertEqual(station.up_station, None)
        self.assertEqual(station.down_station.name, 'rnd_94583') # S1521

        self.assertEqual(station.up_exit.name, 'rnd_94569')
        self.assertEqual(station.up_rnode.name, 'rnd_94569')
        self.assertEqual(station.up_entrance, None)

        self.assertEqual(station.down_exit.name, 'rnd_94571')
        self.assertEqual(station.down_rnode.name, 'rnd_94597')
        self.assertEqual(station.down_entrance.name, 'rnd_94597')


if __name__ == '__main__':
    unittest.main()