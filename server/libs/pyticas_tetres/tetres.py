# -*- coding: utf-8 -*-
"""
pyticas_tetres.tetres
======================

- returns `Infra` object used in the system

"""
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas.infra import Infra

infra = None
""":type: pyticas.infra.Infra """

def get_infra():
    """ returns `Infra` object. All modules must get `Infra` object from this function.

    :rtype: pyticas.infra.Infra
    """
    global infra

    infra = Infra.get_infra()
    return infra
