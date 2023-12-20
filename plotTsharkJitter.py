import sys
import matplotlib.pyplot as plt 
import numpy as np
from decimal import Decimal

class rowData :
    def __init__(self, name, delta=None, color=None):
        self.name = name
        self.delta = delta
        self.color = color
    def getName(self):
        return self.name
    def getDelta(self):
        return self.delta
    def setDelta(self, delta):
        self.delta = delta
    def getColor(self):
        return self.color
    def setColor(self, color):
        self.color = color

def getIndex(li,target): 
    for index, x in enumerate(li): 
        if x.name == target: 
            return index 
    return -1

data = {}
f = open('test.txt','r') 
max = 0
min = sys.maxsize * 2 + 1
avg = 0

for row in f: 
    row = row.strip('\n').split('\t') 
    if(row[0].isnumeric()) :      
        name = row[0] 
    if(row[1]) :
        rowdata = (Decimal(row[1][:7]) * 1000).normalize()
        if(rowdata < 300000000) :
            data[name] = rowData(name, rowdata, color=(0.1, 0.1, 0.8, 1))
        else :
            data[name] = rowData(name, rowdata, color=(0.6, 0.0, 0.4, 1))
        if(rowdata > max) : 
            max = rowdata
        if(rowdata < min) :
            min = rowdata
        avg = (rowdata + avg * (int(name) - 1)) / int(name)
        

print("Number of packets:", len(data))
print("Maximum packet delta:", max)
print("Minimum packet delta:", min)
print("Average packet delta:", '%.2f'%(avg))

fig, axs = plt.subplots(1)
fig.suptitle('Relay, delta between packets', fontsize = 20)

for key, elem in data.items() :     
    axs.bar(elem.name, elem.delta, color = elem.color)
axs.set_ylabel('Latency\n(ms)', fontsize = 12)
axs.set_xlabel('Object sequence number', fontsize = 12)
num = round(len(axs.get_xticks()) / 10)
axs.set_xticks(axs.get_xticks()[::num])
# axs.set_ylim(min, max+20)

props = {"rotation" : 45}
for ax in [axs] : 
    plt.setp(ax.get_xticklabels(), **props)
plt.legend() 
plt.show() 