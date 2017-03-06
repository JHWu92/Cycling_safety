# coding=utf-8
import subprocess
import os
import glob
import math
import pandas as pd
import xmltodict
import datetime
import json
from snap2road import snap2road
from utils import *
from geom_helper import distance_diff


# =============================================
# GPX trace Quality Control
# =============================================
def duration_of_video(vpath):
    """ use ffmpeg's ffprobe command to find video's duration in seconds, return a float number
    :param vpath: The absolute (full) path of the video file, string.
    """

    command = ["ffprobe", "-loglevel", "quiet", "-print_format", "json", "-show_format", "-show_streams", vpath]
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = pipe.communicate()
    _json = json.loads(out)

    # parse duration
    if 'format' in _json:
        if 'duration' in _json['format']:
            return float(_json['format']['duration'])

    if 'streams' in _json:
        # commonly stream 0 is the video
        for s in _json['streams']:
            if 'duration' in s:
                return float(s['duration'])

    # if everything didn't happen,
    # we got here because no single 'return' in the above happen.
    raise Exception('I found no duration')


def get_time_diff_from_start(timestamps, form='%Y-%m-%dT%H:%M:%SZ'):
    """
    :return: the time differences for each timestamp from the start timestamp
    """
    first = timestamps[0]
    return [diff_in_sec(t, first, form) for t in timestamps]


def get_time_consecutive_diff(timestamps, form='%Y-%m-%dT%H:%M:%SZ'):
    """
    :return: the time differences between t(i+1) and t(i)
    """
    return [diff_in_sec(timestamps[i + 1], timestamps[i], form) for i in range(len(timestamps) - 1)]


def bad_quality_diff_not_int(timestamps, form='%Y-%m-%dT%H:%M:%SZ'):
    """
    :return: quality determined by difference among timestamps has non int second
    """
    diff_consecutive = get_time_consecutive_diff(timestamps, form)
    diff_not_int = [d for d in diff_consecutive if not d.is_integer()]
    return len(diff_not_int) != 0


def bad_quality_max_diff(timestamps, form='%Y-%m-%dT%H:%M:%SZ', thres=10):
    """
    :param thres: the threshold defining bad quality of GPX trace in terms of consecutive time difference
    :return: whether the quality of the GPX is bad.
    """
    diff_consecutive = get_time_consecutive_diff(timestamps, form)
    max_diff = max(diff_consecutive)
    return max_diff > thres


def fill_gpx_gap(locs, timestamps):
    """
    fill in the timestamp gap of the gpx trace; use this on raw gpx and before alignment
    """
    diff_consecutive = get_time_consecutive_diff(timestamps)
    new_ts = []
    new_locs = []
    for i, d in enumerate(diff_consecutive):
        for increasement in range(int(d)):
            # append the current location for d times;
            new_locs.append(locs[i])
            # append the current timestamp for d times with increasement = 1 second each time
            new_ts.append(add_secs(timestamps[i], increasement))

    # append the last location and timestamp
    new_locs.append(locs[-1])
    new_ts.append(timestamps[-1])
    return new_locs, new_ts


def align_loc_ts_duration(lon_lats, timestamps, duration):
    """
    Assuming gpx is right aligned to the vtime. In other words, the first few seconds have no gpx coordinates
    after aligned, the first few seconds share the same location with the first recorded coordinate.
    aligned timestamps are back counted second by second
    :return: lon_lats, timestamps
    """
    seconds = range(duration + 1)
    diff = len(seconds) - len(lon_lats)
    for _ in range(diff):
        lon_lats.insert(0, lon_lats[0])
        timestamps.insert(0, add_secs(timestamps[0],-1))
    return lon_lats, timestamps


# =============================================
# parsing the gpx file
# =============================================
def parse_gpx(gpx_file):
    """ given gpx file, parse corresponding video name, lon lat coordinates, timestamps and duration of video
    :return: video_name, lon_lats, timestamps, duration
    """
    with open(gpx_file) as f:
        doc = xmltodict.parse(f.read())['gpx']['trk']
        video_name = doc['link']['@href'][1:].replace('\\', '/')

        lon_lats = []
        timestamps = []
        for seg in doc['trkseg']['trkpt']:
            lat = float(seg['@lat'])
            lon = float(seg['@lon'])
            loc = (lon, lat)
            ts = seg['time']
            lon_lats.append(loc)
            timestamps.append(ts)

        # duration of video in seconds
        try:
            duration = int(doc['extensions']['gpxtrkx:TrackStatsExtension']['gpxtrkx:TotalElapsedTime'])
        except:
            duration = None

    return video_name, lon_lats, timestamps


# =============================================
# for splitting the videos
# =============================================
def second2vtime(sec):
    """given sec, return the timestamp in video. E.g. sec=0, vtime= 00:00:00; sec=61, vtime = 00:01:01
    """
    hours = int(math.floor(sec / 3600))
    minutes = int(math.floor((sec - (hours * 3600)) / 60))
    seconds = int(math.floor(sec - (hours * 3600) - (minutes * 60)))
    vtime = "%02d:%02d:%02d" % (hours, minutes, seconds)
    return vtime


def split_cmd_part(sub_vname, svtime, evtime):
    return "-vcodec copy -acodec copy -ss {} -to {} {}".format(svtime, evtime, sub_vname)


def smooth_nonstop(stops, window=3, percentage=0.8):
    stops_size = len(stops)
    for i in range(stops_size):
        # do nothing about stops
        if stops[i]:
            continue

        left, right = max(0, i - window), min(stops_size, i + window + 1)

        context = stops[left: i] + stops[i + 1: right]
        stop_percentage = float(sum(context))/len(context)
        if stop_percentage>=percentage:
            stops[i] = True


def split_points_indices_by_stop(locs, stop_thres=0.05, short_stop=10, smooth=True):
    diff = distance_diff(locs)
    stops = [d < stop_thres for d in diff]
    if smooth:
        smooth_nonstop(stops)
    groups = group_consecutive(stops, stepsize=0)

    # merge short stop
    split_points_indices = []
    i, j = 0, 0
    for g in groups:
        # long stop
        if sum(g) and len(g) > short_stop:
            # save nonstop left and right pointers
            if i != j:
                split_points_indices.append((i, j))
            # move left pointer to current right pointer
            j += len(g)
            i = j
        # nonstop or short stop
        else:
            j += len(g)  # move right pointer

    # the last group is nonstop
    if i != j:
        split_points_indices.append((i, j))

    return split_points_indices


def get_chunk_size(args, size):
    """
    :return: get chunk size based on cmd arguments
    """
    if args.l:
        return args.l
    return math.ceil(float(size) / args.b)


# =============================================
# split one gpx and corresponding video
# =============================================
def split_one_gpx_video(args, video_name, lon_lats, timestamps, sub_vname_template, json_file):
    # preprocess locations and timestamps
    # fill in timestamps gap
    fill_gpx, fill_timestamps = fill_gpx_gap(lon_lats, timestamps)
    # alignment based on video duration
    vdur_round = int(round(duration_of_video(video_name)))
    aligned_gpx, aligned_timestamps = align_loc_ts_duration(fill_gpx, fill_timestamps,vdur_round)
    aligned = zip(range(len(aligned_gpx)), aligned_gpx, aligned_timestamps)

    # find separate points by long stop
    split_points = split_points_indices_by_stop(aligned_gpx, stop_thres=args.stop_thres,
                                                short_stop=args.short_stop, smooth=args.smooth)

    # get chunk size based on args
    chunk_size = get_chunk_size(args, len(aligned))
    if args.verbose: print 'video is cut by %d seconds' % chunk_size
    # get chunks based on long stop and largest chunk second size
    chunks = []
    for i, j in split_points:
        chunks.extend(list(even_chunks(aligned[i:j+1], chunk_size, right_close=True)))

    # get one cmd for split a video into server parts
    # one cmd is usually faster than several cmd
    cmd_head = 'ffmpeg -i %s -v quiet -y' % video_name
    split_cmd = [cmd_head]

    # store snapped gpx traces in json file
    json_data = []

    for i, chunk in enumerate(chunks):
        # get information about a part of video
        # print chunk
        sub_vname = sub_vname_template.format(i)
        svtime, evtime = second2vtime(chunk[0][0]), second2vtime(chunk[-1][0])
        pts_lon_lat = [slt[1] for slt in chunk if slt[1]]
        tms = [slt[2] for slt in chunk if slt[2]]

        # add cmd specifying one part of video
        split_cmd.append(split_cmd_part(sub_vname, svtime, evtime))

        # snap to road
        snapped_res = snap2road(pts_lon_lat, tms)
        snapped_res['video_name'] = sub_vname
        json_data.append(snapped_res)

        if args.verbose:
            print 'sub video name = %s, starting at %s and ending at %s, with %d locations and %d timestamps ' % (
                sub_vname, svtime, evtime, len(pts_lon_lat), len(tms))

    # use command line tool ffmpeg to split video via subprocess
    split_cmd = ' '.join(split_cmd)

    # execute the command line and split the video
    if not args.no_video:
        output = subprocess.Popen(split_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()

    # store snap to road coordinates and confidences
    save_json_to_file(json_data, json_file, indent=args.json_indent)

    if args.verbose:
        print 'spliting video: %s with ffmpeg' % video_name


# =============================================
# lopping through all gpx and corresponding video
# =============================================
def main(args):

    # change to the directory with videos
    if args.input_directory:
        os.chdir(args.input_directory)

    if args.verbose:
        print '===========split videos with arguments==========='
        print args
        print '===========current working directory==========='
        print os.getcwd()
        print '===========output directory==========='
        print os.path.join(os.getcwd(), args.output_directory)

    start_time = datetime.datetime.now()

    # parse gpx_files
    gpx_files = glob.glob("GPX/*.gpx") if not args.test else ['GPX/Track_2017-02-21 113002.gpx']

    gpx_video_match = []
    for gpx_f in gpx_files:
        # extract information
        video_name, lon_lats, timestamps = parse_gpx(gpx_f)
        # quality control
        has_video = os.path.isfile(video_name)
        is_bad_max = bad_quality_max_diff(timestamps, thres=args.bad_time_diff)
        is_bad_int = bad_quality_diff_not_int(timestamps)
        gpx_video_match.append((gpx_f, video_name, has_video, is_bad_max, is_bad_int))

        # skip parsing the trace,
        # if the video for a gpx can't be found, or the quality of of gpx is bad
        if not has_video or is_bad_max or is_bad_int:
            if args.verbose:
                print 'GPX: {} will not be processed, has_video={}; time skip={}; time diff not int={}'.format(
                    gpx_f, has_video, is_bad_max, is_bad_int)
            continue

        # file names for the output
        video_name_no_ext = file_name_without_extension(video_name)
        sub_vname_template = os.path.join(args.output_directory, video_name_no_ext + "_{:03d}.MP4")
        json_file = os.path.join(args.output_directory, video_name_no_ext + '.json')
        make_sure_path_exists(os.path.dirname(sub_vname_template))
        make_sure_path_exists(os.path.dirname(json_file))

        # split video and gpx trace; store snap2road(trace) as json file
        split_one_gpx_video(args, video_name, lon_lats, timestamps, sub_vname_template, json_file)

        print 'handled video: %s, gpx: %s' % (video_name, gpx_f), costs(start_time)

    # save the gpx files and corresponding video name
    pd.DataFrame(gpx_video_match, columns=['gpx', 'vfile', 'match', 'bad_max', 'bad_int']).to_csv('gpx_video_match.csv')
    print 'saving gpx_video_match.csv'


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Split video and corresponding gpx trace')
    parser.add_argument('-i', '--input-directory', help='the input  directory of videos and gps traces', type=str)
    parser.add_argument('-o', '--output-directory', type=str, default='split',
                        help='the output directory of splited videos and snapped gps traces')

    parser.add_argument('-l', help='maximum duration for sub videos (seconds)', type=int, default=30)
    parser.add_argument('--short-stop', help='the max length of short stop', type=int, default=10)
    parser.add_argument('--bad-time-diff', type=int, default=10,
                        help='the maximum time different between two consecutive timestamps for good quality')
    parser.add_argument('--stop-thres', type=float, default=0.05,
                        help='Defining stop: the threshold of distance between two consecutive coordinates')

    # default False if not specified
    parser.add_argument('-v', '--verbose', help='be verbose of the output', action='store_true')
    parser.add_argument('--json-indent', action='store_true', help='indent output snap to road json file')
    parser.add_argument('-y', '--overwrite', action='store_true', help='over write existing video without asking')
    parser.add_argument('--no-video', help='not to split the videos', action='store_true')
    parser.add_argument('--test', action='store_true', help='run on test gpx files')

    # default True if not specified
    parser.add_argument('--smooth', help='smooth long stop detection', action='store_false')

    args = parser.parse_args()

    main(args)
