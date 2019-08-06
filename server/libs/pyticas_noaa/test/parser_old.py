# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import re


class Map(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class ISDField(object):
    fields = ()

    def parse(self, text, offset=0):
        """

        :type text: str
        :type offset: int
        :rtype: Map
        """
        result = Map()
        cur_offset = offset
        for field_name, field_len in self.fields:
            if isinstance(field_len, str):
                ref_vals = [ fl for fn, fl in self.fields if fn == field_len ]
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
        :rtype: list[Map]
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


class CDS(ISDField):
    total_variable_chars = None
    """
    TOTAL-VARIABLE-CHARACTERS       (this includes remarks, additional data, and element quality section)
    The number of characters in the variable data section.  The total record length = 105 + the value stored in this field.
    DOM:  A general domain comprised of the characters in the ASCII character set.
    MIN: 0000   MAX: 9999
    """

    station_usaf_id = None
    """
    FIXED-WEATHER-STATION USAF MASTER STATION CATALOG identifier
    The identifier that represents a FIXED-WEATHER-STATION.
    DOM:  A general domain comprised of the characters in the ASCII character set.
    COMMENT:  This field includes all surface reporting stations, including ships, buoys, etc.
    """

    station_wban_id = None
    """
    FIXED-WEATHER-STATION NCEI WBAN identifier
    The identifier that represents a FIXED-WEATHER-STATION.
    MIN: 00000        MAX: 99999
    DOM:  A general domain comprised of the numeric characters (0-9).
    COMMENT:  This field includes all surface reporting stations, including ships, buoys, etc.
    """

    geophysical_point_observation_date = None
    """
    GEOPHYSICAL-POINT-OBSERVATION date
    The date of a GEOPHYSICAL-POINT-OBSERVATION.
    MIN:  00000101     MAX:  99991231
    DOM:  A general domain comprised of integer values 0-9 in the format YYYYMMDD.
    YYYY can be any positive integer value; MM is restricted to values 01-12; and DD is restricted
    to values 01-31.
    """

    geophysical_point_observation_time = None
    """
    GEOPHYSICAL-POINT-OBSERVATION time
    The time of a GEOPHYSICAL-POINT-OBSERVATION based on
    Coordinated Universal Time Code (UTC).
    MIN:  0000         MAX:  2359
    DOM: A general domain comprised of integer values 0-9 in the format HHMM.
    HH is restricted to values 00-23; MM is restricted to values 00-59.
    """

    geophysical_point_observation_data_source_flag = None
    """
    GEOPHYSICAL-POINT-OBSERVATION data source flag
    The flag of a GEOPHYSICAL-POINT-OBSERVATION showing the source or
    combination of sources used in creating the observation.
    MIN:  1         MAX:  Z
    DOM: A general domain comprised of values 1-9 and A-N.
        1 = USAF SURFACE HOURLY observation, candidate for merge with NCEI SURFACE HOURLY (not yet merged, failed element cross-checks)
        2 = NCEI SURFACE HOURLY observation, candidate for merge with USAF SURFACE HOURLY (not yet merged, failed element cross-checks)
        3 = USAF SURFACE HOURLY/NCEI SURFACE HOURLY merged observation
        4 = USAF SURFACE HOURLY observation
        5 = NCEI SURFACE HOURLY observation
        6 = ASOS/AWOS observation from NCEI
        7 = ASOS/AWOS observation merged with USAF SURFACE HOURLY observation
        8 = MAPSO observation (NCEI)
        A = USAF SURFACE HOURLY/NCEI HOURLY PRECIPITATION merged observation, candidate for merge with NCEI SURFACE HOURLY (not yet merged, failed element                                           cross-checks)
        B = NCEI SURFACE HOURLY/NCEI HOURLY PRECIPITATION merged observation, candidate for merge with USAF SURFACE HOURLY (not yet merged, failed element                                           cross-checks)
        C = USAF SURFACE HOURLY/NCEI SURFACE HOURLY/NCEI HOURLY PRECIPITATION merged observation
        D = USAF SURFACE HOURLY/NCEI HOURLY PRECIPITATION merged observation
        E = NCEI SURFACE HOURLY/NCEI HOURLY PRECIPITATION merged observation
        F = Form OMR/1001 – Weather Bureau city office (keyed data)
        G = SAO surface airways observation, pre-1949 (keyed data)
        H = SAO surface airways observation, 1965-1981 format/period (keyed data)
        I = Climate Reference Network observation
        J = Cooperative Network observation
        K = Radiation Network observation
        L = Data from Climate Data Modernization Program (CDMP) data source
        M = Data from National Renewable Energy Laboratory (NREL) data source
        N = NCAR / NCEI cooperative effort (various national datasets)
        O = Summary observation created by NCEI using hourly observations that may not share the same data source flag
        9 = Missing
    """

    def __init__(self):
        self.fields = (
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
    def __init__(self):
        self.fields = (
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
    def __init__(self):
        self.tag_pattern = r'(REM[a-zA-Z]{3}[\d]{3})'
        self.fields = (
            ('geophysical_point_observation_remark_tag', 3),  # for "REM"
            ('geophysical_point_observation_remark_id', 3),
            ('geophysical_point_observation_remark_length_quantity', 3),
            ('data', 'geophysical_point_observation_remark_length_quantity')
        )


"""
Element Quality Data Section
"""
class EQDS(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(EQD[\w]{3})'
        self.fields = (
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
    def __init__(self):
        self.tag_pattern = r'(AA[\d][\w]{8})'
        self.fields = (
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
    def __init__(self):
        self.tag_pattern = r'(AU[\d][\w]{8})'
        self.fields = (
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
    def __init__(self):
        self.tag_pattern = r'(AG[\d][\w]{4})'
        self.fields = (
            ('precipitation_estimated_observation_id', 3),  # for "AG1"
            ('precipitation_estimated_observation_discrepancy_code', 1),
            ('precipitation_estimated_observation_estimated_water_depth_dimension', 3), # in millimeter
        )

"""
Liquid Precipitation Data (AO1-AO4)
"""
class ISD_AO(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(AO[\d][\w]{8})'
        self.fields = (
            ('liquid_precipitation_occurrence_id', 3),  # for "AO1"
            ('liquid_precipitation_period_quantity_in_minutes', 2),
            ('liquid_precipitation_depth_dimension', 4), # scaling factor = 10, unit=millimeter
            ('liquid_precipitation_condition_code', 1),
            ('liquid_precipitation_quality_code', 1),
        )

"""
Present Weather Observation Data (AW1-AW4)
"""
class ISD_AW(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(AW[\d][\w]{3})'
        self.fields = (
            ('present_weather_observation_automated_occurrence_id', 3),  # for "AW1-AW4"
            ('present_weather_observation_automated_atmospheric_condition_code', 2),
            ('present_weather_observation_quality_automated_atmospheric_condition_code', 1),
        )

"""
Present Weather Observation Data (AW1-AW4)
"""
class ISD_CH(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(CH[\d])'
        self.fields = (
            ('relative_humidity_temperature_id', 3),  # for "CH1-CH2"
            ('relative_humidity_temperature_period_quantity_in_minutes', 2),
            ('avg_rh_average_air_temperature', 5),
            ('avg_rh_average_air_temperature_quality_code', 1),
            ('avg_rh_average_air_temperature_flag', 1),
            ('avg_rh_relative_humidity', 4),
            ('avg_rh_relative_humidity_qulaity_code', 1),
            ('avg_rh_relative_humidity_flag', 1),
        )


class ISD_MA(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(MA[\d])'
        self.fields = (
            ('tag', 3),  # for "MA1"
            ('altimeter_setting_rate', 5),
            ('altimeter_quality_code', 1),
            ('station_pressure_rate', 5),
            ('station_pressure_rate_quality_code', 1),
        )

class ISD_MD(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(MD[\d])'
        self.fields = (
            ('tag', 3),  # for "MA1"
            ('altimeter_setting_rate', 5),
            ('altimeter_quality_code', 1),
            ('station_pressure_rate', 5),
            ('station_pressure_rate_quality_code', 1),
        )

class ISD_RH(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(RH[\d])'
        self.fields = (
            ('tag', 3),  # for "RH1"
            ('period_quantity', 3),
            ('code', 1),
            ('percentage', 3),
            ('derived_code', 1),
            ('quality_code', 1),
        )

class ISD_GA(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(GA[\d])'
        self.fields = (
            ('tag', 3),  # for "GA1-GA6"
            ('coverage_code', 2),
            ('coverage_code_quality_code', 1),
            ('base_height_dimension', 6),
            ('base_height_dimension_quality_code', 1),
            ('cloud_type_code', 2),
            ('cloud_type_code_quality_code', 1),
        )

class ISD_OC(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(OC[\d])'
        self.fields = (
            ('tag', 3),  # for "GA1-GA6"
            ('speed_rate', 4),
            ('quality_code', 1),
        )

class ISD_KG(ISDAdditionalData):
    def __init__(self):
        self.tag_pattern = r'(KG[\d])'
        self.fields = (
            ('tag', 3),  # for "GA1-GA6"
            ('period_quantity', 3),
            ('code', 1),
            ('temperature', 5),
            ('derived_code', 1),
            ('quality_code', 1),
        )

DATA_FILE = '726575-94960-2017' # CRYSTAL AIRPORT
#DATA_FILE = '726580-14922-2017' # MINNEAPOLIS-ST PAUL INTERNATIONAL AP

cds = CDS()
mds = MDS()
rds = RDS()
eqds = EQDS()
aa = ISD_AA()
au = ISD_AU()
ag = ISD_AG()
ao = ISD_AO()
aw = ISD_AW()
ch = ISD_CH()
ma = ISD_MA()
rh = ISD_RH()
ga = ISD_GA()
oc = ISD_OC()
kg = ISD_KG()

def find_tags(line, offset=0):
    """

    :type line: str
    :type offset: int
    :return:
    """
    res = []
    for m in re.finditer(r"([A-Z]{2}[\d]{1})", line[offset:]):
        # print(m.start(), m.group(), line[offset+m.start():])
        res.append((m.group(), m.start() + offset))
    return res

def additional_data_string(s, ads_start):
    if 'ADD' != s[ads_start:ads_start+3]:
        return None
    try:
        end1 = s.index(' RMK ', ads_start+3)
        end2 = s.index('REM', ads_start+3) if 'REM' in s else 999999
        end = min(end1, end2)
        return s[ads_start+3:end]
    except:
        return None

tags = {}
with open(DATA_FILE, 'r') as f:
    for num, line in enumerate(f):
        res = cds.parse(line, 0)
        # print(line)
        # print()
        TIME_OFFSET_FROM_UTC = -6
        date = '%04d-%02d-%02d' % (
            res.geophysical_point_observation_year,
            res.geophysical_point_observation_month,
            res.geophysical_point_observation_day)

        dt = datetime.datetime.strptime('%04d-%02d-%02d %02d:%02d' % (
            res.geophysical_point_observation_year,
            res.geophysical_point_observation_month,
            res.geophysical_point_observation_day,
            res.geophysical_point_observation_hour,
            res.geophysical_point_observation_minute,
            ), '%Y-%m-%d %H:%M')

        #dt = dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime('%Y-%m-%d %H:%M')
        dt = dt.replace(tzinfo=datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M')

        print('## %s' % dt)
        if 1:
            res = cds.parse(line)
            print('!! CDS')
            for fn, fl in cds.fields:
                print('    - ', fn, ' : ', res[fn])

            print('  !! MDS')
            offset = cds.total_field_length()
            res = mds.parse(line, offset)
            if any(res):
                for fn, fl in mds.fields:
                    print('    - ', fn, ' : ', res[fn])

            print('  !! RDS')
            ress = rds.parse(line)
            if any(ress):
                for fn, fl in rds.fields:
                    print('    - ', fn, ' : ', ress[0][fn])

            print('  !! EQDS')
            ress = eqds.parse(line)
            if any(ress):
                for fn, fl in eqds.fields:
                    print('    - ', fn, ' : ', ress[0][fn])

            print('-----------------------------')

        ads_start = cds.total_field_length() + mds.total_field_length()
        ad_line = additional_data_string(line, ads_start)

        if not ad_line:
            print('!!! No Additional Data Section : ', dt)
            continue

        res = find_tags(ad_line)
        print('# Additional Tags')
        additional_tags = sorted([ fn for fn, fl in res ])
        print(additional_tags)
        print('-'*30)
        for t, o in res:
            if t not in tags:
                tags[t] = 0
            tags[t] += 1

        ads = [ aa, au, oc, kg]#, au, ag, ao, aw]
        for ad in ads:
            print(' $ ', ad.__class__.__name__)
            ress = ad.parse(ad_line)
            if any(ress):
                for idx, res in enumerate(ress):
                    print('   #%d' % idx)
                    for fn, fl in ad.fields:
                        print('    - ', fn, ' : ', res[fn])

        # if [ dt for t in [ '2017-01-31 02', '2017-01-31 03', '2017-01-31 04'] if t in dt ]:
        #     print(ad_line)
        #     print()
        #     input('# Enter to continue : ')
        #     print()


print('used tags : ')
for t, n in tags.items():
    print(t, ' : ', n)
