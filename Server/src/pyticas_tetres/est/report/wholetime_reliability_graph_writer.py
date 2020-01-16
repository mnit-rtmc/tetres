# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime
import gc
import os
from collections import deque

import matplotlib.pyplot as plt
import numpy as np

from pyticas.tool import tb
from pyticas_tetres.est.helper import util
from pyticas_tetres.logger import getLogger

OUTPUT_DIR_NAME = 'graphs (whole-time-period)'
MISSING_VALUE = -1
XAXIS_LIMIT = 60

DEFAULT_BI_MAX = 2
DEFAULT_PTI_MAX = 3
DEFAULT_TTI_MAX = 3
DEFAULT_TTR_MAX = 3.5
DEFAULT_MAX_INDEX = max(DEFAULT_BI_MAX, DEFAULT_PTI_MAX, DEFAULT_TTI_MAX)


def write(uid, eparam, operating_conditions, whole, yearly, monthly, daily):
    """
    :type uid: str
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type whole: list[dict]
    :type yearly: list[(list[dict], list[int])]
    :type monthly: list[(list[dict], list[str])]
    :type daily: list[(list[dict], list[datetime.date])]
    :type output_dir: str
    """
    output_dir = util.output_path(
        '%s/%s - %s' % (uid, eparam.travel_time_route.corridor, eparam.travel_time_route.name))

    try:
        _write_cumulative_travel_rates(eparam, operating_conditions, output_dir)
    except Exception as ex:
        getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    try:
        _write_whole_indices(eparam, operating_conditions, whole, output_dir, chart_type='bar')
    except Exception as ex:
        getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    if yearly:
        try:
            _write_yearly_index_variations(eparam, operating_conditions, yearly, output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_yearly_index_variations_oc(eparam, operating_conditions, yearly, output_dir, chart_type='bar')
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    if monthly:
        try:
            _write_monthly_index_variations(eparam, operating_conditions, monthly, output_dir)
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

        try:
            _write_monthly_index_variations_by_oc(eparam, operating_conditions, monthly, output_dir, chart_type='line')
        except Exception as ex:
            getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    try:
        _write_daily_index_variations(eparam, operating_conditions, daily, output_dir, chart_type='line')
    except Exception as ex:
        getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))

    try:
        _write_daily_travel_rate_and_buffer_index(eparam, operating_conditions, daily, output_dir)
    except Exception as ex:
        getLogger(__name__).warning('Exception occured when writing data table : %s' % tb.traceback(ex, f_print=False))


def _write_whole_indices(eparam, operating_conditions, results_whole, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_whole: list[dict]
    :type output_dir: str
    """
    marker, color = kwargs.get('marker', 'o'), kwargs.get('color', 'b')
    chart_type = kwargs.get('chart_type', 'bar')
    missing_value = 0

    whole_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME)

    if not os.path.exists(whole_output_dir):
        os.makedirs(whole_output_dir)

    n_ocs = len(operating_conditions)
    xlabels = [oc.label for gidx, oc in enumerate(operating_conditions)]
    xaxis = np.array(list(range(n_ocs)))
    _xaxis, _xlabels = _get_xaxis(xlabels)
    _xaxis = np.array(_xaxis)

    ttrs, bi95s, bi85s, pt95s, pt85s, ttis, tts = [], [], [], [], [], [], []
    for gidx, oc in enumerate(operating_conditions):
        res = results_whole[gidx]
        if not res:
            ttrs.append(missing_value)
            bi95s.append(missing_value)
            bi85s.append(missing_value)
            pt95s.append(missing_value)
            pt85s.append(missing_value)
            ttis.append(missing_value)
            tts.append(missing_value)
            continue

        ttrs.append(res['tt_rate'] if res['tt_rate'] else missing_value)
        bi95s.append(res['buffer_index'][95] if res['buffer_index'][95] else missing_value)
        bi85s.append(res['buffer_index'][85] if res['buffer_index'][85] else missing_value)
        pt95s.append(res['planning_time_index'][95] if res['planning_time_index'][95] else missing_value)
        pt85s.append(res['planning_time_index'][85] if res['planning_time_index'][85] else missing_value)
        ttis.append(res['travel_time_index'] if res['travel_time_index'] else missing_value)
        tts.append(res['avg_tt'] if res['avg_tt'] else missing_value)

    indices = [ttis, bi95s, bi85s, pt95s, pt85s]
    names = ['Travel Time Index', 'Buffer Index (95th-%ile)', 'Buffer Index (85th-%ile)',
             'Planning Time Index (95th-%ile)', 'Planning Time Index (85th-%ile)']
    sw = 0.5

    for indice, indice_name in zip(indices, names):
        if not indice:
            continue
        fig = plt.figure(figsize=(16, 8), facecolor='white')
        ax1 = plt.subplot(111)

        if chart_type == 'bar':
            ax1.bar(xaxis, indice, color=color, label=indice_name)
            plt.xticks(_xaxis + sw, _xlabels, rotation=70)
        else:
            ax1.plot(xaxis, indice, marker=marker, c=color, label=indice_name)
            plt.xticks(_xaxis, _xlabels, rotation=70)

        plt.grid()
        plt.xlim(xmin=0)
        ax1.legend(prop={'size': 12})
        plt.title('%s by Operating Conditions' % indice_name)
        plt.xlabel('Operating Condition')
        ax1.set_ylabel('Index Value')
        output_file = _output_path(whole_output_dir, '%s by Operating Conditions.png' % (indice_name))
        plt.tight_layout()
        plt.savefig(output_file)
        plt.clf()
        plt.close(fig)

        del indice
        gc.collect()


def _write_cumulative_travel_rates(eparam, operating_conditions, output_dir):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type output_dir: str
    """
    wt_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME)

    if not os.path.exists(wt_output_dir):
        os.makedirs(wt_output_dir)

    route_length = eparam.travel_time_route.route.length()
    n_bins = 100

    cm = ColorMarkers()
    fig = plt.figure(figsize=(16, 8), facecolor='white')
    for gidx, oc in enumerate(operating_conditions):
        ttrs = np.array(
            [extdata.tti.tt / route_length for extdata in oc.whole_data if extdata.tti and extdata.tti.tt])
        if not any(ttrs):
            continue
        h, xs = np.histogram(ttrs, bins=n_bins, normed=True)
        dx = xs[1] - xs[0]
        cums = np.cumsum(h) * dx

        marker, color = cm.next()
        plt.plot(xs[1:], cums, c=color, marker=marker,
                 label='%s (n=%d)' % (eparam.operating_conditions[gidx].name, len(ttrs)))

    plt.xlim(xmin=0, xmax=3)
    plt.ylim(ymin=0, ymax=1)
    plt.grid()
    plt.legend(loc='lower right')
    plt.title('Cumulative Probability of Travel Time Rate')
    plt.xlabel('Travel Time Rate (minute/mile)')
    plt.ylabel('Cumulative Probability')
    output_file = _output_path(wt_output_dir, 'Cumulative Probability of Travel Time Rate.png')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.clf()
    plt.close(fig)


def _write_yearly_index_variations(eparam, operating_conditions, results_yearly, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_yearly: list[(list[dict], list[int])]
    :type output_dir: str
    """
    yearly_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME, 'yearly-variations')

    if not os.path.exists(yearly_output_dir):
        os.makedirs(yearly_output_dir)

    all_years = util.years(eparam.start_date, eparam.end_date)
    xaxis = np.array(list(range(len(all_years))))
    _xaxis, _xlabels = _get_xaxis(all_years)
    _xaxis = np.array(_xaxis)

    for gidx, oc in enumerate(operating_conditions):
        results, years = results_yearly[gidx]
        if not results:
            continue

        ch = ColorHatches()
        tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s = _get_indices(results, years, all_years, 0)

        fig = plt.figure(figsize=(16, 8), facecolor='white')
        ax1 = plt.subplot(111)

        space = 0.4
        n = 3
        w = (1 - space) / n
        sw = w * n / 2
        h, c = ch.next()
        ax1.bar(xaxis, bi95s, width=w, color=c, hatch=h, label='BufferIndex(95th-%ile)')
        h, c = ch.next()
        ax1.bar(xaxis + 1 * w, pt95s, width=w, color=c, hatch=h, label='PlanningTimeIndex(95th-%ile)')
        h, c = ch.next()
        ax1.bar(xaxis + 2 * w, ttis, width=w, color=c, hatch=h, label='Travel Time Index')

        plt.xticks(_xaxis + sw, _xlabels, rotation=70)

        plt.grid()

        ax1.legend(prop={'size': 12})

        plt.title('Yearly Index Variations [%s]' % oc.label)
        plt.xlabel('Year')
        ax1.set_ylim(ymin=0, ymax=max(DEFAULT_MAX_INDEX, np.nanmax([bi95s, pt95s, ttis])))
        ax1.set_ylabel('Index Value')
        output_file = _output_path(yearly_output_dir, 'Yearly-Variations (%s).png' % oc.label)
        plt.tight_layout()
        plt.savefig(output_file)
        plt.clf()
        plt.close(fig)

        del tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s
        gc.collect()


def _write_yearly_index_variations_oc(eparam, operating_conditions, results_yearly, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_yearly: list[(list[dict], list[int])]
    :type output_dir: str
    """
    yearly_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME, 'yearly-variations')

    if not os.path.exists(yearly_output_dir):
        os.makedirs(yearly_output_dir)

    marker, color = kwargs.get('marker', 'o'), kwargs.get('color', 'b')
    chart_type = kwargs.get('chart_type', 'bar')

    all_years = util.years(eparam.start_date, eparam.end_date)
    xaxis = list(range(len(all_years)))
    _xaxis, _xlabels = _get_xaxis(all_years)
    _xaxis = np.array(_xaxis)
    sw = 0.5

    for gidx, oc in enumerate(operating_conditions):
        results, years = results_yearly[gidx]
        if not results:
            continue

        tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s = _get_indices(results, years, all_years)

        indices = [ttis, bi95s, bi85s, pt95s, pt85s]
        default_maxs = [DEFAULT_TTI_MAX, DEFAULT_BI_MAX, DEFAULT_BI_MAX, DEFAULT_PTI_MAX, DEFAULT_PTI_MAX]
        names = ['Travel Time Index', 'Buffer Index (95th-%ile)', 'Buffer Index (85th-%ile)',
                 'Planning Time Index (95th-%ile)', 'Planning Time Index (85th-%ile)']

        for idx, (indice, indice_name) in enumerate(list(zip(indices, names))):
            if not indice:
                continue
            fig = plt.figure(figsize=(16, 8), facecolor='white')
            ax1 = plt.subplot(111)

            if chart_type == 'bar':
                ax1.bar(xaxis, indice, color=color, label=indice_name)
                plt.xticks(_xaxis + sw, _xlabels, rotation=70)
            else:
                indice = [v if v >= 0 else None for v in indice]
                ax1.plot(xaxis, indice, marker=marker, c=color, label=indice_name)
                plt.xticks(_xaxis, _xlabels, rotation=70)

            plt.grid()
            plt.xlim(xmin=0)
            ax1.legend(prop={'size': 12})
            plt.title('Yearly %s Variations [%s]' % (indice_name, oc.label))
            plt.xlabel('Year')
            ax1.set_ylim(ymin=0, ymax=max(default_maxs[idx], np.nanmax([bi95s, pt95s, ttis])))
            ax1.set_ylabel('Index Value')
            output_file = _output_path(yearly_output_dir, 'Yearly %s Variations (%s).png' % (indice_name, oc.label))
            plt.tight_layout()
            plt.savefig(output_file)
            plt.clf()
            plt.close(fig)

            del indice
            gc.collect()


def _write_monthly_index_variations(eparam, operating_conditions, results_monthly, output_dir):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_monthly: list[(list[dict], list[str])]
    :type output_dir: str
    """
    monthly_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME, 'monthly-variations')

    if not os.path.exists(monthly_output_dir):
        os.makedirs(monthly_output_dir)

    all_months = util.months(eparam.start_date, eparam.end_date)
    xaxis = np.array(list(range(len(all_months))))
    _xaxis, _xlabels = _get_xaxis(['%04d-%02d' % (m[0], m[1]) for m in all_months])
    _xaxis = np.array(_xaxis)

    for gidx, oc in enumerate(operating_conditions):
        results, months = results_monthly[gidx]
        if not results:
            continue

        cm = ColorMarkers()
        tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s = _get_indices(results, months, all_months, 0)

        fig = plt.figure(figsize=(16, 8), facecolor='white')
        ax1 = plt.subplot(111)

        m, c = cm.next()
        ax1.plot(bi95s, marker=m, color=c, label='Buffer Index(95th-%ile)')
        m, c = cm.next()
        ax1.plot(pt95s, marker=m, color=c, label='Planning Time Index(95th-%ile)')
        m, c = cm.next()
        ax1.plot(ttis, marker=m, color=c, label='Travel Time Index')

        plt.xticks(_xaxis, _xlabels, rotation=70)

        plt.grid()
        plt.xlim(xmin=0)

        ax1.legend(prop={'size': 12})

        plt.title('Monthly Variations of BI, PTI and TTI [%s]' % oc.label)
        plt.xlabel('Month')

        ax1.set_ylim(ymin=0, ymax=max(DEFAULT_MAX_INDEX, np.nanmax([bi95s, pt95s, ttis])))
        ax1.set_ylabel('Index Value')
        output_file = _output_path(monthly_output_dir, 'Monthly Variations of BI, PTI and TTI (%s).png' % oc.label)
        plt.tight_layout()
        plt.savefig(output_file)
        plt.clf()
        plt.close(fig)

        del tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s
        gc.collect()


def _write_monthly_index_variations_bar(eparam, operating_conditions, results_monthly, output_dir):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_monthly: list[(list[dict], list[str])]
    :type output_dir: str
    """
    monthly_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME, 'monthly-variations')

    if not os.path.exists(monthly_output_dir):
        os.makedirs(monthly_output_dir)

    all_months = util.months(eparam.start_date, eparam.end_date)
    xaxis = np.array(list(range(len(all_months))))
    _xaxis, _xlabels = _get_xaxis(['%04d-%02d' % (m[0], m[1]) for m in all_months])
    _xaxis = np.array(_xaxis)

    for gidx, oc in enumerate(operating_conditions):
        results, months = results_monthly[gidx]
        if not results:
            continue

        ch = ColorHatches()
        tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s = _get_indices(results, months, all_months, 0)

        fig = plt.figure(figsize=(16, 8), facecolor='white')
        ax1 = plt.subplot(111)

        space = 0.4
        n = 3
        w = (1 - space) / n
        sw = w * n / 2
        h, c = ch.next()
        ax1.bar(xaxis, bi95s, width=w, color=c, hatch=h, label='Buffer Index(95th-%ile)')
        h, c = ch.next()
        ax1.bar(xaxis + 1 * w, pt95s, width=w, color=c, hatch=h, label='Planning Time Index(95th-%ile)')
        h, c = ch.next()
        ax1.bar(xaxis + 2 * w, ttis, width=w, color=c, hatch=h, label='Travel Time Index')

        plt.xticks(_xaxis + sw, _xlabels, rotation=70)

        plt.grid()
        plt.xlim(xmin=0)

        ax1.legend(prop={'size': 12})

        plt.title('Monthly Variations of BI, PTI and TTI [%s]' % oc.label)
        plt.xlabel('Month')

        ax1.set_ylim(ymin=0, ymax=max(DEFAULT_MAX_INDEX, np.nanmax([bi95s, pt95s, ttis])))
        ax1.set_ylabel('Index Value')
        output_file = _output_path(monthly_output_dir, 'Monthly-Variations of BI, PTI and TTI (%s).png' % oc.label)
        plt.tight_layout()
        plt.savefig(output_file)
        plt.clf()
        plt.close(fig)

        del tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s
        gc.collect()


def _write_monthly_index_variations_by_oc(eparam, operating_conditions, results_monthly, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_monthly: list[(list[dict], list[str])]
    :type output_dir: str
    """
    monthly_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME, 'monthly-variations')

    if not os.path.exists(monthly_output_dir):
        os.makedirs(monthly_output_dir)

    marker, color = kwargs.get('marker', 'o'), kwargs.get('color', 'b')
    chart_type = kwargs.get('chart_type', 'bar')

    all_months = util.months(eparam.start_date, eparam.end_date)
    xaxis = np.array(list(range(len(all_months))))
    _xaxis, _xlabels = _get_xaxis(['%04d-%02d' % (m[0], m[1]) for m in all_months])
    _xaxis = np.array(_xaxis)
    sw = 0.5

    for gidx, oc in enumerate(operating_conditions):
        results, months = results_monthly[gidx]
        if not results:
            continue

        tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s = _get_indices(results, months, all_months, 0)

        indices = [ttis, bi95s, bi85s, pt95s, pt85s]
        default_maxs = [DEFAULT_TTI_MAX, DEFAULT_BI_MAX, DEFAULT_BI_MAX, DEFAULT_PTI_MAX, DEFAULT_PTI_MAX]
        names = ['Travel Time Index', 'Buffer Index (95th-%ile)', 'Buffer Index (85th-%ile)',
                 'Planning Time Index (95th-%ile)', 'Planning Time Index (85th-%ile)']

        for idx, (indice, indice_name) in enumerate(zip(indices, names)):
            if not indice:
                continue
            fig = plt.figure(figsize=(16, 8), facecolor='white')
            ax1 = plt.subplot(111)

            if chart_type == 'bar':
                ax1.bar(xaxis, indice, color=color, label=indice_name)
                plt.xticks(_xaxis + 0.5, _xlabels, rotation=70)
            else:
                ax1.plot(xaxis, indice, marker=marker, c=color, label=indice_name)
                plt.xticks(_xaxis, _xlabels, rotation=70)

            plt.grid()
            plt.xlim(xmin=0)
            ax1.legend(prop={'size': 12})
            plt.title('Monthly %s Variations [%s]' % (indice_name, oc.label))
            plt.xlabel('Month')
            ax1.set_ylim(ymin=0, ymax=max(default_maxs[idx], np.nanmax([bi95s, pt95s, ttis])))
            ax1.set_ylabel('Index Value')
            output_file = _output_path(monthly_output_dir, 'Monthly %s Variations (%s).png' % (indice_name, oc.label))
            plt.tight_layout()
            plt.savefig(output_file)
            plt.clf()
            plt.close(fig)

            del indice
            gc.collect()


def _write_daily_index_variations(eparam, operating_conditions, results_daily, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_daily: list[(list[dict], list[datetime.date])]
    :type output_dir: str
    """
    daily_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME, 'daily-variations')

    if not os.path.exists(daily_output_dir):
        os.makedirs(daily_output_dir)

    marker, color = kwargs.get('marker', 'o'), kwargs.get('color', 'b')
    chart_type = kwargs.get('chart_type', 'bar')

    all_dates = util.dates(eparam.start_date, eparam.end_date,
                           except_holiday=eparam.except_holiday, weekdays=eparam.weekdays.get_weekdays())
    xaxis = np.array(list(range(len(all_dates))))

    _xaxis, _xlabels = _get_xaxis([m.strftime('%Y-%m-%d') for m in all_dates])

    for gidx, oc in enumerate(operating_conditions):
        results, dates = results_daily[gidx]
        if not results:
            continue

        tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s = _get_indices(results, dates, all_dates, 0)

        indices = [ttis, bi95s, bi85s, pt95s, pt85s]
        default_maxs = [DEFAULT_TTI_MAX, DEFAULT_BI_MAX, DEFAULT_BI_MAX, DEFAULT_PTI_MAX, DEFAULT_PTI_MAX]
        names = ['Travel Time Index', 'Buffer Index (95th-%ile)', 'Buffer Index (85th-%ile)',
                 'Planning Time Index (95th-%ile)', 'Planning Time Index (85th-%ile)']

        for idx, (indice, indice_name) in enumerate(zip(indices, names)):
            if not indice:
                continue
            fig = plt.figure(figsize=(16, 8), facecolor='white')
            ax1 = plt.subplot(111)
            if chart_type == 'bar':
                ax1.bar(xaxis, indice, color=color, label=indice_name)
            else:
                ax1.plot(xaxis, indice, c=color, label=indice_name)

            plt.xticks(_xaxis, _xlabels, rotation=70)

            plt.grid()
            plt.xlim(xmin=0)
            ax1.legend(prop={'size': 12})
            plt.title('Daily %s Variations [%s]' % (indice_name, oc.label))
            plt.xlabel('Day')
            ax1.set_ylim(ymin=0, ymax=max(default_maxs[idx], np.nanmax(indice)))
            ax1.set_ylabel('Index Value')
            output_file = _output_path(daily_output_dir, 'Daily %s Variations (%s).png' % (indice_name, oc.label))
            plt.tight_layout()
            plt.savefig(output_file)
            plt.clf()
            plt.close(fig)
            del indice
            gc.collect()


def _write_daily_travel_rate_and_buffer_index(eparam, operating_conditions, results_daily, output_dir, **kwargs):
    """
    :type eparam: pyticas_tetres.ttypes.EstimationRequestInfo
    :type operating_conditions: list[pyticas_tetres.rengine.filter.ftypes.ExtFilterGroup]
    :type results_daily: list[(list[dict], list[datetime.date])]
    :type output_dir: str
    """
    daily_output_dir = os.path.join(output_dir, OUTPUT_DIR_NAME, 'daily-buffer-index')

    if not os.path.exists(daily_output_dir):
        os.makedirs(daily_output_dir)

    marker, color = kwargs.get('marker', 'o'), kwargs.get('color', '#333333')

    all_dates = util.dates(eparam.start_date, eparam.end_date,
                           except_holiday=eparam.except_holiday, weekdays=eparam.weekdays.get_weekdays())

    for gidx, oc in enumerate(operating_conditions):
        results, dates = results_daily[gidx]
        if not results:
            continue

        tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s = _get_indices(results, dates, all_dates, 0)

        indice_name = 'Buffer Index (95th-%ile)'
        indice = bi95s
        if not bi95s:
            continue

        fig = plt.figure(figsize=(16, 8), facecolor='white')
        ax1 = plt.subplot(111)
        ax1.scatter(ttrs, indice, color=color, label=indice_name)

        plt.grid()
        plt.xlim(xmin=0, xmax=max([DEFAULT_TTR_MAX] + ttrs))
        ax1.legend(prop={'size': 12})
        plt.title('Buffer Index (95th-%%ile) and Travel Time Rate [%s]' % oc.label)
        plt.xlabel('Travel Time Rate (minute/mile)')
        ax1.set_ylim(ymin=0, ymax=max(DEFAULT_MAX_INDEX, np.nanmax(indice)))
        ax1.set_ylabel('Index Value')
        output_file = _output_path(daily_output_dir, 'Daily %s vs Travel Time Rate (%s).png' % (indice_name, oc.label))
        plt.tight_layout()
        plt.savefig(output_file)

        plt.clf()
        plt.close(fig)

        del tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s, indice
        gc.collect()


def _output_path(output_dir, filename):
    return os.path.join(output_dir, filename)


def _get_indices(results, ymds, all_ymds, missing_value=0):
    """

    :type results: list[dict]
    :type ymds: list[[int, int]]
    :type missing_value: Union(int, float, str, None)
    :rtype: list, list, list, list, list, list, list
    """
    ttrs, bi95s, bi85s, pt95s, pt85s, ttis, tts = [], [], [], [], [], [], []
    tidx = -1
    for idx, m in enumerate(ymds):
        for midx, m2 in enumerate(all_ymds):
            if midx <= tidx:
                continue
            if m > m2:
                ttrs.append(missing_value)
                bi95s.append(missing_value)
                bi85s.append(missing_value)
                pt95s.append(missing_value)
                pt85s.append(missing_value)
                ttis.append(missing_value)
                tts.append(missing_value)
            elif m <= m2:
                tidx = midx
                break

        res = results[idx]
        ttrs.append(res.get('tt_rate', missing_value))
        bi95s.append(res.get('buffer_index', {}).get(95, missing_value))
        bi85s.append(res.get('buffer_index', {}).get(85, missing_value))
        pt95s.append(res.get('planning_time_index', {}).get(95, missing_value))
        pt85s.append(res.get('planning_time_index', {}).get(85, missing_value))
        ttis.append(res.get('travel_time_index', missing_value))
        tts.append(res.get('avg_tt', missing_value))

    m = ymds[-1]
    for midx, m2 in enumerate(all_ymds):
        if m < m2:
            ttrs.append(missing_value)
            bi95s.append(missing_value)
            bi85s.append(missing_value)
            pt95s.append(missing_value)
            pt85s.append(missing_value)
            ttis.append(missing_value)
            tts.append(missing_value)

    return tts, ttrs, ttis, bi95s, bi85s, pt95s, pt85s


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
