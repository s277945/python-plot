import argparse
from functools import reduce
import json

class Stream :
    def __init__(self, id, packets = {},  moqHeader = {}, occurrences = 0) -> None:
        self.id = id
        self.packets = packets
        self.moqHeader = moqHeader
        self.occurrences = occurrences
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
                if key == 'quic.stream.offset_raw' :
                    offset = int(entry[0], 16)
                    temp = entry[0]
                    if len(temp) < 4 : 
                        offset = int(entry[0], 16)
                    elif len(temp) == 4 :
                        offset = int(entry[0], 16) - 0x4000
                    elif len(temp) > 4 :
                        offset = int(entry[0], 16) - 0x80004000
                if key == 'quic.stream_data_raw' :
                    data = entry[0]
                    length = entry[2]                    
            if streamId is not None :
                if streamId not in streams : 
                    stream = Stream(streamId)
                    streams[streamId] = stream
                else :                    
                    stream = streams[streamId]      
                if offset < 0x10 and data is not None and len(data) > 0:
                    if ((len(data) + offset) <= 0x10) : 
                        dataEnd = len(data) + offset
                    else : 
                        dataEnd = 0x10
                    for index in range(offset, dataEnd) :
                        stream.moqHeader[index] = data[index - offset]
                if offset not in stream.packets : 
                    packetRetransmitted = False
                    for key in stream.packets :
                        if (offset >= key and offset < stream.packets[key].length) or (length > key and length <= stream.packets[key].length) :
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
                if len(header) >= 16 and '40540000' in header :
                    moqHeader = header.replace('40540000', '')
                    trackId = int(moqHeader[0:2], 16)
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
    # print(stream.occurrences)
    if stream.trackId is not None : 
        print(stream.trackId, 0, stream.groupId, streamId, stream.occurrences)
        w.write(str(stream.trackId) + ";" + "0;" + 
                        str(stream.groupId) + ";" + 
                        str(streamId) + ";" + 
                        str(stream.occurrences) + 
                        ";\n")   
    
# Closing file
f.close()
w.close()
