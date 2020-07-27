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
    print('# combines cad and iris data to load incident data into tetres system')
    print('')

    sdt_str = input('# Enter start date to load data (e.g. 2015-01-01) : ')
    sdate = datetime.datetime.strptime(sdt_str, '%Y-%m-%d').date()

    edt_str = input('# Enter end date to load data (e.g. 2017-12-31) : ')
    edate = datetime.datetime.strptime(edt_str, '%Y-%m-%d').date()

    print('')
    print('!! Data during the given time period will be deleted.')
    res = input('!! Do you want to proceed data loading process ? [N/y] : ')
    if res.lower() not in ['y', 'ye', 'yes']:
        print('\nAported!')
        exit(1)

    from pyticas_tetres.systasks import initial_data_maker

    try:
        initial_data_maker.load_incident_data(sdate, edate)
    except Exception as ex:
        print('exception:', ex)
