# -*- coding: utf-8 -*-

import gzip
import os
import platform
import urllib.error
import urllib.request

import datetime

from pyticas.infra import Infra
from pyticas.logger import getLogger
from pyticas_noaa.cfg import ISD_DATA_URL, ISD_DIR
from pyticas_noaa.isd.isdtypes import CDS, MDS, ISD_AA, ISD_AU, ISD_OC, ISDRawData, ISDData

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def download(usaf, wban, year):
    """
    :type usaf: int or str
    :type wban: int or str
    :type year: int or str
    :rtype: str or bool
    """
    fileurl = _dataurl(usaf, wban, year)
    output_dir = _output_dir(year)
    output_file = os.path.join(output_dir, _filename(usaf, wban, year))

    if os.path.exists(output_file):
        os.remove(output_file)

    # if os.path.exists(output_file):
    #     ctime = _created_time(output_file)
    #     if (datetime.datetime.now() - ctime).days <= 1:
    #         return output_file

    try:
        input_file = gzip.open(urllib.request.urlretrieve(fileurl)[0])
        with open(output_file, "wb") as of:
            for line in input_file:
                of.write(line)
    except urllib.error.URLError as ex:
        getLogger(__name__).warn('Could not download ISD file : %s (%s)' % (fileurl, ex.reason))
        if os.path.exists(output_file):
            os.remove(output_file)
        return False
    except Exception as ex:
        getLogger(__name__).warn('Could not download ISD file : %s (%s)' % (fileurl, ex))
        if os.path.exists(output_file):
            os.remove(output_file)
        return False

    #save_as_daily_data(output_file)

    return os.path.abspath(output_file)


def parse(filepath, data_filter=None, line_filter=None):
    """

    :type filepath: Union(str, list[str])
    :type data_filter: function
    :rtype: Generator : pyticas_noaa.isd.isdtypes.ISDData
    """

    cds = CDS()
    mds = MDS()
    aa = ISD_AA()
    au = ISD_AU()
    oc = ISD_OC()
    time_cache = []
    filepaths = []
    if filepath is str:
        filepaths.append(filepath)
    else:
        filepaths.extend(filepath)

    for fpath in filepaths:
        with open(fpath, 'r') as f:
            for num, line in enumerate(f):
                if line_filter and not line_filter(line):
                    continue
                res_cds = cds.parse(line)
                res_mds = mds.parse(line, cds.total_field_length())
                ads_start = cds.total_field_length() + mds.total_field_length()
                ad_line = _additional_data_string(line, ads_start)
                if not ad_line:
                    continue
                ress_aa = aa.parse(ad_line)
                ress_au = au.parse(ad_line)
                ress_oc = oc.parse(ad_line)
                isd_data = ISDData(ISDRawData(res_cds, res_mds, ress_aa, ress_au, ress_oc))
                # to avoid duplicated data
                dtime = isd_data.time().timestamp()
                if dtime in time_cache:
                    continue
                if not data_filter or data_filter(isd_data):
                    time_cache.append(dtime)
                    yield isd_data


def _dataurl(usaf, wban, year):
    """
    :type usaf: int or str
    :type wban: int or str
    :type year: int or str
    :rtype: str
    """


    return '%s/%s/%s-%s-%s.gz' % (ISD_DATA_URL, year, usaf, wban, year)


def _filename(usaf, wban, year):
    """
    :type usaf: int or str
    :type wban: int or str
    :type year: int or str
    :rtype: str
    """
    return '%s-%s-%s' % (usaf, wban, year)


def _output_dir(year):
    """
    :type year: int or str
    :rtype: str
    """
    return Infra.get_infra().get_path('%s/%s' % (ISD_DIR, year), create=True)


def _additional_data_string(s, additional_data_section_start):
    """

    :type s: str
    :type additional_data_section_start: int
    :return:
    """
    if 'ADD' != s[additional_data_section_start:additional_data_section_start + 3]:
        return None
    try:
        end = s.index('REM', additional_data_section_start + 3)
        return s[additional_data_section_start + 3:end]
    except:
        return None


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

if __name__ == '__main__':
    file = download(726580, 14922, 2016)
    print('Downloaded file : ', file)
