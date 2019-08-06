# -*- coding: utf-8 -*-

import numpy as np
from scipy.optimize import curve_fit as data_fitting

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


def curve_fit(func, ks, us, popts, **kwargs):
    """

    :type func: callable
    :type ks: Union(list[float], numpy.ndarray)
    :type us: Union(list[float], numpy.ndarray)
    :type popts: list[float]
    :return:
    """
    def _curve_fit(cfunc, x, y, **kwargs):
        return data_fitting(cfunc, x, y, **kwargs)

    sigma = kwargs.get('sigma', None)

    try:
        xdata = np.array(ks)
        ydata = np.array(us)
        popts, pcov = _curve_fit(func, xdata, ydata, p0=popts, sigma=sigma, maxfev=9999999)
    except Exception as ex:
        raise ex

    return None, list(popts), None, lambda k: func(k, *popts)
