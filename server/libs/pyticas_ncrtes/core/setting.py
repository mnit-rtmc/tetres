# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.core.setting
============================

- configuration variables

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

# traffic data collecting interval
DATA_INTERVAL = 180 # 3minute

# free-flow speed density threshold
#  - it is assumed that traffic is recovered to free-flow when density is less than `FFS_K` in estimation process
FFS_K = 30

# data collecting period
#   - from: SNOW_START_TIME - EXTEND_START_HOUR
#   - to  : SNOW_END_TIME + EXTEND_END_HOUR
EXTEND_START_HOUR = 2
EXTEND_END_HOUR = 8

# whole_data will stored in `data/ncrtes` folder
OUTPUT_DIR_NAME = 'ncrtes'


# Daytime and Nighttime
LATE_NIGHT_START_TIME = 21 #23
LATE_NIGHT_END_TIME = 7 #7
AM_START = 5 #5
AM_END = 12
PM_START = 12
PM_END = 19 #21

# rate threshold to check rainy or dry
DRY_RATE_THRESHOLD = 0.9

# smoothing window size for daytime UK data
SMOOTHING_SIZE = 11

# number of data for the given time
INTV15MIN = int((15 * 60) / DATA_INTERVAL)
INTV30MIN = INTV15MIN * 2
INTV1HOUR = INTV30MIN * 2
INTV2HOUR = INTV1HOUR * 2
INTV3HOUR = INTV1HOUR * 3
INTV4HOUR = INTV1HOUR * 4
INTV5HOUR = INTV1HOUR * 5

# smoothing windows
SWM = DATA_INTERVAL / 60 # nsr_data interval in minute
SW_4HOURS = (240 / SWM) + 1
SW_3HOURS = (180 / SWM) + 1
SW_2HOURS = (120 / SWM) + 1
SW_1HOUR = (60 / SWM) + 1
SW_30MIN = (30 / SWM) + 1
SW_15MIN = (15 / SWM)

# NCRT TYPE
NCRT_TYPE_QK = 1
NCRT_TYPE_SECTIONWISE = 2