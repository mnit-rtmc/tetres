# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import re
import datetime
import math

PRECIP_TYPES = {
    0 : 'No Precip',
    1 : 'Drizzle',
    2 : 'Rain',
    3 : 'Snow',
    4 : 'Snow Grains',
    5 : 'Ice Crystals',
    6 : 'Ice Pellets',
    7 : 'Hail',
    8 : 'Small Hail and/or Snow Pellets',
    9 : 'Unknown',
    99 : 'Missing'
}

INTENSITY_TYPES = {
    0 : "Not Reported",
    1 : "Light",
    2 : "Moderate or Not Reported",
    3 : "Heavy",
    4 : "Vicinity",
    9 : "Missing",
}

OBSCURATION_CODE = {
    0 : "No Obscuration",
    1 : "Mist",
    2 : "Fog",
    3 : "Smoke",
    4 : "Volcanic Ash",
    5 : "Widespread Dust",
    6 : "Sand",
    7 : "Haze",
    8 : "Spray",
    9 : "Missing"
}

DISCRIPTOR_CODE = {
    0 : "No Descriptor",
    1 : "Shallow",
    2 : "Partial",
    3 : "Patches",
    4 : "Low Drifting",
    5 : "Blowing",
    6 : "Shower(s)",
    7 : "Thunderstorm",
    8 : "Freezing",
    9 : "Missing"
}

QUALITY_CODE = {
    0 : "Passed gross limits check",
    1 : "Passed all quality control checks",
    2 : "Suspect",
    3 : "Erroneous",
    4 : "Passed gross limits check , data originate from an NCEI data source",
    5 : "Passed all quality control checks, data originate from an NCEI data source",
    6 : "Suspect, data originate from an NCEI data source",
    7 : "Erroneous, data originate from an NCEI data source",
    9 : "Passed gross limits check if element is present   ",
    "A" : "Data value flagged as suspect, but accepted as good value",
    "I" : "Data value not originally in data, but inserted by validator",
    "M" : "Manual change made to value based on information provided by NWS or FAA",
    "P" : "Data value not originally flagged as suspect, but replaced by validator",
    "R" : "Data value replaced with value computed by NCEI software",
    "U" : "Data value replaced with edited value",
    "C" : "Temperature and dew point received from Automated Weather Observing System (AWOS) are reported in whole degrees Celsius. Automated QC flags these values, but they are accepted as valid.",
}

class QLCDStation(object):

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
        self.begin = datetime.datetime.strptime(self.begin, '%Y%m%d').date()
        self.end = datetime.datetime.strptime(self.end, '%Y%m%d').date()

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

