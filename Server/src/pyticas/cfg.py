# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from collections import namedtuple

DEVELOPMENT_MODE = True

# logger setting
ROOT_LOGGER_NAME = 'pyticas'
ROOT_LOGGER_FILENAME = 'pyticas' if not DEVELOPMENT_MODE else None
ROOT_LOGGER_TO_CONSOLE = True if DEVELOPMENT_MODE else False
ROOT_LOGGER_LEVEL = 'DEBUG' if DEVELOPMENT_MODE else 'INFO'

LOG_FORMAT = '%(asctime)s :: %(levelname)-5s :: %(name)-40s :: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

LOG_MAX_FILE_SIZE = 10000000  # 10 MB
LOG_BACKUP_COUNT = 10

NAME = 'MN TMC'
TRAFFIC_DATA_URL = 'http://data.dot.state.mn.us:80/trafdat'
CONFIG_XML_URL = 'http://data.dot.state.mn.us/iris_xml/metro_config.xml.gz'
SCANWEB_URL = 'http://rwis.dot.state.mn.us/scanweb/'

MISSING_VALUE = -1
MISSING_THRESHOLD = 80  # it is missing when confidence is less than 80%
SAMPLES_PER_HOUR = 120
DENSITY_THRESHOLD = 1.2
FEET_PER_MILE = 5280
MAX_SCANS = 1800
MAX_VOLUME = 37
MAX_OCCUPANCY = 100
MAX_SPEED = 100.0
RADIUS_IN_EARTH_FOR_MILE = 3955.7  # mean radius or use your radius value
DETECTOR_DATA_INTERVAL = 30  # detector data saved with 30 seconds interval
SAMPLES_PER_DAY = 24 * 60 * 60 // DETECTOR_DATA_INTERVAL  # detector data sample length per day (= 2880)
USE_DETECTOR_CACHE = False
RWIS_DISTANCE_THRESHOLD = 15
RWIS_SITE_INFO = []

PROXIES = {'http' : '', 'https' : ''}

def get_proxy(protocol):
    return PROXIES.get(protocol, None)