
import matplotlib.pyplot as plt 
import numpy as np

class rowData :
    def __init__(self, name, latency):
        self.name = name
        self.latency = latency

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
            data.append(rowData(row[0] + "-" + int(row[2]), int(row[4])))        
            # add track to track array if not present and the received packet data to the individual track data array
            if row[0] not in tracks :
                track_ids.append(row[0])
                tracks.append([])
            tracks[track_ids.index(row[0])].append(rowData(int(row[2]), int(row[4])))
        else if(row[3] == 'too slow') :
            # add row data (received packet data) to general data array
            data.append(rowData(row[0] + "-" + int(row[2]), int(row[4])))        
            # add track to track array if not present and the received packet data to the individual track data array
            if row[0] not in tracks :
                track_ids.append(row[0])
                tracks.append([])
            tracks[track_ids.index(row[0])].append(rowData(int(row[2]), int(row[4])))
        
    objects.append(int(row[1])) 
    status.append(row[3]) 
    latency.append(int(row[4])) 
    highLatency.append(int(row[4]))
    lowLatency.append(int(row[4]))
    oldPacket.append(int(row[4]))
    slowPacket.append(int(row[4]))
  
mask1 = y < 0.5
mask2 = y >= 0.5

fig, axs = plt.subplots(2)
plt.bar(names, marks, color = 'g', label = 'File Data') 
  
plt.xlabel('Student Names', fontsize = 12) 
plt.ylabel('Marks', fontsize = 12) 
  
plt.title('Students Marks', fontsize = 20) 
plt.legend() 
plt.show() 
