
import math
import matplotlib as mpl
import matplotlib.pyplot as plt 
import numpy as np
import argparse

class rowData :
    def __init__(self, name, latency=None, color=None, sender_ts=None, receiver_ts=None, sender_jitter=None, receiver_jitter=None):
        self.name = name
        self.color = color
        self.sender_ts = sender_ts
        self.receiver_ts = receiver_ts
        self.sender_jitter = sender_jitter
        self.receiver_jitter = receiver_jitter
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
    def getColor(self):
        return self.latency
    def setColor(self, color):
        self.color = color

def getIndex(li,target): 
    for index, x in enumerate(li): 
        if x.name == target: 
            return index 
    return -1

data = {}
tracks = {}
names = {}
argParser = argparse.ArgumentParser(prog='plotMoqjsTimestamp.py',
                    description='Program that allows to plot moq-js logger data',
                    epilog='By Alessandro Bottisio')
argParser.add_argument('-f', '--file', required=False)
argParser.add_argument('-sks', '--skipstart', required=False)
args = argParser.parse_args()

if args.file is not None and args.file != "" :
    filename = 'H:\\Tesi\\moq-js\\moq-js\\logs\\' + args.file
    print(filename)
    f = open(filename,'r') 
    print("a")
else :
    f = open('H:\\Tesi\\moq-js\\moq-js\\logs\\log.txt','r')
    
skip = 0
if args.skipstart is not None :    
    skip = int(args.skipstart)
    if skip < 0 or math.isnan(skip) :
        skip = 0

audio_row = -1
video_row = -1
skipping = True 
for row in f: 
    row = row.strip('\n').split(';') 
    # print(row)
    if(row[0].isnumeric()) :      
        name = row[0] + "-" + row[2] 
        # if row has track id and latency value
        if(4 < len(row) and row[4].isnumeric() and int(row[2]) > 0) :     
            if int(row[2]) >= skip :
                skipping = False   
            if (not skipping) and ((audio_row == row[0] and int(row[2]) >= skip) or video_row == row[0]) :           
                # add track to track array if not present and the received packet data to the individual track data array
                # add row data (received packet data) to general data array
                if row[0] not in tracks :
                    tracks[row[0]] = {}
                if(row[3] == 'sent') :
                    if name in data :
                        data[name].setSenderTS(int(row[4]))
                        tracks[row[0]][row[2]].setSenderTS(int(row[4]))
                    else :
                        data[name] = rowData(row[0] + "-" + row[2], sender_ts=int(row[4]), color=(0.1, 0.1, 0.8, 1))
                        tracks[row[0]][row[2]] = rowData(row[2], sender_ts=int(row[4]), color=(0.1, 0.1, 0.8, 1))
                    if(5 < len(row) and row[5].isnumeric()) :
                        data[name].setSenderJitter(int(row[5]))
                        tracks[row[0]][row[2]].setSenderJitter(int(row[5]))
                elif(row[3] == 'received') :
                    if(name in data) :
                        data[name].setReceiverTS(int(row[4]))
                        tracks[row[0]][row[2]].setReceiverTS(int(row[4]))
                    else :
                        data[name] = rowData(row[0] + "-" + row[2], receiver_ts=int(row[4]), color=(0.1, 0.1, 0.8, 1))
                        tracks[row[0]][row[2]] = rowData(row[2], receiver_ts=int(row[4]), color=(0.1, 0.1, 0.8, 1))                
                    if(5 < len(row) and row[5].isnumeric()) :
                        data[name].seReceiverJitter(int(row[5]))
                        tracks[row[0]][row[2]].setReceiverJitter(int(row[5]))
                if name in data and int(data[name].getLatency()) > 35  :
                    data[name].setColor((0.8, 0.1, 0.1, 1))
                    tracks[row[0]][row[2]].setColor((0.8, 0.1, 0.1, 1))
        elif(row[3] == 'too slow' and not skipping) :
            # change item color if too slow packet
            if name in data : 
                data[name].setColor((0.6, 0.0, 0.4, 1)) 
                tracks[row[0]][row[2]].setColor((0.6, 0.0, 0.4, 1))
        elif(row[3] == 'too old'  and not skipping) :
            # change item color if too old packet
            if name in data : 
                data[name].setColor((0.6, 0.2, 0.2, 1)) 
                tracks[row[0]][row[2]].setColor((0.6, 0.2, 0.2, 1))
        elif(row[3] == 'AUDIO') :
            names[row[0]] = 'Audio'
            audio_row = row[0]
        elif(row[3] == 'VIDEO') :
            names[row[0]] = 'Video'
            video_row = row[0]

# print(data)
print("Tracks found: " + str(len(tracks)))
if len(tracks) == 0 :
    print("No tracks found, program will exit") 
    exit()
elif len(tracks) == 1 :
    fig, axs = plt.subplots(2)
    fig.suptitle('moq-js latency test', fontsize = 20)
    ticks0 = []
    
    for index, key in enumerate(tracks) :    
        for elem in tracks[key].values() :
            axs[0].bar(elem.name, elem.latency, color = elem.color)
            if elem.sender_jitter == None :
                elem.setSenderJitter(0)
            axs[1].bar(elem.name, elem.sender_jitter, color = elem.color)
    axs[0].set_title("All packets")
    axs[0].set_ylabel(names[key] + ' latency\n(ms)', fontsize = 12)
    axs[1].set_ylabel(names[key] + ' jitter\n(ms)', fontsize = 12)
    axs[1].set_xlabel('Object sequence number', fontsize = 12)
    num = round(len(axs[0].get_xticks()) / 10)
    if num == 0 :
        num = 1
    axs[0].set_xticks(axs[0].get_xticks()[::num])    
    axs[1].set_xticks(axs[1].get_xticks()[::num])
    props = {"rotation" : 45}
    for ax in axs : 
        plt.setp(ax.get_xticklabels(), **props)
    
else :
    fig, axs = plt.subplots(len(tracks)*2 + 1, figsize=(14, 9))
    fig.suptitle('moq-js latency test', fontsize = 20)
    ticks0 = []
    for key, elem in data.items() :     
        axs[0].bar(elem.name, elem.latency, color = elem.color)
        axs[0].set_title("All packets")
        axs[0].set_ylabel('Latency\n(ms)', fontsize = 12)
        num = round(len(axs[0].get_xticks()) / 10)
        if num == 0 : 
            num = 1
        axs[0].set_xticks(axs[0].get_xticks()[::num])

    for index, key in enumerate(tracks) : 
        for elem in tracks[key].values() : 
            axs[index+1].bar(elem.name, elem.latency, color = elem.color)
            if elem.sender_jitter == None :
                elem.setSenderJitter(0)
            axs[index + len(tracks) + 1].bar(elem.name, elem.sender_jitter, color = elem.color)
        if(index + 1 == len(tracks))  :
            axs[index + len(tracks) + 1].set_xlabel('Object sequence number', fontsize = 12)
            axs[index+1].set_ylabel(names[key] + '\nlatency', fontsize = 12)
            axs[index + len(tracks) + 1].set_ylabel(names[key] + '\njitter', fontsize = 12)
        else :
            axs[index+1].set_ylabel(names[key] + '\nlatency', fontsize = 12)
            num = round(len(axs[index+1].get_xticks()) / 10)
            if num == 0 : 
                num = 1
            axs[index+1].set_xticks(axs[index+1].get_xticks()[::num])        
            axs[index + len(tracks) + 1].set_ylabel(names[key] + '\njitter', fontsize = 12)
            num = round(len(axs[index + len(tracks) + 1].get_xticks()) / 10)            
            if num == 0 : 
                num = 1
            axs[index + len(tracks) + 1].set_xticks(axs[index + len(tracks) + 1].get_xticks()[::num])
    
    props = {"rotation" : 45}
    for ax in axs : 
        plt.setp(ax.get_xticklabels(), **props)
plt.subplots_adjust(left = 0.078, right = 0.98, hspace = 0.5)
mpl.rcParams['figure.dpi'] = 300
plt.legend() 
plt.show() 
