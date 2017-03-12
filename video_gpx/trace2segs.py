# coding=utf-8
from collections import Counter
from itertools import chain
import os

import pandas as pd
import geopandas as gp
from shapely.geometry import Point

from utils import *
from geom_helper import pts2segs
from constants import index_seg


def seg_disambiguation(list_of_seg_candidates, window_size=3, debug=False, decrease_weight=0.0, keep_tie=False):
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


def trace2segs(segs, trace, tms=(), need_snap=True, pause=False, bfr_crs=3559, close_jn_dist=10, far_jn_dist=30,
               cnsectv_stepsize=3, cnsectv_thres=0.08, length_col=None):
    """
    input:
        segs: gpdf, one line per segment
        trace: list of (lon, lat) points
    return:
        {'segs': segment_linear_reference_df, '#pts_no_segs': number of pts without segment assignment}
        columns of 'segs': ['index_seg', 'start', 'end', 'ratio', 'ratio_before_round']
    options:
        # For snap2road()
        tms: default (). list of "%Y-%m-%dT%H:%M:%SZ". It would help improve snapped quality
        need_snap: default True. if True, perform snap2road on trace
        pause: default False. If True, pause every 0.5 second between snap requests.

        # For pts2segs()
        bfr_crs: default 3559. Used in pts2segs().
        close_jn_dist: default 10 meter. Allowing multiple segments for one point(assumed as intersection)
        far_jn_dist: default 20 meter. Find the nearest segment for one point

        # For finalizing segment assignment
        consectv_stepsize: default 3. Used in group_consecutive(), define consecutive.
        cnsectv_thres: default 0.08. The ratio threshold to determine whether a video covers a segment.

        # For output:
        tms: default (), if not null, calculate velocity.
        length_col: default None, value for the output column length is NaN. Otherwise, value=segs[length_col]*ratio
    """

    if need_snap:
        # snapped every point in trace to OSM road network
        from snap2road import snap2road
        snapped_res = snap2road(trace, tms, pause=pause)
        snapped_df = pd.DataFrame.from_dict(snapped_res['snapped'])
        snapped_trace = list(chain(*snapped_df.snapped.values))
    else:
        snapped_trace = trace

    # find segment index for each point, keep #points without segment assignment
    snapped_trace_gpdf = gp.GeoDataFrame([Point(x) for x in snapped_trace], columns=['geometry'])
    pts_segs, pts_no_segs = pts2segs(snapped_trace_gpdf, segs, bfr_crs=bfr_crs,
                                     close_jn_dist=close_jn_dist, far_jn_dist=far_jn_dist)

    # get the segment index(indices) for each point(index) and merge into snapped_trace_gpdf
    pts_idx_ln_idx = snapped_trace_gpdf.merge(pts_segs, left_index=True, right_on='index_pt') \
        .groupby('index_pt')['index_ln'].apply(list).to_frame()
    snapped_trace_gpdf = snapped_trace_gpdf.merge(pts_idx_ln_idx, left_index=True, right_index=True)

    # 2 phrases seg_disambiguation
    snapped_trace_gpdf['clean_seg'] = seg_disambiguation(snapped_trace_gpdf.index_ln.values, keep_tie=True)
    snapped_trace_gpdf['clean_seg2'] = seg_disambiguation(snapped_trace_gpdf.clean_seg.values)

    # get unique segment candidates
    trace_segs_idx = pd.unique(chain(*snapped_trace_gpdf.clean_seg2.values))

    # for each candidate, calculate the projected ratio of snapped traces to determine whether a segment is covered
    segs_lin_ref = []
    for seg_index in trace_segs_idx:
        # select the geometry of a segment
        seg = segs.loc[seg_index]
        length = seg[length_col] if length_col else None
        seg = seg.geometry
        # use segment index before seg_disambiguation to find relevant points for this segment, and project the point.
        projected = snapped_trace_gpdf[snapped_trace_gpdf.index_ln.apply(lambda x: seg_index in x)].geometry \
            .apply(lambda x: seg.project(x, normalized=True))

        # projected.index.values is the order of the points. consecutive points here is a consecutive trip on a segment
        for sub_indices in group_consecutive(projected.index.values, stepsize=cnsectv_stepsize):
            sub = projected[sub_indices]
            s, e = sub.min(), sub.max()
            ratio_before_round = e - s
            round_s, round_e = float_round(s, direction='down'), float_round(e, direction='up')
            ratio = round_e - round_s
            ratio_length = ratio * length if length else None
            # keep segment where the projected ratio is larger than threshold
            if ratio_before_round > cnsectv_thres:
                segs_lin_ref.append((seg_index, round_s, round_e, ratio, ratio_length, ratio_before_round))

    res = pd.DataFrame(segs_lin_ref, columns=['index_seg', 'start', 'end', 'ratio', 'length', 'ratio_before_round'])
    return {'segs': res, '#pts_no_segs': pts_no_segs.shape[0]}


def parse_json_of_one_video(args, segs, video_snapped, clip_quality_res, segs_lin_res):
    for snapped_res in video_snapped:
        clip_name = snapped_res['clip_name']

        if args.verbose:
            print 'processing clip:', clip_name

        # find segments for a clip, in terms of linear reference
        snapped_df = pd.DataFrame.from_dict(snapped_res['snapped'])
        snapped_trace = list(chain(*snapped_df.snapped.values))
        segs_res = trace2segs(segs, snapped_trace, need_snap=False, length_col='SHAPE_Length')
        segs_lin = segs_res['segs']
        segs_lin['clip_name'] = clip_name
        segs_lin_res.append(segs_lin)

        # record quality (# pts without segment, velocity) of a clip
        quality = {
            'clip_name': clip_name,
            'v_avg': snapped_res['v_avg'],
            'v_median': snapped_res['v_median'],
            'v_max': snapped_res['v_max'],
            'duration_clip': snapped_res['duration_clip'],
            'start': snapped_res['start'],
            'end': snapped_res['end'],
            'num_pts_no_segs': segs_res['#pts_no_segs'],
            'clip_no_seg': len(segs_lin) == 0
        }
        clip_quality_res.append(quality)


def find_segs_for_clips(args):

    print 'loading segment file...'
    segs = gp.read_file(args.segs)

    match_file = pd.read_csv(args.match_file)
    snapped_files = match_file.json_file.values
    segs_lin_res = []
    clip_quality_res = []

    for sfile in snapped_files:
        if not os.path.exists(sfile):
            if args.verbose:
                print 'does not exist: %s' % sfile
            continue

        print 'processing clips of video:', sfile
        video_snapped = load_json_file(sfile)
        parse_json_of_one_video(args, segs, video_snapped, clip_quality_res, segs_lin_res)

    print 'saving segments result and clips quality'
    segs_lin_res = pd.concat(segs_lin_res, ignore_index=True)
    segs_lin_res[index_seg] = segs_lin_res[index_seg].astype(int)
    segs_lin_res.to_csv(args.segs_for_clips_csv)
    clip_quality_res = pd.DataFrame.from_dict(clip_quality_res)
    clip_quality_res.to_csv(args.clips_quality_csv)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='find corresponding segments for each clip')

    parser.add_argument('--segs', help='segments file', required=True)
    parser.add_argument('-r', '--root-dir', type=str, help='root directory containing videos and gps traces, ' +
                                                           'it is the working directory(chdir to it)')
    parser.add_argument('--match-file', default='gpx_video_match.csv',
                        help='match between gpx, video and snapped file, it will be saved in the input-directory')
    parser.add_argument('--segs-for-clips-csv', default='segs_for_clips.csv', help='segs_for clips')
    parser.add_argument('--clips-quality-csv', default='clips_quality.csv', help='clips quality')
    # test/debug argument, default False if not specified
    parser.add_argument('-v', '--verbose', help='be verbose of the output', action='store_true')

    args = parser.parse_args()

    # change to working root directory
    if args.root_dir:
        os.chdir(args.root_dir)

    if args.verbose:
        print '===========arguments==========='
        print args
        print '===========current working directory==========='
        print os.getcwd()

    find_segs_for_clips(args)
