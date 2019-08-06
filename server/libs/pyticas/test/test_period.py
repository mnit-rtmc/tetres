# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import unittest

from pyticas import ttypes
from pyticas import period as ph


class TestPeriod(unittest.TestCase):

    def test_period(self):

        prd = ph.create_period((2015, 9, 1, 7, 0), (2015, 9, 1, 10, 0), 30)
        prd2 = ph.create_period_from_string('2015-09-01 07:00:00', '2015-09-01 10:00:00', 30)
        prd3 = ph.create_period_with_duration((2015, 9, 1, 7, 0), 3*60, 30)
        self.assertEqual(str(prd), str(prd2))
        self.assertEqual(str(prd2), str(prd3))

        prd4 = ph.create_period((2015, 9, 1, 6, 0), (2015, 9, 1, 10, 0), 30)
        prd.extend_start_hour(1)
        self.assertEqual(str(prd4), str(prd))

        prd5 = ph.create_period((2015, 9, 1, 6, 0), (2015, 9, 1, 13, 0), 30)
        prd.extend_end_hour(3)
        self.assertEqual(str(prd5), str(prd))

        prd6 = prd.clone()
        self.assertEqual(str(prd6), str(prd))

        prd7 = ph.create_period((2015, 9, 1, 6, 1), (2015, 9, 1, 6, 2), 30)
        prd8 = prd.clone().shrink(2, 4)
        self.assertEqual(str(prd7), str(prd8))

        prd9 = ph.create_period((2015, 9, 1, 6, 0), (2015, 9, 5, 6, 0), 30)
        prd92 = ph.create_period((2015, 9, 1, 6, 0), (2015, 9, 5, 6, 0), 30)
        self.assertEqual(prd9.days(), 5)
        self.assertEqual(prd9.days(), len(prd9.get_dates()))
        self.assertEqual(str(prd9), str(prd92))

        holidays = {
            2013 : [ datetime.date(2013, 1, 1), # New Years Day
                     datetime.date(2013, 1, 21), # Martin Luther King Day
                     datetime.date(2013, 2, 18), # Presidents Day
                     datetime.date(2013, 5, 27), # Memorial Day
                     datetime.date(2013, 7, 4), # Independence Day (observed)
                     datetime.date(2013, 9, 2), # Labor Day
                     datetime.date(2013, 10, 14), # Columbus Day
                     datetime.date(2013, 11, 11), # Veterans Day
                     datetime.date(2013, 11, 28), # thanks giving
                     datetime.date(2013, 11, 29), # day after thanks giving
                     datetime.date(2013, 12, 24), # christmas eve
                     datetime.date(2013, 12, 25), # christmas
                     ],
            2014 : [ datetime.date(2014, 1, 1), # New Years Day
                     datetime.date(2014, 1, 20), # Martin Luther King Day
                     datetime.date(2014, 2, 17), # Presidents Day
                     datetime.date(2014, 5, 26), # Memorial Day
                     datetime.date(2014, 7, 4), # Independence Day (observed)
                     datetime.date(2014, 9, 1), # Labor Day
                     datetime.date(2014, 10, 13), # Columbus Day
                     datetime.date(2014, 11, 11), # Veterans Day
                     datetime.date(2014, 11, 27), # thanks giving
                     datetime.date(2014, 11, 28), # day after thanks giving
                     datetime.date(2014, 12, 24), # christmas eve
                     datetime.date(2014, 12, 25), # christmas
                     ],
            2015 : [ datetime.date(2015, 1, 1), # New Years Day
                     datetime.date(2015, 1, 19), # Martin Luther King Day
                     datetime.date(2015, 2, 16), # Presidents Day
                     datetime.date(2015, 5, 25), # Memorial Day
                     datetime.date(2015, 7, 3), # Independence Day (observed)
                     datetime.date(2015, 9, 7), # Labor Day
                     datetime.date(2015, 10, 12), # Columbus Day
                     datetime.date(2015, 11, 11), # Veterans Day
                     datetime.date(2015, 11, 26), # thanks giving
                     datetime.date(2015, 11, 27), # day after thanks giving
                     datetime.date(2015, 12, 24), # christmas eve
                     datetime.date(2015, 12, 25), # christmas
                     ]
        }
        for y, dates in holidays.items():
            res = ph.get_holidays(y)
            self.assertEqual(len(res), len(dates))
            bools = [ res[idx]['date'] == dates[idx] for idx, _v in enumerate(res) ]
            self.assertTrue((False not in bools))

        self.assertTrue(ph.is_holiday(datetime.date(2013, 5, 27)))
        self.assertTrue(ph.is_holiday(datetime.date(2014, 10, 13)))
        self.assertTrue(ph.is_holiday(datetime.date(2015, 9, 7)))

if __name__ == '__main__':
    unittest.main()
