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
