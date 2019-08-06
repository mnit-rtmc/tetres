# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import csv
import os

from sqlalchemy.sql import text

from pyticas_rwis import conn

# for sqlite
# DB_INFO = {
#     'engine' : 'sqlite',
#     'filename' : 'ttrms.db'
# }

# for postgresql
DB_INFO = {
    'engine': 'postgresql',
    'host': 'localhost',
    'port': 5432,
    'db_name': 'rwis',
    'user': 'postgres',
    'passwd': 'natsrl207'
}

conn.connect(DB_INFO)


def insert_sf_data(DATA_DIR):
    conn.engine.execute("TRUNCATE surface")
    conn.session.commit()
    fields = ['site_id', 'sen_id', 'dtime', 'cond', 'temp', 'frz_temp', 'chem', 'chem_pct', 'depth', 'ice_pct', 'salinity', 'conductivity', 'blackice_signal', 'error']
    fields_string = ', '.join(fields)

    for f in os.listdir(DATA_DIR):
        if not f.endswith('.txt'):
            continue
        year = f.replace('.txt', '').split('_')[-1]
        filepath = os.path.join(DATA_DIR, f)
        data_initial = open(filepath, "rU")
        creader = csv.reader((line.replace('\0', '') for line in data_initial), delimiter="|")
        is_different_type = False
        print('Start for %s' % f)
        for ridx, row in enumerate(creader):
            if len(row) != 14:
                is_different_type = True
                break
            to_db = row
            if ridx == 0:
                continue

            #conn.session.execute("INSERT INTO surface (%s) VALUES (%s);" % (fields_string, fields_params), dictionary)
            conn.session.execute(text("INSERT INTO surface (%s) VALUES (%s);" % (fields_string, ','.join(["'%s'" % str(v) if v else "''" for v in to_db]))))
            # site_id, sen_id, dtime, cond, temp, frz_temp, chem, chem_pct, depth, ice_pct, salinity, conductivity, blackice_signal, error = to_db

            #
            # model_data = model.Surface(
            #     site_id=site_id,
            #     sen_id=sen_id,
            #     dtime=dtime,
            #     cond=cond,
            #     temp=temp,
            #     frz_temp=frz_temp,
            #     chem=chem,
            #     chem_pct=chem_pct,
            #     depth=depth,
            #     ice_pct=ice_pct,
            #     salinity=salinity,
            #     conductivity=conductivity,
            #     blackice_signal=blackice_signal,
            #     error=error
            # )
            #
            # conn.session.add(model_data)

            if ridx and ridx % 10000 == 0:
                print('  - commit', ridx, end='')
                conn.session.commit()
                conn.close()
                conn.connect(DB_INFO)
                print('  : done')


        if is_different_type:
            print('  - "%s" has different file format' % f)
        else:
            print('  - commit', ridx)
            conn.session.commit()

        print('Done for %s' % f)

def _v(v):
    if v == '' or v == None or v == 'None' or v == '-':
        return None
    elif v == 0:
        return 0
    else:
        return v

def insert_atm_data(DATA_DIR):
    conn.engine.execute("TRUNCATE atmospheric")
    conn.session.commit()

    fields = ['site_id', 'dtime', 'temp', 'temp_alt', 'temp_max', 'temp_min', 'dew_point', 'rh', 'pc_type', 'pc_intens', 'pc_rate', 'pc_accum', 'pc_accum_10min', 'pc_start_dtime', 'pc_end_dtime', 'pc_past_1hour', 'pc_past_3hours', 'pc_past_6hours', 'pc_past_12hours', 'pc_past_24hours', 'pc_time_since', 'wet_build_temp', 'vis_distance', 'vis_situation', 'barometric', 'wnd_spd_avg', 'wnd_spd_gust', 'wnd_dir_avg', 'wnd_dir_gust']
    fields_string = ', '.join(fields)

    n_col = 29
    already = []
    for f in os.listdir(DATA_DIR):
        if not f.endswith('.txt'):
            continue
        if f in already:
            print('!! already inserted file "%s" !!' % f)
            continue

        year = f.split('_')[1][:4]

        filepath = os.path.join(DATA_DIR, f)

        data_initial = open(filepath, "r")
        creader = csv.reader((line.replace('\0', '') for line in data_initial), delimiter="|")

        is_different_type = False
        print('Start for %s' % f)
        for ridx, row in enumerate(creader):
            if not row:
                print('==> ', row)
                print('  - no data : %d line' % ridx)
                continue
            if ridx == 1 and len(row) != n_col:
                is_different_type = True
                break
            to_db = row
            if ridx == 0:
                continue

            site_id, dtime, temp, temp_alt, temp_max, temp_min, dew_point, rh, pc_type, pc_intens, pc_rate, pc_accum, pc_accum_10min, pc_start_dtime, pc_end_dtime, pc_past_1hour, pc_past_3hours, pc_past_6hours, pc_past_12hours, pc_past_24hours, pc_time_since, wet_build_temp, vis_distance, vis_situation, barometric, wnd_spd_avg, wnd_spd_gust, wnd_dir_avg, wnd_dir_gust = to_db
            to_db = _sanit_number(to_db)
            site_id, _1, temp, temp_alt, temp_max, temp_min, dew_point, rh, pc_type, pc_intens, pc_rate, pc_accum, pc_accum_10min, _2, _3, pc_past_1hour, pc_past_3hours, pc_past_6hours, pc_past_12hours, pc_past_24hours, pc_time_since, wet_build_temp, vis_distance, vis_situation, barometric, wnd_spd_avg, wnd_spd_gust, wnd_dir_avg, wnd_dir_gust = to_db

            pc_start_dtime = pc_start_dtime if pc_start_dtime else None
            pc_end_dtime = pc_end_dtime if pc_end_dtime else None

            to_db[fields.index('dtime')] = dtime
            to_db[fields.index('pc_start_dtime')] = pc_start_dtime
            to_db[fields.index('pc_end_dtime')] = pc_end_dtime

            tmp = [_v(v) for v in to_db]
            fields_value = ', '.join([ 'null' if v == None else "'%s'"%v for v in tmp ])
            conn.session.execute(text("INSERT INTO atmospheric (%s) VALUES (%s);" % (fields_string, fields_value)))

            #
            # model_data = model.Atmospheric(
            #     site_id=site_id,
            #     dtime=dtime,
            #     temp=temp,
            #     temp_alt=temp_alt,
            #     temp_max=temp_max,
            #     temp_min=temp_min,
            #     dew_point=dew_point,
            #     rh=rh,
            #     pc_type=pc_type,
            #     pc_intens=pc_intens,
            #     pc_rate=pc_rate,
            #     pc_accum=pc_accum,
            #     pc_accum_10min=pc_accum_10min,
            #     pc_start_dtime=pc_start_dtime,
            #     pc_end_dtime=pc_end_dtime,
            #     pc_past_1hour=pc_past_1hour,
            #     pc_past_3hours=pc_past_3hours,
            #     pc_past_6hours=pc_past_6hours,
            #     pc_past_12hours=pc_past_12hours,
            #     pc_past_24hours=pc_past_24hours,
            #     pc_time_since=pc_time_since,
            #     wet_build_temp=wet_build_temp,
            #     vis_distance=vis_distance,
            #     vis_situation=vis_situation,
            #     barometric=barometric,
            #     wnd_spd_avg=wnd_spd_avg,
            #     wnd_spd_gust=wnd_spd_gust,
            #     wnd_dir_avg=wnd_dir_avg,
            #     wnd_dir_gust=wnd_dir_gust
            # )
            # conn.session.add(model_data)
            if ridx and ridx % 10000 == 0:
                print('  - commit', ridx, end='')
                conn.session.commit()
                print('  : done')

        if is_different_type:
            print('  - "%s" has different file format' % f)
        else:
            print('  - commit', ridx)
            conn.session.commit()

        print('Done for %s' % f)


def _sanit_number(datalist):
    for didx, data in enumerate(datalist):
        if data == 'None' or data == None or data == '':
            datalist[didx] = None
            continue
        if data == 0 or data == '0':
            datalist[didx] = 0
            continue
        if not isinstance(data, str):
            continue
        dstr = ''.join(i for i in data if i.isdigit() or i == '.')
        if dstr:
            datalist[didx] = float(dstr) if '.' in dstr else int(dstr)
        else:
            datalist[didx] = None

    return datalist


if __name__ == '__main__':
    # SF_DATA_DIR = "Z:\\RWIS DATA\\surface"
    # insert_sf_data(SF_DATA_DIR)

    # ATM_DATA_DIR = "Z:\\RWIS DATA"
    # insert_atm_data(ATM_DATA_DIR)

    pass
