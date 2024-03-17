import argparse
from functools import reduce

class rowData :
    def __init__(self, trackId, groupId, objectId, streamId, ack = 0, pnum = 0):
        self.trackId = trackId
        self.groupId = groupId
        self.objectId = objectId
        self.streamId = streamId
        self.ack = ack
        self.pnum = pnum

argParser = argparse.ArgumentParser(prog='plotMoqjsTimestamp.py',
                    description='Program that allows to convert wireshark decrypted quic moq-js data',
                    epilog='By Alessandro Bottisio')

argParser.add_argument('-f', '--file', required=False)
args = argParser.parse_args()

if args.file is not None and args.file != "" :
    filename = args.file
    print("Opening moq-js log file", filename)
    f = open(filename,'r') 
else :
    print("Opening moq-js log file", 'log.txt')
    f = open('log.txt','r')
  
prevRow = None  
entries = {}
for row in f: 
    if prevRow is not None and "Decrypted QUIC" in prevRow :
        # print(row)
        row1 = row.split("40 54 00 00 ")
        if len(row1) > 1 :
            data = row1[1].split()
            if len(data) >=1 : data.pop()
            # print(len(data), data)
            if(len(data) >= 2 and data[0].isalnum() and data[1].isalnum()) :
                trackId = int(data[0], 16)
                if len(data) >= 4  and data[2].isalnum() and data[3].isalnum(): 
                    if (int(data[1], 16) < 0x40) :
                        groupId = int(data[1], 16)
                        objectId = int("0x" + data[2], 16)
                    else : 
                        groupId = int("0x" + data[1] + data[2], 16) - 0x4000
                        objectId = int("0x" + data[3], 16)
                if lastStream is not None : entries[lastStream] = rowData(trackId, groupId, objectId, lastStream)
                print("entry ", trackId, groupId, objectId)
    elif "Stream ID:" in row :
        data = row.replace("Stream ID:", "").strip()
        lastStream = int(data)
    elif "Largest Acknowledged:" in row :
        data = row.replace("Largest Acknowledged:", "").strip()
        lastAck = int(data)
        if lastAck not in entries.keys() :
            entries[lastAck] = True
        else : 
            data = entries[lastAck]
            if isinstance(data, rowData) : data.ack = True
                     
    prevRow = row
    