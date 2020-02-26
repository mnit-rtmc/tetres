# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import time

import dbinfo
import global_settings

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
    print('!! Do not run multiple instances of this program. '
          '(DB sync problem can be caused in bulk-insertion and deletion)')
    print('!! Stop TeTRES Server if it is running.')
    print('')
    print('# Have you defined the travel time reliability route in administrator client?')
    print('# This program loads weather and incident data,')
    print('# and calculate travel times during the given time period')
    print('# Then the operating condition data will be linked to each travel time data')
    print('')

    sdate = datetime.datetime.strptime('2018-01-01', '%Y-%m-%d').date()
    edate = datetime.datetime.strptime('2018-01-31', '%Y-%m-%d').date()

    print('')
    print('!! Data during the given time period will be deleted.')
    res = input('!! Do you want to proceed data loading process ? [N/y] : ')
    if res.lower() not in ['y', 'ye', 'yes']:
        print('\nAborted!')
        exit(1)

    # with open('_dataloader.log', 'w') as f:
    #     f.write('started at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')

    from pyticas_tetres.systasks import initial_data_maker

    try:
        initial_data_maker.run(sdate, edate, db_info=dbinfo.tetres_db_info())
        # with open('_dataloader.log', 'a+') as f:
        #     f.write('ended at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
    except Exception as ex:
        print('EX [dataloader.py]:', ex)
        # with open('_dataloader.log', 'a+') as f:
        #     f.write('exception occured at ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
