import argparse
from functools import reduce
import json

dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
wanted_keys = ('quic.stream_data_raw')
# Opening JSON file
f = open('test2.json')
 
# returns JSON object as 
# a dictionary
data = json.load(f)
 
# Iterating through the json
# list
for i in data:
    filteredData = i['_source']['layers']['quic']['quic.frame']
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
    if offset < 16 and streamId is not None :
        print("Stream id:", streamId, "\nOffset:", offset, "\nLength:", length, "\nData:", data)
    
# Closing file
f.close()
