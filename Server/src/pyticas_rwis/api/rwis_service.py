# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from flask import make_response
from flask import request

from pyticas.tool import json
from pyticas.ttypes import Period
from pyticas_server import protocol as prot
from pyticas_rwis import rwis

def register_api(app):

    @app.route('/rwis/get', methods=['POST', 'GET'])
    def rwis_get_weather():
        qry_data = {}
        if request.method == 'POST':
            qry_data = request.form
        elif request.method == 'GET':
            qry_data = request.args

        sdate = qry_data.get('start_date')
        edate = qry_data.get('end_date')
        site_id = qry_data.get('site_id', None)
        sen_id = qry_data.get('sen_id', 0)

        if not site_id:
            return prot.response_fail( 'site_id is required')
        if not sdate or not edate:
            return prot.response_fail( 'starte_date and end_date are required')

        try:
            sdate = datetime.datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S')
            edate = datetime.datetime.strptime(edate, '%Y-%m-%d %H:%M:%S')
        except:
            return prot.response_fail( 'datetime format must be "yyyy-mm-dd hh:ii:ss"')

        if sdate >= edate:
            return prot.response_fail( 'end_date must be greater than start_date')

        if (edate - sdate).seconds <= 600:
            return prot.response_fail( 'time duration must be longer than 10 minutes')

        wd = rwis.get_weather(site_id, Period(sdate, edate, 300), sen_id)

        return prot.response_success(wd)
