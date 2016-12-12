#!/usr/bin/env python
import math
import sys
import subprocess
import json
import os
import xmltodict
import mapbox as mp
import pandas as pd
#Class definitions
class Video:
    def __init__(self, name, duration, cords):
        self.name = name
        self.duration = duration
        self.cords = cords

class Location:
    def __init__(self, lat, long):
        self.lat = float(lat)
        self.long = float(long)
    def __str__(self):
        return "%f, %f" % (self.lat, self.long)

#Returns tuple where first elemnt is the path, second element is array of gpx names
def getGpxNames():
    #Set path to folder containing gpx
    #Assumes videos are in the same folder
    path = os.getcwd() #Assumes current directory, can maually set string to wanted directory
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    gpxNames = []; videoNames = []
    for f in files:
        if ".gpx" in f:
            gpxNames.append(f)
        if (".MP4" or ".mp4") in f:
            videoNames.append(f)


    return (path, gpxNames, videoNames)


#Retrieves the names of all of the video files as indicated by the gpx files that are present in the directory
#returns a tuple where first value is the video name and secondvalue is the duration
def getDataFromGpx():
    gpxTup = getGpxNames()
    videoList = []
    for gpx in gpxTup[1]:
        with open(gpxTup[0]+"/"+gpx) as f:
            doc = xmltodict.parse(f.read())['gpx']['trk']
            raw_path = doc['link']['@href']
            vid_name = raw_path[raw_path.rfind('\\')+1:]
            if vid_name in gpxTup[2]:
                # Duration path in the GPX file
                locations = []
                for seg in doc['trkseg']['trkpt']:
                    lat = seg['@lat']
                    long = seg['@lon']
                    loc = Location(lat, long)
                    locations.append(loc)
                length = doc['extensions']['gpxtrkx:TrackStatsExtension']['gpxtrkx:TotalElapsedTime']
                videoList.append(Video(name=vid_name,duration=length,cords=locations))
    return videoList

def convertTimes(times):
    c_times = []
    for time in times:
        hours = int(math.floor(time/3600))
        minutes = int(math.floor((time - (hours*3600))/60))
        seconds = int(math.floor(time - (hours*3600) - (minutes*60)))
        c_time = "%02d:%02d:%02d" % (hours,minutes,seconds)
        c_times.append(c_time)
    return  c_times

def splitVideo(video, times):
    splitVideos = []
    split_cmd =  "ffmpeg -i " + str(video.name)
    limit = len(times)-1
    for n in range(0, limit):
        name = video.name[:video.name.rfind(".")] + ("_%d.MP4" % n)
        split_cmd += (" -vcodec copy -acodec copy" + " -ss " + str(times[n]) + " -to " + str(times[n+1])  +
                     " " + name )

        cSplit = int(video.duration)/limit
        splitcords = []
        for i in range(cSplit*(n), cSplit*(n+1)-1):
            splitcords.append(video.cords[i])
        splitVideos.append(Video(name=name, cords=splitcords, duration=len(splitcords)))

    output = subprocess.Popen(split_cmd , shell=True, stdout=subprocess.PIPE).stdout.read()
    return splitVideos

def transformLocationData(video, split_length):
    access = "pk.eyJ1Ijoic3VyYWpuYWlyIiwiYSI6ImNpdWoyZGQzYjAwMXkyb285b2Q5NmV6amEifQ.WBQAX7ur2T3kOLyi11Nybw"
    service = mp.MapMatcher(access_token=access)
    lats = []; longs = []
    for c in video.cords:
        lats.append(c.lat)
        longs.append(c.long)
    data = pd.DataFrame(data={'latitude':lats, 'longitude':longs})
    gps = snap_to_road(service, data);
    return gps

def main(args):

    videos = getDataFromGpx()
    json_data = []
    for v in videos:
        filename = v.name
        video_length = int(v.duration) #Split by the length of chunk desired
        times = []
        # args[3] is command line argument for the number of seconds
        # args[2] is the option (will be a 10 second split default if nothing is supplied
        # args[1] is the directory of the file
        # args[0] is the file location
        if len(args) >3:
            os.chdir(args[1])
            if args[2] == '-l':
                split_length = int(args[3])
            elif args[2] == '-b':  # Split number of chunks desired
                split_length = int(video_length) / int(args[3])
            else:  ##split length is 10 by default
                split_length = 10

            for x in range(0, (video_length + 1), split_length):
                if x <= video_length:
                    times.append(x)
            if video_length not in times:
                times.append(video_length)
            c_times = convertTimes(times)
            splits = splitVideo(video=v, times=c_times)
            for split in splits:
                split.cords = transformLocationData(video=split, split_length=split_length)
                json_data.append({split.name: split.cords})
            with open('%s.json'%v.name[:v.name.rfind(".")], 'w+') as outfile:
                json.dump(json_data, outfile)
        if len(args) >=2:
            # args[2] is command line argument for the number of seconds
            # args[1] is the option (will be a 10 second split default if nothing is supplied
            # args[0[ is the file location
            print "hello" + args[1]
            if args[1] == '-l':
                split_length = int(args[2])
            elif args[1] == '-b': #Split number of chunks desired
                split_length = int(video_length)/int(args[2])
                print "Split length %d" % split_length
            else: ##split length is 10 by default
                split_length = 10

            for x in range(0, (video_length + 1), split_length):
                if x <= video_length:
                    times.append(x)
            if video_length not in times:
                times.append(video_length)
            c_times = convertTimes(times)
            splits = splitVideo(video=v, times=c_times)
            for split in splits:
                split.cords = transformLocationData(video=split, split_length=split_length)
                json_data.append({split.name:split.cords})
            with open('%s.json'%v.name[:v.name.rfind(".")], 'w+') as outfile:
                json.dump(json_data, outfile)
        else:
            print "missing or incorrect arguments"


def snap_to_road(service, df):
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    linestr = [[row['longitude'], row['latitude']] for key, row in df.iterrows()]
    points = len(linestr)
    iter_end = int(math.ceil(points / 100.0))
    new_gps = []
    for i in range(iter_end):
        start = i * 100
        end = start + 99
        size = end - start + 1
        if (size <= 2):
            start = start - 2
        geojson = {'type': 'Feature',
                   'properties': {'coordTimes': []},
                   'geometry': {'type': 'LineString',
                                'coordinates': []}}
        geojson['geometry']['coordinates'] = linestr[start:end + 1]
        response = service.match(geojson, profile='mapbox.cycling')
        var = response.geojson()
        for x in var['features']:
            new_gps.append(x['geometry']['coordinates'])
    return new_gps

if __name__ == '__main__':
    main(sys.argv)
