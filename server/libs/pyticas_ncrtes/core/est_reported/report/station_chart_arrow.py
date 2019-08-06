# -*- coding: utf-8 -*-
import math

import numpy as np
from matplotlib import pyplot as plt

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

REPORT_MODE = True


def write(output_dir, name, edata_list, prefix=''):
    """

    :type output_dir: str
    :type name: str
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    """
    for edata in edata_list:
        _write(edata, output_dir, prefix)


def _write(edata, output_path, prefix=''):
    """

    :type edata: pyticas_ncrtes.core.etypes.ESTData
    :type output_path: str
    :type prefix: str
    """
    if edata is None or not edata.is_loaded:
        return

    ecs = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#9400D3']

    long_title = '%s (%s[s_limit=%d, label=%s], %s)' % (
        edata.snow_event.snow_period.get_date_string(),
        edata.target_station.station_id,
        edata.target_station.s_limit,
        edata.target_station.label,
        edata.target_station.corridor.name)

    title = '%s (%s, %s)' % (
        edata.snow_event.snow_period.get_date_string(),
        edata.target_station.station_id,
        edata.target_station.corridor.name)


    fig = plt.figure(dpi=100, facecolor='white')
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(222)
    ax3 = plt.subplot(223)
    ax4 = plt.subplot(224)

    from pyticas_ncrtes.core.nsrf import cache as nsr_cache
    normal_data = nsr_cache.loads_data(edata.target_station.station_id, edata.months)
    dt_func = edata.normal_func.daytime_func
    cidata = dt_func.cidata
    _recv_ks = list(range(10, 120))
    all_ks = list(normal_data.daytime_data.all_uk.keys())
    all_us = [normal_data.daytime_data.all_uk[_k] for _k in all_ks]

    axs = [ax1, ax2, ax3, ax4]
    for ax in axs:
        ax.scatter(all_ks, all_us, marker='x', color='#E0E0E0')
        ax.plot(cidata.ciks, cidata.cils, ls='-.', lw=2, label='cils')
        ax.plot(_recv_ks, dt_func.uk_func_speeds(_recv_ks), ls='-.', lw=2, label='uk-function')

    _scatter(ax1, edata.sks, edata.sus, 'smoothed u-k (4h)')
    _scatter(ax2, edata.lsks, edata.lsus, 'smoothed u-k (2h)')
    _scatter(ax3, edata.llsks, edata.llsus, 'smoothed u-k (1h)')
    _scatter(ax4, edata.lllsks, edata.lllsus, 'smoothed u-k (30min)')

    for ax in axs:
        #ax.set_title(title)
        ax.set_ylabel('speed')
        ax.set_xlabel('density')
        ax.set_ylim(ymin=0, ymax=90)
        ax.set_xlim(xmin=0, xmax=140)
        ax.grid(True)
        ax.legend()

    fig.suptitle(long_title)
    ##############
    fig = plt.figure(dpi=100, facecolor='white')
    ax1 = fig.add_subplot(111)
    ax1.scatter(all_ks, all_us, marker='x', color='#E0E0E0')
    ax1.plot(cidata.ciks, cidata.cils, ls='-.', lw=2, label='cils')
    ax1.plot(_recv_ks, dt_func.uk_func_speeds(_recv_ks), ls='-.', lw=2, label='uk-function')
    _scatter(ax1, edata.ks, edata.us, '5min u-k')
    ax1.set_ylabel('speed')
    ax1.set_xlabel('density')
    ax1.set_ylim(ymin=0, ymax=90)
    ax1.set_xlim(xmin=0, xmax=140)
    ax1.grid(True)
    ax1.legend()
    fig.suptitle(long_title)
    ##############
    fig = plt.figure(dpi=100, facecolor='white')
    ax1 = fig.add_subplot(111)
    ax1.plot(edata.us, marker='', label='us', c='#3794D5')
    ax1.plot(edata.ks, marker='', label='ks', c='#ADE2CD')

    for idx, h in enumerate(edata.hills):
        data = np.array([None] * len(edata.sus))
        data[h.sidx:h.eidx + 1] = edata.sus[h.sidx:h.eidx + 1]
        c = ecs[idx % len(ecs)]
        ax1.plot(data, c=c, lw=2)

    for idx, h in enumerate(edata.small_speed_hills):
        data = np.array([None] * len(edata.llsus))
        data[h.sidx:h.eidx + 1] = edata.llsus[h.sidx:h.eidx + 1]
        c = ecs[idx % len(ecs)]
        ax1.plot(data, c=c, lw=1)

    nt_us = edata.normal_func.nighttime_func.speeds(edata.snow_event.data_period.get_timeline(as_datetime=True))
    ax1.plot(nt_us, c='k', label='us (night)')
    fig.suptitle(long_title)

    ax1.set_ylabel('speed, density')
    ax1.set_xlabel('time interval')
    ax1.set_ylim(ymin=0, ymax=90)
    ax1.grid(True)
    ax1.legend()

    plt.show()

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
