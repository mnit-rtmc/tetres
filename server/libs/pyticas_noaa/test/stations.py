# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import csv
import datetime

class ISDStation(object):

    def __init__(self, row):
        """
        :type row: list[str]
        """
        self.usaf = None
        self.wban = None
        self.station_name = None
        self.city = None
        self.state = None
        self.icao = None
        self.lat = None
        self.lon = None
        self.elev = None
        self.begin = None
        self.end = None

        attrs = ['usaf', 'wban', 'station_name', 'city', 'state', 'icao', 'lat', 'lon', 'elev', 'begin', 'end']
        for idx, aname in enumerate(attrs):
            setattr(self, aname, row[idx])

    def get_date_range(self):
        """
        :rtype: (datetime.date, datetime.date)
        """
        return (datetime.datetime.strptime(self.begin, "%Y%m%d").date(),
                datetime.datetime.strptime(self.end, "%Y%m%d").date())

    def is_valid(self, dt):
        """

        :type dt: datetime.date
        :rtype: bool
        """
        begin, end = self.get_date_range()
        return (begin <= dt <= end)

    def __str__(self):
        return '<ISDStation usaf="%s" wban="%s" name="%s" begin="%s" end="%s">' % (
            self.usaf, self.wban, self.station_name, self.begin, self.end
        )

def load_isd_stations(filepath, state='MN', station_filter=None):
    """

    :type filepath: str
    :type state: str
    :type station_filter: function
    :rtype: list[ISDStation]
    """
    stations = []
    with open(filepath, 'r') as f:
        cr = csv.reader(f)
        for idx, row in enumerate(cr):
            if not idx:
                continue
            if row[4] != state:
                continue
            st = ISDStation(row)
            if not station_filter or station_filter(st):
                stations.append(st)
    return stations

DATA_FILE = 'isd-history.csv'

stations = load_isd_stations(DATA_FILE, 'MN', lambda st: st.is_valid(datetime.date(2017, 1, 31)))
for idx, st in enumerate(stations):
    print(idx, ':', st)