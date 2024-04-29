import argparse
from functools import reduce
import json

dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
wanted_keys = ('quic.stream_data_raw')
# Opening JSON file
f = open('test1.json')
 
# returns JSON object as 
# a dictionary
data = json.load(f)
 
# Iterating through the json
# list
for i in data:
    filteredData = i['_source']['layers']['quic']['quic.frame']
    for key, entry in filteredData.items() :
        if key == 'quic.stream_data_raw' :
            print(entry[0])
    
# Closing file
f.close()
