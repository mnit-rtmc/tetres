# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import urllib.request
import urllib.error
import os
import gzip
from zipfile import ZipFile

from pyticas.infra import Infra
from pyticas.logger import getLogger
from pyticas_noaa.cfg import ISD_DATA_URL, ISD_DIR

QCLCD_DATA_URL = 'https://www.ncdc.noaa.gov/orders/qclcd'
QCLCD_DIR = 'noaa/qclcd'
QCLCD_DATA_DIR = 'noaa/qclcd/data'

def download(year, month):
    """
    :type year: int or str
    :type month: int or str
    :rtype: str or bool
    """
    fileurl = _dataurl(year, month)
    try:
        with ZipFile(urllib.request.urlretrieve(fileurl)[0], 'r') as input_file:
            output_dir = _output_dir(year)
            output_file = os.path.join(output_dir, _filename(year, month))
            with input_file.open('%s%02dhourly.txt' % (year, int(month))) as input_fp:
                with open(output_file, "wb") as output_fp:
                    for line in input_fp:
                        output_fp.write(line)
    except urllib.error.URLError as ex:
        getLogger(__name__).warn('Could not download QCLCD data : %s (%s)' % (fileurl, ex.reason))
        return False
    except Exception as ex:
        getLogger(__name__).warn('Could not download QCLCD data file : %s (%s)' % (fileurl, ex))
        return False

    return os.path.abspath(output_file)


def _dataurl(year, month):
    """
    :type year: int or str
    :type month: int or str
    :rtype: str
    """
    return '%s/QCLCD%s%02d.zip' % (QCLCD_DATA_URL, year, int(month))

def _filename(year, month):
    """
    :type year: int or str
    :type month: int or str
    :rtype: str
    """
    return '%s%02dhourly.txt' % (year, int(month))

def _output_dir(year):
    """
    :type year: int or str
    :rtype: str
    """
    return Infra.get_infra().get_path(QCLCD_DATA_DIR, create=True)



if __name__ == '__main__':
    file = download(726580, 14922, 2016)
    print('Downloaded file : ', file)