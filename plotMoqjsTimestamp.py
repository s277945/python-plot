import os
import math
import sys
import matplotlib.pyplot as plt 
import numpy as np
import argparse

class rowData :
    def __init__(self, name, latency=None, color=None, sender_ts=None, receiver_ts=None, sender_jitter=None, receiver_jitter=None, value=None):
        self.name = name
        self.color = color
        self.sender_ts = sender_ts
        self.receiver_ts = receiver_ts
        self.sender_jitter = sender_jitter
        self.receiver_jitter = receiver_jitter
        self.value = value
        self.retransmissions = 0
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
    def getValue(self):
        return self.value
    def isSent(self):
        return self.sender_ts is not None
    def isReceived(self):
        return self.receiver_ts is not None

def getIndex(li,target): 
    for index, x in enumerate(li): 
        if x.name == target: 
            return index 
    return -1

# ---- PATCH: funzione per il cumulativo dei persi, ALLINEATA ----
def build_cumulative_lost(tracks, startTS):
    """
    Ritorna una curva cumulativa delle perdite allineata ai timestamp di tutti i pacchetti.
    """
    packet_entries = []
    for track in tracks.values():
        for elem in track.values():
            if elem.sender_ts is not None:
                packet_entries.append((elem.sender_ts, not elem.isReceived()))
    # Ordina per timestamp
    packet_entries.sort()
    x = []
    y = []
    count = 0
    for ts, lost in packet_entries:
        if lost:
            count += 1
        x.append((ts - startTS)/1000)
        y.append(count)
    return x, y

data = {}
tracks = {}
cpuTrack = {}
names = {}
argParser = argparse.ArgumentParser(prog='plotMoqjsTimestamp.py',
                    description='Program that allows to plot moq-js logger data',
                    epilog='By Alessandro Bottisio')
argParser.add_argument('-f', '--file', required=False)
argParser.add_argument('-wpf', '--wshparsedfile', required=False)
argParser.add_argument('-sks', '--skipstart', required=False)
argParser.add_argument('-ske', '--skipend', required=False)
argParser.add_argument('-mh', '--maxheight', required=False)
argParser.add_argument('-cpu', '--cpulog', required=False)
argParser.add_argument('-shx', '--sharex', required=False)
argParser.add_argument('-lsl', '--logslow', required=False)
argParser.add_argument('-phd', '--pheader', required=False)
argParser.add_argument('-shl', '--showlost', required=False)
argParser.add_argument('-sf', '--savefile', required=False)
args = argParser.parse_args()

if args.file is not None and args.file != "" :
    filename = args.file
    print("Opening moq-js log file", filename)
    f = open(filename,'r') 
else :
    print("Opening moq-js log file", 'log.txt')
    f = open('log.txt','r')
    
if args.wshparsedfile is not None and args.wshparsedfile != "" :
    wshfilename = args.wshparsedfile
    wshfile = True
    print("Opening wireshark parsed moq-js data file", wshfilename)
    wshf = open(wshfilename,'r') 
else :
    wshfile = False

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

sharex = False       
if args.sharex == 'true' : sharex = True 
    
logSlow = False
if args.logslow == 'true': logSlow = True

header = 'false'
if args.pheader is not None : header = args.pheader

showLost = False
if args.showlost == 'true': showLost = True

saveFile = False
if args.savefile == 'true': saveFile = True
   
audio_row = -1
video_row = -1
skipping = True 
cpuLogCount = 0
startTS = 0
packetCount = 0
for row in f: 
    row = row.strip('\n').split(';') 
    if row[0].isnumeric() :   
        name = row[0] + "-" + row[1] + "-" + row[2]
        if 4 < len(row) and row[4].isnumeric() and int(row[2]) > 0 and row[1].isnumeric() and (header == 'true' or (header == 'false' and int(row[1]) > 0) or (header == 'only' and int(row[1]) == 0)) :    
            if packetCount >= skip and packetCount <= skipend :
                skipping = False   
            else : skipping = True
            if (not skipping) and ((audio_row == row[0] and packetCount >= skip) or (video_row == row[0] and (int(audio_row) > 0 or (int(audio_row) < 0 and packetCount >= skip)))) :            
                if row[0] not in tracks :
                    tracks[row[0]] = {}
                if(row[3] == 'sent') :
                    if startTS == 0 : 
                        startTS  = int(row[4])
                    if name in data :
                        data[name].setSenderTS(int(row[4]))
                        tracks[row[0]][row[1] + "-" + row[2]].setSenderTS(int(row[4]))
                    else :
                        data[name] = rowData(name, sender_ts=int(row[4]), color=(0.1, 0.1, 0.8, 1))
                        tracks[row[0]][row[1] + "-" + row[2]] = rowData(row[1] + "-" + row[2], sender_ts=int(row[4]), color=(0.1, 0.1, 0.8, 1))
                    if(5 < len(row) and row[5].isnumeric()) :
                        data[name].setSenderJitter(int(row[5]))
                        tracks[row[0]][row[1] + "-" + row[2]].setSenderJitter(int(row[5]))
                elif(row[3] == 'received') :
                    if(name in data) :
                        data[name].setReceiverTS(int(row[4]))
                        tracks[row[0]][row[1] + "-" + row[2]].setReceiverTS(int(row[4]))
                    else :
                        data[name] = rowData(name, receiver_ts=int(row[4]), color=(0.1, 0.1, 0.8, 1))
                        tracks[row[0]][row[1] + "-" + row[2]] = rowData(row[1] + "-" + row[2], receiver_ts=int(row[4]), color=(0.1, 0.1, 0.8, 1))                
                    if(5 < len(row) and row[5].isnumeric()) :
                        data[name].setReceiverJitter(int(row[5]))
                        tracks[row[0]][row[1] + "-" + row[2]].setReceiverJitter(int(row[5]))
                if name in data and int(data[name].getLatency()) > 35  :
                    data[name].setColor((0.8, 0.1, 0.1, 1))
                    tracks[row[0]][row[1] + "-" + row[2]].setColor((0.8, 0.1, 0.1, 1))                
            if (audio_row == row[0] and int(audio_row) > 0) or (video_row == row[0] and int(video_row) < 0 and int(video_row) > 0) : packetCount += 1
        elif(row[3] == 'too slow' and not skipping and logSlow) :
            if name in data : 
                data[name].setColor((0.6, 0.0, 0.4, 1)) 
                tracks[row[0]][row[1] + "-" + row[2]].setColor((0.6, 0.0, 0.4, 1))
        elif(row[3] == 'too old'  and not skipping) :
            if name in data : 
                data[name].setColor((0.6, 0.2, 0.2, 1)) 
                tracks[row[0]][row[1] + "-" + row[2]].setColor((0.6, 0.2, 0.2, 1))
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
        cpuTrack[cpuLogCount] = rowData(cpuLogCount, value=float(row[4]), sender_ts=int(row[2]), color=color)
        cpuLogCount += 1

if wshfile :
    for row in wshf :
        row = row.strip('\n').split(';') 
        if row[0].isnumeric() :
            track = row[0]
            name = row[1] + "-" + row[2]
            if row[4].isnumeric() and row[0] in tracks and name in tracks[row[0]] :
                print('a')
                tracks[row[0]][name].retransmissions = int(row[4])

i = -1
lastTS = None
while lastTS is None and cpuLogCount + i > 0 :    
    lastTS = data[list(data)[i]].sender_ts
    i = i - 1
if lastTS is not None : cpuTrack = {k:v for k,v in cpuTrack.items() if (lastTS + 99 > v.sender_ts and v.sender_ts is not None)}
print("Tracks found: " + str(len(tracks)))

additional_axs = 0
if cpulog: 
    additional_axs += 1
if wshfile:
    additional_axs += 1
if showLost:
    additional_axs += 1

if len(tracks) == 0 :
    print("No tracks found, program will exit") 
    exit()
    
elif len(tracks) == 1:
    fig, axs = plt.subplots(2 + additional_axs, figsize=(12, 7))
    fig.suptitle('moq-js latency test', fontsize=20)
    maxRetransmissions = 0
    totalPackets = 0
    totalNotReceived = 0
    totalLatency = 0
    totalJitter = 0
    totalCPU = 0
    startAxis = 0
    if showLost:
        # Usa stringhe per l’asse x cumulativo
        bar_x = []
        for elem in tracks[list(tracks)[0]].values():
            if elem.sender_ts is not None:
                bar_x.append(str((elem.sender_ts - startTS)/1000))
        x_lost_raw, y_lost = build_cumulative_lost(tracks, startTS)
        x_lost = [str(xx) for xx in x_lost_raw]
        axs[startAxis].step(bar_x, y_lost, where='mid', color='tab:red', label='Cumulative Lost Packets')
        axs[startAxis].set_title("Cumulative lost packets")
        axs[startAxis].set_ylabel('Cumulative\nlost packets', fontsize=12)
        axs[startAxis].legend()
        startAxis += 1

    axs[startAxis].set_title("All packets")
    for key in names:
        if(key.isnumeric()):
            axs[startAxis].set_ylabel(names[key] + ' latency\n(ms)', fontsize=12)
            axs[startAxis + 1].set_ylabel(names[key] + ' jitter\n(ms)(tx)', fontsize=12)
    for index, key in enumerate(tracks):
        for elem in tracks[key].values():
            totalPackets += 1
            if elem.isReceived() == False:
                print("Packet not received for entry", elem.name, "of track", key)
                totalNotReceived += 1
            else:
                if elem.isSent() == False:
                    print("Empty sender timestamp value for entry", elem.name, "of track", key)
                else:
                    axs[startAxis].bar(str((elem.sender_ts - startTS)/1000), elem.latency, color=elem.color)
                    totalLatency += elem.latency
                    if elem.sender_jitter == None:
                        elem.setSenderJitter(0)
                    axs[startAxis + 1].bar(str((elem.sender_ts - startTS)/1000), elem.sender_jitter, color=elem.color)
                    if elem.sender_jitter > 100 and maxheight < 0:
                        totalJitter += 100
                    else:
                        totalJitter += elem.sender_jitter
                    if wshfile:
                        if sharex:
                            axs[-additional_axs].bar((elem.sender_ts - startTS)/1000, elem.retransmissions, color=elem.color)
                        else:
                            axs[-additional_axs].bar(str((elem.sender_ts - startTS)/1000), elem.retransmissions, color=elem.color)
                        if elem.retransmissions > maxRetransmissions:
                            maxRetransmissions = elem.retransmissions
    
    for elem in cpuTrack.values():
        if cpulog: 
            if sharex:
                axs[-1].bar((elem.sender_ts - startTS)/1000, elem.value, color=elem.color)
            else:
                axs[-1].bar(str((elem.sender_ts - startTS)/1000), elem.value, color=elem.color)
            totalCPU += elem.value
                
    if wshfile:
        axs[-additional_axs].set_xlabel('Time in seconds', fontsize=12)
        axs[-additional_axs].set_ylabel('Number of retransmissions', fontsize=12)
        num = round(len(axs[-additional_axs].get_xticks()) / 20)            
        if num == 0 : num = 1
        axs[-additional_axs].set_xticks(axs[-additional_axs].get_xticks()[::num])
        if maxRetransmissions > 0: 
            axs[-additional_axs].set_yticks(np.arange(0, maxRetransmissions*5/4, maxRetransmissions/4))
    if cpulog: 
        axs[-1].set_xlabel('Time in seconds', fontsize=12)
        axs[-1].set_ylabel('CPU usage\n(%)', fontsize=12)
        num = round(len(axs[-1].get_xticks()) / 20)            
        if num == 0: num = 1
        axs[-1].set_xticks(axs[-1].get_xticks()[::num])
    if not cpulog and not wshfile: axs[1].set_xlabel('Time in seconds', fontsize=12)
    # if showLost:        
    #     axs[0].set_xlim(0, axs[0].get_xlim()[1])
    props = {"rotation" : 45} # label rotation property
    for ax in axs : 
        num = round(len(ax.get_xticks()) / 20) # set number of labels to show
        if num == 0 : num = 1        
        ax.set_xticks(ax.get_xticks()[::num])
        plt.setp(ax.get_xticklabels(), **props) # apply label rotation property
    
    bottom, top = axs[startAxis].get_ylim()
    ylen = top - bottom 
    if maxheight > 0 and ylen > maxheight: 
        axs[startAxis].set_ylim(0, maxheight)
        axs[startAxis + 1].set_ylim(0, maxheight/10)
    if maxheight < 0:
        axs[startAxis].set_ylim(0, totalLatency * 1.9 / len(data))
        
    bottom, top = axs[startAxis + 1].get_ylim()
    ylen = top - bottom 
    if maxheight < 0 and (totalJitter * 1.9 / len(data)) > 10: 
        axs[startAxis + 1].set_ylim(0, totalJitter / len(tracks[key]))

else:
    fig, axs = plt.subplots(len(tracks)*2 + 1 + additional_axs, figsize=(14, 9), sharex = sharex)
    fig.suptitle('moq-js latency test', fontsize = 20)
    
    maxRetransmissions = 0
    totalLatency = 0
    totalCPU = 0
    totalPackets = 0
    totalNotReceived = 0

    # --- Sostituisci plot generale con cumulativo se richiesto ---
    if showLost:
        x_lost, y_lost = build_cumulative_lost(tracks, startTS)
        axs[0].step(x_lost, y_lost, where='post', color='tab:red', label='Cumulative Lost Packets')
        axs[0].set_ylabel('Cumulative\nlost packets', fontsize=12)
        axs[0].legend()
    else:
        axs[0].set_title("All packets")
        axs[0].set_ylabel('Latency\n(ms)', fontsize=12)
        for key, elem in data.items():   
            if elem.sender_ts is not None:  
                if sharex:
                    axs[0].bar((elem.sender_ts - startTS)/1000, elem.latency, color=elem.color)
                else:
                    axs[0].bar(str((elem.sender_ts - startTS)/1000), elem.latency, color=elem.color)
                totalLatency += elem.latency
        num = round(len(axs[0].get_xticks()) / 20)
        if num == 0: num = 1        
        axs[0].set_xticks(axs[0].get_xticks()[::num])

        bottom, top = axs[0].get_ylim()
        ylen = top - bottom 
        if maxheight > 0 and ylen > maxheight: 
            axs[0].set_ylim(0, maxheight)
        if maxheight < 0:
            axs[0].set_ylim(0, totalLatency * 1.9 / len(data))
    
    for index, key in enumerate(tracks): 
        totalLatency = 0
        totalJitter = 0
        for elem in tracks[key].values():
            totalPackets += 1
            if elem.isReceived() == False:
                print("Packet not received for entry", elem.name, "of track", key)
                totalNotReceived += 1
            else:
                if elem.isSent() == False: 
                    print("Empty sender timestamp value for entry", elem.name, "of track", key)
                else:      
                    if sharex:
                        axs[(index+1)*2 - 1].bar((elem.sender_ts - startTS)/1000, elem.latency, color=elem.color)
                    else:
                        axs[(index+1)*2 - 1].bar(str((elem.sender_ts - startTS)/1000), elem.latency, color=elem.color)
                    totalLatency += elem.latency
                    if elem.sender_jitter == None:
                        elem.setSenderJitter(0)
                    if sharex:
                        axs[(index+1)*2].bar((elem.sender_ts - startTS)/1000, elem.sender_jitter, color=elem.color)
                    else:
                        axs[(index+1)*2].bar(str((elem.sender_ts - startTS)/1000), elem.sender_jitter, color=elem.color)
                    if elem.sender_jitter > 100 and maxheight < 0:
                        totalJitter += 100
                    else:
                        totalJitter += elem.sender_jitter
                    if wshfile:
                        if sharex:
                            axs[-additional_axs].bar((elem.sender_ts - startTS)/1000, elem.retransmissions, color=elem.color)
                        else:
                            axs[-additional_axs].bar(str((elem.sender_ts - startTS)/1000), elem.retransmissions, color=elem.color)
                        if elem.retransmissions > maxRetransmissions:
                            maxRetransmissions = elem.retransmissions

        if not cpulog and not wshfile: axs[-1].set_xlabel('Time in seconds', fontsize=12)
        axs[(index+1)*2 - 1].set_ylabel(names[key] + '\nlatency (ms)', fontsize=12)
        num = round(len(axs[(index+1)*2 - 1].get_xticks()) / 20)
        if num == 0: 
            num = 1
        axs[(index+1)*2 - 1].set_xticks(axs[(index+1)*2 - 1].get_xticks()[::num])   
        axs[(index+1)*2].set_ylabel(names[key] + ' tx\njitter (ms)', fontsize=12)
        num = round(len(axs[(index+1)*2].get_xticks()) / 20)            
        if num == 0: num = 1
        axs[(index+1)*2].set_xticks(axs[(index+1)*2].get_xticks()[::num])
            
        bottom, top = axs[(index+1)*2 - 1].get_ylim()
        ylen = top - bottom 
        if maxheight > 0 and ylen > maxheight: 
            axs[(index+1)*2 - 1].set_ylim(0, maxheight)
        if maxheight < 0:
            axs[(index+1)*2 - 1].set_ylim(0, totalLatency * 1.9 / len(tracks[key]))
        
        bottom, top = axs[(index+1)*2].get_ylim()
        ylen = top - bottom 
        if maxheight < 0 and (totalJitter * 1.9 / len(data)) > 10: 
            axs[(index+1)*2].set_ylim(0, totalJitter / len(tracks[key]))
        else: axs[(index+1)*2].set_ylim(0, 10)
    
    for elem in cpuTrack.values():
        if cpulog: 
            if sharex:
                axs[-1].bar((elem.sender_ts - startTS)/1000, elem.value, color=elem.color)
            else:
                axs[-1].bar(str((elem.sender_ts - startTS)/1000), elem.value, color=elem.color)
            totalCPU += elem.value
        
    if wshfile:
        axs[-additional_axs].set_xlabel('Time in seconds', fontsize=12)
        axs[-additional_axs].set_ylabel('Number of\nretransmissions', fontsize=12)
        num = round(len(axs[-additional_axs].get_xticks()) / 20)            
        if num == 0: num = 1
        axs[-additional_axs].set_xticks(axs[-additional_axs].get_xticks()[::num])        
        if maxRetransmissions > 0: 
            axs[-additional_axs].set_yticks(np.arange(0, maxRetransmissions*5/4, maxRetransmissions/4))
    if cpulog: 
        axs[-1].set_xlabel('Time in seconds', fontsize=12)
        axs[-1].set_ylabel('CPU usage\n(%)', fontsize=12)
        num = round(len(axs[-1].get_xticks()) / 20)            
        if num == 0: num = 1
        axs[-1].set_xticks(axs[-1].get_xticks()[::num])
           
    props = {"rotation" : 45, "visible" : True}
    for ax in axs: 
        plt.setp(ax.get_xticklabels(), **props)

plt.subplots_adjust(left = 0.07, right = 0.975, hspace = 0.85)
print("Total packets:", totalPackets, "\nTotal not received packets:", totalNotReceived)
if hasattr(args, "file") and args.file and saveFile:
    base = os.path.basename(args.file).replace('.txt','_cumuloss')
    plt.savefig(base + ".png")
    plt.savefig(base + ".svg")
    plt.close()
    print("Saved:", base + ".png and .svg")
    exit()  # evita plt.show()
else : plt.show() 
