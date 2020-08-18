# -*- coding: utf-8 -*-
from pyticas_tetres.api.admin.systemconfig import create_rw_moe_param_object, save_rw_param_object

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import sys
import time

sys.path.append("Server/src")
import global_settings
import dbinfo

if __name__ == '__main__':
    from pyticas import ticas
    from pyticas.infra import Infra
    from pyticas_tetres.db.tetres import conn

    ticas.initialize(global_settings.DATA_PATH)
    infra = Infra.get_infra()

    conn.connect(dbinfo.tetres_db_info())

    time.sleep(1)

    print('')
    print(
        '!! Do not run multiple instances of this program. (DB sync problem can be caused in bulk-insertion and deletion)')
    print('!! Stop TeTRES Server if it is running.')
    print('')
    print('# Have you defined the travel time reliability route in administrator client?')
    print('# calculates travel times and moe values during the given time period')
    print('')

    sdt_str = input('# Enter start date to load data (e.g. 2015-01-01) : ')
    sdate = datetime.datetime.strptime(sdt_str, '%Y-%m-%d').date()

    edt_str = input('# Enter end date to load data (e.g. 2017-12-31) : ')
    edate = datetime.datetime.strptime(edt_str, '%Y-%m-%d').date()
    moe_lane_capacity = input("Enter moe_lane_capacity: ")
    moe_critical_density = input("Enter moe_critical_density: ")
    moe_congestion_threshold_speed = input("Enter moe_congestion_threshold_speed: ")
    rw_moe_param_json = {
        "rw_moe_lane_capacity": moe_lane_capacity,
        "rw_moe_critical_density": moe_critical_density,
        "rw_moe_congestion_threshold_speed": moe_congestion_threshold_speed,
    }
    print('')
    print('!! Data during the given time period will be updated if exists or created if does not exist.')
    res = input('!! Do you want to proceed data loading process ? [N/y] : ')
    if res.lower() not in ['y', 'ye', 'yes']:
        print('\nAborted!')
        exit(1)

    filename = '_initial_data_maker.log'
    with open(filename, 'w') as f:
        f.write('started at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')

    from pyticas_tetres.systasks import initial_data_maker
    from pyticas_tetres.da.route import TTRouteDataAccess

    try:
        ttr_route_da = TTRouteDataAccess()
        ttr_ids = [ttri.id for ttri in ttr_route_da.list()]
        ttr_route_da.close_session()
        initial_data_maker.create_or_update_tt_and_moe(sdate, edate, db_info=dbinfo.tetres_db_info(),
                                                       rw_moe_param_json=rw_moe_param_json)
        for route_id in ttr_ids:
            rw_moe_param_info = create_rw_moe_param_object(route_id, moe_critical_density, moe_lane_capacity,
                                                           moe_congestion_threshold_speed,
                                                           datetime.datetime.strptime(sdt_str, '%Y-%m-%d').strftime(
                                                               '%Y-%m-%d %H:%M:%S'),
                                                           datetime.datetime.strptime(edt_str, '%Y-%m-%d').strftime(
                                                               '%Y-%m-%d %H:%M:%S'), status='Completed'
                                                           )

            rw_moe_object_id = save_rw_param_object(rw_moe_param_info)

        with open(filename, 'a+') as f:
            f.write('ended at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
    except Exception as ex:
        print('exception:', ex)
        with open(filename, 'a+') as f:
            f.write('exception occured at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
