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
    print('!! Do not run multiple instances of this program. (DB sync problem can be caused in bulk-insertion and deletion)')
    print('!! Stop TeTRES Server if it is running.')
    print('')

    print('# This program calculates time-of-day (TOD) reliability for all routes.')
    print('# If you entered target-date as 2014-02-10,')
    print('# TOD reliability will be calculated using travel time data during 2013-02-10 ~ 2014-02-09')
    print('')

    sdt_str = input('# Enter target date (e.g. 2015-01-01) : ')
    target_date = datetime.datetime.strptime(sdt_str, '%Y-%m-%d').date()

    print('')
    res = input('!! Do you want to proceed data loading process ? [N/y] : ')
    if res.lower() not in ['y', 'ye', 'yes']:
        print('\nAported!')
        exit(1)

    filename = '_initial_data_maker.log'
    with open(filename, 'w') as f:
        f.write('started at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')

    from pyticas_tetres.systasks import initial_tod_reliability_maker
    try:
        initial_tod_reliability_maker.run(target_date, db_info=dbinfo.tetres_db_info())
        with open(filename, 'a+') as f:
                f.write('ended at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
    except Exception as ex:
        print('exception:', ex)
        with open(filename, 'a+') as f:
                f.write('exception occured at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
