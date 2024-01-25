
import math
import sys
import matplotlib.pyplot as plt 
import numpy as np
import argparse

class rowData :
    def __init__(self, id, track=None, latency=None, sender_ts=None, receiver_ts=None, sender_jitter=None, receiver_jitter=None, value=None, slow=None, old=None):
        self.id = id
        self.sender_ts = sender_ts
        self.track = track
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
    def getTrack(self):
        return self.track
    def getId(self):
        return self.id
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

audio = True
if args.audio == 'false': audio = False

video = True
if args.video == 'false': video = False

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
            
cpulog = False
if args.cpulog == 'true' : cpulog = True
    
logSlow = False
if args.logslow == 'true': logSlow = True

separateTracks = False
if args.separatetracks == 'true': 
    separateTracks = True
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
                    if not separateTracks :
                        if name in data : data[name].setSenderTS(int(row[4]))
                        else : data[name] = rowData(row[2], track = row[0], sender_ts = int(row[4]))
                    else :
                        if row[2] in tracks[row[0]].keys() : tracks[row[0]][row[2]].setSenderTS(int(row[4]))
                        else : tracks[row[0]][row[2]] = rowData(row[2], sender_ts = int(row[4]))
                    if(5 < len(row) and row[5].isnumeric()) :
                        if not separateTracks : data[name].setSenderJitter(int(row[5]))
                        else : tracks[row[0]][row[2]].setSenderJitter(int(row[5]))
                elif(row[3] == 'received') :
                    if not separateTracks :
                        if name in data : data[name].setReceiverTS(int(row[4]))
                        else : data[name] = rowData(row[2], track = row[0], receiver_ts = int(row[4]))
                    else :
                        if row[2] in tracks[row[0]].keys() : tracks[row[0]][row[2]].setReceiverTS(int(row[4]))
                        else : tracks[row[0]][row[2]] = rowData(row[2], receiver_ts = int(row[4]))                
                    if(5 < len(row) and row[5].isnumeric()) :
                        if not separateTracks : data[name].seReceiverJitter(int(row[5]))
                        else : tracks[row[0]][row[2]].setReceiverJitter(int(row[5]))
        elif(row[3] == 'too slow' and not skipping and logSlow) :
            # change item color if too slow packet
            if not separateTracks and name in data : data[name].setSlow(True) 
            elif row[2] in tracks[row[0]].keys() : tracks[row[0]][row[2]].setSlow(True) 
        elif(row[3] == 'too old'  and not skipping) :
            # change item color if too old packet
            if not separateTracks and name in data : data[name].setOld(True) 
            elif row[2] in tracks[row[0]].keys() : tracks[row[0]][row[2]].setOld(True) 
        elif(row[3] == 'AUDIO' and audio) :
            names[row[0]] = 'Audio'
            audio_row = row[0]
        elif(row[3] == 'VIDEO' and video) :
            names[row[0]] = 'Video'
            video_row = row[0]
    elif (not skipping) and cpulog and row[3] == 'CPU' :
        cpuTrack[cpuLogCount] = rowData(cpuLogCount, value=row[4], sender_ts=int(row[2]))
        cpuLogCount += 1

if len(tracks) == 0 and len(cpuLogCount) == 0 :    
    print("No tracks found, program will exit") 
    exit()

# check which tracks are empty
if audio_row not in tracks.keys() : audio = False
if video_row not in tracks.keys() : video = False

if separateTracks : 
    if audio :
        faudio = open(audioFileName, "w")
        faudio.write("Track ID;Object ID;Group ID;Status;Latency;\n")
        faudio.write(audio_row + ";-;-;AUDIO;-;\n")
    if video :
        fvideo = open(videoFileName, "w")
        fvideo.write("Track ID;Object ID;Group ID;Status;Latency;\n")
        fvideo.write(video_row + ";-;-;VIDEO;-;\n")
else :
    fout = open(filenameConverted, "w")
    fout.write("Track ID;Object ID;Group ID;Status;Latency;\n")
    if audio : fout.write(audio_row + ";-;-;AUDIO;-;\n")
    if video : fout.write(video_row + ";-;-;VIDEO;-;\n")


totalLatency = 0
totalJitter = 0
totalCPU = 0
# if separate files for audio and video
if separateTracks : 
    if audio : 
        totalAudioLatency = 0
        totalAudioJitter = 0
    if video :
        totalVideoLatency = 0
        totalVideoJitter = 0    
    for index, key in enumerate(tracks) :   
        # set file variable to write to according to track type
        if key == audio_row and audio : fout = faudio
        elif key == video_row and video : fout = fvideo
        # read track, write file
        if (key == audio_row and audio) or (key == video_row and video) :            
            for elem in tracks[key].values() :    
                if elem.sender_ts == None : 
                    None
                    # print("Empty sender timestamp value for entry", elem.id, "of track", key, ":",  elem.sender_ts)    
                else :                   
                    if elem.sender_jitter == None :
                        elem.setSenderJitter(0)
                    fout.write(str(key) + ";0;" + str(elem.id) + ";sent;" + str(elem.sender_ts) + ";" + str(elem.sender_jitter) + "\n")
                    fout.write(str(key) + ";0;" + str(elem.id) + ";received;" + str(elem.receiver_ts) + "\n")
                    if elem.slow : fout.write(str(key) + ";0;" + str(elem.id) + ";too slow;" + str(elem.receiver_ts) + "\n")
                    if elem.old : fout.write(str(key) + ";0;" + str(elem.id) + ";too old;" + str(elem.receiver_ts) + "\n")
                    totalLatency += elem.latency
                    totalJitter += elem.sender_jitter   
                    if key == audio_row :
                        totalAudioLatency += elem.latency
                        totalAudioJitter += elem.sender_jitter
                    elif key == video_row :
                        totalVideoLatency += elem.latency
                        totalVideoJitter += elem.sender_jitter
else : 
    # read track, write file
    for elem_id, elem in data.items() :             
            if elem.sender_ts == None : 
                print("Empty sender timestamp value for entry", elem.id, "of track", elem_id)    
            else :                   
                if elem.sender_jitter == None :
                    elem.setSenderJitter(0)
                fout.write(str(elem.id) + ";0;" + str(elem.id) + ";sent;" + str(elem.sender_ts) + ";" + str(elem.sender_jitter) + "\n")
                fout.write(str(elem.id) + ";0;" + str(elem.id) + ";received;" + str(elem.receiver_ts) + "\n")
                if elem.slow : fout.write(str(elem.id) + ";0;" + str(elem.id) + ";too slow;" + str(elem.receiver_ts) + "\n")
                if elem.old : fout.write(str(elem.id) + ";0;" + str(elem.id) + ";too old;" + str(elem.receiver_ts) + "\n")
                totalLatency += elem.latency
                totalJitter += elem.sender_jitter

for elem in cpuTrack.values() :
    if cpulog : 
        if separateTracks :
            if audio : faudio.write("-;-;" + str(elem.sender_ts) + ";CPU;" + str(elem.value) + "\n")
            if video : fvideo.write("-;-;" + str(elem.sender_ts) + ";CPU;" + str(elem.value) + "\n")
        else :
            fout.write("-;-;" + str(elem.sender_ts) + ";CPU;" + str(elem.value) + "\n")
        totalCPU += elem.value
 
if separateTracks : 
    if audio : 
        faudio.close()
        print("Average audio latency", totalAudioLatency/len(tracks[audio_row]))
        print("Average audio jitter", totalAudioJitter/len(tracks[audio_row])) 
    if video : 
        fvideo.close()      
        print("Average video latency", totalVideoLatency/len(tracks[video_row]))
        print("Average video jitter", totalVideoJitter/len(tracks[video_row]))
else : 
    fout.close()
    entries = len(data)
    if(entries > 0) :
        print("Average latency", totalLatency/len(data)) 
        print("Average jitter", totalJitter/len(data))          
    