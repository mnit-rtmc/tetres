# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'


from pyticas import cfg
from pyticas.infra import Infra

QUEUE_OCC_THRESHOLD = 25
K_JAM_RAMP = 140
QUEUE_EMPTY_STEPS = 3
WAIT_TARGET_RATIO = 0.75
PASSAGE_DEMAND_FACTOR = 1.15

def demand(ent, prd, **kwargs):
    """ return demand of entrance

    :type ent: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    """
    queues = ent.get_queue_detectors()
    if any(queues):
        return ramp_queue_flow(ent, prd, **kwargs)

    pflows = ramp_passage_flow(ent, prd)
    return [ pq * PASSAGE_DEMAND_FACTOR if pq > 0 else pq for pq in pflows ]


def cumulative_input_output(ent, prd, **kwargs):
    """ return estimated cumulative input and output of the entrance

    :type ent: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    """
    infra = kwargs.get('infra', Infra.get_infra())
    ddr = infra.ddr
    queue_full_count = 0
    queue_empty_count = 0
    green_accum = 0
    occ = ramp_queue_occupancy(ent, prd, 'max')
    input = ramp_queue_volume(ent, prd)
    output = ramp_passage_volume(ent, prd)
    if input == None or output == None:
        return None, None
    greens = ent.get_green_detectors()
    green_volumes = ddr.get_volume(greens[0], prd) if any(greens) else [0] * len(output)
    cumulative_input = []
    cumulative_output = []
    cumulative_input.append(max(input[0], 0))
    cumulative_output.append(max(output[0], 0))
    reset_count = 0
    met = ent.meters[0]

    for idx in range(1, len(input)):
        passage_failure = output[idx] < 0
        green_accum += (green_volumes[idx] if green_volumes[idx] > 0 else 0)
        queue_length = max(cumulative_input[idx - 1] - cumulative_output[idx - 1], 0)
        estimated_under_count = 0

        # if occupancy is high
        if occ[idx] > QUEUE_OCC_THRESHOLD:
            queue_full_count += 1
            max_storage = met.storage * ent.lanes * K_JAM_RAMP / cfg.FEET_PER_MILE
            under = max_storage - queue_length
            queue_overflow_ratio = min(2 * queue_full_count * 30.0 / max(met.max_wait, 1), 1)
            min_demand_adjustment = int(round(queue_full_count * 30 / 60)) * 30 / 60.0
            estimated_under_count = max(queue_overflow_ratio * under, min_demand_adjustment)
            input_volume = input[idx] + estimated_under_count
        else:
            queue_full_count = 0
            input_volume = input[idx]

        ci = cumulative_input[idx - 1] + max(input_volume, 0)
        co = cumulative_output[idx - 1] + max(output[idx], 0)

        # reset cumulative data
        # count queue empty
        # if count queue empty > 3 time stpes
        is_demand_below_passage = ci - co < -1
        is_passage_below_green = co - green_accum < -1
        is_queue_volume_low = is_demand_below_passage or is_passage_below_green
        if is_queue_volume_low and occ[idx] < QUEUE_OCC_THRESHOLD:
            queue_empty_count += 1
        else:
            queue_empty_count = 0

        if queue_empty_count >= QUEUE_EMPTY_STEPS:
            reset_count += 1
            ci = 0
            co = 0
            queue_full_count = 0
            queue_empty_count = 0
            green_accum = 0

        cumulative_input.append(ci)
        cumulative_output.append(co)

    return cumulative_input, cumulative_output


def ramp_queue_occupancy(ent, prd, agg_method='max', **kwargs):
    """ return average occupancy of queue detectors

    :type ent: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    :param agg_method: aggregation method. it can be 'avg' or 'max' or 'min' or 'sum'
    :type agg_method: str
    """
    infra = kwargs.get('infra', Infra.get_infra())
    ddr = infra.ddr
    queues = ent.get_queue_detectors()
    if any(queues):
        occs = []
        for q in queues:
            occs.append(ddr.get_occupancy(q, prd))

        occ_data = []
        q_count = len(queues)
        for didx in range(len(occs[0])):
            total = 0
            min_value = 999
            max_value = -999
            for qidx in range(q_count):
                o = occs[qidx][didx]
                if min_value > o: min_value = o
                if max_value < o: max_value = o
                total += o
            avg = total / q_count if total > 0 else 0
            if agg_method == 'avg':
                occ_data.append(avg)
            elif agg_method == 'min':
                occ_data.append(min_value)
            elif agg_method == 'max':
                occ_data.append(max_value)
            elif agg_method == 'sum':
                occ_data.append(total)

        del occs

        return occ_data

    return None


def ramp_queue_flow(ent, prd, **kwargs):
    """ return total flow rates of queue detectors

    :type ent: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    """
    infra = kwargs.get('infra', Infra.get_infra())
    volumes = ramp_queue_volume(ent, prd, infra=infra)
    return [(v * 3600 / prd.interval if v > 0 else cfg.MISSING_VALUE) for v in volumes]


def ramp_queue_volume(ent, prd, **kwargs):
    """ return total volume of queue detectors

    if there is no queue detectors in the entrance,
    use passage volume * PASSAGE_DEMAND_FACTOR

    :type ent: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    """
    infra = kwargs.get('infra', Infra.get_infra())
    queues = ent.get_queue_detectors()
    if any(queues):
        return _total_volume(infra.ddr, queues, prd)
    else:
        return [-1]*len(prd.get_timeline())


def ramp_passage_flow(ent, prd):
    """ return total volume of passage detector

    :type ent: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    """
    volumes = ramp_passage_volume(ent, prd)
    return [(v * 3600 / prd.interval if v > 0 else v) for v in volumes]


def ramp_passage_volume(ent, prd, **kwargs):
    """ return total volume of passage detector

    if there is a merge detector, use volume of merge detector
    if there is passage and bypass detectors, use passage flow rates - bypass volume
    if there is no passage detector, use volume of bypass detector

    :type ent: pyticas.ttypes.RNodeObject
    :type prd: pyticas.ttypes.Period
    """
    infra = kwargs.get('infra', Infra.get_infra())
    ddr = infra.ddr
    merges = ent.get_merge_detectors()
    passages = ent.get_passage_detectors()
    bypasses = ent.get_bypass_detectors()
    n_data = len(prd.get_timeline())
    volumes = [-1] * n_data

    if merges:
        volumes = _total_volume(ddr, merges, prd)
    elif passages:
        volumes = _total_volume(ddr, passages, prd)
        if bypasses:
            b_vols = _total_volume(ddr, bypasses, prd)
            volumes = [ max(v - b_vols[idx], 0) if b_vols[idx] > 0 else v for idx, v in enumerate(volumes) ]
    elif bypasses:
        volumes = _total_volume(ddr, bypasses, prd)

    return volumes


def _total_volume(ddr, dets, prd, **kwargs):
    """

    :param dets:
    :param prd:
    :param kwargs:
    :return:
    """
    volumes = []
    for det in dets:
        volumes.append(ddr.get_volume(det, prd))

    total_volumes = []
    for idx in range(len(volumes[0])):
        data_at_i = [ vol[idx] for didx, vol in enumerate(volumes) if vol[idx] >= 0 ]
        if data_at_i:
            total_volumes.append(sum(data_at_i))
        else:
            total_volumes.append(cfg.MISSING_VALUE)

    return total_volumes



