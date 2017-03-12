# ORGANIZE VIDEO AND GPX:
## File system of the camera:
- root/
  - DCIM/
    - 100_VIRB/ 
      - VIRB????.MP4  # starts from VIRB0001.MP4
    - 101_VIRB/  # keep increasing, no repetition even if previous folder is deleted
      - VIRB????.MP4  # starts from VIRB0001.MP4 too
    - ???_VIRB/  # not sure whether there is repetition if SD card is changed
  - Garmin/GPX/Track_yyyy-mm-dd HHMMSS.gpx  # [track_name].gpx
    
## File system in server:
- root/directory/in/server  # $r
  - raw_video/10?_VIRB  # copy the whole DCIM/* in camera
  - DCIM/10?_VIRB  # 480p videos after face blurring by Youtube and manual plate blurring
  - GPX/  # all gpx data, no sub directory
    - Track_yyyy-mm-dd HHMMSS.gpx  # [track_name].gpx

## Video preprocessing:
1. Backup raw video(720/1080p without any preprocessing) in $r/raw_video
2. Upload raw video to YouTube, apply face blurring. It takes about 1 day for a 20 minute 1080p video. Blurring is parallel.
3. After blurring, transfer HD to 480p, manual blur car plates.
4. Upload/sync 480p processed videos to hornbake server in $r/DCIM


# SPLIT VIDEO AND GPX
- script: split_vidoe_gpx.py
  - arguments: 
    - $r=root/directory/in/server
    - $split: directory to store video_clips and snapped traces (default: ./split)
    - For information of different options: $ python split_video_gpx --help
  - Common usage: $ python split_video_gpx.py -r $r -l 30
- require package: 
  - command line package: ffmpeg
  - python package: subprocess, xmltodict
- Input: 
  - videos and gpx in $r
- Process:
  - split video ($r/DCIM/*/*.MP4) and gpx ($r/GPX/*.gpx)
- Output:
  - $r/gpx_video_match.csv  # mapping between GPX/[track_name].gpx and [video_name].MP4, and information of gpx quality
  - $r/$split/DCIM/???_VIRB/
    - [video_name]_[cnt].MP4  # clips of original [video_name].MP4
    - [video_name].json  # snapped result of gpx, list of dict with the following keys:
      - clip_name: [video_name]_[cnt].MP4;
      - duration_clip: duration (in seconds) of this clip;
      - raw: list of dict {"batch": No.X batch of the clip traces; "raw_len": number of points; "raw": list of (lon lat) points}
      - snapped: list of dict {"batch": No.X batch of the clip traces; "sub_batch": one snap request can return multiple snapped traces; "snapped_len": number of snapped points; "confidence": confidence of this snapped traces; "snapped": list of (lon lat) points}
      - v_max: maximum velocity computed by raw_traces of this clip;
      - v_avg: average velocity of this clip;
      - v_median: median velocity of this clip;


# TRACE2SEGS: GET SEGMENT RATIO FOR SANPPED TRACES
- script: trace2segs.py
  - arguments:
    - $segs: the path to the segment file (require)
    - $r: the root directory the same as split_video_gpx.py
  - For information of different options: $ python trace2segs --help
  - Common usage: $ python trace2segs.py -r $r --segs $segs
- Input: 
  - $r/$split/DCIM/???_VIRB/[video_name].json
- Process:
  - Common usage: $python trace2segs.py  #TODO: finish arguments
- Output:
  - $r/segs_for_clips.csv 
  - $r/clips_quality.csv  # some clips have no segment, e.g. crossing road(103_VIRB/VIRB0007_001.MP4); some clips have no snapped point at all


# UPLOAD VIDEOS CLIPS
> TODO: a bash script to call upload_video.py to iterate all video files and store result in a csv file
- script: upload_video.py  # $py
- Input:
  - CLIENT_SECRETS_FILE
  - $r/$split/DCIM/???_VIRB/[video_name]_[cnt].MP4
- Process:
  - ??
- Output:
  - $r/upload_result.csv  # video_clip_path, parent_dir, video_name, video_clip_cnt, url


# COMBINE SPLIT, TRACE2SEGS, UPLOAD RESULT
> TODO: combine them and output csv files w.r.t. website DB structure




# ########################
# Deprecate
# ########################
# GPX-Video-Splitter
###Please note: This script can only be used on a UNIX system. Also make sure 'ffmpeg' is installed on your machine. Also the following python modules are used: "math, sys, subprocess, os, xmltodict."  They can be installed using pip, however most if not all should be included in the python installation (ie: "pip install math") 
##Instructions
* Make sure gpx data and video are in the same directory.
* This script takes three command arguments 
  * The first is optional, and is the location of the directory of containing the gpx and video. If this option is not supplied, the script will assume its in the same directory as the video and gpx 
  * The second is '-l' or '-b'. '-l' indicates you would like to split the video by length, '-b' indicates you would like a certain number of splits to occur in the video. 
  * The third is the argument for the second option. ie '-l 5' indicates you would like videos of 5 second length, '-b 12' indicates you would like the video split into 12 pieces 
* Sample command - 'python split.py /path -b 3' - this command will split the video into 3 seperate videos 
* **Please note, all gpx and video must be in the directory in pairs. The program will assume that the video name in the gpx file is also in the directory containing the gpx file.** 
