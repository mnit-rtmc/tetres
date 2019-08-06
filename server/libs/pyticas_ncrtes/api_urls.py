# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.api_urls
========================
- API url list
"""

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

# estimation
ESTIMATION = '/ncrtes/est/'
TSI = '/ncrtes/tsi/'

# snow route
SNR_LIST = '/ncrtes/snowroute/list'
SNR_DELETE = '/ncrtes/snowroute/delete'
SNR_UPDATE = '/ncrtes/snowroute/update'
SNR_INSERT = '/ncrtes/snowroute/add'
SNR_GET = '/ncrtes/snowroute/get'

SNR_GROUP_LIST = '/ncrtes/snowroute_group/list'
SNR_GROUP_LIST_BY_YEAR = '/ncrtes/snowroute_group/list/year'
SNR_GROUP_DELETE = '/ncrtes/snowroute_group/delete'
SNR_GROUP_UPDATE = '/ncrtes/snowroute_group/update'
SNR_GROUP_INSERT = '/ncrtes/snowroute_group/add'
SNR_GROUP_GET = '/ncrtes/snowroute_group/get'
SNR_GROUP_YEARS = '/ncrtes/snowroute_group/years'
SNR_GROUP_COPY = '/ncrtes/snowroute_group/copy'

# snow event
SNE_LIST = '/ncrtes/snowevent/list'
SNE_LIST_BY_YEAR = '/ncrtes/snowevent/list/year'
SNE_DELETE = '/ncrtes/snowevent/delete'
SNE_UPDATE = '/ncrtes/snowevent/update'
SNE_INSERT = '/ncrtes/snowevent/add'
SNE_GET = '/ncrtes/snowevent/get'
SNE_YEARS = '/ncrtes/snowevent/years'

# target station
TS_LIST = '/ncrtes/ts/list'
TS_DELETE = '/ncrtes/ts/delete'
TS_UPDATE = '/ncrtes/ts/update'
TS_YEARS = '/ncrtes/ts/years'

# target station (manual, deprecated)
MANUAL_TS_LIST = '/ncrtes/ts/manual/list'
MANUAL_TS_DELETE = '/ncrtes/ts/manual/delete'
MANUAL_TS_INSERT = '/ncrtes/ts/manual/add'


