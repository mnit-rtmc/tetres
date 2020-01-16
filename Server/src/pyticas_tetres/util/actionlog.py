# -*- coding: utf-8 -*-
import datetime
from flask import request

from pyticas_tetres.da.actionlog import ActionLogDataAccess
from pyticas_tetres.ttypes import ActionLogInfo

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

INSERT = ActionLogDataAccess.INSERT
UPDATE = ActionLogDataAccess.UPDATE
DELETE = ActionLogDataAccess.DELETE

def add(action_type, datatype, tablename, target_id, data_desc, handled=False, dbsession=None, commit=True):
    """

    :type action_type: str
    :type datatype: str
    :type tablename: str
    :type target_id: int
    :type data_desc: str
    :type handled: bool
    :type dbsession: sqlalchemy.orm.Session
    :type commit: bool
    :rtype; Union(pyticas_tetres.db.model.ActionLog, False)
    """
    if dbsession:
        da_actionlog = ActionLogDataAccess(session=dbsession)
    else:
        da_actionlog = ActionLogDataAccess()

    a = ActionLogInfo()
    a.action_type = action_type
    a.target_datatype = datatype
    a.target_table = tablename
    a.target_id = int(target_id) if target_id else None
    a.data_desc = data_desc
    a.handled = handled
    a.user_ip = request.remote_addr
    a.handled_date = None if not handled else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # print('Action Log ====================')
    # import pprint
    # pprint.pprint(a.get_dict())
    # print('================================')

    inserted = da_actionlog.insert(a, print_exception=True)

    if commit or not dbsession:
        da_actionlog.commit()
