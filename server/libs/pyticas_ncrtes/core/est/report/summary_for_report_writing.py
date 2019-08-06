# -*- coding: utf-8 -*-

import xlsxwriter

from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def write(filepath, name, edata_list):
    """

    :type filepath: str
    :type name: str
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    """
    logger = getLogger(__name__)
    logger.debug('Writing summary sheets of %s' % name)
    nonon_edata_list = [ edata for edata in edata_list if edata is not None and edata.is_loaded ]
    results = [ _get_summary_from_edata(edata) for edata in nonon_edata_list ]
    _write_summary_xlsx(results, nonon_edata_list, filepath)


def _write_summary_xlsx(results, edata_list, file_path):
    """

    :type results: list[dict]
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    :type file_path: str
    """

    keys = [
        ('station_id', 'Station'),
        # ('date', 'Date'),

        ('srst_time', 'SRST'),
        ('lst_time', 'LST'),
        ('sist_time', 'SIST'),
        ('pst_time', 'PST'),
        ('ncrt_time', 'NCRT'),
        # ('bpst_time', 'BPST'),
        # ('apst_time', 'APST'),
        # ('nfrt_time', 'NRFT'),

        ('rp_time', 'Reported'),

        ('ncrt_u', 'U at NCRT'),
        ('rp_u', 'U at Reported'),

        ('corridor', 'Corridor'),
        ('region', 'Region'),
        ('sub_region', 'SubRegion'),
        ('truckroute_id', 'TruckRoute ID'),

        ('label', 'Label'),
        ('speed_limit', 'Speed Limit'),

        ('snow_start_time', 'Snow Start Time'),
        ('snow_end_time', 'Snow End Time'),


        ('srst_num_time', 'SRST'),
        ('lst_num_time', 'LST'),

        ('ncrt_num_time', 'NCRT'),
        ('rp_num_time', 'Reported Barelane Regain Time'),

        # ('rst_u', 'U at RST'),


        ('ncrt_ratio', 'Ratio at NCRT'),
        # ('rst_ratio', 'Ratio at RST'),

        ('diff_ncrt_and_rt', 'Reported - NCRT (hour)'),
        # ('diff_rst_and_rt', 'Reported - RST (hour)'),

        ('snow_start_idx', 'Snow Start (index)'),
        ('snow_end_idx', 'Snow End (index)'),
        ('srst_idx', 'SRST (index)'),
        ('lst_idx', 'LST (index)'),

        ('bpst_idx', 'BPST (index)'),
        ('pst_idx', 'PST (index)'),
        ('apst_idx', 'APST (index)'),
        ('nfrt_idx', 'NFRT (index)'),

        ('ncrt_idx', 'NCRT (index)'),
        ('rp_idx', 'Reported Barelane Regain Time (index)'),

    ]

    wb = xlsxwriter.Workbook(file_path)
    ws = wb.add_worksheet('data')
    ws.write_row(0, 0, [k[1] for k in keys])
    r = 1
    for res in results:
        _row = []
        for k in keys:
            _v = res.get(k[0], None)
            if _v and 'numpy' in str(type(_v)):
                _v = _v.item()
            _row.append(_v)
        ws.write_row(r, 0, _row)
        r += 1

    for edata in edata_list:
        try:
            _write_station_data_sheet(wb, edata.target_station.station_id, edata)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing data sheet : ' + str(ex))
            from pyticas.tool.tb import traceback
            traceback(ex)
            pass

    wb.close()


def _get_summary_from_edata(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :return:
    """
    snow_route = edata.snow_route
    if snow_route:
        region = snow_route.region
        sub_region = snow_route.truck_station
        truckroute_id = snow_route.id
    else:
        region = sub_region = truckroute_id = ''

    rp_idx = [ rep.reported_regain_time for rep in edata.reported_events ][-1] if edata.reported_events else None

    return {
        'date': edata.snow_event.index_to_time(edata.srst,
                                                     string_format='%m/%d/%y') if edata.srst != None else None,
        'region': region,
        'sub_region': sub_region,
        'truckroute_id': truckroute_id,
        'corridor': edata.target_station.corridor.name,
        'station_id': edata.target_station.station_id,
        'label': edata.target_station.label,
        'speed_limit': edata.target_station.s_limit,
        'snow_start_idx': edata.snow_event.time_to_index(edata.snow_event.snow_start_time),
        'snow_end_idx': edata.snow_event.time_to_index(edata.snow_event.snow_end_time),
        'snow_start_time': edata.snow_event.snow_start_time.strftime('%Y-%m-%d %H:%M'),
        'snow_end_time': edata.snow_event.snow_end_time.strftime('%Y-%m-%d %H:%M'),

        'pst_idx': edata.pst,
        # 'bpst_idx': edata.sbpst,
        # 'apst_idx': edata.sapst,
        # 'nfrt_idx': edata.nfrt,

        'srst_idx': edata.srst,
        'lst_idx': edata.lst,
        # 'rst_idx': edata.rst,
        'ncrt_idx': edata.ncrt,
        'rp_idx': edata.rps[-1] if edata.rps else None,

        'srst_time': edata.snow_event.index_to_time(edata.srst,
                                                          string_format='%H:%M') if edata.srst != None else None,
        'lst_time': edata.snow_event.index_to_time(edata.lst,
                                                         string_format='%H:%M') if edata.lst != None else None,
        'sist_time': edata.snow_event.index_to_time(edata.sist,
                                                         string_format='%H:%M') if edata.sist != None else None,

        'pst_time': edata.snow_event.index_to_time(edata.pst,
                                                         string_format='%H:%M') if edata.pst != None else None,

        # 'bpst_time': edata.snow_event.index_to_time(edata.sbpst,
        #                                               string_format='%H:%M') if edata.sbpst != None else None,
        #
        # 'apst_time': edata.snow_event.index_to_time(edata.sapst,
        #                                               string_format='%H:%M') if edata.sapst != None else None,
        #
        # 'nfrt_time': edata.snow_event.index_to_time(edata.nfrt,
        #                                            string_format='%H:%M') if edata.nfrt != None else None,

        'ncrt_time': edata.snow_event.index_to_time(edata.ncrt,
                                                          string_format='%H:%M') if edata.ncrt != None else None,
        'rp_time': edata.snow_event.index_to_time(edata.rps[-1],
                                                        string_format='%H:%M') if edata.rps else None,

        'srst_num_time': _numbered_time(
            edata.snow_event.index_to_time(edata.srst, as_string=False)) if edata.srst != None else None,
        'lst_num_time': _numbered_time(
            edata.snow_event.index_to_time(edata.lst, as_string=False)) if edata.lst != None else None,
        # 'rst_num_time': _numbered_time(
        #     edata.snow_event.index_to_time(edata.rst, as_string=False)) if edata.rst != None else None,
        'ncrt_num_time': _numbered_time(
            edata.snow_event.index_to_time(edata.ncrt, as_string=False)) if edata.ncrt != None else None,
        'rp_num_time': _numbered_time(
            edata.snow_event.index_to_time(edata.rps[-1], as_string=False)) if edata.rps else None,

        'ncrt_u': edata.sus[edata.ncrt] if edata.ncrt else None,
        # 'rst_u': edata.additional.get('rst_u', None),

        'rp_u': edata.sus[edata.rps[-1]] if edata.rps else None,

        'ncrt_ratio': edata.additional.get('ncrt_ratio', None),
        # 'rst_ratio': edata.additional.get('rst_ratio', None),
        'diff_ncrt_and_rt': ((edata.rps[-1] - edata.ncrt) / 60.0) if edata.rps and edata.ncrt else None,
        # 'diff_rst_and_rt': ((edata.rps[-1] - edata.rst) / 60.0) if edata.rps and edata.rst else None,
    }


def _numbered_time(dt):
    """

    :type dt: datetime.datetime
    :rtype: float
    """
    return dt.hour + round(dt.minute / 60, 2)


def _write_station_data_sheet(wb, sheet_name, edata):
    """

    :type wb: xlsxwriter.Workbook
    :type sheet_name: str
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    if not any(edata.sus):
        return

    col = Col(0)
    timeline = edata.snow_event.data_period.get_timeline()
    n_data = len(timeline)
    rrts = [rep.reported_regain_time for rep in edata.reported_events] if edata.reported_events else []
    if any(rrts):
        sheet_name = sheet_name + '(rp)'
    ws = wb.add_worksheet(sheet_name)

    ws.write_column(0, col.next('time'), ['Time'] + timeline)
    ws.write_column(0, col.next('sk'), ['Smoothed Density'] + edata.sks.tolist())
    ws.write_column(0, col.next('su'), ['Smoothed Speed'] + edata.sus.tolist())
    ws.write_column(0, col.next('su'), ['Smoothed Flow'] + edata.sqs.tolist())

    # ws.write_column(0, col.next('tu'), ['Speed Trend'] + sdata.tu)
    ws.write_column(0, col.next('ks'), ['Density'] + edata.ks.tolist())
    ws.write_column(0, col.next('us'), ['Speed'] + edata.us.tolist())
    ws.write_column(0, col.next('qs'), ['Flow'] + edata.qs.tolist())
    ws.write_column(0, col.next('wn_ffs'), ['WN-FFS'] + [edata.wn_ffs])
    # ws.write_column(0, col.next('fu'), ['NSRFunction Speed'] + sdata.u_by_func)
    ws.write_column(0, col.next('ratios'), ['Normal Ratios'] + (edata.ratios.tolist() if hasattr(edata.ratios, 'tolist') else []))
    ws.write_column(0, col.next('wn_ratios'), ['WetNormal Ratios'] + (edata.wn_sratios.tolist() if hasattr(edata.wn_sratios, 'tolist') else []))

    def _get_idx_data(n_data, indice):
        _data = [None] * n_data
        if not indice:
            return _data
        for idx in indice:
            if idx == None:
                continue
            _data[idx] = edata.sus[idx]
        return _data

    def _get_timepoint_data(n_data, get_func, ignore_ex=True):
        _data = [None] * n_data
        _time = get_func(as_string=False)
        if _time:
            if isinstance(_time, list):
                for _t in _time:
                    try:
                        _point = edata.snow_event.time_to_index(_t)
                        _data[_point] = edata.sus[_point]
                    except Exception as ex:
                        if not ignore_ex:
                            raise ex
                        else:
                            getLogger(__name__).error(str(ex))
            else:
                try:
                    _point = edata.snow_event.time_to_index(_time)
                    _data[_point] = edata.sus[_point]
                except Exception as ex:
                    if not ignore_ex:
                        raise ex
                    else:
                        getLogger(__name__).warn(str(ex))
        return _data

    srst_data = _get_idx_data(n_data, [edata.srst])
    lst_data = _get_idx_data(n_data, [edata.lst])
    sist_data = _get_idx_data(n_data, [edata.sist])
    ncrt_data = _get_idx_data(n_data, [edata.ncrt])
    nfrt_data = _get_idx_data(n_data, [edata.nfrt])
    # bpst_data = _get_idx_data(n_data, [edata.sbpst])
    # apst_data = _get_idx_data(n_data, [edata.sapst])
    pst_data = _get_idx_data(n_data, [edata.pst])

    reported_lanelost_data = _get_timepoint_data(n_data, lambda as_string: [rep.reported_lost_time for rep in
                                                                            edata.reported_events] if edata.reported_events else None)
    reported_regaintime_data = _get_timepoint_data(n_data, lambda as_string: [rep.reported_regain_time for rep in
                                                                              edata.reported_events] if edata.reported_events else None,
                                                   ignore_ex=True)

    ws.write_column(0, col.next('srst_data'), ['SRST'] + srst_data)
    ws.write_column(0, col.next('lst_data'), ['LST'] + lst_data)
    ws.write_column(0, col.next('sist_data'), ['SIST'] + sist_data)
    ws.write_column(0, col.next('pst_data'), ['PST'] + pst_data)
    ws.write_column(0, col.next('ncrt_data'), ['NCRT'] + ncrt_data)
    # ws.write_column(0, col.next('bpst_data'), ['BPST'] + bpst_data)
    # ws.write_column(0, col.next('apst_data'), ['APST'] + apst_data)
    # ws.write_column(0, col.next('nfrt_data'), ['NFRT'] + nfrt_data)
    ws.write_column(0, col.next('reported_lanelost_data'), ['Reported Lane Lost Time Point'] + reported_lanelost_data)
    ws.write_column(0, col.next('reported_regaintime_data'),
                    ['Reported Barelane Regain Time Point'] + reported_regaintime_data)

    k_list = [v for v in range(5, 200)]

    if edata.normal_func and edata.normal_func.is_valid() and edata.normal_func.daytime_func.recovery_function.is_valid():
        u_list = edata.normal_func.daytime_func.recovery_speeds(k_list)
        ws.write_column(0, col.next('recovery_pattern_k'), ['Recovery-Pattern K'] + k_list)
        ws.write_column(0, col.next('recovery_pattern_u'), ['Recovery-Pattern U'] + u_list)

        # u_list = edata.normal_func.daytime_func.reduction_speeds(k_list)
        # ws.write_column(0, col.next('reduction_pattern_k'), ['Reduction-Pattern K'] + k_list)
        # ws.write_column(0, col.next('reduction_pattern_u'), ['Reduction-Pattern U'] + u_list)

        uk_function = edata.normal_func.daytime_func.get_uk_function()
        if uk_function and uk_function._wn_uk:
            u_list = uk_function.wet_normal_speeds(k_list) if edata.wn_ffs else []
            ws.write_column(0, col.next('recovery_pattern_k'), ['WetNormal-Pattern K'] + k_list)
            ws.write_column(0, col.next('recovery_pattern_u'), ['WetNormal-Pattern U'] + u_list)


    # if edata.normal_func.daytime_func.recovery_function.is_valid():
    #     u_list = edata.normal_func.daytime_func.recovery_speeds(k_list)
    #     ws.write_column(0, col.next('recovery_pattern_k'), ['Recovery Pattern K'] + k_list)
    #     ws.write_column(0, col.next('recovery_pattern_u'), ['Recovery Pattern U'] + u_list)
    #
    # if edata.normal_func.daytime_func.reduction_function.is_valid():
    #     u_list = edata.normal_func.daytime_func.reduction_speeds(k_list)
    #     ws.write_column(0, col.next('reduction_pattern_k'), ['Reduction Pattern K'] + k_list)
    #     ws.write_column(0, col.next('reduction_pattern_u'), ['Reduction Pattern U'] + u_list)
    if edata.normal_func:
        u_list = edata.normal_func.nighttime_func.get_night_speeds()
        t_list = edata.normal_func.nighttime_func.get_timeline()
        ws.write_column(0, col.next('nighttime_time'), ['NightTime Timeline'] + t_list)
        ws.write_column(0, col.next('nighttime_speed'), ['NightTime Avg Speed'] + u_list)


class Col(object):
    def __init__(self, init_col):
        self.col = init_col
        self._cols = {}

    def next(self, name):
        self._cols[name] = self.col
        self.col += 1
        return self.col - 1

    def c(self, name):
        return self._cols.get(name, -1)
