# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import urllib.request
import urllib.error
import os
import gzip

from pyticas.logger import getLogger

WBAN_STATION_LIST_URL = 'https://www.ncdc.noaa.gov/homr/file/wbanmasterlist.psv.zip'

def download(dirpath):
    fileurl = WBAN_STATION_LIST_URL
    try:
        input_file = gzip.open(urllib.request.urlretrieve(fileurl)[0])
        output_file = os.path.join(dirpath, 'wbanmasterlist.psv')
        with open(output_file, "wb") as of:
            for line in input_file:
                of.write(line)
    except urllib.error.URLError as ex:
        getLogger(__name__).warn('Could not download ISD file : %s (%s)' % (fileurl, ex.reason))
        return False
    except Exception as ex:
        getLogger(__name__).warn('Could not download ISD file : %s (%s)' % (fileurl, ex))
        return False

    return os.path.abspath(output_file)


download('.')