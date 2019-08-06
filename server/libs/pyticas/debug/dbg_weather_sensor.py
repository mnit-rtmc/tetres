# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import pprint
import unittest

from pyticas.dr import weather_sensor
from pyticas.dr.weather_sensor import WeatherSensor
from pyticas.ttypes import Period
from pyticas.test.base import TestPyTICAS


class TestWeatherDevice(TestPyTICAS):
    def test_weather_info(self):
        prd = Period(datetime.datetime(2015, 9, 9, 1, 0), datetime.datetime(2015, 9, 9, 23, 30), 60)
        wi = weather_sensor.get_weather(WeatherSensor.WS35W25.name, prd)
        pprint.pprint(list(zip(prd.get_timeline(), [wi.type_to_str(t) for t in wi.types], wi.rains)))

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
