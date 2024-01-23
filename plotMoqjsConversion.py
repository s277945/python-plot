
import math
import sys
import matplotlib.pyplot as plt 
import numpy as np
import argparse

class rowData :
    def __init__(self, name, latency=None, sender_ts=None, receiver_ts=None, sender_jitter=None, receiver_jitter=None, value=None, slow=None, old=None):
        self.name = name
        self.sender_ts = sender_ts
        self.receiver_ts = receiver_ts
        self.sender_jitter = sender_jitter
        self.receiver_jitter = receiver_jitter
        self.value = value
        self.slow = slow
        self.old = old
        if (sender_ts is not None and receiver_ts is not None and receiver_ts > sender_ts) : 
            self.latency = receiver_ts - sender_ts
        elif (latency is not None) : 
            self.latency = latency
        else :
            self.latency = 0
    def getName(self):
        return self.name
    def getSenderTS(self):
        return self.sender_ts
    def setSenderTS(self, sender_ts):
        self.sender_ts = sender_ts
        if (sender_ts is not None and self.receiver_ts is not None and self.receiver_ts > sender_ts) : 
            self.latency = self.receiver_ts - sender_ts
    def setSenderJitter(self, sender_jitter):
        self.sender_jitter = sender_jitter
    def getReceiverTS(self):
        return self.receiver_ts
    def setReceiverTS(self, receiver_ts):
        self.receiver_ts = receiver_ts
        if (self.sender_ts is not None and receiver_ts is not None and receiver_ts > self.sender_ts) : 
            self.latency = receiver_ts - self.sender_ts
    def setReceiverJitter(self, receiver_jitter):
        self.receiver_jitter = receiver_jitter
    def getLatency(self):
        return self.latency
    def getValue(self):
        return self.value
    def setOld(self, old):
        self.old = old
    def setSlow(self, slow):
        self.slow = slow
    def getOld(self):
        return self.old
    def getSlow(self):
        return self.slow

def getIndex(li,target): 
    for index, x in enumerate(li): 
        if x.name == target: 
            return index 
    return -1

data = {}
tracks = {}
cpuTrack = {}
names = {}
argParser = argparse.ArgumentParser(prog='plotMoqjsTimestamp.py',
                    description='Program that allows to plot moq-js logger data',
                    epilog='By Alessandro Bottisio')
argParser.add_argument('-f', '--file', required=False)
argParser.add_argument('-sks', '--skipstart', required=False)
argParser.add_argument('-ske', '--skipend', required=False)
argParser.add_argument('-ml', '--maxlatency', required=False)
argParser.add_argument('-cpu', '--cpulog', required=False)
argParser.add_argument('-lsl', '--logslow', required=False)
argParser.add_argument('-st', '--separatetracks', required=False)
argParser.add_argument('-a', '--audio', required=False)
argParser.add_argument('-v', '--video', required=False)
args = argParser.parse_args()

if args.file is not None and args.file != "" :
    filename = args.file
else :
    filename = "log.txt"
    print("Opening moq-js log file", filename)
f = open(filename,'r') 
fNameNoExtension = filename[:len(filename)-4]

audio = False
if args.audio == 'true': audio = True

video = False
if args.video == 'true': video = True

if (not audio) and (not video) : 
    print("No tracks selected")
    exit()
    
skip = 0
if args.skipstart is not None :    
    skip = int(args.skipstart)
    if skip < 0 or math.isnan(skip) :
        skip = 0
        
skipend = sys.maxsize
if args.skipend is not None :    
    skipend = int(args.skipend)
    if skipend < 0 or math.isnan(skipend) :
        skipend = sys.maxsize 
        
maxlatency = 0
if args.maxlatency is not None : 
    if type(args.maxlatency) != int :   
        if str(args.maxlatency) == 'auto' :
            maxlatency = -1
        else :
            maxlatency = int(args.maxlatency)
            if maxlatency < 0 or math.isnan(maxlatency) : 
                maxlatency = 0
    else :
        maxlatency = int(args.maxlatency)
        if maxlatency < 0 or maxlatency : 
            maxlatency = 0
            
cpulog = False
if args.cpulog == 'true' : cpulog = True
    
logSlow = False
if args.logslow == 'true': logSlow = True

separateTracks = False
if args.separatetracks == 'true': 
    separatetracks = True
    audioFileName = fNameNoExtension + "_audio_converted.txt"
    videoFileName = fNameNoExtension + "_video_converted.txt"
    print ("Output files path:\nAudio:", audioFileName, "\nVideo:", videoFileName)
else : 
    filenameConverted = fNameNoExtension + "_converted.txt"
    print ("Output file path: ", filenameConverted)
   
audio_row = -1
video_row = -1
skipping = True 
cpuLogCount = 0
startTS = 0
for row in f: 
    row = row.strip('\n').split(';') 
    # print(row)
    if(row[0].isnumeric()) :      
        name = row[0] + "-" + row[2] 
        # if row has track id and latency value
        if(4 < len(row) and row[4].isnumeric() and int(row[2]) > 0) :     
            if int(row[2]) > skip and int(row[2]) <= skipend :
                skipping = False   
            else : skipping = True
            if (not skipping) and ((audio_row == row[0] and int(row[2]) > skip and audio == True) or (video_row == row[0] and int(row[2]) > skip) and video == True) :           
                # add track to track array if not present and the received packet data to the individual track data array
                # add row data (received packet data) to general data array
                if row[0] not in tracks :
                    tracks[row[0]] = {}
                if(row[3] == 'sent') :
                    if startTS == 0 : 
                        startTS  = int(row[4])
                    if name in data :
                        if separateTracks : data[name].setSenderTS(int(row[4]))
                        else : tracks[row[0]][row[2]].setSenderTS(int(row[4]))
                    else :
                        if separateTracks : data[name] = rowData(row[0] + "-" + row[2], sender_ts=int(row[4]))
                        else : tracks[row[0]][row[2]] = rowData(row[2], sender_ts=int(row[4]))
                    if(5 < len(row) and row[5].isnumeric()) :
                        if separateTracks : data[name].setSenderJitter(int(row[5]))
                        else : tracks[row[0]][row[2]].setSenderJitter(int(row[5]))
                elif(row[3] == 'received') :
                    if(name in data) :
                        if separateTracks : data[name].setReceiverTS(int(row[4]))
                        else : tracks[row[0]][row[2]].setReceiverTS(int(row[4]))
                    else :
                        if separateTracks : data[name] = rowData(row[0] + "-" + row[2], receiver_ts=int(row[4]))
                        else : tracks[row[0]][row[2]] = rowData(row[2], receiver_ts=int(row[4]))                
                    if(5 < len(row) and row[5].isnumeric()) :
                        if separateTracks : data[name].seReceiverJitter(int(row[5]))
                        else : tracks[row[0]][row[2]].setReceiverJitter(int(row[5]))
        elif(row[3] == 'too slow' and not skipping and logSlow) :
            # change item color if too slow packet
            if name in data : 
                if separateTracks : data[name].setSlow(True) 
                else : tracks[row[0]][row[2]].setSlow(True) 
        elif(row[3] == 'too old'  and not skipping) :
            # change item color if too old packet
            if name in data : 
                if separateTracks : data[name].setOld(True) 
                else : tracks[row[0]][row[2]].setOld(True) 
        elif(row[3] == 'AUDIO' and audio) :
            names[row[0]] = 'Audio'
            audio_row = row[0]
        elif(row[3] == 'VIDEO' and video) :
            names[row[0]] = 'Video'
            video_row = row[0]
    elif (not skipping) and cpulog and row[3] == 'CPU' :
        color = (0, 0, 0, 1)
        if float(row[4]) > 50 :
            color=(0.6, 0.2, 0.2, 1)
        else :
            color=(0.1, 0.1, 0.8, 1)
        cpuTrack[cpuLogCount] = rowData(cpuLogCount, value=float(row[4]), sender_ts=int(row[2]), color=color)
        cpuLogCount += 1

if len(tracks) == 0 and len(cpuLogCount) == 0 :    
    print("No tracks found, program will exit") 
    exit()

# filter cpu logs with timestamp greater than last valid packet log sender_ts
i = -1
lastTS = None
while lastTS is None and cpuLogCount + i > 0 :    
    lastTS = data[list(data)[i]].sender_ts
    i = i - 1
if lastTS is not None : cpuTrack = {k:v for k,v in cpuTrack.items() if (lastTS + 99 > v.sender_ts and v.sender_ts is not None)}
print("Tracks found: " + str(len(tracks)))

# check which tracks are empty
if not audio_row in tracks.keys : audio = False
if not video_row in tracks.keys : video = False

if separateTracks : 
    if audio :
        faudio = open(audioFileName, "w")
        faudio.write("Track ID;Object ID;Group ID;Status;Latency;")
        faudio.write(audio_row + ";-;-;AUDIO;-;")
    if video :
        fvideo = open(videoFileName, "w")
        fvideo.write("Track ID;Object ID;Group ID;Status;Latency;")
        fvideo.write(video_row + ";-;-;VIDEO;-;")
else :
    fout = open(filenameConverted, "w")
    fout.write("Track ID;Object ID;Group ID;Status;Latency;")
    if audio : fout.write(audio_row + ";-;-;AUDIO;-;")
    if video : fout.write(video_row + ";-;-;VIDEO;-;")

totalLatency = 0
totalJitter = 0
totalCPU = 0
for index, key in enumerate(tracks) :    
    for elem in tracks[key].values() :             
        if elem.sender_ts == None : 
            print("Empty sender timestamp value for entry", elem.name, "of track", key)    
        else :   
            if separateTracks : 
                if key == audio_row :
                    faudio.write()
                elif key == video_row : 
                    fvideo.write()
            else : fout.write()
            if sharex : axs[0].bar((elem.sender_ts - startTS)/1000, elem.latency, color = elem.color)
            else : axs[0].bar(str((elem.sender_ts - startTS)/1000), elem.latency, color = elem.color)
            totalLatency += elem.latency
            if elem.sender_jitter == None :
                elem.setSenderJitter(0)
            if sharex : axs[1].bar((elem.sender_ts - startTS)/1000, elem.sender_jitter, color = elem.color)
            else : axs[1].bar(str((elem.sender_ts - startTS)/1000), elem.sender_jitter, color = elem.color)
            if elem.sender_jitter > 100 and maxlatency < 0 :
                totalJitter += 100
            else : 
                totalJitter += elem.sender_jitter

for elem in cpuTrack.values() :
    if cpulog : 
        if sharex : axs[-1].bar((elem.sender_ts - startTS)/1000, elem.value, color = elem.color)
        else : axs[-1].bar(str((elem.sender_ts - startTS)/1000), elem.value, color = elem.color)
        totalCPU += elem.value

# print("Average latency", totalLatency/totalNum)         
# if audio : print("Average latency", totalLatency) 
# if video : print("Average latency", totalLatency)
    