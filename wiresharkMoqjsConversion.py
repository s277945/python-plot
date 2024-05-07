import argparse
from functools import reduce
import json

class Stream :
    def __init__(self, id) -> None:
        self.id = id
        self.packets = {}
        self.moqHeader = {}
        self.occurrences = 1
        self.trackId = None
        self.groupId = None
    
class Packet :
    def __init__(self, offset, length, data = "", occurrences = 1) -> None:
        self.offset = offset
        self.length = length
        self.data = data
        self.occurrences = occurrences

argParser = argparse.ArgumentParser(prog='plotMoqjsTimestamp.py',
                    description='Program that allows to convert wireshark decrypted quic moq-js data in json format',
                    epilog='By Alessandro Bottisio')

argParser.add_argument('-f', '--file', required=False)
argParser.add_argument('-wof', '--writeOutputFile', required=False)
argParser.add_argument('-ie', '--includeEmpty', required=False)
args = argParser.parse_args()

if args.file is not None and args.file != "" :
    filename = args.file
    print("Opening moq-js log file", filename)
    f = open(filename,'r') 
else :
    print("Opening moq-js log file", 'log.txt')
    f = open('log.json','r')

    
if args.writeOutputFile is not None and args.writeOutputFile != "" :
    outFilename = args.writeOutputFile
    w = open(outFilename,'w') 
else :
    w = open('moqjsRetransmissionData.txt','w')


includeEmpty = False
if args.includeEmpty == 'true' : includeEmpty = True

# returns JSON object as 
# a dictionary
data = json.load(f)
 
streams = {}

# Iterating through the json
# list
for i in data:
    filteredData = i['_source']['layers']['quic']
    for key, entry in filteredData.items() :
        if key == 'quic.frame' :
            filteredData = entry
            length = 0
            offset = 0
            streamId = None
            data = None
            stream = None
            frameType = 0
            for key, entry in filteredData.items() :
                if key == 'quic.frame_type' :
                    frameType = int(entry)
                    if frameType not in range(0x08, 0x0f) :
                        streamId = None
                        break
                if key == 'quic.stream.stream_id' :
                    streamId = entry
                if key == 'quic.stream.offset' :
                    offset = int(entry)
                if key == 'quic.stream.length' :
                    length = int(entry)
                if key == 'quic.stream_data_raw' :
                    data = entry[0]                 
            if streamId is not None :
                if streamId not in streams : 
                    stream = Stream(streamId)
                    streams[streamId] = stream
                else :                    
                    stream = streams[streamId]      
                if offset < 0x0a and data is not None and len(data) > 0:
                    if ((len(data) + offset*2) < 0x16) : 
                        dataEnd = len(data) + offset*2
                    else : 
                        dataEnd = 0x15
                    for index in range(offset*2, dataEnd) :
                        stream.moqHeader[index] = data[index - offset*2]
                if length > 0 or includeEmpty :
                    if offset not in stream.packets : 
                        packetRetransmitted = False
                        for key in stream.packets :
                            if (offset >= key and offset < (stream.packets[key].length + key)) or (offset + length > key and offset + length <= (stream.packets[key].length + key)) :
                                print(offset, length, key, stream.packets[key].length)
                                packetRetransmitted = True
                                stream.occurrences += 1
                                break
                        if not packetRetransmitted :
                            stream.packets[offset] = Packet(offset, length)      
                    else :
                        packet = stream.packets[offset]
                        if length > packet.length : 
                            packet.length = length
                        stream.occurrences += 1
                keys = list(stream.moqHeader.keys())
                keys.sort()
                header = ""
                for i in keys : 
                    header +=  stream.moqHeader[i]
                if offset < 0x0b and len(header) >= 0x0b and '40540000' in header :
                    moqHeader = header.replace('40540000', '')
                    if moqHeader[0:1] == '0' :
                        trackId = int(moqHeader[0:2], 16)
                    else :
                        trackId = int(moqHeader[0:1], 16)
                    if(trackId < 0xf and trackId > 1) :
                        temp = int(moqHeader[2:4], 16)
                        if temp < 0x40 :
                            groupId = temp
                        else :
                            if moqHeader[2:4] == '80' :
                                groupId = int(moqHeader[2:10], 16) - 0x80004000
                            if moqHeader[2:3] == '4' :
                                groupId = int(moqHeader[2:6], 16) - 0x4000
                            else :
                                groupId = int(moqHeader[2:3], 16)
                        stream.trackId = trackId
                        stream.groupId = groupId

w.write("Track ID;Object ID;Group ID;StreamId;Number of retransmissions;\n")
for streamId in streams :
    stream = streams[streamId]
    if stream.trackId is not None : 
        print(stream.trackId, 0, stream.groupId, streamId, stream.occurrences - 1)
        w.write(str(stream.trackId) + ";" + "0;" + 
                        str(stream.groupId) + ";" + 
                        str(streamId) + ";" + 
                        str(stream.occurrences - 1) + 
                        ";\n")   
    
# Closing file
f.close()
w.close()
