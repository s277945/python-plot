
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
# tracks = [] 
# objects = [] 
# groups = [] 
# status = [] 
# latency = [] 
# highLatency = [] 
# lowLatency = [] 
# oldPacket = [] 
# slowPacket = [] 
names = []
track_ids = []
tracks = []
names_tracks = []
color = []
color_tracks = []
f = open('test.txt','r') 
for row in f: 
    row = row.split(';') 
    if(row[0].isnumeric()) :        
        # if row has track id and latency value
        if(row[4].isnumeric()) : 
            # add row data (received packet data) to general data array
            data.append(rowData(row[0] + "-" + int(row[2]), int(row[4]), (0.1, 0.1, 0.8, 1)))        
            # add track to track array if not present and the received packet data to the individual track data array
            if row[0] not in tracks :
                track_ids.append(row[0])
                tracks.append([])
            tracks[track_ids.index(row[0])].append(rowData(int(row[2]), int(row[4]), (0.1, 0.1, 0.8, 1)))
        elif(row[3] == 'too slow') :
            # change item color if too slow packet
            row_name = row[0] + "-" + int(row[2])
            index = getIndex(data, row_name)
            if( index>=0 ) : 
                data[index].setColor((0.6, 0.1, 0.3, 1)) 
                index2 = getIndex(tracks[track_ids.index(row[0])], row_name)
                if( index2>=0 ) : 
                    tracks[track_ids.index(row[0])][index2].setColor((0.6, 0.1, 0.3, 0.7))
        elif(row[3] == 'too old') :
            # change item color if too old packet
            row_name = row[0] + "-" + int(row[2])
            index = getIndex(data, row_name)
            if( index>=0 ) : 
                data[index].setColor((0.6, 0.1, 0.3, 1)) 
                index2 = getIndex(tracks[track_ids.index(row[0])], row_name)
                if( index2>=0 ) : 
                    tracks[track_ids.index(row[0])][index2].setColor((0.6, 0.3, 0.1, 0.7))
        
    objects.append(int(row[1])) 
    status.append(row[3]) 
    latency.append(int(row[4])) 
    highLatency.append(int(row[4]))
    lowLatency.append(int(row[4]))
    oldPacket.append(int(row[4]))
    slowPacket.append(int(row[4]))
  

fig, axs = plt.subplots(2)
plt.bar( data.map(a.foo, a), marks, color = 'g', label = 'File Data') 
  
plt.xlabel('Student Names', fontsize = 12) 
plt.ylabel('Marks', fontsize = 12) 
  
plt.title('Students Marks', fontsize = 20) 
plt.legend() 
plt.show() 
