
import functools
import math
import sys
import matplotlib.pyplot as plt 
import numpy as np
import argparse
import seaborn as sb

class rowData :
    def __init__(self, name, latency=None, color=None, sender_ts=None, receiver_ts=None, sender_jitter=0, receiver_jitter=None, value=None, slow=None, old=None):
        self.name = name
        self.color = color
        self.sender_ts = sender_ts
        self.receiver_ts = receiver_ts
        self.sender_jitter = sender_jitter
        self.receiver_jitter = receiver_jitter
        self.value = value
        self.slow = slow
        self.old = old
        if (sender_ts is not None and receiver_ts is not None and receiver_ts > sender_ts) : 
            self.latency = int(receiver_ts) - int(sender_ts)
        elif (latency is not None) : 
            self.latency = int(latency)
        else :
            self.latency = 0
    def getSenderTS(self):
        return self.sender_ts
    def setSenderTS(self, sender_ts):
        self.sender_ts = int(sender_ts)
        if (sender_ts is not None and self.receiver_ts is not None and self.receiver_ts > sender_ts) : 
            self.latency = int(self.receiver_ts) - int(sender_ts)
    def setSenderJitter(self, sender_jitter):
        self.sender_jitter = int(sender_jitter)
    def getReceiverTS(self):
        return self.receiver_ts
    def setReceiverTS(self, receiver_ts):
        self.receiver_ts = int(receiver_ts)
        if (self.sender_ts is not None and receiver_ts is not None and receiver_ts > self.sender_ts) : 
            self.latency = int(receiver_ts) - int(self.sender_ts)
    def setReceiverJitter(self, receiver_jitter):
        self.receiver_jitter = receiver_jitter
    def getLatency(self):
        return self.latency
    def getColor(self):
        return self.latency
    def setColor(self, color):
        self.color = color
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

def getLatencies(entry: rowData):
  return entry.getLatency()

def getJitters(entry: rowData):
  return entry.sender_jitter

def getValues(entry: rowData):
  return entry.value

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
argParser.add_argument('-mh', '--maxheight', required=False)
argParser.add_argument('-cpu', '--cpulog', required=False)
argParser.add_argument('-psl', '--plotslow', required=False)
argParser.add_argument('-pld', '--plotold', required=False)
argParser.add_argument('-phd', '--pheader', required=False)
argParser.add_argument('-tp', '--type', required=False)

args = argParser.parse_args()

if args.file is not None and args.file != "" :
    filename = args.file
    print("Opening moq-js log file", filename)
    f = open(filename,'r') 
else :
    print("Opening moq-js log file", 'log.txt')
    f = open('log.txt','r')
    
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
            

maxheight = 0
if args.maxheight is not None : 
    if type(args.maxheight) != int :   
        if str(args.maxheight) == 'auto' :
            maxheight = -1
        else :
            maxheight = int(args.maxheight)
            if maxheight < 0 or math.isnan(maxheight) : 
                maxheight = 0
    else :
        maxheight = int(args.maxheight)
        if maxheight < 0 or maxheight : 
            maxheight = 0
cpulog = False
if args.cpulog == 'true' : cpulog = True
    
plotSlow = False
if args.plotslow == 'true': plotSlow = True

plotOld = False
if args.plotold == 'true': plotOld = True

header = 'false'
if args.pheader is not None : header = args.pheader

type = 'latency'
if args.type == 'jitter' : type = args.type
if args.type == 'all' : type = args.type
   
audio_row = -1
video_row = -1
skipping = True 
cpuLogCount = 0
startTS = 0
packetCount = 0
for row in f: 
    row = row.strip('\n').split(';') 
    # print(row)
    # print(row[1].isnumeric())
    if row[0].isnumeric() :   
        name = row[0] + "-" + row[1] + "-" + row[2]
        # if row has track id and latency value
        if 4 < len(row) and row[4].isdecimal() and int(row[2]) > 0 and row[1].isnumeric() and (header == 'true' or (header == 'false' and int(row[1]) > 0) or (header == 'only' and int(row[1]) == 0)) :    
            if packetCount >= skip and packetCount <= skipend :
                skipping = False   
            else : skipping = True
            if (not skipping) and ((audio_row == row[0] and packetCount >= skip) or (video_row == row[0] and (int(audio_row) > 0 or (int(audio_row) < 0 and packetCount >= skip)))) :            
                # add track to track array if not present and the received packet data to the individual track data array
                # add row data (received packet data) to general data array
                if row[0] not in tracks :
                    tracks[row[0]] = {}
                if(row[3] == 'sent') :
                    if startTS == 0 : 
                        startTS  = int(row[4])
                    if name in data :
                        data[name].setSenderTS(int(row[4]))
                        tracks[row[0]][row[1] + "-" + row[2]].setSenderTS(int(row[4]))
                    else :
                        data[name] = rowData(name, sender_ts=int(row[4]))
                        tracks[row[0]][row[1] + "-" + row[2]] = rowData(row[1] + "-" + row[2], sender_ts=int(row[4]))
                    if(5 < len(row) and row[5].isdecimal()) :
                        data[name].setSenderJitter(int(row[5]))
                        tracks[row[0]][row[1] + "-" + row[2]].setSenderJitter(int(row[5]))
                elif(row[3] == 'received') :
                    if(name in data) :
                        data[name].setReceiverTS(int(row[4]))
                        tracks[row[0]][row[1] + "-" + row[2]].setReceiverTS(int(row[4]))
                    else :
                        data[name] = rowData(name, receiver_ts=int(row[4]))
                        tracks[row[0]][row[1] + "-" + row[2]] = rowData(row[1] + "-" + row[2], receiver_ts=int(row[4]))                
                    if(5 < len(row) and row[5].isdecimal()) :
                        data[name].seReceiverJitter(int(row[5]))
                        tracks[row[0]][row[1] + "-" + row[2]].setReceiverJitter(int(row[5]))      
            if (audio_row == row[0] and int(audio_row) > 0) or (video_row == row[0] and int(video_row) < 0 and int(audio_row) > 0) : packetCount += 1
        elif(plotSlow and row[3] == 'too slow' and not skipping) :
            # change item color if too slow packet
            if name in data : 
                data[name].setSlow(True) 
                tracks[row[0]][row[1] + "-" + row[2]].setSlow(True) 
        elif(plotOld and row[3] == 'too old'  and not skipping) :
            # change item color if too old packet
            if name in data : 
                data[name].setOld(True) 
                tracks[row[0]][row[1] + "-" + row[2]].setOld(True) 
        elif(row[3] == 'AUDIO') :
            names[row[0]] = 'Audio'
            audio_row = row[0]
        elif(row[3] == 'VIDEO') :
            names[row[0]] = 'Video'
            video_row = row[0]
    elif (not skipping) and cpulog and row[3] == 'CPU' :
        color = (0, 0, 0, 1)
        if float(row[4]) > 50 :
            color=(0.6, 0.2, 0.2, 1)
        else :
            color=(0.1, 0.1, 0.8, 1)
        cpuTrack[cpuLogCount] = rowData(cpuLogCount, value=float(row[4]), sender_ts=int(row[2]))
        print(cpuTrack[cpuLogCount].value)
        cpuLogCount += 1

# filter cpu logs with timestamp greater than last valid packet log sender_ts
i = -1
lastTS = None
while lastTS is None and cpuLogCount + i > 0 :    
    lastTS = data[list(data)[i]].sender_ts
    i = i - 1
if lastTS is not None : cpuTrack = {k:v for k,v in cpuTrack.items() if (lastTS + 99 > v.sender_ts and v.sender_ts is not None)}
print("Tracks found: " + str(len(tracks)))

if len(tracks) == 0 :
    print("No tracks found, program will exit") 
    exit()
 
total_axs = 0
plotData = []
labels = []
binsList = []

if int(audio_row) > 0 and int(video_row) > 0 :
    if type == 'latency' or type == 'all' : 
        dataLatencyValues = list(map(getLatencies, data.values()))
        plotData.append(dataLatencyValues)
        labels.append("Fragments latency distribution")        
        _, FD_bins = np.histogram(dataLatencyValues, bins="fd")
        binsList.append(min(len(FD_bins)-1, 50))
        totalLatency = functools.reduce(lambda a, b: int(a)+int(b), dataLatencyValues)  
        total_axs += 1
    if type == 'jitter' or type == 'all' : 
        dataJitterValues = list(map(getJitters, data.values()))
        plotData.append(dataJitterValues)
        labels.append("Fragments jitter distribution")
        _, FD_bins = np.histogram(dataJitterValues, bins="fd")
        binsList.append(min(len(FD_bins)-1, 50))
        totalJitter = functools.reduce(lambda a, b: int(a)+int(b), dataJitterValues)  
        total_axs += 1
for index, key in enumerate(tracks) :   
    if int(audio_row) > 0 and key == audio_row :
        if type == 'latency' or type == 'all' : 
            audioTrackLatencyValues = list(map(getLatencies, tracks[key].values()))
            plotData.append(audioTrackLatencyValues)
            labels.append("Audio fragments latency distribution")   
            _, FD_bins = np.histogram(audioTrackLatencyValues, bins="fd")
            binsList.append(min(len(FD_bins)-1, 50))
            totalAudioLatency = functools.reduce(lambda a, b: int(a)+int(b), audioTrackLatencyValues)  
            total_axs += 1
        if type == 'jitter' or type == 'all' : 
            audioTrackJitterValues = list(map(getJitters, tracks[key].values()))
            plotData.append(audioTrackJitterValues)
            labels.append("Audio fragments jitter distribution")
            _, FD_bins = np.histogram(audioTrackJitterValues, bins="fd")
            binsList.append(min(len(FD_bins)-1, 50))
            totalAudioJitter = functools.reduce(lambda a, b: int(a)+int(b), audioTrackJitterValues)  
            total_axs += 1
    if int(video_row) > 0 and key == video_row :
        if type == 'latency' or type == 'all' : 
            videoTrackLatencyValues = list(map(getLatencies, tracks[key].values()))
            plotData.append(videoTrackLatencyValues)
            labels.append("Video fragments latency distribution")   
            _, FD_bins = np.histogram(videoTrackLatencyValues, bins="fd")
            binsList.append(min(len(FD_bins)-1, 50))
            totalVideoLatency = functools.reduce(lambda a, b: int(a)+int(b), videoTrackLatencyValues)  
            total_axs += 1
        if type == 'jitter' or type == 'all' : 
            videoTrackJitterValues = list(map(getJitters, tracks[key].values()))
            plotData.append(videoTrackJitterValues)
            labels.append("Video fragments jitter distribution")
            _, FD_bins = np.histogram(videoTrackJitterValues, bins="fd")
            binsList.append(min(len(FD_bins)-1, 50))
            totalVideoJitter = functools.reduce(lambda a, b: int(a)+int(b), videoTrackJitterValues)   
            total_axs += 1
if cpulog : 
    cpuTrackValues = list(map(lambda a: a.value, cpuTrack.values()))
    plotData.append(cpuTrackValues)
    labels.append("Cpu usage value distribution")
    _, FD_bins = np.histogram(cpuTrackValues, bins="fd")
    binsList.append(min(len(FD_bins)-1, 50)*3)
    totalCPU = functools.reduce(lambda a, b: int(a)+int(b), cpuTrackValues)   
    total_axs += 1    
    
fig, axs = plt.subplots(total_axs , figsize=(12, 9.5))
fig.suptitle('moq-js distribution plot', fontsize = 20)  


for index in range(total_axs):
    # sb.distplot(x = plotData[index]  ,  bins = 20 , kde = True , color = (0, 0.2, 0.8, 1), kde_kws=dict(linewidth = 4 , color = (0.0, 0, 0.4)), ax=axs[index])   
    sb.histplot(data=plotData[index], bins = binsList[index], stat='probability', alpha=0.4, kde=True, kde_kws={"cut": 3}, ax=axs[index]) 
    axs[index].set_title(labels[index])
    

plt.subplots_adjust(left = 0.07, right = 0.975, hspace = 1.2 - 3/total_axs, bottom = 0.045, top = 0.9)
plt.show() 
