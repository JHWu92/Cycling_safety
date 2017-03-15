# coding=utf-8
import os
import argparse
import shlex

import geopandas as gp
import pandas as pd


def parse_upload_log(log_file):
    with open(log_file) as f:
        lines = [eval(line.strip().split('\t')[1]) for line in f]
    return pd.DataFrame.from_dict(lines)


def transform_save_segments(seg_geojson):
    segs = gp.read_file(seg_geojson)
    segs['wkt'] = segs.geometry.apply(lambda x: x.wkt)
    segs.index.name = 'index_seg'
    segs = segs[['STREETSEGID', 'wkt']].reset_index()
    segs['sid'] = ''
    segs['totalScore'] = ''
    segs['how_many'] = ''
    segs[['sid', 'STREETSEGID', 'index_seg', 'totalScore', 'how_many', 'wkt']].to_csv('2DB_RoadSegment.csv',
                                                                                      header=False, index=False)
    return segs


def parse_arguments(cmd=None):
    if isinstance(cmd, (str, unicode)):
        cmd = shlex.split(cmd)
    parser = argparse.ArgumentParser(description='convert log files to DB importable files')
    parser.add_argument('-r', '--root-dir', type=str, help='root directory containing videos and gps traces, ' +
                                                           'it is the working directory(chdir to it)')
    parser.add_argument('--upload-logger', default='upload_video.log', help='record uploaded result, clip-url pair')
    parser.add_argument('--segs-for-clips-csv', default='segs_for_clips.csv', help='segs_for clips')
    parser.add_argument('--segs', help='segments file', required=True)
    args = parser.parse_args(cmd) if cmd is not None else parser.parse_args()
    return args


def main(args):
    print 'tranforming segments'
    segs = transform_save_segments(args.segs)

    print 'saving clips url and videoRoadSeg'
    df_log = parse_upload_log(args.upload_logger)
    df_log_uploaded = df_log[~df_log.videoId.isnull()]
    df_segs_clips = pd.read_csv(args.segs_for_clips_csv, index_col=0)
    clips_uploaded_with_segs = df_segs_clips.merge(df_log_uploaded)[['index_seg', 'clip_name', 'title', 'videoId']]
    clips_uploaded_with_segs['empty_col'] = ''
    clips_uploaded_with_segs['empty_col2'] = ''
    clips_uploaded_with_segs['empty_col3'] = ''

    clips_uploaded_with_segs[['empty_col', 'clip_name', 'title', 'videoId']].to_csv(
        '2DB_video.csv', header=None, index=None)

    clips_uploaded_with_segs[['empty_col', 'empty_col2', 'empty_col3', 'clip_name', 'index_seg']].to_csv(
        '2DB_VideoRoadSeg.csv', header=None, index=None)


if __name__ == "__main__":
    args = parse_arguments()
    if args.root_dir is not None:
        print 'changing to the root dir'
        os.chdir(args.root_dir)
    main(args)