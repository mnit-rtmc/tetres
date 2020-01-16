# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

def traceback(ex, f_print=True):
    import traceback
    tb = traceback.format_exc()
    if f_print:
        print(tb)
    else:
        return tb