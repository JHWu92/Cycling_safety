# coding=utf-8
import subprocess
import os
import glob
import math
import pandas as pd
import xmltodict
import datetime
import json
from trace2seg import snap2road

def costs(start_time):
    dnow = datetime.datetime.now()
    delta = dnow - start_time
    del_secs = int(delta.total_seconds())
    return 'now = %s, costs = %d days %02d:%02d:%02d' % (dnow.strftime('%Y-%m-%d %H:%M:%S'),
           del_secs / 3600 / 24, del_secs / 3600 % 24, del_secs / 60 % 60, del_secs % 60)


def parse_gpx(gpx_file):
    """ given gpx file, parse corresponding video name, lon lat coordinates, timestamps and duration of video
    return video_name, lon_lats, timestamps, duration
    """
    with open(gpx_file) as f:
        doc = xmltodict.parse(f.read())['gpx']['trk']
        video_raw_path = doc['link']['@href'][1:].replace('\\','/')

        lon_lats = []
        timestamps = []
        for seg in doc['trkseg']['trkpt']:
            lat = float(seg['@lat'])
            lon = float(seg['@lon'])
            loc = (lon,lat)
            ts = seg['time']
            lon_lats.append(loc)
            timestamps.append(ts)

        # duration of video in seconds
        try:
            duration = int(doc['extensions']['gpxtrkx:TrackStatsExtension']['gpxtrkx:TotalElapsedTime'])
        except:
            duration = None

    return video_name, lon_lats, timestamps, duration


def second2vtime(sec):
    """given sec, return the timestamp in video. E.g. sec=0, vtime= 00:00:00; sec=61, vtime = 00:01:01
    """
    hours = int(math.floor(sec/3600))
    minutes = int(math.floor((sec - (hours*3600))/60))
    seconds = int(math.floor(sec - (hours*3600) - (minutes*60)))
    vtime = "%02d:%02d:%02d" % (hours,minutes,seconds)
    return vtime


def align_loc_ts_duration(lon_lats, timestamps, duration):
    """
    assumming each video records gpx second by second, and gpx is right aligned to the vtime.
    In other words, the first few seconds have no gpx coordinates
    :return: zip(seconds, lon_lats, timestamps)
    """
    seconds = range(duration+1)
    diff = len(seconds) - len(lon_lats)
    for _ in range(diff):
        lon_lats.insert(0, None)
        timestamps.insert(0, None)
    return zip(seconds, lon_lats, timestamps)


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


def get_chunk_size(args, size):
    if args.l:
        return args.l
    return math.ceil(float(size)/args.b)


def split_cmd_part(sub_vname, svtime, evtime):
    return "-vcodec copy -acodec copy -ss {} -to {} {}".format(svtime, evtime, sub_vname)


def split(video_name, lon_lats, timestamps, duration, sub_vname_template, json_file):

    # assuming gpx is recorded second by second, and coordinates for the first few seconds are not recorded
    aligned = align_loc_ts_duration(lon_lats, timestamps, duration)

    # get chunk size based on args
    chunk_size = get_chunk_size(args, len(aligned))
    if args.verbose: print 'video is cut by %d seconds' % chunk_size

    # get one cmd for split a video into server parts
    # one cmd is usually faster than several cmd
    split_cmd = ['ffmpeg -i %s -v quiet -y' % video_name]

    # store snapped gpx traces in json file
    json_data = []

    for i, chunk in enumerate(chunks(aligned, chunk_size, right_close=True)):
        # get information about a part of video
        # print chunk
        sub_vname = sub_vname_template.format(i)
        svtime, evtime = second2vtime(chunk[0][0]),second2vtime(chunk[-1][0])
        pts_lon_lat = [slt[1] for slt in chunk if slt[1]]
        tms = [slt[2] for slt in chunk if slt[2]]

        # add cmd specifying one part of video
        split_cmd.append(split_cmd_part(sub_vname, svtime, evtime))

        # snap to road
        snap_pts, confidences = snap2road(pts_lon_lat, tms, return_confidence=True)
        json_data.append({'video_name': video_name, 'lonlat': snap_pts, 'confidences': confidences})

        if args.verbose:
            print 'sub video name = %s, starting at %s and ending at %s, with %d locations and %d timestamps ' %(
                sub_vname, svtime, evtime, len(pts_lon_lat), len(tms))

    # use command line tool ffmpeg to split video via subprocess
    split_cmd = ' '.join(split_cmd)
    output = subprocess.Popen(split_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    # print split_cmd
    if args.verbose:
        print 'spliting video: %s with ffmpeg' % video_name
        print 'split cmd ouput:', output

    # store snap to road coordinates and confidences
    with open(json_file, 'wb') as f:
        json.dump(json_data, f, indent=4)


def main(args):
    if args.verbose:
        print 'split videos with argments =', args

    # default split length
    if not args.l and not args.b:
        args.l=10

    # change to the directory with videos
    if args.p:
        os.chdir(args.p)

    start_time = datetime.datetime.now()

    # parse gpx_files
    gpx_files = glob.glob("*.gpx")
    gpx_video_match = []
    for gpx_f in gpx_files:
        video_name, lon_lats, timestamps, duration = parse_gpx(gpx_f)

        # record the (gpx, video) pair when the video for a gpx can't be found
        if not os.path.isfile(video_name):
            gpx_video_match.append((gpx_f, video_name, False))
            if args.verbose:
                print "can't find video=%s for gpx=%s" % (video_name, gpx_f)
            continue

        # the corresponding video is found
        gpx_video_match.append((gpx_f, video_name, True))
        # split video and gpx trace; store snap2road(trace) as json file
        sub_vname_template = video_name[:video_name.rfind(".")] + "_{0:03d}.MP4"
        json_file = video_name + '.json'
        split(video_name, lon_lats, timestamps, duration, sub_vname_template, json_file)

        print 'handled video: %s, gpx: %s' % (video_name, gpx_f), costs(start_time)

    # save the gpx files and corresponding video name
    pd.DataFrame(gpx_video_match, columns=['gpx', 'video', 'found']).to_csv('gpx_video_match.csv')





if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Split video and corresponding gpx trace')
    parser.add_argument('-l', help='split video by length (seconds)', type=int)
    parser.add_argument('-b', help='split video into N equal length parts', type=int)
    parser.add_argument('-p', help='the directory of videos and gps traces', type=str)
    parser.add_argument('-v', '--verbose', help='the directory of videos and gps traces', action='store_true')
    args = parser.parse_args()
    main(args)
