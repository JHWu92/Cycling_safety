# coding=utf-8
import argparse
import logging
import os
import time
import datetime
import pandas as pd

from upload_video import Upload, log_msg, set_Logger


def parse_clip_name(clip_name):
    direct_folder = os.path.basename(os.path.dirname(clip_name))
    clip_fn = os.path.basename(clip_name).replace('.MP4','')
    return direct_folder, clip_fn


def get_uploaded_clips(log_file):
    if not os.path.exists(log_file):
        return set()

    with open(log_file) as f:
        lines = [eval(line.strip().split('\t')[1]) for line in f]
    if lines:
        df = pd.DataFrame.from_dict(lines)
        return set(df[~df.videoId.isnull()].clip_name)
    return set()

def main(args):
    # change to working root directory
    if args.root_dir:
        os.chdir(args.root_dir)
    if args.start_over:
        os.remove(args.upload_logger)
    logger = set_Logger(args)

    # resume upload
    uploaded_clips = get_uploaded_clips(args.upload_logger)

    clips = pd.read_csv(args.clips_quality_csv)
    bad_quality_clips = clips.clip_no_seg | clips.no_snapped_pts
    uploaded = clips.clip_name.isin(uploaded_clips)
    clips_to_upload = clips[~bad_quality_clips & ~uploaded]
    print 'we have {} clips, {} of them are uploaded, {} are bad quality, {} to go'.format(
        len(clips), len(uploaded_clips), len(bad_quality_clips[bad_quality_clips==True]), len(clips_to_upload))

    for cnt, clip_name in enumerate(clips_to_upload.clip_name.values):
        if cnt>10 and args.test:
            break
        while True:
            direct_folder, clip_fn = parse_clip_name(clip_name)
            title = '{}-{}'.format(direct_folder, clip_fn)

            cmd = '--file "{clip_name}" --title {title} --upload-logger {upload_logger}'.format(
                clip_name=clip_name, title=title, upload_logger=args.upload_logger)

            upload = Upload(cmd)
            upload_result = upload.upload()
            log_msg(logger, upload.get_args(), upload_result)
            print cnt, 'file: %s, uploaded status: %s' % (clip_name, upload_result['uploaded'])
            if exceed_limit(upload_result):
                print 'uploadLimitExceeded'
                print upload_result
                print 'pause uploading for 3600 seconds', datetime.datetime.now()
                time.sleep(3600)
                print 'resume'
            else:
                time.sleep(20)
                break


def exceed_limit(upload_result):
    if 'error.content' in upload_result and 'uploadLimitExceeded' in upload_result['error.content']:
        return True
    return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='upload videos clips in the input directory')
    parser.add_argument('-r', '--root-dir', type=str, help='root directory containing videos and gps traces, ' +
                                                           'it is the working directory(chdir to it)')
    parser.add_argument('--clips-quality-csv', default='clips_quality.csv', help='clips quality')
    parser.add_argument('--upload-logger', default='upload_video.log', help='record uploaded result, clip-url pair')

    # test/debug argument, default False if not specified
    parser.add_argument('-v', '--verbose', help='be verbose of the output', action='store_true')
    parser.add_argument('--start-over', help='if specified, delete existing upload log results', action='store_true')
    parser.add_argument('--test', help='if specified, upload top 20 videos', action='store_true')
    
    # directory = r"Sample Data/test_upload_videos_in_dir/"
    args = parser.parse_args()

    print args
    main(args)
