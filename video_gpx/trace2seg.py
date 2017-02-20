# coding=utf-8

def consecutive(data, stepsize=1):
    """
    group consecutive number as as sub list.
    E.g. data = [1, 2, 3, 5, 6, 7, 10, 11]
    stepsize=1: return [[1,2,3], [5,6,7], [10,11]]
            =2: return [[1,2,3,5,6,7], [10,11]]
    :param data: list/array
    :param stepsize: define consecutive.
    """
    import numpy as np
    return np.split(data, np.where(np.diff(data) > stepsize)[0] + 1)


def float_round(num, places=1, direction='up'):
    from math import ceil, floor
    assert direction in ['up', 'down'], 'direction options are: up and down'
    func = {'up': ceil, 'down': floor}[direction]
    return func(num * (10 ** places)) / float(10 ** places)


def even_chunks(array, max_chunk_size, indices=False):
    import math
    size = len(array)
    num_chunks = math.ceil(size * 1.0 / max_chunk_size)
    new_chunk_size = int(math.ceil(size * 1.0 / num_chunks))
    return chunks(array, new_chunk_size, indices)


def chunks(array, chunk_size, indices=False, right_close=False):
    """Yield successive chunks with chunk_size from array.
    params:
        indices: if false, yield chunks of array; if True, yield indices pair (left, right) only
        right_close: if False return elements with indices in [left, right); if True, return indices in [left, right]
    """
    for i in range(0, len(array), chunk_size):
        left = i
        right = min(len(array), i + chunk_size + right_close)
        if indices:
            yield (left, right)
        else:
            yield array[left: right]


def snap2road(pts_lon_lat, timestamps=[], return_confidence=False):
    """
    params:
        pts_lon_lat: [[lon, lat], [], ...]
        timestamps: ['2015-10-15T12:06:50Z', ...]
    return:
        new_gps: [[lon, lat], [], ...], len(new_gps) not necessarily equals to len(pts_lon_lat)
        confidences: [ (which batch, # origin pts, # snapped pts, confidence), (), ..]
    """
    import mapbox as mp
    access = "pk.eyJ1Ijoic3VyYWpuYWlyIiwiYSI6ImNpdWoyZGQzYjAwMXkyb285b2Q5NmV6amEifQ.WBQAX7ur2T3kOLyi11Nybw"
    service = mp.MapMatcher(access_token=access)
    new_gps = []
    confidences = []
    for num_batch, (s, e) in enumerate(even_chunks(pts_lon_lat, 100, indices=True)):
        batch_pts = pts_lon_lat[s:e]
        batch_tss = timestamps[s:e]
        geojson = {'type': 'Feature',
                   'properties': {'coordTimes': batch_tss},
                   'geometry': {'type': 'LineString',
                                'coordinates': batch_pts}}
        response = service.match(geojson, profile='mapbox.cycling')
        var = response.geojson()
        features = var['features']
        for f in features:
            coords = f['geometry']['coordinates']
            new_gps.extend(coords)
            properties = f['properties']
            if return_confidence:
                confidences.append((num_batch, len(batch_pts), len(coords), properties['confidence']))
    if return_confidence:
        return new_gps, confidences
    return new_gps


def seg_disambiguation(list_of_seg_candidates, window_size=3, debug=False, decrease_weight=0.0, keep_tie=False):
    from itertools import chain
    from collections import Counter
    def debug_tie_count():
        max_count = counter.most_common(1)[0][1]
        tie_node = []
        for node, count in counter.most_common():
            if count >= max_count:
                tie_node.append(node)
        tie_count = len(tie_node)
        if tie_count == 2: print i, counter
        assert tie_count <= 3, ('index=', i, 'context_counter=', counter)

    def get_tie():
        max_count = counter.most_common(1)[0][1]
        tie_node = []
        for node, count in counter.most_common():
            if count >= max_count:
                tie_node.append(node)
        return tie_node

    clean_segs = []
    list_size = len(list_of_seg_candidates)
    for i, seg_cands in enumerate(list_of_seg_candidates):
        if len(seg_cands) == 0:
            clean_segs.append([])
            continue
        left, right = max(0, i - window_size), min(list_size, i + window_size + 1)
        context_left = clean_segs[left: i]  # use clean seg instead of original seg_candidates
        context_right = list_of_seg_candidates[i + 1: right]
        counter_left = Counter(list(chain(*context_left)))
        counter_right = Counter(list(chain(*context_right)))
        # counter_self = Counter(seg_cands * int(window_size * (1-decrease_weight)))  # solution1, doesn't work well
        counter_self = Counter(seg_cands * (window_size * 2 - len(context_left) - len(context_right) + 1))
        counter = counter_left + counter_right + counter_self
        tie = get_tie()
        if keep_tie:
            seg = tie  # keep all tie
        else:
            seg = [tie[0]]  # keep the first element of tie
        clean_segs.append(seg)
        if debug:
            debug_tie_count()
    return clean_segs
    # print counter_left.most_common(1),counter_right.most_common(1),counter.most_common(1)


def trace2segs(segs, trace_pts, tss=[], return_confidence=False, close_jn_dist=10, far_jn_dist=30, cnsectv_stepsize=3,
               cnsectv_thres=0.08):
    """

    """
    from geom_helper import pts2segs
    from itertools import chain
    import pandas as pd
    import geopandas as gp
    from shapely.geometry import Point
    pts_lon_lat = list(trace_pts.geometry.apply(lambda x: x.coords[0]).values)
    snap_pts = snap2road(pts_lon_lat, tss, return_confidence=return_confidence)

    if return_confidence:  # if return_confidence
        snap_pts, confs = snap_pts
        print 'confidence of snap to road', confs

    snap_pts_gpdf = gp.GeoDataFrame([Point(x) for x in snap_pts], columns=['geometry'])

    pts_segs, _ = pts2segs(snap_pts_gpdf, segs, bfr_crs=3559, close_jn_dist=close_jn_dist, far_jn_dist=far_jn_dist)

    snap_pts_gpdf = snap_pts_gpdf.merge(
        snap_pts_gpdf.merge(pts_segs, left_index=True, right_on='index_pt').groupby('index_pt')['index_ln'].apply(
            list).to_frame(),
        left_index=True, right_index=True)
    snap_pts_gpdf['clean_seg'] = seg_disambiguation(snap_pts_gpdf.index_ln.values, keep_tie=True)

    snap_pts_gpdf['clean_seg2'] = seg_disambiguation(snap_pts_gpdf.clean_seg.values)

    trace_segs_idx = pd.unique(chain(*snap_pts_gpdf.clean_seg2.values))
    segs_linear_reference = []
    for seg_index in trace_segs_idx:
        seg = segs.loc[seg_index, 'geometry']
        projected = snap_pts_gpdf[snap_pts_gpdf.index_ln.apply(lambda x: seg_index in x)].geometry.apply(
            lambda x: seg.project(x, normalized=True))
        for sub_indices in consecutive(projected.index.values, stepsize=cnsectv_stepsize):
            sub = projected[sub_indices]
            s, e = sub.min(), sub.max()
            round_s, round_e = float_round(s, direction='down'), float_round(e, direction='up')
            if e - s > cnsectv_thres:
                segs_linear_reference.append((seg_index, round_s, round_e, round_e - round_s))
    return segs_linear_reference
