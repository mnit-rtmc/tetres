# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

import datetime

from pyticas_tetres.cfg import SE_ARRIVAL_WINDOW, SE_DEPARTURE_WINDOW1, SE_DEPARTURE_WINDOW2
from pyticas_tetres.da.tt_specialevent import TTSpecialeventDataAccess
from pyticas_tetres.logger import getLogger
from pyticas_tetres.rengine.helper import loc
from pyticas_tetres.rengine.helper import special_event as se_helper
from pyticas_tetres.util.noop_context import nonop_with


def categorize(ttri, prd, ttdata, **kwargs):
    """

    :type ttri: pyticas_tetres.ttypes.TTRouteInfo
    :type prd: pyticas.ttypes.Period
    :type ttdata: list[pyticas_tetres.ttypes.TravelTimeInfo]
    :return:
    """
    lock = kwargs.get('lock', nonop_with())

    given_seis = kwargs.get('specialevents', None)
    seis = given_seis or se_helper.find_specialevents(prd, SE_ARRIVAL_WINDOW, SE_DEPARTURE_WINDOW1,
                                                      SE_DEPARTURE_WINDOW2)

    specialevents = []
    for sei in seis:
        distance = loc.minimum_distance(ttri.route, float(sei.lat), float(sei.lon))
        specialevents.append((sei, distance))

    year = prd.start_date.year
    ttseDA = TTSpecialeventDataAccess(year)

    # avoid to save duplicated data
    with lock:
        is_deleted = ttseDA.delete_range(ttri.id, prd.start_date, prd.end_date, item_ids=[v.id for v in seis])
        if not is_deleted or not ttseDA.commit():
            ttseDA.rollback()
            ttseDA.close_session()
            getLogger(__name__).debug('! specialevent.categorize(): fail to delete existing data')
            return -1

    dict_data = []
    for idx, tti in enumerate(ttdata):
        seis = _find_ses(specialevents, tti.str2datetime(tti.time))
        for (sei, distance, event_type) in seis:
            dict_data.append({
                'tt_id': tti.id,
                'specialevent_id': sei.id,
                'distance': distance,
                'event_type': event_type
            })

    if dict_data:
        with lock:
            inserted_ids = ttseDA.bulk_insert(dict_data, print_exception=True)
            if not inserted_ids or not ttseDA.commit():
                ttseDA.rollback()
                ttseDA.close_session()
                getLogger(__name__).warning('! specialevent.categorize(): fail to insert categorized data')
                return -1

    ttseDA.close_session()
    return len(dict_data)


def _find_ses(specialevents, dt):
    """
    :type specialevents: list[(pyticas_tetres.ttrms_types.SpecialeventInfo, float)]
    :type dt: datetime.datetime
    :rtype: list[(pyticas_tetres.ttrms_types.SpecialeventInfo, float, int)]
    """
    seis = []
    for idx, (sei, distance) in enumerate(specialevents):
        sdt2 = sei.str2datetime(sei.start_time)
        sdt1 = sdt2 - datetime.timedelta(minutes=SE_ARRIVAL_WINDOW)
        edt = sei.str2datetime(sei.end_time)
        edt1 = min(sdt2 + datetime.timedelta(minutes=SE_DEPARTURE_WINDOW1), edt)
        edt2 = edt1 + datetime.timedelta(minutes=SE_DEPARTURE_WINDOW2)

        # print('dt=', dt, ', event: name=', sei.name, ', start_time=', sei.start_time, ', end_time=', sei.end_time, ', arrival=', sdt1, '~', sdt2, ', departure=', edt1, '~', edt2)
        if sdt1 <= dt <= sdt2:
            # print(' : type=_A')
            seis.append((sei, distance, 'A'))  # Arrival
        elif edt1 <= dt <= edt2:
            # print(' : type=_D')
            seis.append((sei, distance, 'D'))  # Departure

    return seis
