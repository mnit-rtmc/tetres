# -*- coding: utf-8 -*-

import numpy as np

from pyticas.tool import tb
from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import etypes, data_util
from pyticas_ncrtes.core import setting
from pyticas_ncrtes.core.est import target, wnffs_finder, ncrt_finder, wn_uk
from pyticas_ncrtes.da.target_lane_config import TargetLaneConfigDataAccess
from pyticas_ncrtes.logger import getLogger

FFS_K = setting.FFS_K

UTH = 10
NTH = 5
UTH_FOR_HIGH_K = 30
LOW_K = 10

U_DIFF_THRESHOLD = 8
K_DIFF_THRESHOLD = 5

CONGESTED_SPEED = 30

DEBUG_MODE = False
SAVE_CHART = False

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def estimate(num, tsi, edata):
    """

    :type num: int
    :type tsi: pyticas_ncrtes.itypes.TargetStationInfo
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: pyticas_ncrtes.core.etypes.ESTData
    """
    if not _check_edata(tsi, edata):
        return edata

    logger = getLogger(__name__)
    logger.info('>>> Determine NCRT Process for Target Station %s' % (edata.target_station.station_id))

    try:
        _pre_process_before_determination(edata)

        has_recovered_region = wnffs_finder.find(edata)
        if not has_recovered_region:
            _chart(edata, edata.ratios, edata.lsratios, edata.sratios)
            return

        wn_uk.make(edata)

        ncrt_finder.find(edata)

        _chart(edata, edata.ratios, edata.lsratios, edata.sratios)

    except Exception as ex:
        logger.error(tb.traceback(ex, f_print=False))

    logger.info('<<< End of NCRT Determination Process for Target Station %s' % (edata.target_station.station_id))

    return edata


def prepare_data(tsi, station, year, stime, etime, snow_routes, reported, normal_func):
    """

    :type tsi: pyticas_ncrtes.itypes.TargetStationInfo
    :type station: pyticas.ttypes.RNodeObject
    :type year: int
    :type stime: datetime.datetime
    :type etime: datetime.datetime
    :type snow_routes: list[pyticas_ncrtes.core.etypes.SnowRoute]
    :type reported: dict[str, list[pyticas_ncrtes.core.etypes.ReportedEvent]]
    :type normal_months: list[(int, int)]

    :rtype: pyticas_ncrtes.core.etypes.ESTData
    """
    sevent = etypes.SnowEvent(stime, etime)
    infra = ncrtes.get_infra()
    target_station = infra.get_rnode(tsi.station_id)

    tlcDA = TargetLaneConfigDataAccess()
    tlci = tlcDA.get_by_station_id(year, station.station_id)
    if tlci:
        valid_detectors = [infra.get_detector(det_name.strip()) for det_name in tlci.detectors.split(',')]
    else:
        valid_detectors = target.get_target_detectors(station)

    if not valid_detectors:
        return None

    try:
        edata = etypes.ESTData(tsi, target_station, sevent, snow_routes, reported, normal_func)
        edata.prepare_data(detectors=valid_detectors)
        return edata

    except Exception as ex:
        log = getLogger(__name__)
        log.warning('!!!!! Error : %s : %s' % (tsi.station_id, ex))
        from pyticas.tool import tb
        tb.traceback(ex)
        return None


def _check_edata(tsi, edata):
    """

    :type tsi: pyticas_ncrtes.itypes.TargetStationInfo
    :type nsr_func: pyticas_ncrtes.core.etypes.NSRFunction
    :rtype: bool
    """
    log = getLogger(__name__)
    if not edata:
        log.info('> %s : No ESTData' % tsi.station_id)
        return False

    if not edata or not edata.is_loaded:
        log.info('> %s : Data are not loaded for snow event' % tsi.station_id)
        return False

    # if not edata.search_start_idx:
    #     log.info('> %s : No Search Start Idx' % tsi.station_id)
    #     return False

    return True


def _pre_process_before_determination(edata):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    logger = getLogger(__name__)

    # determine FFS
    if edata.normal_func and edata.normal_func.is_valid():
        normal_ffs = edata.normal_func.daytime_func.get_FFS()
    else:
        normal_ffs = None
    edata.normal_ffs = normal_ffs

    # determine snowday-FFS
    snowday_ffs = _snowday_ffs(edata)
    edata.snowday_ffs = snowday_ffs
    if not snowday_ffs:
        logger.warning('Snowday FFS is not found')

    # get/make normal ratios
    normal_ratios = _normal_ratios(edata, snowday_ffs)
    edata.normal_ratios = normal_ratios

    # may-recovered-speed : FFS * 0.9
    may_recovered_speed = _may_recovered_speed(edata, rth=0.9)
    if not may_recovered_speed:
        logger.debug(' - Cannot determine `may-recovered-speed` ')
        return
    edata.may_recovered_speed = may_recovered_speed

    logger.debug(' - FFS : %s' % snowday_ffs)
    logger.debug(' - may_recovered_speed : %s' % may_recovered_speed)

    # speed and ratio threshold for candidate time intervals of free-flow
    edata.ncrt_search_uth, edata.ncrt_search_rth = _uth_rth(edata)


def _snowday_ffs(edata):
    """


    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: float
    """
    ffs_percentile = 80

    after_snow_ffs = None
    tus, tks = edata.sus[edata.snow_event.snow_end_index:], edata.sks[edata.snow_event.snow_end_index:]
    wh = np.where( (tks < FFS_K) & (tks > LOW_K) & (tus > edata.target_station.s_limit) )[0]
    if any(wh):
        after_snow_ffs = np.percentile(tus[wh], ffs_percentile)

    tus, tks = edata.sus[:edata.snow_event.snow_start_index], edata.sks[:edata.snow_event.snow_start_index]
    wh = np.where( (tks < FFS_K) & (tks > LOW_K) )[0]
    if any(wh):
        before_snow_ffs = np.percentile(tus[wh], ffs_percentile)
        if not after_snow_ffs or before_snow_ffs > after_snow_ffs:
            return before_snow_ffs

    wh = np.where( (tks < FFS_K) )[0]
    if any(wh):
        before_snow_ffs = np.percentile(tus[wh], ffs_percentile)
        if not after_snow_ffs or before_snow_ffs > after_snow_ffs:
            return before_snow_ffs
    # else:
        # tus, tks = edata.sus[edata.snow_event.snow_end_index:], edata.sks[edata.snow_event.snow_end_index:]
        # wh = np.where( (tks < FFS_K) & (tks > LOW_K) )[0]
        # if any(wh):
    return after_snow_ffs

    # return None


def _normal_ratios(edata, ffs):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type ffs: float
    :rtype: numpy.ndarray
    """
    if edata.normal_func and edata.normal_func.is_valid():
        return edata.normal_ratios
    else:
        return np.array([ (u / ffs) if u else -1 for u in edata.lsus ])


def _uth_rth(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype: float, float
    """
    uth = -1
    rth = 0.7

    maxu_limit = edata.normal_ffs if edata.normal_ffs else edata.snowday_ffs
    _ssidx, _seidx = edata.snow_event.snow_start_index, edata.snow_event.snow_end_index
    minu = min(edata.sus[_ssidx:_seidx])
    while minu >= uth and rth < 1.0:
        uth = maxu_limit * rth
        rth += 0.05

    # Test
    # s_limit = edata.target_station.s_limit
    # if uth < s_limit:
    #     uth = s_limit
    #     rth = maxu_limit / uth

    return uth, rth


def _may_recovered_speed(edata, rth=0.9):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :rtype:
    """
    getLogger(__name__).debug(' - Snowday FFS : %s' % edata.snowday_ffs)

    normal_ffs = edata.normal_ffs
    snowday_ffs = edata.snowday_ffs

    if normal_ffs and snowday_ffs:
        return max(normal_ffs, snowday_ffs) * rth

    if normal_ffs:
        return normal_ffs* rth

    if snowday_ffs:
        return snowday_ffs * rth

    return None


def _smoothing_data(edata):
    """
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    """
    sw = setting.SW_2HOURS
    ssu, ssk = 5, 3

    sus = data_util.smooth(edata.us, sw)
    sks = data_util.smooth(edata.ks, sw)

    qus = data_util.stepping(sus, ssu)
    qks = data_util.stepping(sks, ssk)

    edata.sus = sus
    edata.sks = sks
    edata.qus = np.array(qus)
    edata.qks = np.array(qks)


def _chart(edata, ratios, lsratios, sratios):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type ratios:  numpy.ndarray
    :type lsratios:  numpy.ndarray
    :type sratios:  numpy.ndarray
    """
    if not DEBUG_MODE:
        return

    import matplotlib.pyplot as plt

    infra = ncrtes.get_infra()
    output_path = infra.get_path('ncrtes/ut', create=True)

    plt.figure(facecolor='white', figsize=(16, 8))
    plt.plot(edata.lsks, edata.lsus)
    _ks = list(range(5, 100))
    _nus = edata.normal_func.daytime_func.recovery_speeds(_ks)
    _wnus = edata.normal_func.daytime_func.recovery_function.wet_normal_speeds(_ks)
    plt.plot(edata.lsks, edata.lsus)
    plt.plot(_ks, _nus, c='k')
    plt.plot(_ks, _wnus, c='orange')
    plt.grid()

    plt.figure(facecolor='white', figsize=(16, 8))
    ax1 = plt.subplot(111)
    ax1.plot(edata.us, c='#aaaaaa')
    ax1.plot(edata.ks, c='#90A200')
    ax1.plot(edata.night_us, c='k')
    ax1.plot(edata.qus, c='r')
    # ax1.plot(edata.qks, c='#C2CC34')
    ax1.plot(edata.sus, c='#0B7CCC')
    # ax1.plot(edata.qus, c='#CC50AA')

    if edata.wn_ffs:
        ax1.axhline(y=edata.wn_ffs, c='r', label='wn_ffs') # r

    if edata.snowday_ffs:
        ax1.axhline(y=edata.snowday_ffs, c='#E5E900', label='snowday_ffs') # light yellow

    ax1.axhline(y=edata.target_station.s_limit, c='b')
    if edata.ncrt_search_uth:
        ax1.axhline(y=edata.ncrt_search_uth, c='k')

    if edata.may_recovered_speed:
        ax1.axhline(y=edata.may_recovered_speed, c='k')

    ax1.axvline(x=edata.snow_event.snow_start_index, c='#EAEAEA', ls='-.')
    ax1.axvline(x=edata.snow_event.snow_end_index, c='#EAEAEA', ls='-.')

    if edata.ncrt_search_sidx:
        ax1.axvline(x=edata.ncrt_search_sidx, c='b', ls='-.')
    if edata.ncrt_search_eidx:
        ax1.axvline(x=edata.ncrt_search_eidx, c='b', ls='-.')

    if edata.wn_ffs_idx:
        ax1.axvline(x=edata.wn_ffs_idx, c='g')

    if edata.ncrt:
        ax1.axvline(x=edata.ncrt, c='r', lw=2, label='ncrt')

    ax2 = None
    if ratios is not None and any(ratios):
        ax2 = ax1.twinx()
        # ax2.plot(edata.normal_ratios, c='#FF001A')
        ax2.plot(lsratios, c='#00CC04', label='normal-ratios')
        # ax2.plot(sratios, c='#CC34B1')
        ax2.set_ylim(ymax=1.4, ymin=0.5)

    if edata.wn_ffs and edata.wn_sratios is not None and any(edata.wn_sratios):
        if not ax2:
            ax2 = ax1.twinx()
        ax2.plot(edata.wn_sratios, c='#CC07B7', label='wn-ratios')
        ax2.plot(edata.wn_qratios, c='k', label='wn-qatios')

    plt.title('%s (%s, s_limit=%d)' % (
        edata.target_station.station_id,
        edata.target_station.corridor.name,
        edata.target_station.s_limit
    ))

    plt.grid()

    if ax2:
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1+h2, l1+l2)
    else:
        ax1.legend()

    plt.show()
    filename = '%s.png' % edata.target_station.station_id
    # plt.savefig(os.path.join(output_path, filename))
    plt.show()

    #
    # filename = '%s.xlsx' % edata.target_station.station_id
    # wb = xlsxwriter.Workbook(np.os.path.join(output_path, filename))
    # ws = wb.add_worksheet('data')
    # ws.write_column(0, 0, ['Time'] + edata.snow_event.data_period.get_timeline(as_datetime=False))
    # ws.write_column(0, 1, ['Density'] + edata.ks.tolist() )
    # ws.write_column(0, 2, ['Speed'] + edata.us.tolist() )
    # ws.write_column(0, 3, ['QK'] + qks.tolist() )
    # ws.write_column(0, 4, ['QU'] + qus.tolist() )
    # if edata.normal_func and edata.normal_func.is_valid():
    #     klist = list(range(5, 100))
    #     ulist = edata.normal_func.daytime_func.recovery_speeds(klist)
    #     ws.write_column(0, 5, ['NormalK'] + klist )
    #     ws.write_column(0, 6, ['NormalU'] + ulist )
    # wb.close()