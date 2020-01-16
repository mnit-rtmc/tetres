# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import csv
import os
import urllib.error
import urllib.request

from pyticas.infra import Infra
from pyticas.logger import getLogger
from pyticas_noaa.cfg import ISD_STATION_LIST_URL, ISD_DIR
from pyticas_noaa.isd.isdtypes import ISDStation


def download_station_list(redownload=False):
    """

    :type redownload: bool
    :rtype:
    """
    filepath = station_list_file()

    if not os.path.exists(filepath) or redownload:
        try:
            input_file = open(urllib.request.urlretrieve(ISD_STATION_LIST_URL)[0], 'rb')
            with open(filepath, "wb") as ofile:
                for line in input_file:
                    ofile.write(line)
        except urllib.error.URLError as ex:
            getLogger(__name__).warn('Could not download WBAN station list file : %s (%s)' % (ISD_STATION_LIST_URL, ex.reason))
            os.remove(filepath)
            return False
        except Exception as ex:
            getLogger(__name__).warn('Could not download WBAN station list file : %s (%s)' % (ISD_STATION_LIST_URL, ex))
            os.remove(filepath)
            return False

    return os.path.abspath(filepath)

def load_station_list(filepath, state='MN', station_filter=None):
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


def station_list_file():
    """
    :rtype: str
    """
    output_dir = Infra.get_infra().get_path(ISD_DIR, create=True)
    return os.path.join(output_dir, 'isd-history.csv')