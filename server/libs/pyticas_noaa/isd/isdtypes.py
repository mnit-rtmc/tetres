# -*- coding: utf-8 -*-

import calendar
import datetime
import math
import re

from pyticas.ttypes import AttrDict

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

PRECIP_TYPES = {
    0: 'No Precip',
    1: 'Drizzle',
    2: 'Rain',
    3: 'Snow',
    4: 'Snow Grains',
    5: 'Ice Crystals',
    6: 'Ice Pellets',
    7: 'Hail',
    8: 'Small Hail and/or Snow Pellets',
    9: 'Unknown',
    99: 'Missing'
}

INTENSITY_TYPES = {
    0: "Not Reported",
    1: "Light",
    2: "Moderate or Not Reported",
    3: "Heavy",
    4: "Vicinity",
    9: "Missing",
}

OBSCURATION_CODE = {
    0: "No Obscuration",
    1: "Mist",
    2: "Fog",
    3: "Smoke",
    4: "Volcanic Ash",
    5: "Widespread Dust",
    6: "Sand",
    7: "Haze",
    8: "Spray",
    9: "Missing",
}

DISCRIPTOR_CODE = {
    0: "No Descriptor",
    1: "Shallow",
    2: "Partial",
    3: "Patches",
    4: "Low Drifting",
    5: "Blowing",
    6: "Shower(s)",
    7: "Thunderstorm",
    8: "Freezing",
    9: "Missing",
}

QUALITY_CODE = {
    0: "Passed gross limits check",
    1: "Passed all quality control checks",
    2: "Suspect",
    3: "Erroneous",
    4: "Passed gross limits check , data originate from an NCEI data source",
    5: "Passed all quality control checks, data originate from an NCEI data source",
    6: "Suspect, data originate from an NCEI data source",
    7: "Erroneous, data originate from an NCEI data source",
    9: "Passed gross limits check if element is present   ",
    "A": "Data value flagged as suspect, but accepted as good value",
    "I": "Data value not originally in data, but inserted by validator",
    "M": "Manual change made to value based on information provided by NWS or FAA",
    "P": "Data value not originally flagged as suspect, but replaced by validator",
    "R": "Data value replaced with value computed by NCEI software",
    "U": "Data value replaced with edited value",
    "C": "Temperature and dew point received from Automated Weather Observing System (AWOS) are reported in whole degrees Celsius. Automated QC flags these values, but they are accepted as valid.",
}


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
        return '<ISDStation usaf="%s" wban="%s" name="%s" begin="%s" end="%s" lat="%s" lon="%s">' % (
            self.usaf, self.wban, self.station_name, self.begin, self.end, self.lat, self.lon
        )


class ISDField(object):
    fields = ()

    def parse(self, text, offset=0):
        """

        :type text: str
        :type offset: int
        :rtype: pyticas.ttypes.AttrDict
        """
        result = AttrDict()
        cur_offset = offset
        for field_name, field_len in self.fields:
            if isinstance(field_len, str):
                ref_vals = [fl for fn, fl in self.fields if fn == field_len]
                if ref_vals:
                    next_offset = cur_offset + ref_vals[0]
                else:
                    raise Exception('!! reference-field error : %s' % field_len)
            else:
                next_offset = cur_offset + field_len

            v = text[cur_offset:next_offset]
            if v.replace('.', '', 1).isdigit():
                if '.' in v:
                    v = float(v)
                else:
                    v = int(v)
            cur_offset = next_offset
            result[field_name] = v

        return result

    def total_field_length(self):
        """
        :rtype: int
        """
        return sum([fl for fn, fl in self.fields])


class ISDAdditionalData(ISDField):
    tag_pattern = ''

    def parse(self, text):
        """
        :type text: str
        :rtype: list[AttrDict]
        """
        res = []
        offsets = self.start_positions(text)
        for offset in offsets:
            res.append(super().parse(text, offset))
        return res

    def start_positions(self, line):
        """

        :type line: str
        :rtype: list[int]
        """
        offsets = []
        for m in re.finditer(self.tag_pattern, line):
            offsets.append(m.start())
        return offsets


"""
Control Data Section
"""


class CDS(ISDField):
    fields = (
        # control data section
        ('total_variable_chars', 4),
        ('station_usaf_id', 6),
        ('station_wban_id', 5),
        ('geophysical_point_observation_year', 4),  # yyyy
        ('geophysical_point_observation_month', 2),  # mm
        ('geophysical_point_observation_day', 2),  # dd
        ('geophysical_point_observation_hour', 2),  # HH
        ('geophysical_point_observation_minute', 2),  # MM
        ('geophysical_point_observation_data_source_flag', 1),
        ('geophysical_point_observation_lat', 6),
        ('geophysical_point_observation_lon', 7),
        ('geophysical_report_type', 5),
        ('geophysical_point_observation_elevation_dimension', 5),
        ('fixed_weather_station_call_letter_id', 5),
        ('meteorological_point_observation_quality_control_process_name', 4),
    )


"""
Mandatory Data Section
"""


class MDS(ISDField):
    fields = (
        # mandatory data section
        ('wind_observation_direction_angle', 3),
        ('wind_observation_direction_quality_code', 1),
        ('wind_observation_direction_type_code', 1),
        ('wind_observation_speed_rate', 4),
        ('wind_observation_speed_quality_code', 1),
        ('sky_condition_observation_ceiling_height_dimension', 5),
        ('sky_condition_observation_ceiling_quality_code', 1),
        ('sky_condition_observation_ceiling_determination_code', 1),
        ('sky_condition_observation_cavok_code', 1),
        ('visibility_observation_distance_dimension', 6),
        ('visibility_observation_quality_code', 1),
        ('visibility_observation_variability_code', 1),
        ('visibility_observation_quality_variability_code', 1),
        ('air_temperature_observation_air_temperature', 5),
        ('air_temperature_observation_air_temperature_quality_code', 1),
        ('air_temperature_observation_dew_point_temperature', 5),
        ('air_temperature_observation_dew_point_quality_code', 1),
        ('atmospheric_pressure_observation_sea_level_pressure', 5),
        ('atmospheric_pressure_observation_sea_level_pressure_quality_code', 1),
    )


"""
Remarks Data Section
"""


class RDS(ISDAdditionalData):
    tag_pattern = r'(REM[a-zA-Z]{3}[\d]{3})'
    fields = (
        ('geophysical_point_observation_remark_tag', 3),  # for "REM"
        ('geophysical_point_observation_remark_id', 3),
        ('geophysical_point_observation_remark_length_quantity', 3),
        ('data', 'geophysical_point_observation_remark_length_quantity')
    )


"""
Element Quality Data Section
"""


class EQDS(ISDAdditionalData):
    tag_pattern = r'(EQD[\w]{3})'
    fields = (
        ('geophysical_point_observation_quality_data_id', 3),  # for "EQD"
        ('original_observation_element_quality_id', 3),
        ('original_observation_element_quality_original_value_text', 6),
        ('original_observation_element_quality_reason_code', 1),
        ('original_observation_element_quality_parameter_code', 6),
    )


"""
Liquid Precipitation Data (AA1-AA4)
"""


class ISD_AA(ISDAdditionalData):
    tag_pattern = r'(AA[\d][\w]{8})'
    fields = (
        ('liquid_precipitation_occurrence_id', 3),  # for "AA1-AA4"
        ('liquid_precipitation_period_quantity_in_hours', 2),
        ('liquid_precipitation_depth_dimension', 4),
        ('liquid_precipitation_condition_code', 1),
        ('liquid_precipitation_quality_code', 1),
    )


"""
Present Weather Observation Data (AU1-AU9)
"""


class ISD_AU(ISDAdditionalData):
    tag_pattern = r'(AU[\d][\w])'
    fields = (
        ('present_weather_observation_id', 3),  # for "AU1-AU9"
        ('present_weather_observation_intensity_code', 1),
        ('present_weather_observation_descriptor_code', 1),
        ('present_weather_observation_precipitation_code', 2),
        ('present_weather_observation_obscuration_code', 1),
        ('present_weather_observation_other_weather_phenomena_code', 1),
        ('present_weather_observation_combination_indicator_code', 1),
        ('present_weather_observation_quality_code', 1),
    )


"""
Present Estimated Observation Data (AU1-AU9)
"""


class ISD_AG(ISDAdditionalData):
    tag_pattern = r'(AG[\d][\w])'
    fields = (
        ('precipitation_estimated_observation_id', 3),  # for "AG1"
        ('precipitation_estimated_observation_discrepancy_code', 1),
        ('precipitation_estimated_observation_estimated_water_depth_dimension', 3),  # in millimeter
    )


"""
Liquid Precipitation Data (AO1-AO4)
"""


class ISD_AO(ISDAdditionalData):
    tag_pattern = r'(AO[\d][\w])'
    fields = (
        ('liquid_precipitation_occurrence_id', 3),  # for "AO1"
        ('liquid_precipitation_period_quantity_in_minutes', 2),
        ('liquid_precipitation_depth_dimension', 4),  # scaling factor = 10, unit=millimeter
        ('liquid_precipitation_condition_code', 1),
        ('liquid_precipitation_quality_code', 1),
    )


"""
Present Weather Observation Data (AW1-AW4)
"""


class ISD_AW(ISDAdditionalData):
    tag_pattern = r'(AW[\d][\w])'
    fields = (
        ('present_weather_observation_automated_occurrence_id', 3),  # for "AW1-AW4"
        ('present_weather_observation_automated_atmospheric_condition_code', 2),
        ('present_weather_observation_quality_automated_atmospheric_condition_code', 1),
    )


"""
Wind Gust Observation Data (OC1)
"""


class ISD_OC(ISDAdditionalData):
    tag_pattern = r'(OC[\d])'
    fields = (
        ('tag', 3),  # for "GA1-GA6"
        ('speed_rate', 4),
        ('quality_code', 1),
    )


class ISDRawData(object):
    def __init__(self, cds_data, mds_data, aa_data_list, au_data_list, oc_data_list):
        aa_data = aa_data_list[0] if any(aa_data_list) else {}
        au_data = au_data_list[0] if any(au_data_list) else {}
        oc_data = oc_data_list[0] if any(oc_data_list) else {}

        dt_string = '%04d-%02d-%02d %02d:%02d:00' % (
            cds_data.geophysical_point_observation_year,
            cds_data.geophysical_point_observation_month,
            cds_data.geophysical_point_observation_day,
            cds_data.geophysical_point_observation_hour,
            cds_data.geophysical_point_observation_minute,
        )

        dt_local = self.utc_2_local(dt_string)  # unaware-timezone

        self.dt = dt_local
        """:type: datetime.datetime """

        self.report_type = cds_data.get('geophysical_report_type', '99999')
        """
        :type: str(5)
        ""GEOPHYSICAL-REPORT-TYPE code""
        The code that denotes the type of geophysical surface observation.
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - AERO = Aerological report
                - AUST = Dataset from Australia
                - AUTO = Report from an automatic station
                - BOGUS = Bogus report
                - BRAZ = Dataset from Brazil
                - COOPD = US Cooperative Network summary of day report
                - COOPS = US Cooperative Network soil temperature report
                - CRB = Climate Reference Book data from CDMP
                - CRN05 = Climate Reference Network report, with 5-minute reporting interval
                - CRN15 = Climate Reference Network report, with 15-minute reporting interval
                - FM-12 = SYNOP Report of surface observation form a fixed land station
                - FM-13 = SHIP Report of surface observation from a sea station
                - FM-14 = SYNOP MOBIL Report of surface observation from a mobile land station
                - FM-15 = METAR Aviation routine weather report
                - FM-16 = SPECI Aviation selected special weather report
                - FM-18 = BUOY Report of a buoy observation
                - GREEN = Dataset from Greenland
                - MESOH – Hydrological observations from MESONET operated civilian or government agency
                - MESOS – MESONET operated civilian or government agency
                - MESOW – Snow observations from MESONET operated civilian or government agency
                - MEXIC = Dataset from Mexico
                - NSRDB = National Solar Radiation Data Base
                - PCP15 = US 15-minute precipitation network report
                - PCP60 = US 60-minute precipitation network report
                - S-S-A = Synoptic, airways, and auto merged report
                - SA-AU = Airways and auto merged report
                - SAO = Airways report (includes record specials)
                - SAOSP = Airways special report (excluding record specials)
                - SHEF – Standard Hydrologic Exchange Format
                - SMARS = Supplementary airways station report
                - SOD = Summary of day report from U.S. ASOS or AWOS station
                - SOM = Summary of month report from U.S. ASOS or AWOS station
                - SURF = Surface Radiation Network report
                - SY-AE = Synoptic and aero merged report
                - SY-AU = Synoptic and auto merged report
                - SY-MT = Synoptic and METAR merged report
                - SY-SA = Synoptic and airways merged report
                - WBO = Weather Bureau Office
                - WNO = Washington Naval Observatory
                - 99999 = Missing

        """

        self.precipitation = aa_data.get('liquid_precipitation_depth_dimension', 9999)
        """
        **LIQUID-PRECIPITATION depth dimension**
        The depth of LIQUID-PRECIPITATION that is measured at the time of an observation.
            - MIN:  0000
            - MAX:  9998
            - UNITS:  millimeters
            - SCALING FACTOR: 10
            - DOM:  A general domain comprised of the numeric characters (0 9).
                - 9999 = Missing.
        """
        self.precipitation_condition = aa_data.get('liquid_precipitation_condition_code', 9)
        """
        **LIQUID-PRECIPITATION condition code**
        The code that denotes whether a LIQUID-PRECIPITATION depth dimension was a trace value.
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 1: Measurement impossible or inaccurate
                - 2: Trace
                - 3: Begin accumulated period (precipitation amount missing until end of accumulated period)
                - 4: End accumulated period
                - 5: Begin deleted period (precipitation amount missing due to data problem)
                - 6: End deleted period
                - 7: Begin missing period
                - 8: End missing period
                - E: Estimated data value (eg, from nearby station)
                - I:  Incomplete precipitation amount, excludes one or more missing reports, such as one or more 15-minute                                              reports not included in the 1-hour precipitation total
                - J:  Incomplete precipitation amount, excludes one or more erroneous reports, such as one or more 1-hour                                               precipitation amounts excluded from the 24-hour total
                - 9: Missing
        """
        self.precipitation_qc = aa_data.get('liquid_precipitation_quality_code', 3)
        """
        **LIQUID-PRECIPITATION quality code**
        The code that denotes a quality status of the reported LIQUID-PRECIPITATION data.
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = Passed gross limits check
                - 1 = Passed all quality control checks
                - 2 = Suspect
                - 3 = Erroneous
                - 4 = Passed gross limits check , data originate from an NCEI data source
                - 5 = Passed all quality control checks, data originate from an NCEI data source
                - 6 = Suspect, data originate from an NCEI data source
                - 7 = Erroneous, data originate from an NCEI data source
                - 9 = Passed gross limits check if element is present
                - A = Data value flagged as suspect, but accepted as good value
                - I = Data value not originally in data, but inserted by validator
                - M = Manual change made to value based on information provided by NWS or FAA
                - P = Data value not originally flagged as suspect, but replaced by validator
                - R = Data value replaced with value computed by NCEI software
                - U = Data value replaced with edited value
        """

        self.precipitation_quantity_in_hours = aa_data.get('liquid_precipitation_period_quantity_in_hours', 99)
        """
        **LIQUID-PRECIPITATION period quantity in hours**
        The quantity of time over which the LIQUID-PRECIPITATION was measured.
            - MIN:  00
            - MAX:  98
            - UNITS:  Hours
            - SCALING FACTOR:  1
            - DOM:  A specific domain comprised of the characters in the ASCII character set
                - 99 = Missing.
        """

        self.intensity = au_data.get('present_weather_observation_intensity_code', 9)
        """
        **PRESENT-WEATHER-OBSERVATION intensity and proximity code**
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = Not Reported
                - 1 = Light (-)
                - 2 = Moderate or Not Reported (no entry in original observation)
                - 3 = Heavy (+)
                - 4 = Vicinity (VC)
                - 9 = Missing
        """

        self.precipitation_code = au_data.get('present_weather_observation_precipitation_code', 99)
        """
        **PRESENT-WEATHER-OBSERVATION precipitation code**
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 00 = No Precipitation
                - 01 = Drizzle (DZ)
                - 02 = Rain (RA)
                - 03 = Snow (SN)
                - 04 = Snow Grains (SG)
                - 05 = Ice Crystals (IC)
                - 06 = Ice Pellets (PL)
                - 07 = Hail (GR)
                - 08 = Small Hail and/or Snow Pellets (GS)
                - 09 = Unknown Precipitation (UP)
                - 99 = Missing
        """

        self.obscuration_code = au_data.get('present_weather_observation_obscuration_code', 9)
        """
        PRESENT-WEATHER-OBSERVATION obscuration code
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = No Obscuration
                - 1 = Mist (BR)
                - 2 = Fog (FG)
                - 3 = Smoke (FU)
                - 4 = Volcanic Ash (VA)
                - 5 = Widespread Dust (DU)
                - 6 = Sand (SA)
                - 7 = Haze (HZ)
                - 8 = Spray (PY)
                - 9 = Missing
        """

        self.descriptor = au_data.get('present_weather_observation_descriptor_code', 9)
        """
        PRESENT-WEATHER-OBSERVATION descriptor code
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = No Descriptor
                - 1 = Shallow (MI)
                - 2 = Partial (PR)
                - 3 = Patches (BC)
                - 4 = Low Drifting (DR)
                - 5 = Blowing (BL)
                - 6 = Shower(s) (SH)
                - 7 = Thunderstorm (TS)
                - 8 = Freezing (FZ)
                - 9 = Missing
        """

        self.visibility = mds_data.get('visibility_observation_distance_dimension', 999999)  # in meters
        """
        :type: int
        **VISIBILITY-OBSERVATION distance dimension**
        The horizontal distance at which an object can be seen and identified.
            - MIN:  000000
            - MAX:  160000
            - UNITS:  Meters
            - DOM:  A general domain comprised of the numeric characters (0 9).
                - Missing = 999999
            - NOTE:  Values greater than 160000 are entered as 160000
        """

        self.visibility_qc = mds_data.get('visibility_observation_quality_code', 3)
        """
        :type: int
        **VISIBILITY-OBSERVATION distance quality code**
        The code that denotes a quality status of a reported distance of a visibility observation.

            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = Passed gross limits check
                - 1 = Passed all quality control checks
                - 2 = Suspect
                - 3 = Erroneous
                - 4 = Passed gross limits check , data originate from an NCEI data source
                - 5 = Passed all quality control checks, data originate from an NCEI data source
                - 6 = Suspect, data originate from an NCEI data source
                - 7 = Erroneous, data originate from an NCEI data source
                - 9 = Passed gross limits check if element is present
        """

        self.wind_direction = mds_data.get('wind_observation_direction_angle', 999)
        """
        :type: int
        **WIND-OBSERVATION direction angle**
        The angle, measured in a clockwise direction, between true north and the direction from which
        the wind is blowing.
            - MIN:  001
            - MAX:  360
            - UNITS:  Angular Degrees
            - SCALING FACTOR:  1
            - DOM:  A general domain comprised of the numeric characters (0 9).
                - 999 = Missing.  If type code (below) = V, then 999 indicates variable wind direction.

        """

        self.wind_direction_qc = mds_data.get('wind_observation_direction_quality_code', 3)
        """
        :type: int
        **WIND-OBSERVATION direction quality code**
        The code that denotes a quality status of a reported WIND-OBSERVATION direction angle.
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = Passed gross limits check
                - 1 = Passed all quality control checks
                - 2 = Suspect
                - 3 = Erroneous
                - 4 = Passed gross limits check , data originate from an NCEI data source
                - 5 = Passed all quality control checks, data originate from an NCEI data source
                - 6 = Suspect, data originate from an NCEI data source
                - 7 = Erroneous, data originate from an NCEI data source
                - 9 = Passed gross limits check if element is present
        """

        self.wind_speed_rate = mds_data.get('wind_observation_speed_rate', 9999)
        """
        :type: int
        **WIND-OBSERVATION speed rate**
        The rate of horizontal travel of air past a fixed point.
            - MIN:  0000
            - MAX:  0900
            - UNITS:  meters per second
            - SCALING FACTOR:  10
            - DOM:   A general domain comprised of the numeric characters (0 9).
                - 9999 = Missing.
        """

        self.wind_speed_rate_qc = mds_data.get('wind_observation_speed_rate', 3)
        """
        **WIND OBSERVATION speed quality code**
        The code that denotes a quality status of a reported WIND-OBSERVATION speed rate.
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = Passed gross limits check
                - 1 = Passed all quality control checks
                - 2 = Suspect
                - 3 = Erroneous
                - 4 = Passed gross limits check , data originate from an NCEI data source
                - 5 = Passed all quality control checks, data originate from an NCEI data source
                - 6 = Suspect, data originate from an NCEI data source
                - 7 = Erroneous, data originate from an NCEI data source
                - 9 = Passed gross limits check if element is present

        """

        self.air_temp = int(mds_data.get('air_temperature_observation_air_temperature', 9999))
        """
        **AIR-TEMPERATURE-OBSERVATION air temperature**
        The temperature of the air.
            - MIN:   0932
            - MAX:  +0618
            - UNITS:  Degrees Celsius
            - SCALING FACTOR:  10
            - DOM:  A general domain comprised of the numeric characters (0 9), a plus sign (+), and a minus sign (-).
                - +9999 = Missing.
        """

        self.air_temp_qc = mds_data.get('air_temperature_observation_air_temperature_quality_code', 3)
        """
        **AIR-TEMPERATURE-OBSERVATION air temperature quality code**
        The code that denotes a quality status of an AIR-TEMPERATURE-OBSERVATION.
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = Passed gross limits check
                - 1 = Passed all quality control checks
                - 2 = Suspect
                - 3 = Erroneous
                - 4 = Passed gross limits check , data originate from an NCEI data source
                - 5 = Passed all quality control checks, data originate from an NCEI data source
                - 6 = Suspect, data originate from an NCEI data source
                - 7 = Erroneous, data originate from an NCEI data source
                - 9 = Passed gross limits check if element is present
                - A = Data value flagged as suspect, but accepted as a good value
                - C = Temperature and dew point received from Automated Weather Observing System (AWOS) are reported in                           whole degrees Celsius. Automated QC flags these values, but they are accepted as valid.
                - I = Data value not originally in data, but inserted by validator
                - M = Manual changes made to value based on information provided by NWS or FAA
                - P = Data value not originally flagged as suspect, but replaced by validator
                - R = Data value replaced with value computed by NCEI software
                - U = Data value replaced with edited value
        """

        self.dew_pooint = int(mds_data.get('air_temperature_observation_dew_point_temperature', 9999))
        """
        **AIR TEMPERATURE OBSERVATION dew point temperature**
        The temperature to which a given parcel of air must be cooled at constant pressure and water vapor
        content in order for saturation to occur.
            - MIN:  -0982
            - MAX:  +0368
            - UNITS:  Degrees Celsius
            - SCALING FACTOR:  10
            - DOM:  A general domain comprised of the numeric characters (0 9), a plus sign (+), and a minus sign (-).
                - +9999 = Missing.
        """

        self.dew_pooint_qc = mds_data.get('air_temperature_observation_dew_point_quality_code', 3)
        """
        **AIR TEMPERATURE OBSERVATION dew point quality code**
        The code that denotes a quality status of the reported dew point temperature.
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = Passed gross limits check
                - 1 = Passed all quality control checks
                - 2 = Suspect
                - 3 = Erroneous
                - 4 = Passed gross limits check , data originate from an NCEI data source
                - 5 = Passed all quality control checks, data originate from an NCEI data source
                - 6 = Suspect, data originate from an NCEI data source
                - 7 = Erroneous, data originate from an NCEI data source
                - 9 = Passed gross limits check if element is present
                - A = Data value flagged as suspect, but accepted as a good value
                - C = Temperature and dew point received from Automated Weather Observing System (AWOS) are reported in                           whole degrees Celsius. Automated QC flags these values, but they are accepted as valid.
                - I = Data value not originally in data, but inserted by validator
                - M = Manual changes made to value based on information provided by NWS or FAA
                - P = Data value not originally flagged as suspect, but replaced by validator
                - R = Data value replaced with value computed by NCEI software
                - U = Data value replaced with edited value
        """

        self.rel_humidity = -1
        """:type: float
        **RH (Relative Humidity)**
         percentage value from air-temperature and dew-point
        """

        if self.air_temp != 9999 and self.dew_pooint != 9999:
            a_c = self.air_temp / 10.0  # apply scaling factor
            b_c = self.dew_pooint / 10.0  # apply scaling factor
            c = 6.11 * math.pow(10, ((7.5 * a_c / (237.7 + a_c))))
            d = 6.11 * math.pow(10, ((7.5 * b_c / (237.7 + b_c))))
            self.rel_humidity = (d / c) * 100

        self.wind_gust_speed_rate = oc_data.get('speed_rate', 9999)
        """
        **WIND GUST OBSERVATION speed rate**
        The rate of speed of a wind gust.
            - MIN:  0050
            - MAX:  1100
            - UNITS:  Meters per second
            - SCALING FACTOR:  10
            - DOM:  A general domain comprised of the numeric characters (0 9).
                - 9999 = Missing
        """
        self.wind_gust_speed_rate_qc = oc_data.get('quality_code', 3)
        """
        **WIND GUST-OBSERVATION quality code**
        The code that denotes a quality status of a reported WIND-GUST-OBSERVATION speed rate.
            - DOM:  A specific domain comprised of the characters in the ASCII character set.
                - 0 = Passed gross limits check
                - 1 = Passed all quality control checks
                - 2 = Suspect
                - 3 = Erroneous
                - 4 = Passed gross limits check , data originate from an NCEI data source
                - 5 = Passed all quality control checks, data originate from an NCEI data source
                - 6 = Suspect, data originate from an NCEI data source
                - 7 = Erroneous, data originate from an NCEI data source
                - M = Manual change made to value based on information provided by NWS or FAA
                - 9 = Passed gross limits check if element is present
        """

    def utc_2_local(self, utc):
        """
        :type utc: str
        :rtype: datetime.datetime
        """
        timestamp = calendar.timegm((datetime.datetime.strptime(utc, '%Y-%m-%d %H:%M:%S')).timetuple())
        return datetime.datetime.fromtimestamp(timestamp)


class ISDData(object):
    def __init__(self, raw_data):
        """
        :type raw_data: ISDRawData
        """
        self.raw = raw_data

    def time(self):
        """ observation datetime
        :rtype: datetime.datetime
        """
        return self.raw.dt

    def precipitation(self, unit='inch'):
        """
        :type unit: str
        :rtype: float or None
        """
        if unit == 'inch':
            return _mm2inch(self.raw.precipitation / 10.0) if self.raw.precipitation != 9999 else None
        else:
            return (self.raw.precipitation / 10.0) if self.raw.precipitation != 9999 else None

    def precipitation_qc(self):
        """
        :rtype: (int, str)
        """
        return self.raw.precipitation_qc, QUALITY_CODE.get(self.raw.precipitation_qc, 3)

    def precipitation_intensity(self):
        """
        :rtype: (int, str)
        """
        return self.raw.intensity, INTENSITY_TYPES.get(self.raw.intensity, 9)

    def precipitation_type(self):
        """
        :rtype: (int, str)
        """
        return self.raw.precipitation_code, PRECIP_TYPES.get(self.raw.precipitation_code, 9)

    def obscuration(self):
        """
        :rtype: (int, str)
        """
        return self.raw.obscuration_code, OBSCURATION_CODE.get(self.raw.obscuration_code, 9)

    def descriptor(self):
        """
        :rtype: (int, str)
        """
        return self.raw.descriptor, DISCRIPTOR_CODE.get(self.raw.descriptor, 9)

    def visibility(self, unit='mile'):
        """
        :type unit: str
        :rtype: float or None
        """
        if unit == 'mile':
            return _meter2mile(self.raw.visibility) if self.raw.visibility != 999999 else None
        else:
            return self.raw.visibility if self.raw.visibility != 999999 else None

    def visibility_qc(self):
        """
        :rtype: (int, str)
        """
        return self.raw.visibility_qc, QUALITY_CODE.get(self.raw.visibility_qc, 3)

    def air_temp(self, unit='F'):
        """
        :type unit: str
        :rtype: float or None
        """
        if unit == 'F':
            return _c2f(int(self.raw.air_temp) / 10.0) if self.raw.air_temp != 9999 else None
        else:
            return (int(self.raw.air_temp) / 10.0) if self.raw.air_temp != 9999 else None

    def air_temp_qc(self):
        """
        :rtype: (int, str)
        """
        return self.raw.air_temp_qc, QUALITY_CODE.get(self.raw.air_temp_qc, 3)

    def dew_point(self):
        """
        :rtype: float or None
        """
        return _c2f(int(self.raw.dew_pooint) / 10.0) if self.raw.dew_pooint != 9999 else None

    def dew_point_qc(self):
        """
        :rtype: (int, str)
        """
        return self.raw.dew_pooint_qc, QUALITY_CODE.get(self.raw.dew_pooint_qc, 3)

    def rel_humidity(self):
        """
        :rtype: float or None
        """
        return self.raw.rel_humidity if self.raw.rel_humidity > 0 else None

    def wind_direction(self):
        """
        :rtype: float
        """
        wd = self.raw.wind_direction
        return (wd, _degree2direction(wd)) if wd != 999 else (None, None)

    def wind_direction_qc(self):
        """
        :rtype: (int, str)
        """
        return self.raw.wind_direction_qc, QUALITY_CODE.get(self.raw.wind_direction_qc, 3)

    def wind_speed(self, unit='mph'):
        """
        :type unit: str
        :rtype: float or None
        """
        if unit == 'mph':
            return (_meter_per_second2mph(self.raw.wind_speed_rate / 10.0)
                    if self.raw.wind_speed_rate != 9999
                    else None)
        else:
            return ((self.raw.wind_speed_rate / 10.0)
                    if self.raw.wind_speed_rate != 9999
                    else None)

    def wind_speed_qc(self):
        """
        :rtype: (int, str)
        """
        return self.raw.wind_speed_rate_qc, QUALITY_CODE.get(self.raw.wind_speed_rate_qc, 3)

    def wind_gust_speed(self, unit='mph'):
        """
        :type unit: str
        :rtype: float or None
        """
        if unit == 'mph':
            return (_meter_per_second2mph(self.raw.wind_gust_speed_rate / 10.0)
                    if self.raw.wind_gust_speed_rate != 9999
                    else None)
        else:
            return ((self.raw.wind_gust_speed_rate / 10.0)
                    if self.raw.wind_gust_speed_rate != 9999
                    else None)

    def wind_gust_speed_qc(self):
        """
        :rtype: (int, str)
        """
        return self.raw.wind_gust_speed_rate_qc, QUALITY_CODE.get(self.raw.wind_gust_speed_rate_qc, 3)

    def __str__(self):
        return '<ISDData time="%s" precip="%s" precip_type="%s" precip_intensity="%s" humidity="%s"visibility="%s" air_temp="%s" dew_point="%s" wind_dir="%s" wind_speed="%s" wind_gust="%s">' % (
            self.time().strftime('%Y-%m-%d %H:%M'),
            '%s inch' % round(self.precipitation(), 3) if self.precipitation() is not None else None,
            self.precipitation_type()[1],
            self.precipitation_intensity()[1],
            '%s %%' % round(self.rel_humidity(), 1) if self.rel_humidity() is not None else None,
            '%s mile' % round(self.visibility(), 2) if self.visibility() is not None else None,
            '%s F' % round(self.air_temp(), 2) if self.air_temp() is not None else None,
            '%s F' % round(self.dew_point(), 2) if self.dew_point() is not None else None,
            self.wind_direction(),
            '%s mph' % round(self.wind_speed(), 2) if self.wind_speed() is not None else None,
            '%s mph' % round(self.wind_gust_speed(), 2) if self.wind_gust_speed() is not None else None
        )


def _mm2inch(v):
    """ millimeter to inch

    :type v: float
    :rtype: float
    """
    return v * 0.0393701


def _c2f(v):
    """ Celsius to Fahrenheit

    :type v: float
    :rtype: float
    """
    return v * (9 / 5) + 32


def _meter2mile(v):
    """ meter to mile

    :type v: float
    :rtype: float
    """
    return v * 0.000621371


def _meter_per_second2mph(v):
    """ meter/second to mile/hour

    :type v: float
    :rtype: float
    """
    return v * 2.23694


def _degree2direction(v):
    """ degree to 16-directions

    :type v: int
    :rtype: str
    """
    val = math.floor((v / 22.5) + 0.5)
    dir_strings = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW",
                   "NNW"]
    return dir_strings[(val % 16)]
