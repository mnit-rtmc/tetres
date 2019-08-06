# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import urllib.request
import urllib.error
import os
import gzip

from pyticas.logger import getLogger

ISD_DATA_URL = 'ftp://ftp.ncdc.noaa.gov/pub/data/noaa'

def _dataurl(usaf, wban, year):
    return '%s/%s/%s-%s-%s.gz' % (ISD_DATA_URL, year, usaf, wban, year)

def _filename(usaf, wban, year):
    return '%s-%s-%s' % (usaf, wban, year)

def download(dirpath, usaf, wban, year):
    fileurl = _dataurl(usaf, wban, year)
    try:
        input_file = gzip.open(urllib.request.urlretrieve(fileurl)[0])
        output_file = os.path.join(dirpath, _filename(usaf, wban, year))
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

if __name__ == '__main__':
    file = download('.', 726580, 14922, 2016)
    print('Downloaded file : ', file)