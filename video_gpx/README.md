# GPX-Video-Splitter
###Please note: This script can only be used on a UNIX system. Also make sure 'ffmpeg' is installed on your machine. Also the following python modules are used: "math, sys, subprocess, os, xmltodict."  They can be installed using pip, however most if not all should be included in the python installation (ie: "pip install math") 
##Instructions
* Download or this python  into the directory containing the gpx data and video. Make sure gpx data and video are in the same directory.
* In terminal/shell using the cd command, change to the directory containing the gpx and video data.
* Run the following command: "python split.py -l 10"
  * This makes will split all of the videos into ten second portions. 
  * If you would like to change the split length change the second parameter. 
  * If you would like to specify the number of videos you would like to divide into, use the "-b" option instead. 
    * For example, "pyton split.py -b 4" will split the videos into four additional videos.
* The original video remains in the folder. 
