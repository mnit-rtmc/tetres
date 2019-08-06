# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import matplotlib

font = {'family': 'Calibri',
        'weight': 'normal',
        'size': 16}

matplotlib.rc('font', **font)
import matplotlib.pyplot as plt

import numpy as np
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from pyticas_ncrtes.core.est.report import distance
from pyticas_ncrtes.core.est.report import report_helper
from pyticas_ncrtes.logger import getLogger


def write(filepath, name, edata_list):
    """

    :type filepath: str
    :type name: str
    :type edata_list: list[pyticas_ncrtes.core.etypes.ESTData]
    """
    logger = getLogger(__name__)
    logger.debug('Writing speed contour chart image of %s' % name)

    if not edata_list:
        return

    timeline = edata_list[0].snow_event.data_period.get_timeline(as_datetime=True)
    n_data = len(timeline)

    c_data = []
    c_y_labels = []
    c_corridor_ids = []
    c_snow_route = []
    c_station_ids = []
    c_stations = []
    c_recovery_points = []

    nonon_edata_list = [ edata for edata in edata_list if edata is not None and edata.is_loaded ]
    n_stations = len(nonon_edata_list)

    for sidx in range(0, n_stations):

        edata = nonon_edata_list[sidx]
        if edata is None or not edata.is_loaded:
            continue
        edata_next = nonon_edata_list[sidx + 1] if sidx < n_stations - 1 else None
        target_station = edata.target_station

        c_station_ids.append(target_station.station_id)
        c_stations.append(target_station)
        mp_map = distance.accumulated_distances(c_stations)
        reported_regain_times = report_helper.get_reported_lane_regain_time(edata, as_datetime=True)
        reported_lost_times = report_helper.get_reported_lane_lost_time(edata, as_datetime=True)

        srst = edata.snow_event.index_to_time(edata.srst, as_string=False) if edata.srst != None else None
        lst = edata.snow_event.index_to_time(edata.lst, as_string=False) if edata.lst != None else None
        pst = edata.snow_event.index_to_time(edata.pst, as_string=False) if edata.pst != None else None
        sist = edata.snow_event.index_to_time(edata.sist, as_string=False) if edata.sist != None else None
        ncrt = edata.snow_event.index_to_time(edata.ncrt, as_string=False) if edata.ncrt != None else None
        # sbpst = edata.snow_event.index_to_time(edata.sbpst, as_string=False) if edata.sbpst != None else None
        # sapst = edata.snow_event.index_to_time(edata.sapst, as_string=False) if edata.sapst != None else None
        nfrt = edata.snow_event.index_to_time(edata.nfrt, as_string=False) if edata.nfrt != None else None

        sst = report_helper.get_snow_start_time(edata, as_datetime=True)
        set = report_helper.get_snow_end_time(edata, as_datetime=True)

        reported_regains = []
        if reported_regain_times:
            for v in reported_regain_times:
                try:
                    vi = edata.snow_event.time_to_index(v)
                    reported_regains.append(vi)
                except Exception as ex:
                    getLogger(__name__).warn(str(ex))

        reported_losts = []
        if reported_lost_times:
            for v in reported_lost_times:
                try:
                    vi = edata.snow_event.time_to_index(v)
                    reported_losts.append(vi)
                except Exception as ex:
                    getLogger(__name__).warn(str(ex))

        # recovery points
        recovery_points = {
            'snow start': edata.snow_event.time_to_index(sst),
            'snow end': edata.snow_event.time_to_index(set),
            'srst': edata.snow_event.time_to_index(srst) if srst else None,
            'lst': edata.snow_event.time_to_index(lst) if lst else None,
            'pst': edata.snow_event.time_to_index(pst) if pst else None,
            'sist': edata.snow_event.time_to_index(sist) if sist else None,
            'ncrt': edata.snow_event.time_to_index(ncrt) if ncrt else None,
            # 'sbpst': edata.snow_event.time_to_index(sbpst) if sbpst else None,
            # 'sapst': edata.snow_event.time_to_index(sapst) if sapst else None,
            'nfrt': edata.snow_event.time_to_index(nfrt) if nfrt else None,
            'reported regains': reported_regains,
            'reported losts': reported_losts,
        }

        if sidx == 0:
            c_data.append(edata.sus)
            c_y_labels.append('')
            c_corridor_ids.append('')
            c_snow_route.append('')
            c_recovery_points.append({})

        sr = edata.snow_route
        if sr:
            y_label = '{0}, {1}, {2}, {3}'.format(sr.id,
                                                  target_station.label,
                                                  target_station.station_id,
                                                  mp_map.get(target_station.station_id, ''))
        else:
            y_label = '{0}, {1}, {2}'.format(target_station.label,
                                             target_station.station_id,
                                             mp_map.get(target_station.station_id, '')
                                             )
        c_data.append(edata.sus)
        c_y_labels.append(y_label)
        c_corridor_ids.append(target_station.corridor.name)
        c_recovery_points.append(recovery_points)

        if edata_next:
            d = distance.distutil.distance_in_mile(target_station, edata_next.target_station)
            n_half = int(round(d / 0.5 / 2, 0))

            # print('-> ', sdata.target_station.station_id, sdata_next.target_station.station_id, d, n_half)

            for nidx in range(n_half):
                c_data.append(edata.sus)
                c_y_labels.append('')
                c_corridor_ids.append('')
                c_snow_route.append('')
                c_recovery_points.append({})

            for nidx in range(n_half):
                c_data.append(edata_next.sus)
                c_y_labels.append('')
                c_corridor_ids.append('')
                c_snow_route.append('')
                c_recovery_points.append({})

    _contour(name, timeline, c_data, c_recovery_points, c_y_labels, c_corridor_ids, c_snow_route, filepath)


def _contour(name, timeline, range_data, recovery_points, y_labels, corridor_ids, snow_routes, file_path):
    """

    :type name: str
    :type timeline:
    :type range_data:
    :type recovery_points:
    :type y_labels:
    :type corridor_ids:
    :type snow_routes:
    :type file_path: str
    :return:
    """
    logging = getLogger(__name__)

    y = np.array(range(len(y_labels)))
    x = np.array(range(len(timeline)))
    Z = np.array(range_data)
    # y_labels = [ ', '.join(reversed(lb.replace(')', '').replace('(', '').split('\n'))) for lb in y_labels ]

    if 0:
        y = y[:20]
        x = x[:200]
        Z = [rd[:200] for rd in range_data[:20]]

    len_y = len(Z)
    if not len_y:
        logging.info('No data for {0}'.format(name))
        return

    len_x = len(Z[0])

    for vv in range_data:
        for idx, rv in enumerate(vv):
            if rv:
                vv[idx] = rv
            else:
                vv[idx] = 0

    y_scatter = {}
    x_scatter = {}
    t_lines = {}

    # print([ (k, v) for k, v in recovery_points[1].items() ])
    for idx in range(len(timeline)):
        for k in recovery_points[1].keys():
            y_ar = y_scatter.get(k, [])
            x_ar = x_scatter.get(k, [])
            lc = t_lines.get(k, [])
            for sidx, v in enumerate(recovery_points):
                vv = v.get(k, None)
                if vv == idx or (isinstance(vv, list) and idx in vv):
                    x_ar.append(idx)
                    y_ar.append(sidx)
                    lc.append((idx, sidx))
            y_scatter[k] = y_ar
            x_scatter[k] = x_ar
            t_lines[k] = lc

    lines = {}
    for key, value in t_lines.items():
        prev_p = None
        lc = []
        for (x, y) in sorted(value, key=lambda v: v[1]):
            if not prev_p:
                prev_p = (x, y)
                continue
            lc.append([(prev_p[0], prev_p[1]), (x, y)])
            prev_p = (x, y)
        lines[key] = lc

    dpi = 96
    img_size_limit = 32768
    #height_pixel = min(500 + 15 * len_y, img_size_limit)
    #width_pixel = min(400 + 5 * len_x, img_size_limit)

    height_pixel = min(300 + 15 * len_y, img_size_limit)
    width_pixel = min(200 + 2 * len_x, img_size_limit)
    width = width_pixel / dpi
    height = height_pixel / dpi

    colors = [
        (0.5, 0.125, 0),  # dark red
        (1, 0, 0),  # red
        (0.8, 0.2, 1.0),  # light purple
        (0.1, 0.1, 1.0),  # blue
        (0.13, 0.6, 0.13),  # green
        (0.95, 0.95, 0.15),  # yellow
        (0.98, 0.98, 0.82),  # bright yellow
        (1, 1, 1),  # white
    ]  # cmap from blue to white to red.

    levels = MaxNLocator(nbins=16).tick_values(0, 80)
    cmap = _make_cmap(colors)
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
    fig = plt.figure(figsize=(width, height), dpi=dpi)
    ax1 = fig.add_subplot(1, 1, 1)
    CS = plt.pcolor(Z, cmap=cmap, norm=norm)

    if any(recovery_points[1]):
        ss = 80

        ax1.scatter(x_scatter['snow start'], y_scatter['snow start'], label='Snow start time', c='#948D90', marker='s',
                    s=ss, zorder=10, lw=0)
        # ax1.scatter(x_scatter['srst'], y_scatter['srst'], label='SRST', c='#4ED8FF', s=ss, zorder=10, lw=0, marker='D')
        # ax1.scatter(x_scatter['lst'], y_scatter['lst'], label='LST', c='#FFAD2A', s=ss, zorder=10, lw=0, marker='D')
        ax1.scatter(x_scatter['pst'], y_scatter['pst'], label='PST', c='#9535CC', s=ss, zorder=11, lw=0, marker='o')
        # ax1.scatter(x_scatter['sist'], y_scatter['sist'], label='SIST', c='#68BD20', s=ss, zorder=11, lw=0, marker='o')
        ax1.scatter(x_scatter['ncrt'], y_scatter['ncrt'], label='NCRT', c='#FF0512', s=ss, zorder=12, lw=0, marker='o')
        # ax1.scatter(x_scatter['sbpst'], y_scatter['sbpst'], label='BPST', c='#bdb76b', s=ss, zorder=11, lw=0, marker='p')
        # ax1.scatter(x_scatter['sapst'], y_scatter['sapst'], label='APST', c='#cdad00', s=ss, zorder=11, lw=0, marker='p')
        # ax1.scatter(x_scatter['nfrt'], y_scatter['nfrt'], label='NFRT', c='#0072CC', s=ss, zorder=12, lw=0, marker='*')

        plt.scatter(x_scatter['reported losts'], y_scatter['reported losts'], label='Reported lane lost time',
                    c='#000000', s=ss, zorder=16, lw=0, marker='^')
        plt.scatter(x_scatter['reported regains'], y_scatter['reported regains'], label='Reported barelane regain time',
                    c='#FF0512', s=ss, zorder=17, lw=0, marker='^')
        ax1.scatter(x_scatter['snow end'], y_scatter['snow end'], label='Snow end time', c='#948D90', marker='s', s=ss,
                    zorder=10, lw=0)

    ax1.xaxis.grid(True, zorder=0)
    ax1.yaxis.grid(True, zorder=0)

    ntimes = [t.strftime('%m-%d %H:%M') for idx, t in enumerate(timeline) if idx % 30 == 0]
    loc_times = [idx for idx, t in enumerate(timeline) if idx % 30 == 0]

    plt.xticks(loc_times, ntimes, rotation=90)
    # plt.yticks([idx for idx in range(len(y_labels)) if idx % 2 == 1],
    #            [v for idx, v in enumerate(y_labels) if idx % 2 == 1])
    #
    plt.yticks([idx for idx in range(len(y_labels))],
               [v for idx, v in enumerate(y_labels)])

    plt.xlim([0, len_x])
    plt.ylim([0, len_y])
    figure_title = 'Speed at {0}'.format(name)
    plt.title(figure_title, y=1.02)

    cbaxes = fig.add_axes([0.905, 0.1, 0.01, 0.8])
    cb = plt.colorbar(CS, cax=cbaxes, ticks=[0, 10, 20, 30, 40, 50, 60, 70, 80])
    cby_labels = ['%s mph' % item.get_text() for item in cb.ax.get_yticklabels()]
    cby_labels[-1] = '> ' + cby_labels[-1]
    cb.ax.set_yticklabels(cby_labels)

    h1, l1 = ax1.get_legend_handles_labels()
    cbaxes.legend(h1, l1, loc='upper left', bbox_to_anchor=(2.5, 1), scatterpoints=1, frameon=False)

    # box = ax1.get_position()
    # ax1.set_position([box.x0, box.y0 + box.height * 0.2, box.width, box.height * 0.8])
    # ncol = int(round(width_pixel / 500, 0))
    # ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=ncol, scatterpoints=1, fancybox=True, frameon=True, borderaxespad=0.)
    # fig.savefig(file_path, dpi=dpi , bbox_inches='tight')
    # plt.close()

    # ncol = int(round(width_pixel / 500, 0))
    # ax1.legend(loc='upper left', bbox_to_anchor=(0, -0.2), ncol=ncol, scatterpoints=1, fancybox=True, frameon=True, borderaxespad=0.)


    fig.savefig(file_path, dpi=dpi, bbox_inches='tight')
    plt.close()


def _make_cmap(colors):
    position = np.linspace(0, 1, len(colors))

    cdict = {'red': [], 'green': [], 'blue': []}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 256)
    return cmap
