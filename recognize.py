from dejavu.recognize import FileRecognizer
import os
import subprocess
import timeFunc
from constants import *
import ffmpeg
from dejavu import Dejavu

djv = Dejavu(CONFIG)

def get_vid_length(filename):

    result = subprocess.Popen(["ffprobe", filename],
    stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    l = [x for x in result.stdout.readlines() if "Duration" in x]
    
    #Some clipping to obtain the time string, this is specific to the version of ffmpeg/ffprobe
    l = l[0].split(",")
    time = l[0]
    time = time.split(" ")[-1]
    time = time.split('.')[0] #Remove milliseconds
    return time

def get_line(filename, index):
    
    f = open(filename)
    i = 0
    for line in f:
        if i == index:
            return line
        i += 1
    return -1

def clean():
    
    #removes the temp files that were created
    os.remove(TEMP_AUDIO)
    os.remove(TEMP_VIDEO)
        
def recognize_audio(start):
    
    print timeFunc.get_time_string(start), "COMPLETE"
    song = djv.recognize(FileRecognizer, TEMP_AUDIO)
    clean()
    if song[DJV_CONFIDENCE] >= CONFIDENCE_THRESH:
        #obtain the start of the commercial
        start -= song[DJV_OFFSET]
        start = int(start)
        
        #Read the database to obtain the end time of the commercial
        index = int(song[DJV_SONG_NAME]) #This is the line containing the db details
        line = get_line(DBNAME, index)
        line = line.split(",")
        print line
        name = line[0]
        duration = line[1]
        duration = timeFunc.get_seconds(duration)
        print duration
        verified = line[-1]
        print type(start)
        print type(duration)
        end = start + duration
            
        f = open(OUTPUT, "a")
        s = timeFunc.get_time_string(start) + " - " + timeFunc.get_time_string(end) + " = " + name 
        if verified == DB_GUESS: #Has not been verified in the database
            s += " (probably)"
        s += "\n"
        f.write(s)
        f.close()
        return (duration + 1)
    else:
        return VIDEO_GAP
        
def analyze(video_name):
    
    #Generates temp.mpg which is the temp video file and temp.wav, its corresponding audio file
    
    duration = get_vid_length(video_name)
    duration = timeFunc.get_seconds(duration)
    base = 0
    while base < duration:
        ffmpeg.create_video(timeFunc.get_time_string(base), timeFunc.get_time_string(VIDEO_SPAN), video_name, TEMP_VIDEO)
        ffmpeg.create_audio(TEMP_VIDEO, TEMP_AUDIO)
        base += recognize_audio(base)
    
def test():
    
    analyze("small.mpg") 

test()
