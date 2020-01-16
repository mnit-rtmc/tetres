# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from pyticas import cfg
from pyticas.ttypes import TrafficType, RNodeData
from pyticas.tool.cache import lru_cache


class RNodeDataReader(object):
    
    def __init__(self, ddr):
        """

        :param ddr: detector data reader
        :type ddr: DetectorDataReader
        :return:
        """
        self.ddr = ddr
    
    def get_volume(self, rn, prd, dc=None, **kwargs):
        """
        :type rn: pyticas.ttypes.RNodeObject
        :type prd: Period
        :type dc: DetectorChecker
        :rtype: RNodeData
        """
        return self._get_traffic_data(rn, prd, TrafficType.volume, dc, self.ddr.get_volume, **kwargs)

    def get_scan(self, rn, prd, dc=None, **kwargs):
        """
        :type rn: pyticas.ttypes.RNodeObject
        :type prd: Period
        :type dc: DetectorChecker
        :rtype: RNodeData
        """
        return self._get_traffic_data(rn, prd, TrafficType.scan, dc, self.ddr.get_scan, **kwargs)
    
    def get_density(self, rn, prd, dc=None, **kwargs):
        """
        :type rn: pyticas.ttypes.RNodeObject or str
        :type prd: Period
        :type dc: DetectorChecker
        :rtype: RNodeData
        """
        return self._get_traffic_data(rn, prd, TrafficType.density, dc, self.ddr.get_density, **kwargs)
    
    def get_total_flow(self, rn, prd, dc=None, **kwargs):
        """
        :type rn: pyticas.ttypes.RNodeObject or str
        :type prd: Period
        :type dc: DetectorChecker
        :rtype: RNodeData
        """
        return self._get_traffic_data(rn, prd, TrafficType.flow, dc, self.ddr.get_flow, **kwargs)
    
    def get_average_flow(self, rn, prd, dc=None, **kwargs):
        """
        :type rn: pyticas.ttypes.RNodeObject or str
        :type prd: Period
        :type dc: DetectorChecker
        :rtype: RNodeData
        """
        return self._get_traffic_data(rn, prd, TrafficType.flow_average, dc, self.ddr.get_flow, **kwargs)
    
    def get_speed(self, rn, prd, dc=None, **kwargs):
        """
        :type rn: pyticas.ttypes.RNodeObject or str
        :type prd: Period
        :type dc: DetectorChecker
        :rtype: RNodeData
        """
        return self._get_traffic_data(rn, prd, TrafficType.speed, dc, self.ddr.get_speed, **kwargs)

        # qs = self.get_average_flow(rn, prd, dc, **kwargs)
        # ks = self.get_density(rn, prd, dc, **kwargs)
        # us = ks.clone()
        # us.data = []
        # us.detector_data = {}
        # us.traffic_type = TrafficType.speed
        #
        # for det_name, data in qs.detector_data.items():
        #     for idx, q in enumerate(data):
        #         try:
        #             k = ks.detector_data[det_name][idx]
        #         except Exception as ex:
        #             print('>> ', rn.station_id, rn.name, det_name, idx, len(ks.detector_data[det_name]))
        #             raise ex
        #         if det_name not in us.detector_data:
        #             us.detector_data[det_name] = []
        #         if q > 0 and k > 0:
        #             us.detector_data[det_name].append(q/k)
        #         else:
        #             us.detector_data[det_name].append(-1)
        #
        # n_data = len(prd.get_timeline())
        #
        # for idx in range(n_data):
        #     _us = [ us.detector_data[det_name][idx] for det_name in us.detector_names if us.detector_data[det_name][idx] > 0 ]
        #     if _us:
        #         us.data.append(sum(_us) / len(_us))
        #     else:
        #         us.data.append(-1)
        #
        # return us

    
    def get_occupancy(self, rn, prd, dc=None, **kwargs):
        """
        :type rn: pyticas.ttypes.RNodeObject or str
        :type prd: Period
        :type dc: DetectorChecker
        :rtype: RNodeData
        """
        return self._get_traffic_data(rn, prd, TrafficType.occupancy, dc, self.ddr.get_occupancy, **kwargs)
    
    @lru_cache
    def _get_traffic_data(self, rn, prd, traffic_type, dc, dm, **kwargs):
        """ real routine to retrieve and manipulate traffic data
    
        :param rn: rnode object
        :type rn: pyticas.ttypes.RNodeObject
    
        :param prd: period
        :type prd: Period
    
        :param traffic_type: traffic type
        :type traffic_type: TrafficType
    
        :param dc: detector checker
        :type dc: DetectorChecker
    
        :param dm: data method name
        :type dm: function
    
        :param kwargs: optional parameters
    
        :rtype: RNodeData
        """
        missing_value = kwargs.get('missing_value', cfg.MISSING_VALUE)
    
        dets = [ det for det in rn.detectors if not dc or dc(det) ]
        prd30 = prd.clone()
        prd30.interval = cfg.DETECTOR_DATA_INTERVAL
    
        data = [ dm(det, prd30) for det in dets ]
    
        rnode_data_obj = RNodeData(rn, prd, traffic_type)
        rnode_data_obj.set_data(dets, data, missing_value=missing_value)
    
        return rnode_data_obj
