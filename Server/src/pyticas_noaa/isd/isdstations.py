# -*- coding: utf-8 -*-

import csv
import os
import platform
import urllib.error
import urllib.request

import datetime

from pyticas.infra import Infra
from pyticas.logger import getLogger
from pyticas_noaa.cfg import ISD_STATION_LIST_URL, ISD_DIR
from pyticas_noaa.isd.isdtypes import ISDStation

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def download_isd_stations(redownload=False):
    """

    :type redownload: bool
    :rtype:
    """
    station_list_file = isd_station_list_file()

    if os.path.exists(station_list_file):
        ctime = _created_time(station_list_file)
        if (datetime.datetime.now() - ctime).days <= 7:
            return os.path.abspath(station_list_file)

    if not os.path.exists(station_list_file) or redownload:
        try:
            with open(urllib.request.urlretrieve(ISD_STATION_LIST_URL)[0], 'rb') as input_file:
                with open(station_list_file, "wb") as ofile:
                    for line in input_file:
                        ofile.write(line)
        except urllib.error.URLError as ex:
            getLogger(__name__).warning(
                'Could not download ISD station list file : %s (%s)' % (ISD_STATION_LIST_URL, ex.reason))
            os.remove(station_list_file)
            return False
        except Exception as ex:
            getLogger(__name__).warning('Could not download ISD station list file : %s (%s)' % (ISD_STATION_LIST_URL, ex))
            os.remove(station_list_file)
            return False

    return os.path.abspath(station_list_file)


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


def isd_station_list_file():
    """
    :rtype: str
    """
    output_dir = Infra.get_infra().get_path(ISD_DIR, create=True)
    return os.path.join(output_dir, 'isd-history.csv')


def _created_time(filepath):
    """

    :type filepath: str
    :rtype: datetime.datetime
    """
    if platform.system() == 'Windows':
        return datetime.datetime.fromtimestamp(os.path.getctime(filepath))
    else:
        stat = os.stat(filepath)
        try:
            return datetime.datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            return datetime.datetime.fromtimestamp(stat.st_mtime)