# -*- coding: utf-8 -*-
"""
actionlog_processor.py
~~~~~~~~~~~~~~

this module handles the request from `data change log tab` of `admin client`

"""
from pyticas_tetres.da.config import ConfigDataAccess

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import request

from pyticas_server import protocol as prot
from pyticas_tetres import api_urls_admin, cfg
from pyticas_tetres.admin_auth import requires_auth
from pyticas_tetres.systasks import actionlog_processor
from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.sched import worker


def register_api(app):
    @app.route(api_urls_admin.AL_LIST, methods=['POST', 'GET'])
    @requires_auth
    def tetres_actionlog_list():
        limit = request.form.get('limit', 100)

        da = ActionLogDataAccess()
        data_list = da.list(limit=limit, order_by=('id', 'desc'))
        da.close_session()

        da_config = ConfigDataAccess()
        running_id_item = da_config.get_by_name(cfg.OPT_NAME_ACTIONLOG_ID_IN_PROCESSING)
        da_config.close_session()

        if running_id_item and running_id_item.content:
            running_id = int(running_id_item.content)
            for item in data_list:
                if item.id == running_id:
                    item.status = ActionLogDataAccess.STATUS_RUNNING

        return prot.response_success({'list': data_list})

    @app.route(api_urls_admin.AL_PROCEED, methods=['POST', 'GET'])
    @requires_auth
    def tetres_actionlog_proceed():
        worker.add_task(actionlog_processor.run)
        return prot.response_success()
