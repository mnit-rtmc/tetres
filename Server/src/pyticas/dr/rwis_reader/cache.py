# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import os

from pyticas import logger
from pyticas.ticas import get_path
from pyticas.tool import util, json
from pyticas.ttypes import RWISData

logging = logger.getDefaultLogger(__name__)

_CACHE_RWIS = 'rwis_data'
_CACHE_FAIL = 'rwis_fail'


def _path():
    _PATHS = {
        _CACHE_RWIS: os.path.join(get_path('cache'), _CACHE_RWIS),
        _CACHE_FAIL: os.path.join(get_path('cache'), _CACHE_FAIL)
    }

    for v in _PATHS.values():
        if not os.path.exists(v):
            os.mkdir(v)

    return _PATHS


def cache(group_id, site_id, date, wd, src_type):
    """

    :type group_id: str
    :type site_id: str
    :type date: datetime.datetime
    :type wd: ScanWebData
    """
    cache_path = _cache_path(_CACHE_RWIS, group_id, site_id, date, src_type)
    util.save_file_contents(cache_path, json.dumps(wd))


def cached(group_id, site_id, date, src_type=None):
    """

    :type group_id: str
    :type site_id: str
    :type date: datetime.datetime
    :rtype: ScanWebData
    """
    cache_path = _cache_path(_CACHE_RWIS, group_id, site_id, date, src_type)
    if os.path.exists(cache_path) == False:
        return None
    try:
        return json.loads(util.get_file_contents(cache_path))
    except Exception:
        os.remove(cache_path)
        return None


def fail(group_id, site_id, date, src_type=None):
    open(_cache_path(_CACHE_FAIL, group_id, site_id, date, src_type), 'w').close()


def is_failed(group_id, site_id, date, src_type=None):
    return os.path.exists(_cache_path(_CACHE_FAIL, group_id, site_id, date, src_type))


def _cache_path(cache_type, group_id, site_id, date, src_type=None):
    """ return cache path according to cache_type, but if not exists, create directory """
    _PATHS = _path()
    cache_path = os.path.join(_PATHS[cache_type], str(date.year),
                              '{0}{1:02}{2:02}'.format(date.year, date.month, date.day))
    try:
        os.makedirs(cache_path)
    except:
        pass

    if src_type:
        return os.path.join(cache_path, '{}-{}-{}.rwis'.format(group_id, site_id, src_type))
    else:
        return os.path.join(cache_path, '{}-{}.rwis'.format(group_id, site_id))
