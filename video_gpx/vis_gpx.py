# coding=utf-8
import argparse
import os

from shapely.geometry import LineString
import geopandas as gp
import pandas as pd

from leaflet_creation import create_map_visualization
from utils import load_json_file
from split_video_gpx import parse_gpx


def conf2color(conf):
    if conf>0.8:
        return '#1CFF00'
    if conf>0.5:
        return '#4EFFC5'
    if conf>0.1:
        return '#E8AE19'
    return '#FF100F'


def concat_gpx_snapped(match_df):
    raw_gpdfs = []
    snapped_gpdfs = []
    for gpx_file, js_file in match_df[match_df.match][['gpx', 'json_file']].values:
        vfile, locs, tms = parse_gpx(gpx_file)
        raw_line = LineString(locs)
        raw_gpdfs.append((raw_line, '#00e', gpx_file, js_file))

        snapped_json = load_json_file(js_file)
        for bidx, batch in enumerate(snapped_json):
            clip_name = batch['clip_name']
            start, end = batch['start'], batch['end']
            for sbidx, sub_batch in enumerate(batch['snapped']):
                conf = sub_batch['confidence']
                snapped_line = LineString(sub_batch['snapped'])
                snapped_gpdfs.append((snapped_line, conf2color(conf), bidx, sbidx, clip_name, start, end))

    raw_gpdfs = gp.GeoDataFrame(raw_gpdfs, columns=['geometry', 'color', 'gpx_file', 'js_file']).reset_index()
    snapped_gpdfs = gp.GeoDataFrame(snapped_gpdfs, columns=['geometry', 'color', 'batch_id', 'sub_batch_id', 'clip_name', 'start', 'end'])
    return raw_gpdfs, snapped_gpdfs


def main(args):

    # change to working root directory
    if args.root_dir:
        os.chdir(args.root_dir)
    match_df = pd.read_csv(args.match_file)
    segs_for_clips_df = pd.read_csv(args.segs_for_clips_csv)
    segs = gp.read_file(args.segs)
    covered_segs = segs_for_clips_df.groupby('index_seg').clip_name.apply(list).apply(lambda x: '<br>'.join(x)).to_frame('clip_name')
    covered_segs = segs[['geometry', 'STREETSEGID']].merge(covered_segs, left_index=True, right_index=True)
    covered_segs['color'] = '#555'
    raw_gpdfs, snapped_gpdfs = concat_gpx_snapped(match_df)
    html_title = 'raw_snap'
    file_path = ''
    file_name = 'raw_snap'
    lon, lat = -77.036484, 38.907215  #D.C.
    zoom = 12
    init_layers = ['streets']
    map_layers = ['light','streets', 'satellite']
    gpdfs = [raw_gpdfs, snapped_gpdfs, covered_segs]
    binding_data = [['ly1', 'raw traces'], ['ly2', 'snapped traces'], ['ly3', 'covered_segs']]
    create_map_visualization(html_title, file_path, file_name, lat, lon, zoom, init_layers, map_layers, binding_data, gpdfs)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Visualizing gpx trace, snapped traces and covered segments')

    parser.add_argument('-r', '--root-dir', type=str, help='root directory containing videos and gps traces, ' +
                        'it is the working directory(chdir to it)')
    parser.add_argument('--segs', help='segments file', required=True)
    parser.add_argument('--match-file', default='gpx_video_match.csv',
                        help='match between gpx, video and snapped file, it will be saved in the input-directory')
    parser.add_argument('--segs-for-clips-csv', default='segs_for_clips.csv', help='segs_for clips')
    # test/debug argument, default False if not specified
    parser.add_argument('-v', '--verbose', help='be verbose of the output', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        print '===========arguments==========='
        print args
        print '===========current working directory==========='
        print os.getcwd()

    main(args)

