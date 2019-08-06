# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from datetime import datetime

cases = [
    {
        'site_id' : 330087,
        'start_time' : datetime(2015, 9, 1, 7, 0, 0),
        'end_time' : datetime(2015, 9, 1, 7, 30, 0),
        'DateTime' : ['2015-09-01 07:30:00', '2015-09-01 07:25:00', '2015-09-01 07:20:00', '2015-09-01 07:15:00', '2015-09-01 07:10:00', '2015-09-01 07:05:00'],
        'SfStat' : ['Dry', 'Dry', 'Dry', 'Dry', 'Dry', 'Dry'],
        'SfTemp' : [74.5, 74.3,73.8,73.4,73.2,73],
        'PvtTemp' : ['', '', '', '', '', ],
        'SubTemp' : [80,80,80,80,80,80],
        'AirTemp' : [70,70,70,70,69,69],
        'RH' : [92,93,94,94,94,94],
        'Dewpoint' : [68,68,68,68,68,68],
        'AvgWindSpeed' : [4,4,4,4,4,3],
        'GustWindSpeed' : [6,6,7,7,6,6],
        'WindDirection' : ['SE', 'SE', 'SE', 'SE', 'SE', 'SE'],
        'PrecipType' : [None, None, None, None, None, None],
        'PrecipIntenisity' : [None, None, None, None, None, None],
    },
]