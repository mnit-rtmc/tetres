# -*- coding: utf-8 -*-
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from flask import jsonify, request
from pyticas_ncrtes.da.winter_season import WinterSeasonDataAccess

from pyticas_ncrtes import api_urls, itypes
from pyticas_ncrtes.core.month import get_normal_months_from_year


def register_api(app):

        @app.route(api_urls.TSI, methods = ['POST'])
        def ncrtes_target_station_identification():

            from pyticas_ncrtes import ncrtes
            from pyticas_ncrtes.service import target_station_identification
            from multiprocessing import Process
            from pyticas import ticas
            from pyticas_ncrtes.app import NCRTESApp
            from pyticas_ncrtes.service.truck_route_updater import target_station_and_snowroute_info

            logger = getLogger(__name__)

            year = int(request.form.get('year'))
            months = get_normal_months_from_year(year)
            infra = ncrtes.get_infra()

            ws = WinterSeasonDataAccess()
            wsi = ws.get_by_months(months)
            if not wsi:
                wsi = itypes.WinterSeasonInfo()
                wsi.set_months(months)
                wsi.name = 'WinterSeason %s-%s' % (months[0][0], months[-1][0])
                ws.insert(wsi, autocommit=True)
            ws.close()

            #######################
            data_path = ticas._TICAS_.data_path
            n_process = 5
            stations = []
            for n in range(n_process):
                stations.append([])

            for cidx, corr in enumerate(infra.get_corridors()):
                if not corr.dir or corr.is_CD() or corr.is_Rev() or corr.is_RTMC():
                    continue

                for sidx, st in enumerate(corr.stations):
                    if not st.is_normal_station() or not st.detectors:
                        continue
                    stations[sidx % n_process].append(st.station_id)

            procs = []
            for idx in range(n_process):
                p = Process(target=target_station_identification.run, args=(idx + 1, stations[idx], months, data_path, NCRTESApp.DB_INFO))
                p.start()
                procs.append(p)

            for p in procs:
                p.join()


            # print('# find alternatives....')
            # for n in range(n_process):
            #     stations[n] = []
            #
            # for cidx, corr in enumerate(infra.get_corridors()):
            #     if not corr.dir or corr.is_CD() or corr.is_Rev() or corr.is_RTMC():
            #         continue
            #
            #     counts = [ len(st_list) for idx, st_list in enumerate(stations)]
            #     tidx = counts.index(min(counts))
            #
            #     for sidx, st in enumerate(corr.stations):
            #         if not st.is_normal_station() or not st.detectors:
            #             continue
            #         stations[tidx].append(st.station_id)

            # for idx, stlist in enumerate(stations):
            #     print('# %d (%d): %s' % (idx, len(stlist), stlist))
            # input('# enter to continue: ')

            # procs = []
            # for idx in range(n_process):
            #     p = Process(target=tsi_alternative.run, args=(idx + 1, stations[idx], months, data_path, NCRTESApp.DB_INFO))
            #     p.start()
            #     procs.append(p)

            for p in procs:
                p.join()

            ##################


            # corr = infra.get_corridor_by_name('I-35W (NB)')
            # for sidx, st in enumerate(corr.stations):
            #     nf = nsrf.get_normal_function(st, months)


            target_station_and_snowroute_info(year)

            return jsonify( {'code' : 1, 'message' : 'success'} )


        # @app.route(api_urls.TSI, methods = ['POST'])
        # def ncrtes_target_station_identification():
        #     from pyticas.infra import Infra
        #     from pyticas_ncrtes.service import tsi
        #     from multiprocessing import Process
        #     from pyticas import ticas
        #     from pyticas_ncrtes.app import NCRTESApp
        #     from pyticas_ncrtes.service.update import target_station_and_snowroute_info
        #
        #     data_path = ticas._TICAS_.data_path
        #
        #     year = int(request.form.get('year'))
        #     months = get_normal_months_from_year(year)
        #     infra = Infra.get_infra()
        #
        #     n_process = 2
        #     stations = []
        #     for n in range(n_process):
        #         stations.append([])
        #
        #     for cidx, corr in enumerate(infra.get_corridors()):
        #         if not corr.dir or corr.is_CD() or corr.is_Rev() or corr.is_RTMC():
        #             continue
        #
        #         for sidx, st in enumerate(corr.stations):
        #             if st.is_temp_station() or not st.detectors:
        #                 continue
        #             stations[sidx % n_process].append(st.station_id)
        #
        #     procs = []
        #     for idx in range(n_process):
        #         p = Process(target=tsi.run, args=(idx + 1, stations[idx], months, data_path, NCRTESApp.DB_INFO))
        #         p.start()
        #         procs.append(p)
        #
        #     for p in procs:
        #         p.join()
        #
        #     target_station_and_snowroute_info(year)
        #     return jsonify( {'code' : 1, 'message' : 'success'} )
