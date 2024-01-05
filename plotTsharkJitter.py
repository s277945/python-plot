import sys
import matplotlib.pyplot as plt 
import numpy as np
from decimal import Decimal
import argparse
import math

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

argParser = argparse.ArgumentParser(prog='plotTsharkJitter.py',
                    description='Program that allows to plot moq-js tshark relay jitter data',
                    epilog='By Alessandro Bottisio')
argParser.add_argument('-f', '--file', required=False)
argParser.add_argument('-sks', '--skipstart', required=False)
argParser.add_argument('-mh', '--maxheight', required=False)
args = argParser.parse_args()

if args.file is not None and args.file != "" :
    filename = args.file
    print(filename)
    f = open(filename,'r') 
    print("a")
else :
    f = open('test.txt','r')
    
skip = 0
if args.skipstart is not None :    
    skip = int(args.skipstart)
    if skip < 0 or math.isnan(skip) :
        skip = 0
maxheight = 0
if args.maxheight is not None :    
    if type(args.maxheight) != int :
        print(str(args.maxheight))
        if str(args.maxheight) == 'auto' :
            maxheight = -1
    else :
        maxheight = int(args.maxheight)
        if maxheight < 0 : 
            maxheight = 0

def getIndex(li,target): 
    for index, x in enumerate(li): 
        if x.name == target: 
            return index 
    return -1

data = {}
max = 0
min = sys.maxsize * 2 + 1
avg = 0
skipping = True 

print(min)
for row in f: 
    row = row.strip('\n').split('\t') 
    if int(row[0]) >= skip :
        skipping = False   
    if (not skipping) and (row[0].isnumeric()) :      
        name = row[0] 
    if (not skipping) and (row[1]) :
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
fig.suptitle('Relay, time difference between packets', fontsize = 20)


totalDelta = 0
for key, elem in data.items() :     
    axs.bar(elem.name, elem.delta, color = elem.color)
    totalDelta += elem.delta
axs.set_ylabel('Time delta \n(ms)', fontsize = 12)
axs.set_xlabel('Object sequence number', fontsize = 12)
num = round(len(axs.get_xticks()) / 10)
axs.set_xticks(axs.get_xticks()[::num])
# axs.set_ylim(min, max+20)
bottom, top = axs.get_ylim()
ylen = top - bottom 
if maxheight > 0 and ylen > maxheight : 
    axs.set_ylim(0, maxheight)
if maxheight < 0 :
    axs.set_ylim(0, float(totalDelta) * 2 / len(data))

props = {"rotation" : 45}
for ax in [axs] : 
    plt.setp(ax.get_xticklabels(), **props)
plt.legend() 
plt.show() 