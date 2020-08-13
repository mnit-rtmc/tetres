# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import time
import sys
sys.path.append("Server/src")
import global_settings
import dbinfo

if __name__ == '__main__':
    from pyticas import ticas
    from pyticas.infra import Infra
    from pyticas_tetres.db.cad import conn as conn_cad
    from pyticas_tetres.db.iris import conn as conn_iris
    from pyticas_tetres.db.tetres import conn

    ticas.initialize(global_settings.DATA_PATH)
    infra = Infra.get_infra()

    conn.connect(dbinfo.tetres_db_info())
    conn_cad.connect(dbinfo.cad_db_info())
    conn_iris.connect(dbinfo.iris_incident_db_info())

    time.sleep(1)

    print('')
    print(
        '!! Do not run multiple instances of this program. (DB sync problem can be caused in bulk-insertion and deletion)')
    print('!! Stop TeTRES Server if it is running.')
    print('')
    print('# Have you defined the travel time reliability route in administrator client?')
    print('# calculates travel times during the given time period')
    print('')

    sdt_str = input('# Enter start date to load data (e.g. 2015-01-01) : ')
    sdate = datetime.datetime.strptime(sdt_str, '%Y-%m-%d').date()

    edt_str = input('# Enter end date to load data (e.g. 2017-12-31) : ')
    edate = datetime.datetime.strptime(edt_str, '%Y-%m-%d').date()
    route_id = int(input("Enter the route id: "))
    print('')
    print('!! Data during the given time period will be deleted.')
    res = input('!! Do you want to proceed data loading process ? [N/y] : ')
    if res.lower() not in ['y', 'ye', 'yes']:
        print('\nAported!')
        exit(1)

    filename = '_initial_data_maker.log'
    with open(filename, 'w') as f:
        f.write('started at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')

    from pyticas_tetres.systasks import initial_data_maker

    rw_moe_param_json = {
        "reference_tt_route_id": route_id
    }
    try:
        initial_data_maker.calculate_tt_only(sdate, edate, db_info=dbinfo.tetres_db_info(), rw_moe_param_json=rw_moe_param_json)
        with open(filename, 'a+') as f:
            f.write('ended at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
    except Exception as ex:
        print('exception:', ex)
        with open(filename, 'a+') as f:
            f.write('exception occured at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
