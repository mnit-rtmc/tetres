# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import math
import statistics

def percentile(data, p, **kwargs):
    """ return percentile

    **Parameter**

    - interpolation : {'linear', 'lower', 'higher', 'midpoint', 'nearest'}

        This optional parameter specifies the interpolation method to use,
        when the desired quantile lies between two data points i and j:

        - linear: i + (j - i) * fraction, where fraction is the fractional part of the index surrounded by i and j.
        - lower: i.
        - higher: j.
        - nearest: i or j whichever is nearest.
        - midpoint: (i + j) / 2.



    :type data: list[float]
    :param p: percentile point (0 < p < 1)
    :type p: float
    :rtype: float
    """
    if p < 0 or p > 1:
        raise ValueError('parameter "p" must be between 0 and 1')

    interpolation = kwargs.get('interpolation', 'linear')
    sdata = sorted(data)
    N = len(sdata)
    realIndex = p * (N - 1)
    idx = int(realIndex)
    frac = realIndex - idx

    if interpolation == 'linear':
        if idx + 1 < N:
            return sdata[idx] * (1 - frac) + sdata[idx + 1] * frac
        else:
            return sdata[idx]
    elif interpolation == 'lower':
        return sdata[idx]
    elif interpolation == 'higher':
        return sdata[int(math.ceil(realIndex))]
    elif interpolation == 'nearest':
        return sdata[int(round(realIndex))]
    elif interpolation == 'midpoint':
        return (sdata[idx] + sdata[int(math.ceil(realIndex))]) / 2


def stddev(data):
    return statistics.stdev(data)

def variance(data):
    return statistics.variance(data)

def average(data):
    return statistics.mean(data)

def median(data):
    return statistics.median(data)