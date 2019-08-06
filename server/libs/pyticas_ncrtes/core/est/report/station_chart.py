# -*- coding: utf-8 -*-
import math
import os

import numpy as np
import xlsxwriter
from matplotlib import pyplot as plt

from pyticas_ncrtes import ncrtes
from pyticas_ncrtes.core import setting, data_util
from pyticas_ncrtes.core.est.helper import hill_helper
from pyticas_ncrtes.logger import getLogger

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

REPORT_MODE = True


def write(output_dir, name, edata_list, prefix=''):
    """

    :type output_dir: str
    :type name: str
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    """
    logger = getLogger(__name__)
    for idx, edata in enumerate(edata_list):
        logger.debug('Writing chart image of %s' % edata.target_station.station_id)
        # if edata.ncrt or (not edata.pst and not edata.stable_speed_region_before_pst and not edata.stable_speed_region_after_pst):
        #     continue
        _write(idx, edata, output_dir, prefix)


def _write(num, edata, output_path, prefix=''):
    """

    :type num: int
    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type output_path: str
    :type prefix: str
    """
    logger = getLogger(__name__)
    if edata is None or not edata.is_loaded:
        logger.debug('  - Data is not loaded : %s' % edata.target_station.station_id if edata else 'N/A')
        return

    sw = setting.SW_3HOURS
    sks, sus = data_util.smooth(edata.ks, sw), data_util.smooth(edata.us, sw)

    hills = hill_helper.create_uk_hills(edata.ks, edata.us, sks, sus)
    ecs = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']

    long_title = '%s (%s[prj_id=%s, s_limit=%d, label=%s], %s)' % (
        edata.snow_event.snow_period.get_date_string(),
        edata.target_station.station_id,
        edata.snow_route.id if edata.snow_route else 'N/A',
        edata.target_station.s_limit,
        edata.target_station.label,
        edata.target_station.corridor.name)

    title = '%s (%s, %s)' % (
        edata.snow_event.snow_period.get_date_string(),
        edata.target_station.station_id,
        edata.target_station.corridor.name)

    if REPORT_MODE:
        fig = plt.figure(figsize=(16, 9), dpi=100, facecolor='white')
    else:
        fig = plt.figure(dpi=100, facecolor='white')
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(223)
    ax3 = plt.subplot(224)

    ax1.axhline(y=edata.target_station.s_limit, c='b')
    if edata.wn_ffs:
        ax1.axhline(y=edata.wn_ffs, c='r')

    #ax1.plot(edata.us, marker='', label='Speed', c='#3794D5')
    ax1.plot(edata.ks, marker='', label='Density', c='#ADE2CD')
    # if edata.wn_avg_us is not None:
    #     ax1.plot(edata.wn_avg_us, c='#8C65C5', label='WN Avg. Speed')

    # ax1.plot(edata.qus, c='#746F69', label='Q-Us')


    if edata.normal_func:
        nt_us = edata.normal_func.nighttime_func.speeds(edata.snow_event.data_period.get_timeline(as_datetime=True))
    else:
        nt_us = [None]*edata.n_data

    ax1.plot(nt_us, c='k', label='Nighttime Speed')

    #nt_ks = edata.normal_func.nighttime_func.densities(edata.snow_event.data_period.get_timeline(as_datetime=True))
    #ax1.plot(nt_ks, c='k', label='Nighttime Density')

    # snow start and end time
    sstime = edata.snow_event.time_to_index(edata.snow_event.snow_start_time)
    setime = edata.snow_event.time_to_index(edata.snow_event.snow_end_time)
    ax1.axvline(x=sstime, c='#948D90')  # grey vertical line
    ax1.axvline(x=setime, c='#948D90')

    # draw chart using UK-Hills
    n_data = len(edata.us)
    ecs = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']
    markers = ['o', 'x', 'd', '^', '<', '>', 'v', 's', '*', '+']
    ls = '-'
    used = []
    for gidx, hill in enumerate(hills):
        lw = 1
        c = ecs[gidx % len(ecs)]
        marker = '|'
        for midx in range(len(markers)):
            marker_stick = '%s-%s' % (c, markers[midx])
            if marker_stick not in used:
                marker = markers[midx]
                used.append(marker_stick)
                break


        sidx, eidx = hill.sidx, hill.eidx
        _sidx, _eidx = sidx, eidx
        ax2.plot(edata.sks[_sidx:_eidx + 1], edata.sus[_sidx:_eidx + 1]*edata.sks[_sidx:_eidx + 1], c=c, marker=marker, ms=4, zorder=2)
        ax3.plot(edata.sks[_sidx:_eidx + 1], edata.sus[_sidx:_eidx + 1], c=c, marker=marker, ms=4, zorder=2)

        _ks, _us = [None] * len(edata.ks), [None] * len(edata.us)
        for idx in range(sidx, eidx + 1):
            if idx >= n_data - 1:
                break
            # _ks[idx] = edata.merged_sks[idx]
            # _us[idx] = edata.merged_sus[idx]

            _ks[idx] = edata.ks[idx]
            _us[idx] = edata.us[idx]

        ax1.plot(_us, lw=lw, ls=ls, c=c)

    # Normal and Wet-Normal Avg UK
    _recv_ks = np.array(list(range(5, 120)))

    if edata.normal_func:
        uk_function = edata.normal_func.daytime_func.get_uk_function()
        if uk_function and uk_function.is_valid():
            ax2.plot(_recv_ks, np.array(uk_function.speeds(_recv_ks))*_recv_ks, ls=':', lw=2, label='Normal Avg. QK')
            # ax2.plot(_recv_ks, uk_function.speeds(_recv_ks), ls=':', lw=2, label='Normal Avg. UK')
            ax3.plot(_recv_ks, uk_function.speeds(_recv_ks), ls=':', lw=2, label='Normal Avg. UK')

            if uk_function._wn_uk:
                ax2.plot(_recv_ks, np.array(uk_function.wet_normal_speeds(_recv_ks))*_recv_ks, ls=':', lw=2, label='Wet-Normal QK')
                # ax2.plot(_recv_ks, uk_function.wet_normal_speeds(_recv_ks, edata.wn_ffs, edata.k_at_wn_ffs), ls=':', lw=2, label='Wet-Normal UK')
                ax3.plot(_recv_ks, uk_function.wet_normal_speeds(_recv_ks), ls=':', lw=2, label='Wet-Normal UK')

    # ax2.scatter(edata.ks, edata.us, c='#5D63FF', marker='.')
    # ax3.scatter(edata.sks, edata.sus, c='#5D63FF', marker='.')

    ms = [14, 13, 12, 11, 10, 8, 7]
    us = data_util.smooth(edata.us, 15)

    # srst
    if edata.srst is not None:
        data = np.array([None] * len(us))
        data[edata.srst] = us[edata.srst]
        ax1.plot(data, marker='o', ms=ms[0], c='#4ED8FF', label='SRST')  # light blue circle

    # lst
    if edata.lst is not None:
        data = np.array([None] * len(us))
        data[edata.lst] = us[edata.lst]
        ax1.plot(data, marker='o', ms=ms[1], c='#FFAD2A', label='LST')  # orange circle

    # sist
    if edata.sist is not None:
        data = np.array([None] * len(us))
        data[edata.sist] = us[edata.sist]
        ax1.plot(data, marker='o', ms=ms[2], c='#68BD20', label='SIST')  # orange green


    # # rst
    # if edata.rst is not None:
    #     data = np.array([None] * len(us))
    #     data[edata.rst] = us[edata.rst]
    #     ax1.plot(data, marker='o', ms=ms[2], c='#68BD20', label='RST')  # green

    # ncrt
    if edata.ncrt is not None:
        data = np.array([None] * len(us))
        data[edata.ncrt] = us[edata.ncrt]
        # ax1.plot(data, marker='o', ms=ms[3], c='#FF0512', label='NCRT (%d)' % edata.ncrt_type)  # navy blue
        ax1.plot(data, marker='o', ms=ms[3], c='#FF0512', label='NCRT')  # navy blue

    # pst
    if edata.pst:
        data = np.array([None] * len(us))
        data[edata.pst] = us[edata.pst]
        ax1.plot(data, marker='o', ms=ms[4], c='#9535CC', label='PST')  # purple diamod


    # sbpst
    # if edata.sbpst:
    #     data = np.array([None] * len(us))
    #     data[edata.sbpst] = us[edata.sbpst]
    #     ax1.plot(data, marker='p', ms=ms[4], c='#bdb76b', label='BPST')  # DarkKhaki
    #
    # # sapst
    # if edata.sapst:
    #     data = np.array([None] * len(us))
    #     data[edata.sapst] = us[edata.sapst]
    #     ax1.plot(data, marker='p', ms=ms[4], c='#cdad00', label='APST')  # gold3

    # nfrt
    if edata.nfrt:
        data = np.array([None] * len(us))
        data[edata.nfrt] = us[edata.nfrt]
        ax1.plot(data, marker='*', ms=ms[4], c='#0072CC', label='NFRT')  # light blue


    # # stable speed area around pst
    # if not edata.ncrt and (edata.sbpst or edata.sapst):
    #     data = np.array([None] * len(us))
    #     if edata.sbpst:
    #         data[edata.sbpst] = us[edata.sbpst]
    #         ax1.plot(data, marker='p', ms=ms[4], c='#FF00F8', label='NCRT-C')  # light-pink pentagon
    #     if edata.sapst and not edata.ncrt:
    #         data[edata.sapst] = us[edata.sapst]
    #         ax1.plot(data, marker='p', ms=ms[4], c='#FF00F8', label='')  # light-pink pentagon

    # snowday-ffs
    # if edata.snowday_ffs:
    #     ax1.axhline(y=edata.snowday_ffs, c='#33CC0A')
    # if edata.nfrt:
    #     data = np.array([None] * len(us))
    #     data[edata.nfrt] = us[edata.nfrt]
    #     ax1.plot(data, marker='*', ms=ms[5], c='#CC00B8', label='SnowDay-FFS')  # navy blue

    # reported time
    for rp in edata.rps:
        data = np.array([None] * len(us))
        data[rp] = us[rp]
        ax1.plot(data, marker='^', ms=ms[6], c='#FF0512', label='RBRT')  # red circle


    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0, box.width * 0.9, box.height])
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), numpoints=1, prop={'size': 12})

    ulist = np.array([ 90, 100, 110, 120, 150, 200, 300 ])
    klist = np.array([ 80, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600 ])
    qlist = np.array([ 0, 2000, 3000, 3500, 4000, 4500, 5000, 6000, 7000 ])
    _maxq = max(edata.sks * edata.sus)
    _maxk = max(edata.sks)
    _maxu = max(edata.sus)
    maxq = qlist[np.where(qlist > _maxq)][0]
    maxu = ulist[np.where(ulist > _maxu)][0]
    maxk = klist[np.where(klist > _maxk)][0]

    ax1.set_title(long_title)
    ax2.set_title(title + ' - Smoothed Q-K')
    ax3.set_title(title + ' - Smoothed U-K')
    ax1.set_ylabel('speed, density')
    ax1.set_xlabel('time')
    ax1.set_ylim(ymin=0, ymax=maxu)
    ax1.set_xlim(xmin=0, xmax=len(edata.sus))
    # ax2.set_ylabel('speed')
    ax2.set_ylabel('flow')
    ax2.set_xlabel('density')
    # ax2.set_ylim(ymin=0, ymax=100)

    ax2.set_ylim(ymin=0, ymax=maxq)
    ax2.set_xlim(xmin=0, xmax=maxk)
    ax3.set_ylim(ymin=0, ymax=maxu)
    ax3.set_xlim(xmin=0, xmax=maxk)
    ax3.set_ylabel('speed')
    ax3.set_xlabel('density')

    ax1.grid()
    ax2.grid()
    ax3.grid()
    ax2.legend(prop={'size': 12})
    ax3.legend(prop={'size': 12})

    if not REPORT_MODE:
        plt.show()
    else:
        import datetime
        timeline = edata.snow_event.data_period.get_timeline(as_datetime=True)
        timeline = [ t - datetime.timedelta(seconds=setting.DATA_INTERVAL) for t in timeline ]

        ntimes = [t.strftime('%H:%M') for idx, t in enumerate(timeline) if
                  idx % (2 * 3600 / setting.DATA_INTERVAL) == 0]
        loc_times = [idx for idx, t in enumerate(timeline) if idx % (2 * 3600 / setting.DATA_INTERVAL) == 0]
        ax1.set_xticks(loc_times)
        ax1.set_xticklabels(ntimes, rotation=90)

        plt.tight_layout()
        postfix = ' (rp)' if edata.reported_events else ''
        file_path = os.path.join(output_path, '(%03d) %s%s%s.png' % (num, prefix, edata.target_station.station_id, postfix))
        fig.savefig(file_path, dpi=100, bbox_inches='tight')

    plt.close(fig)

    if 0:
        wb = xlsxwriter.Workbook(os.path.join(ncrtes.get_infra().get_path('tmp', create=True),
                                              '%s %s (night).xlsx' % (
                                                  edata.snow_event.snow_period.get_date_string(),
                                                  edata.target_station.station_id)))
        ws = wb.add_worksheet('night-data')
        prd = edata.snow_event.data_period.clone()
        prd.interval = setting.DATA_INTERVAL

        ws.write_column(0, 0, ['time'] + prd.get_timeline(as_datetime=False))
        ws.write_column(0, 1, ['speed'] + edata.us.tolist())
        ws.write_column(0, 2, ['nighttime average speed'] + edata.night_us.tolist())
        ws.write_column(0, 3, ['smoothed speed'] + edata.sus.tolist())
        # ws.write_column(0, 4, ['smoothed speed (2h)'] + edata.lsus.tolist())
        # ws.write_column(0, 5, ['smoothed speed (1h)'] + edata.llsus.tolist())
        ws.write_column(0, 6, ['nighttime ratio'] + edata.night_ratios.tolist())

        wb.close()


def _scatter(ax, df_k, df_u, title='', use_arrow=True, xlabel='', ylabel='', datalabel='', xmin=0,
             ymin=0, xlimit_margin=5, ylimit_margin=5, head_width=0.4, head_length=0.5, target_points=None,
             rps_indice=None, n90s_indice=None, n80s_indice=None, color='', lw=1, markder='o'):
    if use_arrow:
        ecs = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']
        for idx in range(0, len(df_k) - 1):
            x1 = df_k[idx]
            y1 = df_u[idx]
            x2 = df_k[idx + 1] - x1
            y2 = df_u[idx + 1] - y1
            if color:
                c = color
            else:
                c = ecs[idx % len(ecs)]
            try:
                head_width = 0
                head_length = 0
                ax.arrow(x1, y1, x2, y2, head_width=head_width, head_length=head_length, fc=c, ec=c, zorder=1,
                         length_includes_head=True, lw=lw)
            except:
                pass

    ax.scatter(df_k, df_u, marker='o', c='#DDDDDD', s=10, label=datalabel, zorder=2)
    ax.scatter(df_k[:1], df_u[:1], marker='d', c='#FD64FF', s=60, label='start' if title else '', zorder=3)
    ax.scatter(df_k[-1:], df_u[-1:], marker='s', c='k', s=60, label='end' if title else '', zorder=3)
    if target_points:
        ecs = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']
        for idx, tp in enumerate(target_points):
            c = ecs[idx % len(ecs)]
            ax.scatter(df_k[tp:tp + 1], df_u[tp:tp + 1], marker='d', c=c, s=80, label='target@%d' % tp, zorder=4)

    if rps_indice != None and any(rps_indice):
        for idx, rp in enumerate(rps_indice):
            ax.scatter(df_k[rp:rp + 1], df_u[rp:rp + 1], marker='^', c='r', s=80, label='reported@%d' % rp, zorder=4)

    if n80s_indice != None and any(n80s_indice):
        for idx, rp in enumerate(n80s_indice):
            if rp < 0:
                continue
            ax.scatter(df_k[rp:rp + 1], df_u[rp:rp + 1], marker='^', c='#15863D', s=80, zorder=5)

    if n90s_indice != None and any(n90s_indice):
        for idx, rp in enumerate(n90s_indice):
            if rp < 0:
                continue
            ax.scatter(df_k[rp:rp + 1], df_u[rp:rp + 1], marker='^', c='#5743F3', s=80, zorder=5)

    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    ax.set_ylim(ymin=ymin, ymax=df_u.max() + ylimit_margin)
    ax.set_xlim(xmin=xmin, xmax=df_k.max() + xlimit_margin)
    ax.grid(True)


def simplified_uk(ks, us, tolerance=0.5, angle_rate=0.25):
    """

    :type ks: numpy.ndarray
    :type us: numpy.ndarray
    :type tolerance: float
    :type angle_rate: float
    :rtype: (numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
    """

    # simplify U-K data
    min_angle = np.pi * angle_rate
    # print('min_angle=%f, pi=%f, degree=%f' % (min_angle, np.pi, 180*angle_rate))
    points = np.array([ks.tolist(), us.tolist()]).T
    simplified = np.array(_rdp(points.tolist(), tolerance))
    sx, sy = simplified.T

    # find turning points
    directions = np.diff(simplified, axis=0)
    theta = _angle(directions)
    turning_points = np.where(theta > min_angle)[0] + 1

    sindice = []
    for idx, k in enumerate(sx):
        ridx = np.where((us == sy[idx]) & (ks == sx[idx]))
        sindice.append(ridx[0][0])
    sindice = np.array(sindice)
    return sx, sy, sindice, turning_points


def _angle(dir):
    """
    Returns the angles between vectors.

    Parameters:
    dir is a 2D-array of shape (N,M) representing N vectors in M-dimensional space.

    The return value is a 1D-array of values of shape (N-1,), with each value
    between 0 and pi.

    0 implies the vectors point in the same direction
    pi/2 implies the vectors are orthogonal
    pi implies the vectors point in opposite directions
    """
    dir2 = dir[1:]
    dir1 = dir[:-1]
    return np.arccos((dir1 * dir2).sum(axis=1) / (
        np.sqrt((dir1 ** 2).sum(axis=1) * (dir2 ** 2).sum(axis=1))))


def _rdp(points, epsilon):
    """
    Reduces a series of points to a simplified version that loses detail, but
    maintains the general shape of the series.
    """
    dmax = 0.0
    index = 0
    for i in range(1, len(points) - 1):
        d = _point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d
    if dmax >= epsilon:
        results = _rdp(points[:index + 1], epsilon)[:-1] + _rdp(points[index:], epsilon)
    else:
        results = [points[0], points[-1]]

    return results


def _point_line_distance(point, start, end):
    if (start == end):
        return _distance(point, start)
    else:
        n = abs(
            (end[0] - start[0]) * (start[1] - point[1]) - (start[0] - point[0]) * (end[1] - start[1])
        )
        d = math.sqrt(
            (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2
        )
        return n / d


def _distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
