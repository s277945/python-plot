import argparse
from functools import reduce

class rowData :
    def __init__(self, trackId, groupId, objectId, streamId, ackNum = 0, pNum = 0, stream = None, data = []):
        self.trackId = trackId
        self.groupId = groupId
        self.objectId = objectId
        self.streamId = streamId
        self.ackNum = ackNum
        self.pNum = pNum
        self.stream = stream
        self.data = data
        
class QuicPacket : 
    def __init__(self, id,  offset, length, dataMode = False,) -> None :    
        self.id = id
        self.offset = offset
        self.length = length
        self.dataMode = dataMode    

class Range :
    def __init__(self, offset, length, occurrences) -> None:
        self.offset = offset
        self.length = length
        self.occurrences = occurrences
        

argParser = argparse.ArgumentParser(prog='plotMoqjsTimestamp.py',
                    description='Program that allows to convert wireshark decrypted quic moq-js data',
                    epilog='By Alessandro Bottisio')

argParser.add_argument('-f', '--file', required=True)
argParser.add_argument('-sa', '--showAll', required=False)
args = argParser.parse_args()

if args.file is not None and args.file != "" :
    filename = args.file
    print("Opening moq-js log file", filename)
    f = open(filename,'r') 
else :
    print("Opening moq-js log file", 'log.txt')
    f = open('log.txt','r')

if args.showAll is not None and args.showAll == "true": 
    showAll = True
else : 
    showAll = False  

prevRow = None  
entries = {}
streams = {}
dataMode = False
ack = False
readingContent = False
for row in f: 
    if readingContent :
        data = row.split("   ")[0].split("  ")[1].strip()
        streamData += data
        data = streamData.replace("40 54 00 00 ", "").split(" ")
        if(len(data) >= 2 and data[0].isalnum() and data[1].isalnum()) :
            trackId = int(data[0], 16)
            if len(data) >= 4  and data[2].isalnum() and data[3].isalnum(): 
                if (int(data[1], 16) < 0x40) :
                    groupId = int(data[1], 16)
                    objectId = int("0x" + data[2], 16)
                else : 
                    groupId = int("0x" + data[1] + data[2], 16) - 0x4000
                    objectId = int("0x" + data[3], 16)  
            row_data =  rowData(trackId, groupId, objectId, streamId)
            row_data.stream = streams[streamId]
            entries[streamId] = row_data
        entries[streamId] = rowData(trackId, groupId, objectId, streamId)
        readingContent = False
    elif "No." in row :
        quicPackets = []
        currentQuicPacket = 0
    elif "ACK" in row :
        ack = True
    elif prevRow is not None and "Decrypted QUIC" in prevRow :
        # print(row)
        if len(quicPackets) > 0 : 
            quicPacket = quicPackets[currentQuicPacket]
            streamId = quicPacket.id
            dataMode = quicPacket.dataMode
            currentQuicPacket += 1
            if not dataMode :            
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
                        entries[streamId] = rowData(trackId, groupId, objectId, streamId)
                        if streamId in streams.keys() :
                            entries[streamId].stream = streams[streamId]
            else : 
                quicInfoLength = 1
                if streamId > 0x3f : quicInfoLength += 2
                else : quicInfoLength += 1
                if ack : quicInfoLength += 6
                if quicPacket.offset > 0x3f : quicInfoLength += 2
                elif quicPacket.offset > 0 : quicInfoLength += 1
                if quicPacket.length > 0x3f : quicInfoLength += 2
                elif quicPacket.length > 0 : quicInfoLength += 1
                rowDataOffset = 16 - quicInfoLength
                if rowDataOffset < 6 :
                    if rowDataOffset > 0 :
                        streamData = row.split("   ")[0].split("  ")[1].strip() + " "
                    if quicPacket.length > rowDataOffset :
                        readingContent = True
                    else : 
                        row_data = rowData(-1, -1, -1, streamId)
                        row_data.data = streamData
                        entries[streamId] = row_data
                        
                dataMode = False
        row1 = row.split("40 54 00 00 ")
        # if len(row1) > 1 :
        #     data = row1[1].split()
        #     if len(data) >=1 : data.pop()
        #     # print(len(data), data)
        #     if(len(data) >= 2 and data[0].isalnum() and data[1].isalnum()) :
        #         trackId = int(data[0], 16)
        #         if len(data) >= 4  and data[2].isalnum() and data[3].isalnum(): 
        #             if (int(data[1], 16) < 0x40) :
        #                 groupId = int(data[1], 16)
        #                 objectId = int("0x" + data[2], 16)
        #             else : 
        #                 groupId = int("0x" + data[1] + data[2], 16) - 0x4000
        #                 objectId = int("0x" + data[3], 16)                
        #         if len(quicPackets) > 0 : 
        #             quicPacket = quicPackets[currentQuicPacket]
        #             streamId = quicPacket.id
        #             dataMode = quicPacket.dataMode
        #             currentQuicPacket += 1
        #             entries[streamId] = rowData(trackId, groupId, objectId, streamId)
        #             if streamId in streams.keys() :
        #                 entries[streamId].stream = streams[streamId]
        ack = False
                        
    elif "STREAM id" in row and "RESET_STREAM id" not in row : 
        data = row.split("fin=")
        if len(data) >= 1 :
            streamId = int(data[0].replace("STREAM id=", "").strip())
            streamDetails = data[1].split(" ")
            streamOffset = int(streamDetails[1].replace("off=", ""))
            pduLength = int(streamDetails[2].replace("len=", ""))
            if ((streamOffset <= 6) and (pduLength <= (6 - streamOffset))) or ack : quicPackets.append(QuicPacket(streamId, streamOffset, pduLength, True))
            elif streamOffset == 0 : quicPackets.append(QuicPacket(streamId, streamOffset, pduLength, False))
            if streamId not in streams.keys() :
                stream = {}
                streams[streamId] = stream
            else :
                stream = streams[streamId]
            found = False
            for offset in stream :
                if (streamOffset >= offset and streamOffset < (streamOffset + pduLength)) or (pduLength > offset and pduLength <= (streamOffset + pduLength)) :
                    stream[offset].occurrences += 1
                    found = True
                    break
            if not found : 
                stream[streamOffset] = Range(streamOffset, pduLength, 1)
                if streamId in entries.keys() :
                    entries[streamId].stream = stream
                  
    prevRow = row

for key in sorted(entries) : 
    data = entries[key]
    if isinstance(data, rowData) : 
        stream = data.stream
        for offset in stream :
            data.pNum += stream[offset].occurrences - 1

f = open(filename + "_converted",'w') 
f.write("Track ID;Object ID;Group ID;SreamId;Number of retransmissions;\n")
for key in sorted(entries) : 
    data = entries[key]
    if isinstance(data, rowData): 
        if showAll or data.pNum > 0: 
            print(data.trackId, data.objectId, data.groupId, data.streamId, data.pNum)
            f.write(str(data.trackId) + ";" + 
                    str(data.objectId) + ";" + 
                    str(data.groupId) + ";" + 
                    str(data.streamId) + ";" + 
                    str(data.pNum) + 
                    ";\n")
    else : 
        print(key, data)
        f.write("/;/;/;" + 
                data + 
                ";1;/;\n")