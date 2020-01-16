# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
# matplotlib.use('Agg')
import gc
import os
from collections import deque

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

from pyticas.tool import tb
from pyticas_tetres import cfg
from pyticas_tetres.est.helper import util
from pyticas_tetres.logger import getLogger

OUTPUT_DIR_NAME = 'graphs (tod)'
XAXIS_LIMIT = 10
MISSING_VALUE = -1


def write(uid, eparam, operating_conditions, whole, yearly, monthly):
    """
    :type uid: str
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type whole: list[list[dict]]
    :type yearly: list[list[list[dict]]]
    :type monthly: list[list[list[dict]]]
    :type output_dir: str
    """
    output_dir = util.output_path(
        '%s/%s - %s' % (uid, eparam.travel_time_route.corridor, eparam.travel_time_route.name))

    if yearly:
        try:
            _write_yearly_index_variations_oc(eparam, operating_conditions, yearly, output_dir)
        except Exception as ex:
            getLogger(__name__).warning(
                'Exception occured when writing TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

    if monthly:
        try:
            _write_monthly_index_variations_by_oc(eparam, operating_conditions, monthly, output_dir)
        except Exception as ex:
            getLogger(__name__).warning(
                'Exception occured when writing TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

    try:
        _write_TOD_tt_variations(eparam, operating_conditions, output_dir)
    except Exception as ex:
        getLogger(__name__).warning(
            'Exception occured when writing TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))


def _write_yearly_index_variations_oc(eparam, operating_conditions, results_yearly, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_yearly: list[list[list[dict]]]
    :type output_dir: str
    """
    missing_value = kwargs.get('missing_value', MISSING_VALUE)
    yearly_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME, 'yearly-variations')

    if not os.path.exists(yearly_output_dir):
        os.makedirs(yearly_output_dir)

    # x : time of day
    # y : year
    # z : index value
    for idx, oc in enumerate(operating_conditions):
        a_year_result = results_yearly[idx]
        if not a_year_result:
            continue
        years, times, bi95s, bi90s, bi85s, pti95s, pti90s, pti85s, ttis, semivars = [], [], [], [], [], [], [], [], [], []
        for yidx, a_year_result in enumerate(a_year_result):
            # make missing data
            if not a_year_result:
                for dt in oc.all_times:
                    years.append(oc.all_years[yidx])
                    times.append(dt.strftime('%H:%M'))
                    bi95s.append(missing_value)
                    bi90s.append(missing_value)
                    bi85s.append(missing_value)
                    pti95s.append(missing_value)
                    pti90s.append(missing_value)
                    pti85s.append(missing_value)
                    ttis.append(missing_value)
                    semivars.append(missing_value)
                continue

            for tidx, a_result in enumerate(a_year_result):
                years.append(oc.all_years[yidx])
                times.append(oc.all_times[tidx].strftime('%H:%M'))
                if a_result:
                    bi95s.append(a_result.get('buffer_index', {}).get(95, missing_value))
                    bi90s.append(a_result.get('buffer_index', {}).get(90, missing_value))
                    bi85s.append(a_result.get('buffer_index', {}).get(85, missing_value))
                    pti95s.append(a_result.get('planning_time_index', {}).get(95, missing_value))
                    pti90s.append(a_result.get('planning_time_index', {}).get(90, missing_value))
                    pti85s.append(a_result.get('planning_time_index', {}).get(85, missing_value))
                    ttis.append(a_result.get('travel_time_index', missing_value))
                    semivars.append(a_result.get('semi_variance', missing_value))
                else:
                    bi95s.append(missing_value)
                    bi90s.append(missing_value)
                    bi85s.append(missing_value)
                    pti95s.append(missing_value)
                    pti90s.append(missing_value)
                    pti85s.append(missing_value)
                    ttis.append(missing_value)
                    semivars.append(missing_value)

        # TODO: check this output
        try:
            _write_line_chart('Yearly', oc.label, 'Buffer Index (95th-%ile)', 'Year', years, times, bi95s, yearly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing yearly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_line_chart('Yearly', oc.label, 'Buffer Index (90th-%ile)', 'Year', years, times, bi90s, yearly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing yearly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_line_chart('Yearly', oc.label, 'Buffer Index (85th-%ile)', 'Year', years, times, bi85s, yearly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing yearly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_line_chart('Yearly', oc.label, 'Planning Time Index (95th-%ile)', 'Year', years, times, pti95s, yearly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing yearly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_line_chart('Yearly', oc.label, 'Planning Time Index (90th-%ile)', 'Year', years, times, pti90s, yearly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing yearly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_line_chart('Yearly', oc.label, 'Planning Time Index (85th-%ile)', 'Year', years, times, pti85s, yearly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing yearly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_line_chart('Yearly', oc.label, 'Travel Time Index', 'Year', years, times, ttis, yearly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing yearly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_line_chart('Yearly', oc.label, 'Semi-Variance', 'Year', years, times, semivars, yearly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing yearly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))


def _write_line_chart(mode, op_name, indice_name, yaxis_name, ymds, times, indices, output_dir):
    """

    :type mode: str
    :type op_name: str
    :type indice_name:  str
    :type yaxis_name:  str
    :type ymds: list
    :type times: list[str]
    :type indices: list[float]
    :type output_dir: str
    """
    if not times:
        return

    unique_times = np.unique(times)
    n_unique_times = len(unique_times)

    unique_ymds = np.unique(ymds)
    n_unique_ymds = len(unique_ymds)

    if not n_unique_times or not n_unique_ymds or not np.nonzero(indices)[0].any():
        return

    y = np.array(range(n_unique_ymds))
    x = np.array(range(n_unique_times))

    data_for_each_ymd = []
    for _ in range(n_unique_ymds):
        data_for_each_ymd.append([])

    ymd_to_idx, idx_to_ymd = {}, {}
    for idx, ymd in enumerate(unique_ymds):
        ymd_to_idx[ymd] = idx
        idx_to_ymd[idx] = ymd

    for idx, indice_value in enumerate(indices):
        ymd = ymds[idx]
        data_for_each_ymd[ymd_to_idx[ymd]].append(indice_value)

    fig = plt.figure(figsize=(16, 8), facecolor='white')

    if n_unique_ymds > 1:
        ax = plt.subplot(111)

        cm = ColorMarkers()
        for idx, ymd_data in enumerate(data_for_each_ymd):
            ymd = idx_to_ymd[idx]
            m, c = cm.next()
            ax.plot(ymd_data, marker=m, color=c, label='%s' % ymd)

        ax.set_xlabel('Time')
        ax.set_ylabel(yaxis_name)
        _yaxis, _ylabels = _get_xaxis(unique_ymds, 20)
        if _yaxis:
            ax.set_yticks(_yaxis)
            ax.set_yticklabels(_ylabels)
        plt.xlim(min(x), max(x))
        plt.ylim(min(y), max(y))
        ax.grid()
        _xaxis, _xlabels = _get_xaxis(unique_times, 20)
        if _xaxis:
            ax.set_xticks(_xaxis)
            ax.set_xticklabels(_xlabels, rotation=70)
        plt.title('%s Time of Day %s [%s]' % (mode, indice_name, op_name))

    else:
        ax = plt.subplot(111)
        xaxis = list(range(len(times)))
        ax.plot(xaxis, indices)
        _xaxis, _xlabels = _get_xaxis(times)
        ax.set_xticks(_xaxis)
        ax.set_xticklabels(_xlabels, rotation=70)
        ax.set_xlabel('Time')
        ax.set_ylabel('Index Value')
        ax.grid()
        plt.title('%s Time of Day %s [%s]' % (unique_ymds[0], indice_name, op_name))

    output_file = os.path.join(output_dir, '%s Time of Day %s (%s).png' % (mode, indice_name, op_name))

    plt.tight_layout()
    plt.savefig(output_file)
    plt.clf()
    plt.close(fig)

    del x, y, unique_times, unique_ymds
    gc.collect()


def _write_monthly_index_variations_by_oc(eparam, operating_conditions, results_monthly, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_monthly: list[list[list[dict]]]
    :type output_dir: str
    """
    missing_value = kwargs.get('missing_value', MISSING_VALUE)
    monthly_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME, 'monthly-variations')

    if not os.path.exists(monthly_output_dir):
        os.makedirs(monthly_output_dir)

    # x : time of day
    # y : month
    # z : index value
    for idx, oc in enumerate(operating_conditions):
        a_month_result = results_monthly[idx]
        if not a_month_result:
            continue
        months, times, bi95s, bi90s, bi85s, pti95s, pti90s, pti85s, ttis, semivars = [], [], [], [], [], [], [], [], [], []
        for yidx, a_month_result in enumerate(a_month_result):
            # make missing data
            if not a_month_result:
                for dt in oc.all_times:
                    months.append('%04d-%02d' % (oc.all_months[yidx][0], oc.all_months[yidx][1]))
                    times.append(dt.strftime('%H:%M'))
                    bi95s.append(missing_value)
                    bi90s.append(missing_value)
                    bi85s.append(missing_value)
                    pti95s.append(missing_value)
                    pti90s.append(missing_value)
                    pti85s.append(missing_value)
                    ttis.append(missing_value)
                    semivars.append(missing_value)
                continue

            for tidx, a_result in enumerate(a_month_result):
                months.append('%04d-%02d' % (oc.all_months[yidx][0], oc.all_months[yidx][1]))
                times.append(oc.all_times[tidx].strftime('%H:%M'))
                if a_result:
                    bi95s.append(a_result.get('buffer_index', {}).get(95, missing_value))
                    bi90s.append(a_result.get('buffer_index', {}).get(90, missing_value))
                    bi85s.append(a_result.get('buffer_index', {}).get(85, missing_value))
                    pti95s.append(a_result.get('planning_time_index', {}).get(95, missing_value))
                    pti90s.append(a_result.get('planning_time_index', {}).get(90, missing_value))
                    pti85s.append(a_result.get('planning_time_index', {}).get(85, missing_value))
                    ttis.append(a_result.get('travel_time_index', missing_value))
                    semivars.append(a_result.get('semi_variance', missing_value))
                else:
                    bi95s.append(missing_value)
                    bi90s.append(missing_value)
                    bi85s.append(missing_value)
                    pti95s.append(missing_value)
                    pti90s.append(missing_value)
                    pti85s.append(missing_value)
                    ttis.append(missing_value)
                    semivars.append(missing_value)

        try:
            _write_contour_chart('Monthly', oc.label, 'Buffer Index (95th-%ile)', 'Month', months, times, bi95s, monthly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing monthly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_contour_chart('Monthly', oc.label, 'Buffer Index (90th-%ile)', 'Month', months, times, bi90s, monthly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing monthly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_contour_chart('Monthly', oc.label, 'Buffer Index (85th-%ile)', 'Month', months, times, bi85s, monthly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing monthly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_contour_chart('Monthly', oc.label, 'Planning Time Index (95th-%ile)', 'Month', months, times, pti95s, monthly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing monthly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_contour_chart('Monthly', oc.label, 'Planning Time Index (90th-%ile)', 'Month', months, times, pti90s, monthly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing monthly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_contour_chart('Monthly', oc.label, 'Planning Time Index (85th-%ile)', 'Month', months, times, pti85s, monthly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing monthly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_contour_chart('Monthly', oc.label, 'Travel Time Index', 'Month', months, times, ttis, monthly_output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing monthly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))

        # try:
        #     _write_contour_chart('Monthly', oc.label, 'Semi-Variance', 'Month', months, times, semivars, monthly_output_dir)
        # except Exception as ex:
        #     getLogger(__name__).warning('Exception occured when writing monthly TOD reliability graphs : %s' % tb.traceback(ex, f_print=False))
        #

def _write_contour_chart(mode, op_name, indice_name, yaxis_name, ymds, times, indices, output_dir):
    """

    :type mode: str
    :type op_name: str
    :type indice_name:  str
    :type yaxis_name:  str
    :type ymds: list
    :type times: list[str]
    :type indices: list[float]
    :type output_dir: str
    """
    if not times:
        return

    unique_times = np.unique(times)
    n_unique_times = len(unique_times)

    unique_ymds = np.unique(ymds)
    n_unique_ymds = len(unique_ymds)

    if not n_unique_times or not n_unique_ymds or not np.nonzero(indices)[0].any():
        return

    y = np.array(range(n_unique_ymds))
    x = np.array(range(n_unique_times))
    z = np.array(indices)

    X, Y = np.meshgrid(x, y)

    z = np.array([z[idx] for idx, (_x, _y) in enumerate(list(zip(np.ravel(X), np.ravel(Y))))])

    Z = z.reshape(X.shape)

    fig = plt.figure(figsize=(16, 8), facecolor='white')

    use_3d = False

    if n_unique_ymds > 1:
        if not use_3d:
            ax = plt.subplot(111)
            levels = MaxNLocator(nbins=32).tick_values(0, 3)
            cmap = plt.get_cmap('hot_r')
            cmap.set_under('#28FF00')  # light green
            cmap.set_over('k')
            norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
            cs = ax.contourf(X, Y, Z, cmap=cmap, norm=norm, levels=levels, extend='both')
            ax.set_xlabel('Time')
            ax.set_ylabel(yaxis_name)

            fig.colorbar(cs)
            _yaxis, _ylabels = _get_xaxis(unique_ymds, 20)
            if _yaxis:
                ax.set_yticks(_yaxis)
                ax.set_yticklabels(_ylabels)
            plt.xlim(min(x), max(x))
            plt.ylim(min(y), max(y))
            ax.grid()
            _xaxis, _xlabels = _get_xaxis(unique_times, 20)

            if _xaxis:
                ax.set_xticks(_xaxis)
                ax.set_xticklabels(_xlabels, rotation=70)
            plt.title('%s Time of Day %s [%s]' % (mode, indice_name, op_name))
        else:
            ax = plt.axes(projection='3d')
            surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
            try:
                cset = ax.contour(X, Y, Z, zdir='z', cmap=cm.coolwarm)
                cset = ax.contour(X, Y, Z, zdir='x', cmap=cm.coolwarm)
                cset = ax.contour(X, Y, Z, zdir='y', cmap=cm.coolwarm)
            except Exception as ex:
                print(mode, op_name, indice_name)
                print('y =', ymds)
                print('x =', times)
                print('z =', indices)
                raise ex

            ax.set_xlabel('Time')
            ax.set_ylabel(yaxis_name)
            ax.set_zlabel('Index Value')
            fig.colorbar(surf, shrink=0.5, aspect=5)
            _yaxis, _ylabels = _get_xaxis(unique_ymds)
            if _yaxis:
                ax.set_yticks(_yaxis)
                ax.set_yticklabels(_ylabels)
            plt.xlim(min(x), max(x))
            plt.ylim(min(y), max(y))
            step = 6
            ax.set_xticks([_x for idx, _x in enumerate(x) if idx % step == 0])
            ax.set_xticklabels([_x for idx, _x in enumerate(unique_times) if idx % step == 0], rotation=40)
            plt.title('%s Time of Day %s [%s]' % (mode, indice_name, op_name))
    else:
        ax = plt.subplot(111)
        xaxis = list(range(len(times)))
        ax.plot(xaxis, indices)
        _xaxis, _xlabels = _get_xaxis(times)
        ax.set_xticks(_xaxis)
        ax.set_xticklabels(_xlabels, rotation=70)
        ax.set_xlabel('Time')
        ax.set_ylabel('Index Value')
        ax.grid()
        plt.title('%s Time of Day %s [%s]' % (unique_ymds[0], indice_name, op_name))

    output_file = os.path.join(output_dir, '%s Time of Day %s (%s).png' % (mode, indice_name, op_name))

    plt.tight_layout()
    plt.savefig(output_file)
    plt.clf()
    plt.close(fig)

    del x, y, z, X, Y, Z, unique_times, unique_ymds
    gc.collect()


def _write_TOD_tt_variations(eparam, operating_conditions, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type output_dir: str
    """
    marker = kwargs.get('marker', '.')
    color = kwargs.get('color', 'b')
    for oc in operating_conditions:
        _write_TOD_tt_variations_for_an_operating_condition(eparam, oc, output_dir, marker=marker, color=color)


def _write_TOD_tt_variations_for_an_operating_condition(eparam, oc, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type oc: pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup
    :type output_dir: str
    """
    tt_var_output_dir = os.path.join(output_dir, 'time-of-day travel time variations')

    if not os.path.exists(tt_var_output_dir):
        os.makedirs(tt_var_output_dir)

    marker, color = kwargs.get('marker', '.'), kwargs.get('color', 'b')

    today = datetime.date.today()
    stime = datetime.datetime.combine(today, util.get_time(eparam.start_time)).replace(second=0, microsecond=0)
    etime = datetime.datetime.combine(today, util.get_time(eparam.end_time)).replace(second=0, microsecond=0)

    step = datetime.timedelta(seconds=cfg.TT_DATA_INTERVAL)

    fig = plt.figure(figsize=(16, 8), facecolor='white')

    cursor = stime
    res, times = [], []
    legend_added = False
    while cursor <= etime:
        h, m = cursor.hour, cursor.minute
        tts = [ext_data.tti.tt for ext_data in oc.whole_data if
               ext_data.tti.time.hour == h and ext_data.tti.time.minute == m]
        res.append(tts)
        times.append(cursor.time())
        cursor += step

    xaxis = list(range(len(times)))
    for xe, ye in zip(xaxis, res):
        plt.scatter([xe] * len(ye), ye, marker=marker, c=color,
                    label=(oc.label if not legend_added else None))
        legend_added = True

    ntimes = [t.strftime('%H:%M') for idx, t in enumerate(times) if
              idx % (3600 / cfg.TT_DATA_INTERVAL) == 0]
    loc_times = [idx for idx, t in enumerate(times) if idx % (3600 / cfg.TT_DATA_INTERVAL) == 0]
    plt.xticks(loc_times, ntimes, rotation=90)
    plt.ylim(ymin=0)
    # plt.axes().set_xticklabels(ntimes, rotation=90)

    plt.title('Travel Time Variations by Time of Day of %s' % oc.label)
    plt.xlabel('Time of Day')
    plt.ylabel('Travel Time (minutes)')
    plt.legend()
    plt.grid()
    output_file = _output_path(tt_var_output_dir, 'TOD_Variations (%s).png' % oc.label)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.clf()
    plt.close(fig)

    del xaxis, res
    gc.collect()


def _output_path(output_dir, filename):
    return os.path.join(output_dir, filename)


def _get_xaxis(xdata, nlimit=XAXIS_LIMIT):
    """
    :type xdata: Union(list[str], list[int])
    :rtype: list[int], list[str]
    """
    n_data = len(xdata)
    xaxis = list(range(n_data))
    if n_data < nlimit:
        return xaxis, xdata
    step = int(n_data / nlimit)
    if not step:
        return xaxis, xdata
    _xaxis = [v for idx, v in enumerate(xaxis) if idx % step == 0]
    _xlabels = [v for idx, v in enumerate(xdata) if idx % step == 0]
    return _xaxis, _xlabels


def _color_map(Z):
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
    CS = plt.pcolor(Z, cmap=cmap, norm=norm)


def _make_cmap(colors):
    position = np.linspace(0, 1, len(colors))

    cdict = {'red': [], 'green': [], 'blue': []}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, 256)
    return cmap


class ColorMarkers(object):
    def __init__(self):
        self.markers = deque(['o', 'x', 'd', '^', '<', '>', 'v', 's', '*', '+'])
        self.colors = deque(
            ['#FF0000', '#FF7F00', '#FFFF00', '#76523c', '#00a994', '#00FF00', '#0000FF', '#f63fae', '#9400D3',
             '#364652'])
        self.cursor = 0

    def next(self):
        marker, color = self.markers[self.cursor], self.colors[self.cursor]
        self.cursor += 1
        if self.cursor >= len(self.colors):
            self.cursor = 0
            self.colors.rotate(-1)

        return marker, color


class ColorHatches(object):
    def __init__(self):
        self.hatches = deque(['', '-', '+', 'x', '\\', '*', 'o', 'O', '.'])
        self.colors = deque(
            ['#FF0000', '#FF7F00', '#FFFF00', '#76523c', '#00a994', '#00FF00', '#0000FF', '#f63fae', '#9400D3'])
        self.cursor = 0

    def next(self):
        hatch, color = self.hatches[self.cursor], self.colors[self.cursor]
        self.cursor += 1
        if self.cursor >= len(self.colors):
            self.cursor = 0
            self.colors.rotate(-1)

        return hatch, color
