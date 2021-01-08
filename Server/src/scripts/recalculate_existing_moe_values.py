# -*- coding: utf-8 -*-

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
    from pyticas_tetres.util.traffic_file_checker import has_traffic_files
    from pyticas_tetres.systasks import initial_data_maker

    ticas.initialize(global_settings.DATA_PATH)
    infra = Infra.get_infra()

    time.sleep(1)

    print('')
    print(
        '!! Do not run multiple instances of this program. (DB sync problem can be caused in bulk-insertion and deletion)')
    print('!! Stop TeTRES Server if it is running.')
    print('')
    print('# Have you defined the travel time reliability route in administrator client?')
    print('# recalculates all the exisitng moe values')
    print('')
    print('!! All the exisitng MOE values will be recalculated.')
    res = input('!! Do you want to proceed data loading process ? [N/y] : ')
    if res.lower() not in ['y', 'ye', 'yes']:
        print('\nAborted!')
        exit(1)
    from pyticas_tetres.db.tetres import conn

    conn.connect(dbinfo.tetres_db_info())
    from pyticas_tetres.da.route_wise_moe_parameters import RouteWiseMOEParametersDataAccess

    moe_calculation_data_access = RouteWiseMOEParametersDataAccess()
    moe_calculation_data = moe_calculation_data_access.search_by_completed_status()
    data_missing_flag = False
    for each_calculation in moe_calculation_data:
        sdt_str = each_calculation.start_time.split()[0]
        edt_str = each_calculation.end_time.split()[0]
        if not has_traffic_files(sdt_str, edt_str):
            print("Missing traffic files for the given time range: {} - {}".format(sdt_str, edt_str))
            print("Please check if you have put the traffic files in the proper directory structure.")
            print("Failed to calculate moe for the given time range.")
            data_missing_flag = True
    if data_missing_flag:
        exit(1)

    for each_calculation in moe_calculation_data:
        sdt_str = each_calculation.start_time.split()[0]
        sdate = datetime.datetime.strptime(sdt_str, '%Y-%m-%d').date()

        edt_str = each_calculation.end_time.split()[0]
        edate = datetime.datetime.strptime(edt_str, '%Y-%m-%d').date()

        rw_moe_param_json = {
            "rw_moe_lane_capacity": each_calculation.moe_lane_capacity,
            "rw_moe_critical_density": each_calculation.moe_critical_density,
            "rw_moe_congestion_threshold_speed": each_calculation.moe_congestion_threshold_speed,
        }
        route_ids = [each_calculation.reference_tt_route_id]

        try:
            initial_data_maker.create_or_update_tt_and_moe(sdate, edate, db_info=dbinfo.tetres_db_info(),
                                                           rw_moe_param_json=rw_moe_param_json, route_ids=route_ids)


        except Exception as ex:
            print('exception:', ex)
