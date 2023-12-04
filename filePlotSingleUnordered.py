
import matplotlib.pyplot as plt 

# class rowData :
#     def __init__(self, l, hl, ll, op, sp):
#         self.latency = l
#         self.highLatency = hl
#         self.lowLatency = ll
#         self.oldPacket = op
#         self.slowPacket = sp

tracks = [] 
objects = [] 
groups = [] 
status = [] 
latency = [] 
highLatency = [] 
lowLatency = [] 
oldPacket = [] 
slowPacket = [] 
  
f = open('test.txt','r') 
for row in f: 
    row = row.split(';') 
    tracks.append(row[0]) 
    objects.append(int(row[1])) 
    groups.append(int(row[2])) 
    status.append(row[3]) 
    latency.append(int(row[4])) 
    highLatency.append(int(row[4]))
    lowLatency.append(int(row[4]))
    oldPacket.append(int(row[4]))
    slowPacket.append(int(row[4]))
  
plt.bar(names, marks, color = 'g', label = 'File Data') 
  
plt.xlabel('Student Names', fontsize = 12) 
plt.ylabel('Marks', fontsize = 12) 
  
plt.title('Students Marks', fontsize = 20) 
plt.legend() 
plt.show() 
