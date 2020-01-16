# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import http.client
import urllib.parse

from pyticas.tool import json
from pyticas_tetres.da.weather import WeatherDataAccess
from pyticas_tetres.ttypes import WeatherInfo

RWIS_ADDR = '131.212.105.85'
RWIS_ADDR = '127.0.0.1'
RWIS_PORT = 5678
TTRMS_DATA_INTERVAL = 600

def load_weather(site_id, prd, sen_id=0):
    """

    :type site_id: int
    :type prd: pyticas.ttypes.Period
    :type sen_id: int
    :rtype: list[pyticas_tetres.ttypes.WeatherInfo]
    """
    conn = http.client.HTTPConnection(RWIS_ADDR, RWIS_PORT)
    params = urllib.parse.urlencode({'site_id': site_id,
                                     'start_date': prd.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                                     'end_date': prd.end_date.strftime('%Y-%m-%d %H:%M:%S'),
                                     'sen_id': sen_id})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    #conn.set_debuglevel(1)
    conn.request("POST", "/rwis/get", params, headers)
    response = conn.getresponse()
    j = json.loads(response.read().decode('utf-8'))

    wDA = WeatherDataAccess(prd.start_date.year)

    if j['code'] == 1:
        wd = j['obj']
    else:
        return None

    results = []
    wis = []
    for idx, dtime in enumerate(prd.get_timeline(with_date=True)):
        row = wd.data[idx]
        if not row:
            wi = WeatherInfo(dtime=dtime)
        else:
            dt = dict(row.__dict__)
            dt['dtime'] = row.dtime.strftime('%Y-%m-%d %H:%M:%S')
            dt['pc_start_dtime'] = dt['pc_start_dtime'].strftime('%Y-%m-%d %H:%M:%S') if dt['pc_start_dtime'] else None
            dt['pc_end_dtime'] = dt['pc_end_dtime'].strftime('%Y-%m-%d %H:%M:%S') if dt['pc_end_dtime'] else None
            wi = WeatherInfo(**dt)

        results.append(wi)
        wm = wDA.da_base.to_model(wi)
        wis.append(wm)
        wDA.insert(wi)

    wDA.commit()
    wDA.close_session()

    return results


def get_weather(site_id, prd, sen_id=0):
    """

    :type site_id: int
    :type prd: pyticas.ttypes.Period
    :type sen_id: int
    :rtype: list[pyticas_tetres.ttypes.WeatherInfo]
    """
    wDA = WeatherDataAccess(prd.start_date.year)
    data = wDA.list_by_period(site_id, prd, sen_id)
    if not data or len(data) != len(prd.get_timeline()):
        return load_weather(site_id, prd, sen_id)

    return wDA.list_by_period(site_id, prd, sen_id)