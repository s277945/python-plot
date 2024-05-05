import argparse
from functools import reduce
import json

class Stream :
    def __init__(self, id, packets = {},  moqHeader = {}, occurrences = 1) -> None:
        self.id = id
        self.packets = packets
        self.moqHeader = moqHeader
        self.occurrences = occurrences
    
class Packet :
    def __init__(self, offset, length, data = "", occurrences = 1) -> None:
        self.offset = offset
        self.length = length
        self.data = data
        self.occurrences = occurrences

dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
wanted_keys = ('quic.stream_data_raw')
# Opening JSON file
f = open('test2.json')
 
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
            for key, entry in filteredData.items() :
                if key == 'quic.stream.stream_id_raw' :
                    streamId = entry[0]
                if key == 'quic.stream.offset_raw' :
                    offset = int(entry[0], 16)
                if key == 'quic.stream_data_raw' :
                    data = entry[0]
                    length = entry[2]
            if streamId is not None :
                # print("Stream id:", streamId, "\nOffset:", offset, "\nLength:", length, "\nData:", data)
                if streamId not in streams : 
                    stream = Stream(streamId)
                    streams[streamId] = stream
                else :                    
                    stream = streams[streamId]
                if offset < 16 and data is not None and len(data) > 0:
                    if ((len(data) + offset) <= 16) : dataEnd = len(data) + offset
                    else : dataEnd = 16
                    for index in range(offset, dataEnd) :
                        stream.moqHeader[index] = data[index - offset]
                    # print(len(data), data[0:16])
                if offset not in stream.packets : 
                    stream.packets[offset] = Packet(offset, length)
                else :
                    packet = stream.packets[offset]
                    if length > packet.length : 
                        packet.length = length
                        packet.occurrences += 1

for streamId in streams :
    stream = streams[streamId]
    # print(stream)
    packets = stream.packets
    keys = list(packets.keys())
    keys.sort()
    sorted_dict = {i: packets[i] for i in keys}
    stream.packets = packets = sorted_dict
    # print(packets)
    
    # packets.sort(reversed = True)
    for offset in packets :
        # print(offset)
        packet = packets[offset]
        if offset < 16 and len(stream.moqHeader) < 16:
            data = packet.data
            # print(data)
            if ((len(data) + offset) <= 16) : length = len(data) + offset
            else : length = 16
            for index in range(offset, length) :
                stream.moqHeader[index] = data[index - offset]
    keys = list(stream.moqHeader.keys())
    keys.sort()
    header = ""
    for i in keys : 
        header +=  stream.moqHeader[i]
    # print(header)
        
    
# Closing file
f.close()
