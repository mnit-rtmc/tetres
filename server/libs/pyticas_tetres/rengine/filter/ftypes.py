# -*- coding: utf-8 -*-

from pyticas.tool import num
from pyticas.ttypes import Serializable

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

M_VMT = 2.0
SLOT_WEATHER = 'weather'
SLOT_INCIDENT = 'incidents'
SLOT_WORKZONE = 'workzones'
SLOT_SPECIALEVENT = 'specialevents'
SLOT_SNOWMANAGEMENT = 'snowmanagements'


class ExtData(Serializable):
    def __init__(self, tti, weather, incidents, workzones, specialevents, snowmanagements):
        """

        :type tti: pyticas_tetres.db.model.TravelTime
        :type weather: pyticas_tetres.db.model.TTWeather
        :type incidents: list[pyticas_tetres.db.model.TTIncident]
        :type workzones: list[pyticas_tetres.db.model.TTWorkzone]
        :type specialevents: list[pyticas_tetres.db.model.TTSpecialevent]
        :type snowmanagements: list[pyticas_tetres.db.model.TTSnowmgmt]
        """
        self.tti = tti
        self.weather = weather
        self.incidents = incidents
        self.workzones = workzones
        self.specialevents = specialevents
        self.snowmanagements = snowmanagements
        self.demand_level = None  # 'L', 'M', 'H'
        """:type: str"""


class IExtFilter(object):
    def __init__(self, name, pass_on_nodata=False, all_items_should_pass=False):
        self.name = name
        self.pass_on_nodata = pass_on_nodata
        self.all_items_should_pass = all_items_should_pass

    def check(self, tti, item):
        """

        :type tti: pyticas_tetres.db.model.TravelTime
        :type item: object
        :rtype: bool
        """
        return False


class And_(IExtFilter):
    def __init__(self, *args):
        self.filters = args
        if (len(set([f.name for f in self.filters])) != 1):
            raise Exception('AND_ can take filters for same data set such as weather or incident..')
        super().__init__(self.filters[0].name)

    def check(self, tti, item):
        """

        :type tti: pyticas_tetres.db.model.TravelTime
        :type item: Union(object, list)
        :rtype: bool
        """
        # if item and hasattr(item[0], 'workzone_id'):
        #     print('==> And_().check() : ', tti, item)
        for filter in self.filters:
            if not filter.check(tti, item):
                # print('--> False')
                return False
        # print('--> True')
        return True


class Or_(IExtFilter):
    def __init__(self, *args):
        self.filters = args
        if (len(set([f.name for f in self.filters])) != 1):
            raise Exception('Or_ can take filters for same data set such as weather or incident..')
        super().__init__(self.filters[0].name)

    def check(self, tti, item):
        """

        :type tti: pyticas_tetres.db.model.TravelTime
        :rtype: bool
        """
        # if item and hasattr(item[0], 'workzone_id'):
        #     print('=> Or_().check() : ', tti, item)
        for filter in self.filters:
            if filter.check(tti, item):
                # print('-> True')
                return True
        # print('-> False')
        return False


class ExtFilter(IExtFilter):
    def __init__(self, name, filters, **kwargs):
        """
        :type name: str
        :type filters: list[callable]
        """
        super().__init__(name, kwargs.get('pass_on_nodata', False), kwargs.get('all_items_should_pass', False))
        self.filters = filters
        self._prev_time = None
        self._prev_item = None
        self.keep_result_in_minute = kwargs.get('keep_result_in_minute', 0)

    def check(self, tti, item):
        """

        :type tti: pyticas_tetres.db.model.TravelTime
        :type item: Union(pyticas_tetres.db.model.TTExtModel, list[pyticas_tetres.db.model.TTExtModel])
        :rtype: bool
        """
        if not item and self.pass_on_nodata:
            return True

        f_passed = True
        for _filter in self.filters:
            # if data (weather or incident or workzone...) related to the travel time are not a single item
            if isinstance(item, list):
                has_passed, has_not_passed = False, False
                for an_item in item:
                    if not _filter(an_item):
                        has_not_passed = True
                    else:
                        has_passed = True
                if (self.all_items_should_pass and has_not_passed) or not has_passed:
                    f_passed = False

            else:
                if not _filter(item):
                    f_passed = False
                    break

        if not self.keep_result_in_minute:
            return f_passed

        # when failed to pass filter
        if not f_passed:

            if self._prev_time:
                cur_time = tti.time
                timediff = cur_time - self._prev_time
                if timediff.seconds / 60.0 < self.keep_result_in_minute:
                    if isinstance(item, list):
                        for _item in item:
                            setattr(_item, 'prev_time', self._prev_time.strftime('%Y-%m-%d %H:%M:00'))
                            setattr(_item, 'prev_item', self._prev_item)
                            _item.is_extended = True
                    else:
                        setattr(item, 'prev_time', self._prev_time.strftime('%Y-%m-%d %H:%M:00'))
                        setattr(item, 'prev_item', self._prev_item)
                        item.is_extended = True
                    f_passed = True

                else:
                    self._prev_item = None
                    self._prev_time = None

        # when passed filter
        else:
            self._prev_time = tti.time
            self._prev_item = item

        return f_passed


class ExtFilterGroup(object):
    def __init__(self, ext_filters, label=''):
        """

        :type ext_filters: list[IExtFilter]
        :type label: str
        """
        self.ext_filters = [ f for f in ext_filters if f ]
        self.label = label
        self.whole_data = []
        """:type: list[ExtData] """
        self.yearly_data = []
        """:type: list[(int, list[ExtData])]"""
        self.monthly_data = []
        """:type: list[([int, int], list[ExtData])]"""
        self.daily_data = []
        """:type: list[(datetime.date, list[ExtData])]"""
        self.all_years = []
        """:type: list[int]"""
        self.all_months = []
        """:type: list[[int, int]"""
        self.all_dates = []
        """:type: list[datetime.date]"""
        self.all_times = []
        """:type: list[datetime.time]"""

    def _vmt(self, m_vmt=None):
        """

        :rtype: (float, float, float)
        """
        if not self.whole_data:
            raise Exception('Run after finishing data filtering')
        m_vmt = m_vmt or M_VMT
        vmts = [extdata.tti.vmt for extdata in self.whole_data]
        stddev = num.stddev(vmts)
        avg = num.average(vmts)
        cut_high = avg + m_vmt * stddev
        cut_low = avg - m_vmt * stddev
        return cut_low, avg, cut_high

    def results_by_demand(self):
        """

        :rtype: (list[ExtData], list[ExtData], list[ExtData])
        """
        cut_low, avg, cut_high = self._vmt()
        low = []
        moderate = []
        high = []
        for extdata in self.whole_data:
            if extdata.tti.vmt < cut_low:
                extdata.demand_level = 'L'
                low.append(extdata)
            elif cut_low <= extdata.tti.vmt < cut_high:
                extdata.demand_level = 'M'
                moderate.append(extdata)
            else:
                extdata.demand_level = 'H'
                high.append(extdata)
        return low, moderate, high

    def check(self, extdata, save_result=True):
        """

        :type extdata: ExtData
        :type save_result: bool
        :rtype: bool
        """
        return self._check(extdata, save_result)

    def check_outofrange(self, extdata):
        """

        :type extdata: ExtData
        :rtype: bool
        """
        return self._check(extdata, False)


    def _check(self, extdata, save_result):
        """

        :type extdata: ExtData
        :type save_result: bool
        :rtype: bool
        """
        f_passed_all = True

        # iterate filter for each data set like weather, incident ...
        for filter in self.ext_filters:

            f_passed = False

            # data of weather or incident or workzone or...
            data = getattr(extdata, filter.name, None)

            if data == None:
                raise Exception('Invalid Data Filter : %s' % filter.name)

            if not data and filter.pass_on_nodata:
                f_passed = True
            else:
                f_passed = filter.check(extdata.tti, data)

            if not f_passed:
                f_passed_all = False
                break

        if save_result and f_passed_all:
            self.whole_data.append(extdata)

        return f_passed_all



    def _check_origin(self, extdata, save_result):
        """

        :type extdata: ExtData
        :type save_result: bool
        :rtype: bool
        """
        f_passed_all = True

        # iterate filter for each data set like weather, incident ...
        for filter in self.ext_filters:

            f_passed = False

            # data of weather or incident or workzone or...
            data = getattr(extdata, filter.name, None)

            if data == None:
                raise Exception('Invalid Data Filter : %s' % filter.name)

            # check if passed at least one item
            if isinstance(data, list):

                if not data and filter.pass_on_nodata:
                    f_passed = True
                else:
                    # check if matching at least one item in given data list (incidents, workzones..)
                    if not filter.all_items_should_pass:
                        f_passed_at_least_1 = False
                        for d in data:
                            if filter.check(d):
                                f_passed_at_least_1 = True
                                break
                        f_passed = f_passed_at_least_1
                    else:
                        # all items must pass filter
                        passed = [ d for d in data if filter.check(d)]
                        f_passed = (len(data) == len(passed))
            else:
                if not filter.check(data):
                    f_passed = False
                else:
                    f_passed = True

            if not f_passed:
                f_passed_all = False
                break

        if save_result and f_passed_all:
            self.whole_data.append(extdata)

        return f_passed_all
