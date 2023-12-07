
import matplotlib.pyplot as plt 
import numpy as np

class rowData :
    def __init__(self, name, latency, color):
        self.name = name
        self.latency = latency
        self.color = color
    def getName(self):
        return self.name
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

data = []
track_ids = []
tracks = []
f = open('test.txt','r') 
for row in f: 
    row = row.strip('\n').split(';') 
    print(row)
    if(row[0].isnumeric()) :        
        # if row has track id and latency value
        if(4 < len(row) and row[4].isnumeric()) : 
            # add row data (received packet data) to general data array
            data.append(rowData(row[0] + "-" + row[2], int(row[4]), (0.1, 0.1, 0.8, 1)))        
            # add track to track array if not present and the received packet data to the individual track data array
            if row[0] not in track_ids :
                track_ids.append(row[0])
                tracks.append([])
            tracks[track_ids.index(row[0])].append(rowData(int(row[2]), int(row[4]), (0.1, 0.1, 0.8, 1)))
        elif(row[3] == 'too slow\n') :
            # change item color if too slow packet
            row_name = row[0] + "-" + row[2]
            index = getIndex(data, row_name)
            if( index>=0 ) : 
                data[index].setColor((0.6, 0.1, 0.3, 1)) 
                index2 = getIndex(tracks[track_ids.index(row[0])], row_name)
                if( index2>=0 ) : 
                    tracks[track_ids.index(row[0])][index2].setColor((0.6, 0.1, 0.3, 0.7))
        elif(row[3] == 'too old\n') :
            # change item color if too old packet
            row_name = row[0] + "-" + row[2]
            index = getIndex(data, row_name)
            if( index>=0 ) : 
                data[index].setColor((0.6, 0.1, 0.3, 1)) 
                index2 = getIndex(tracks[track_ids.index(row[0])], row_name)
                if( index2>=0 ) : 
                    tracks[track_ids.index(row[0])][index2].setColor((0.6, 0.3, 0.1, 0.7))
  
print(len(track_ids) + 1)
print("Tracks found: " + str(track_ids))
fig, axs = plt.subplots(len(tracks) + 1)
fig.suptitle('moq-js latency test', fontsize = 20)
axs[0].bar(list(map(lambda node: node.name, data)), list(map(lambda node: node.latency, data)), color = list(map(lambda node: node.color, data)))
axs[0].set_title("All packets")
axs[0].set_xlabel('Object sequence number', fontsize = 12)
axs[0].set_ylabel('Latency(ms)', fontsize = 12)
for pos, id in enumerate(track_ids) :
    axs[pos + 1].bar(list(map(lambda node: node.name, data)), list(map(lambda node: node.latency, data)), color = list(map(lambda node: node.color, data)))    
    axs[pos + 1].set_title('Track' + id)    
    axs[pos + 1].set_xlabel('Object sequence number', fontsize = 12)
    axs[pos + 1].set_ylabel('Latency(ms)', fontsize = 12)
 
plt.legend() 
plt.show() 
