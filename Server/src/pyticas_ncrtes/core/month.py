# -*- coding: utf-8 -*-
"""
pyticas_ncrtes.core.month
==========================

- return month list for a winter season according to `year`

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

def get_normal_months_from_year(year):
    """ return month list for a winter season according to `year`

    :param year:
    :type year:
    :return:
    :rtype:
    """
    y1 = year
    m1 = 11
    if m1 in [10, 11, 12]:
        return [(y1, 11),
                (y1, 12),
                (y1 + 1, 1),
                (y1 + 1, 2),
                (y1 + 1, 3)]
    elif m1 in [1, 2, 3, 4, 5, 6]:
        return [(y1 - 1, 11),
                (y1 - 1, 12),
                (y1, 1),
                (y1, 2),
                (y1, 3)]
    else:
        raise Exception('Not supported snow event month')


def get_normal_months_from_period(prd):
    """ return month list for a winter season according to `period`

    :type prd: pyticas.ttypes.Period
    :rtype: list[(int, int)]
    """
    y1 = prd.start_date.year
    m1 = prd.start_date.month
    if m1 in [10, 11, 12]:
        return [(y1, 11),
                (y1, 12),
                (y1 + 1, 1),
                (y1 + 1, 2),
                (y1 + 1, 3)]
    elif m1 in [1, 2, 3, 4, 5, 6]:
        return [(y1 - 1, 11),
                (y1 - 1, 12),
                (y1, 1),
                (y1, 2),
                (y1, 3)]
    else:
        raise Exception('Not supported snow event month')


def to_string(months):
    """ return string converted from month list

    :type months: list[(int, int)]
    :rtype: str
    """
    years = ['%d%02d' % (y, m) for (y, m) in months]
    ystr = '-'.join(sorted(years))
    return ystr
