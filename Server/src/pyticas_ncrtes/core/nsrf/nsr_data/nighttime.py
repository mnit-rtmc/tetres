# -*- coding: utf-8 -*-

from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import data_util
from pyticas_ncrtes.core.nsrf.target import lane

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def collect(target_station, periods, **kwargs):
    """ returns nighttime traffic data

    :type target_station: pyticas.ttypes.RNodeObject
    :type periods: list[pyticas.ttypes.Period]
    :rtype: (list[float], list[float], list[list[float]], list[list[float]], list[pyticas.ttypes.Period])
    """
    rdr = ncrtes.get_infra().rdr

    dc, valid_detectors = kwargs.get('dc', None), kwargs.get('valid_detectors', None)
    if not dc:
        dc, valid_detectors = lane.get_detector_checker(target_station)

    if not dc:
        return None, None, None, None, None

    uss, kss, used_periods = [], [], []
    for prd in periods:
        us = rdr.get_speed(target_station, prd, dc)
        if not ncrtes.get_infra().is_missing(us.data):
            ks = rdr.get_density(target_station, prd, dc)
            uss.append(us.data)
            kss.append(ks.data)
            used_periods.append(prd)

    if not uss:
        return None, None, None, None, None


    avg_us = data_util.avg_multi(uss, only_positive=True)
    avg_ks = data_util.avg_multi(kss, only_positive=True)

    import xlsxwriter
    import os
    output_path = ncrtes.get_infra().get_path('ncrtes', create=True)
    filepath = os.path.join(output_path, 'nighttime-%s.xlsx' % target_station.station_id)
    wb = xlsxwriter.Workbook(filepath)
    ws = wb.add_worksheet('nsr_data')
    ws.write_row(0, 0, ['time', 'avg']+[ prd.get_date_string() for prd in periods])
    ws.write_column(1, 0, [ dt.strftime('%H:%M') for dt in periods[0].get_timeline(as_datetime=True)])
    ws.write_column(1, 1, avg_us)
    col = 2
    for idx, us in enumerate(uss):
        ws.write_column(1, col, us)
        col += 1
    wb.close()


    return avg_us, avg_ks, uss, kss, used_periods
