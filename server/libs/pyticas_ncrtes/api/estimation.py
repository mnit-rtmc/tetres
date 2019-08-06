# -*- coding: utf-8 -*-

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import queue
import threading

from flask import request, Response

from pyticas.tool.json import loads as json_loads
from pyticas_ncrtes import api_urls
from pyticas_server import protocol
from pyticas_ncrtes.service import estimation


def register_api(app):

    # @app.route(api_urls.ESTIMATION, methods=['POST'])
    # def ncrtes_estimation():
    #     json_str = request.form.get('param')
    #     request_param = json_loads(json_str)
    #     """:type: pyticas_ncrtes.ncrtes_types.EstimationRequestInfo"""
    #
    #     output_path = estimation.estimate(request_param)
    #
    #     if not output_path:
    #         return protocol.response_fail('Fail to estimate')
    #     else:
    #         return protocol.response_success(output_path)

    # TODO: For Reporting Progress, use event-stream
    @app.route(api_urls.ESTIMATION, methods=['POST'])
    def ncrtes_estimation():
        json_str = request.form.get('param')
        request_param = json_loads(json_str)
        """:type: pyticas_ncrtes.itypes.EstimationRequestInfo"""

        msgs = queue.Queue()
        estimation.estimate(request_param, msgs)
        #_run_estimation(request_param, msgs)
        return protocol.response_success(None)
        #return Response(event_stream(msgs), mimetype="text/event-stream")


def _run_estimation(request_param, msgs):
    t = threading.Thread(target=estimation.estimate, args=(request_param, msgs,))
    t.start()

def event_stream(msgs):
    """

    :type msgs: queue.Queue
    :return:
    """
    def _stream():
        while True:
            msg = msgs.get()
            if msg == None:
                break
            print('>> msg : ', msg)
            msgs.task_done()
            yield '%s\n'% msg

    return _stream()

#
# def _run_case(corridor_name, casefile):
#     case_name = '%s - %s' % (os.path.basename(casefile)[:-4], corridor_name)
#     print('Start : ', case_name)
#
#     snow_routes = SnowRoute.load_snow_routes(os.path.join(INFO_PATH, 'snow_routes.csv'))
#     rep_snow_start_time, rep_snow_end_time, reported_events, reported_events_list = _read_reported_events(casefile,
#                                                                                                           corridor_name,
#                                                                                                           snow_routes)
#
#     prd = Period(rep_snow_start_time, rep_snow_end_time, 300)
#     months = get_normal_months(prd)
#     except_stations = get_except_stations()
#     print('Except stations : ', except_stations)
#     output_path = os.path.join(infra.get_path('ncrtes', create=True))
#     if ntypes not in json.TYPE_MODULES:
#         json.TYPE_MODULES.append(ntypes)
#
#     def tsi_filter(nsr_func):
#         if nsr_func.station.is_radar_station() or nsr_func.station.corridor.name != corridor_name or nsr_func.station.station_id in except_stations:
#             return False
#         return True
#
#     # find real representative snow start and end time
#     rep_sst = []
#     rep_set = []
#     prj_ids = [rpe.prj_id for rpe in reported_events_list]
#     wsi = func_loader.get_winter_season(months)
#     if not wsi:
#         print('Winter season is not found')
#         return
#
#     nsr_funcs = func_loader.get_nsr_functions(wsi.id)
#
#     if not nsr_funcs:
#         print('Target stations are not found')
#         return
#
#     for idx, nsr_func in enumerate(nsr_funcs):
#         if tsi_filter and not tsi_filter(nsr_func):
#             continue
#         st = nsr_func.station
#         if st.station_id != 'S780':
#             continue
#
#         for sr in snow_routes:
#             if ((sr.id in prj_ids or sr.id_old in prj_ids) and
#                         st in sr.get_route().rnodes):
#                 rep_sst.append(min([rep.snow_start_time for rep in reported_events.get(sr.id, [])]))
#                 rep_set.append(max([rep.snow_end_time for rep in reported_events.get(sr.id, [])]))
#     rep_sst.sort()
#     rep_set.sort()
#
#     if rep_sst and rep_set:
#         rep_snow_start_time = rep_sst[0]
#         rep_snow_end_time = rep_set[-1]
#
#         rep_snow_start_time = rep_snow_start_time.replace(second=0, microsecond=0)
#         rep_snow_end_time = rep_snow_end_time.replace(second=0, microsecond=0)
#     ######
#
#     output_file_origin = os.path.join(output_path, '%s.xlsx' % case_name)
#     output_file = util.numbered_filename(output_file_origin)
#
#     countour_file = os.path.join(output_path, '%s.png' % case_name)
#     countour_file = util.numbered_filename(countour_file)
#
#     speed_countour_file = os.path.join(output_path, '%s-speed.png' % case_name)
#     speed_countour_file = util.numbered_filename(speed_countour_file)
#
#     # if os.path.exists(output_file_origin):
#     #    return
#
#     sdata_list = nsrt_est.run_single(rep_snow_start_time, rep_snow_end_time, months, snow_routes, reported_events,
#                                      tsi_filter)
#     prd_str = get_event_name(prd)
#
#     if any(sdata_list):
#         xlsx_writer.write(output_file, sdata_list)
#         contour_writer.write(countour_file, corridor_name, sdata_list)
#         speed_contour_writer.write(speed_countour_file, corridor_name, sdata_list)
#     else:
#         print('No Results !!')
#
#     print('The results are saved in %s' % output_path)
#     profile.print_prof_data()
