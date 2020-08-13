# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas import cfg as pyticas_cfg
from pyticas import tetresconf

DEVELOPMENT_MODE = True

# Log Configs
LOG_FILE_NAME = 'pyticas-ttrms' if not DEVELOPMENT_MODE else None
LOG_LEVEL = pyticas_cfg.ROOT_LOGGER_LEVEL
LOG_TO_CONSOLE = pyticas_cfg.ROOT_LOGGER_TO_CONSOLE

# Admin Client is Acceptable from this IP
USE_WHITELIST = tetresconf.get_property('ticas.use_whitelist')
if USE_WHITELIST.upper() == "FALSE":
    USE_WHITELIST = False
else:
    USE_WHITELIST = True

ip_addresses = tetresconf.get_property('ticas.admin_ip_addresses')
ip_list = [s.strip() for s in ip_addresses.split(',')]
ADMIN_IP_ADDRESSES = []
for ip in ip_list:
    if ip:
        ADMIN_IP_ADDRESSES.append(ip)

# Number of Workers for Estimation
N_WORKERS_FOR_USER_CLIENT = 2

# Data Interval (Do not change this)
TT_DATA_INTERVAL = 300

# NOAA Weather Stations
STATE = 'MN'
TARGET_ISD_STATIONS = [
    # (USAF, WBAN)
    ('726577', '94974'),  # ANOKA CO-BLNE AP(JNS FD) AP
    ('726575', '94960'),  # CRYSTAL AIRPORT
    ('726584', '14927'),  # ST PAUL DWTWN HOLMAN FD AP
    ('726580', '14922'),  # MINNEAPOLIS-ST PAUL INTERNATIONAL AP
    ('726603', '04974'),  # SOUTH ST PAUL MUNI-RICHARD E FLEMING FLD ARPT
    ('726579', '94963'),  # FLYING CLOUD AIRPORT
    ('726562', '04943'),  # AIRLAKE AIRPORT
]

# Option Name for System Configuration and Action Log
# used in `Config` table
OPT_NAME_SYSCONFIG = 'sysconfig'
OPT_NAME_ACTIONLOG_ID_IN_PROCESSING = 'actionlog_id_in_processing'

# default system configuration  ############################################################################
#   - these values are updated in administrator user and stored in to db ('config' table)

DATA_ARCHIVE_START_YEAR = 2011
DAILY_JOB_OFFSET_DAYS = 3  # daily tasks run the task for the day of `today` - `DAILY_JOB_OFFSET_DAYS`

DAILY_JOB_START_TIME = '23:00'
WEEKLY_JOB_START_WEEKDAY = 'Sunday'  #
WEEKLY_JOB_START_TIME = '23:00'
MONTHLY_JOB_START_DAY = 1
MONTHLY_JOB_START_TIME = '23:00'

INCIDENT_DOWNSTREAM_DISTANCE_LIMIT = 10  # ignore incidents far from 10 mile
INCIDENT_UPSTREAM_DISTANCE_LIMIT = 10

WZ_DOWNSTREAM_DISTANCE_LIMIT = 10  # ignore incidents far from 10 mile
WZ_UPSTREAM_DISTANCE_LIMIT = 10

SE_ARRIVAL_WINDOW = 150  # in minutes (2.5 hour)
SE_DEPARTURE_WINDOW1 = 120  # in minutes (beginning at 2 hours after the game start)
SE_DEPARTURE_WINDOW2 = 150  # in minutes (2.5 hour period from DEPARTURE_WINDOW_IN_MINUTE1)

# faverolles 1/12/2020: Adding AdminClient MOE Config Parameters
MOE_CRITICAL_DENSITY = 40  # vehs/mile/lane
MOE_LANE_CAPACITY = 2200  # vehs/hr/lane
MOE_CONGESTION_THRESHOLD_SPEED = 45  # miles/hr

DEFAULT_MOE_CRITICAL_DENSITY = 40  # vehs/mile/lane
DEFAULT_MOE_LANE_CAPACITY = 2200  # vehs/hr/lane
DEFAULT_MOE_CONGESTION_THRESHOLD_SPEED = 45  # miles/hr

###########################################################################################################
