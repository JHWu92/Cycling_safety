# coding=utf-8
from utils import *
from snap2road import snap2road


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
               cnsectv_thres=0.08, return_snap_coords=False):
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
        for sub_indices in group_consecutive(projected.index.values, stepsize=cnsectv_stepsize):
            sub = projected[sub_indices]
            s, e = sub.min(), sub.max()
            round_s, round_e = float_round(s, direction='down'), float_round(e, direction='up')
            if e - s > cnsectv_thres:
                segs_linear_reference.append((seg_index, round_s, round_e, round_e - round_s))

    if return_snap_coords:
        return segs_linear_reference, snap_pts

    return segs_linear_reference
