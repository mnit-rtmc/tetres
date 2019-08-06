# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import unittest

from pyticas import route
from pyticas.logger import getLogger
from .base import TestPyTICAS

"""
Test Items
==========
  - geo.find_exit_to()
  - geo.opposite_rnodes()
  - geo.between_rnodes()
  - geo.iter_to_downstream()
  - geo.iter_to_upstream()

  - dms location
"""


class TestGeo(TestPyTICAS):

    def test_ext_to(self):
        logger = getLogger(__name__, to_console=True, loglevel='INFO')
        cases = [
            {'rnode': 'S430',  # US169 NB
             'corr': 'I-394 (EB)',
             'expected_ext': 'rnd_84811',
             'expected_ent': 'rnd_94380'},

            {'rnode': 'S1095',  # I-35 NB
             'corr': 'I-35E (NB)',
             'expected_ext': 'rnd_89591',
             'expected_ent': 'rnd_91017'},

            {'rnode': 'S1095',  # I-35 NB
             'corr': 'I-35W (NB)',
             'expected_ext': 'rnd_91013',
             'expected_ent': 'rnd_91015'},

            {'rnode': 'S838',  # I-35E NB
             'corr': 'I-94 (WB)',
             'expected_ext': 'rnd_87715',  # it is not exactly correct
             'expected_ent': 'rnd_90827'},

            {'rnode': 'S838',  # I-35E NB
             'corr': 'I-94 (EB)',
             'expected_ext': 'rnd_87715',
             'expected_ent': 'rnd_90821'},
        ]

        geo = self.infra.geo

        for cidx, case in enumerate(cases):
            # logger.info('CASE #%02d' % cidx)
            rn = self.infra.get_rnode(case['rnode'])
            corr = self.infra.get_corridor_by_name(case['corr'])
            (ext, ent) = geo.find_exit_to(rn, corr)
            # if ext:
            #     logger.info('  - ext=%s/%s, ent=%s/%s' % (ext.name, ext.label, ent.name, ent.label))
            self.assertIsNotNone(ext, 'Could not find connection to the given corridor')
            self.assertEqual(ext.name, case['expected_ext'])
            self.assertEqual(ent.name, case['expected_ent'])

    def test_opposite_rnodes_1on1(self):

        geo = self.infra.geo

        cases = [
            {'route': ('S338', 'S342'),
             'expected_rns': ['S338', None, 'rnd_90275', 'S339', 'S340', None, 'rnd_88429', 'S341',
                              'rnd_88435', 'S342'],
             'expected_orns': ['S276', 'rnd_94380', None, 'S275', None, 'S274', 'rnd_88267', 'S273',
                               'rnd_88261', 'S272']
             },
            {'route': ('S36', 'S40'),
             'expected_rns': ['S36', None, 'S37', 'rnd_86373', 'rnd_86377', 'S1702', 'S38', 'S39',
                              None, None, 'rnd_86381', 'rnd_86385', 'S1603', 'rnd_86389', 'S40'],
             'expected_orns': ['S31', 'S30', None, 'rnd_88045', 'rnd_88041', 'S1715', 'S29', 'S28', 'rnd_88035',
                               'rnd_88037', 'rnd_88033', 'rnd_88029', 'S1606', 'rnd_88027', None]
             }
        ]

        for cidx, case in enumerate(cases):
            r = route.create_route(case['route'][0], case['route'][1])
            (rns, orns) = geo.opposite_rnodes(r.rnodes, n_type='RNode')
            self.assertEqual(case['expected_rns'], self._res(rns))
            self.assertEqual(case['expected_orns'], self._res(orns))

    def test_between_rnodes(self):
        geo = self.infra.geo
        cases = [
            {'snode': 'S39',  # I-35W NB
             'enode': 'S41',
             'expected': ['rnd_86381', 'rnd_86385', 'S1603', 'rnd_86389', 'S40', 'rnd_86393', 'rnd_86395',
                          'rnd_86399']
             },
            {'snode': 'S1009',  # I-494 WB
             'enode': 'S486',
             'expected': ['rnd_84991', 'rnd_95825', 'S483', 'rnd_84995', 'rnd_89035', 'rnd_89039', 'S484',
                          'rnd_84997', 'S485', 'rnd_85001']
             },
        ]
        for case in cases:
            rn1 = self.infra.get_rnode(case['snode'])
            rn2 = self.infra.get_rnode(case['enode'])
            rnodes = geo.between_rnodes(rn1, rn2)
            self.assertEqual(self._res(rnodes), case['expected'])

            rnodes = [ rn for rn in geo.iter_to_downstream(rn1,
                                                           filter=lambda rn: rn.n_type,
                                                           break_filter=lambda rn: rn.station_id == case['enode']) ]
            self.assertEqual(self._res(rnodes), case['expected'])

            rnodes = [ rn for rn in geo.iter_to_upstream(rn2,
                                                         filter=lambda rn: rn.n_type,
                                                         break_filter=lambda rn: rn.station_id == case['snode']) ]
            self.assertEqual(self._res(rnodes), [ rn for rn in reversed(case['expected']) ])


    def test_nearby_entrance(self):
        geo = self.infra.geo
        cases = [
            {'ext' : 'rnd_1511',
             'corr' : 'U.S.169 (NB)',
             'expected' : 'rnd_89157'},
            {'ext' : 'rnd_1511',
             'corr' : 'U.S.169 (SB)',
             'expected' : 'rnd_1504'},
            {'ext' : 'rnd_1511',
             'corr' : 'T.H.100 (NB)',
             'expected' : None},

            {'ext' : 'rnd_89021',
             'corr' : 'T.H.100 (NB)',
             'expected' : 'rnd_90930'},

            {'ext' : 'rnd_87053',
             'corr' : 'T.H.100 (NB)',
             'expected' : 'rnd_90930'},
        ]
        for case in cases:
            ent = geo.find_nearby_entrance(self.infra.get_rnode(case['ext']),
                                           self.infra.get_corridor_by_name(case['corr']),
                                           d_limit=1)
            self.assertEqual(ent.name if ent else None, case['expected'])


    def _res(self, rnodes):
        res = []
        for rn in rnodes:
            if not rn:
                res.append(None)
            elif rn.is_station():
                res.append(rn.station_id)
            else:
                res.append(rn.name)
        return res

    def test_dms_location(self):
        s32 = self.infra.get_rnode('S32')
        self.assertEqual(s32.down_dmss[0].name, 'L35WN23')
        self.assertIn('L35WN22', [dms.name for dms in s32.up_dmss])
        self.assertIn('L35WN20', [dms.name for dms in s32.up_dmss])


if __name__ == '__main__':
    unittest.main()
