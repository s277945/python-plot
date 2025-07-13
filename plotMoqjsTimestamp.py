import os
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import argparse

COLORS = {
    "lost": "tab:red",
    "too_old": "tab:orange",
    "too_slow": "tab:blue"
}

class rowData:
    def __init__(self, name, latency=None, color=None, sender_ts=None, receiver_ts=None, sender_jitter=None, receiver_jitter=None, value=None, tooOld=False, tooSlow=False):
        self.name = name
        self.color = color
        self.sender_ts = sender_ts
        self.receiver_ts = receiver_ts
        self.sender_jitter = sender_jitter
        self.receiver_jitter = receiver_jitter
        self.value = value
        self.tooOld = tooOld
        self.tooSlow = tooSlow
        self.retransmissions = 0
        if (sender_ts is not None and receiver_ts is not None and receiver_ts > sender_ts):
            self.latency = receiver_ts - sender_ts
        elif (latency is not None):
            self.latency = latency
        else:
            self.latency = 0
    def getName(self):
        return self.name
    def getSenderTS(self):
        return self.sender_ts
    def setSenderTS(self, sender_ts):
        self.sender_ts = sender_ts
        if (sender_ts is not None and self.receiver_ts is not None and self.receiver_ts > sender_ts):
            self.latency = self.receiver_ts - sender_ts
    def setSenderJitter(self, sender_jitter):
        self.sender_jitter = sender_jitter
    def getReceiverTS(self):
        return self.receiver_ts
    def setReceiverTS(self, receiver_ts):
        self.receiver_ts = receiver_ts
        if (self.sender_ts is not None and receiver_ts is not None and receiver_ts > self.sender_ts):
            self.latency = receiver_ts - self.sender_ts
    def setReceiverJitter(self, receiver_jitter):
        self.receiver_jitter = receiver_jitter
    def getLatency(self):
        return self.latency
    def getColor(self):
        return self.color
    def setColor(self, color):
        self.color = color
    def getValue(self):
        return self.value
    def setTooOld(self, value):
        self.tooOld = value
    def setTooSlow(self, value):
        self.tooSlow = value
    def isTooOld(self):
        return self.tooOld
    def isTooSlow(self):
        return self.tooSlow
    def isSent(self):
        return self.sender_ts is not None
    def isReceived(self):
        return self.receiver_ts is not None

def build_cumulatives(tracks, startTS, data):
    entries = []
    for track in tracks.values():
        for elem in track.values():
            if elem.sender_ts is not None:
                lost = not elem.isReceived() and not elem.isTooOld() and not elem.isTooSlow()
                tooold = elem.isTooOld()
                tooslow = elem.isTooSlow()
                entries.append((elem.sender_ts, lost, tooold, tooslow))
    entries.sort()
    x = []
    lost_y = []
    tooold_y = []
    tooslow_y = []
    lost_cnt = tooold_cnt = tooslow_cnt = 0
    for ts, lost, tooold, tooslow in entries:
        if lost: lost_cnt += 1
        if tooold: tooold_cnt += 1
        if tooslow: tooslow_cnt += 1
        x.append((ts - startTS)/1000)
        lost_y.append(lost_cnt)
        tooold_y.append(tooold_cnt)
        tooslow_y.append(tooslow_cnt)
    return x, lost_y, tooold_y, tooslow_y

def set_all_xticks(axs, x_positions, x_labels, min_tick_spacing_px=80):
    fig = axs[0].figure
    bbox = axs[0].get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width_inch = bbox.width
    width_px = width_inch * fig.dpi
    show_every = max(1, int(np.ceil(len(x_labels) / max(2, width_px // min_tick_spacing_px))))
    indices = [i for i in range(len(x_labels)) if i % show_every == 0]
    labels = [x_labels[i] for i in indices]
    for ax in axs:
        ax.set_xticks(indices)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.xaxis.set_tick_params(labelbottom=True)

def simulated_latency_for_track(track, idx, all_indices, lost_height_mode):
    latencies = [e.latency for e in track.values() if e.isReceived() and e.latency > 0]
    jitters = [e.sender_jitter for e in track.values() if e.isReceived() and e.sender_jitter is not None]
    packets = list(track.values())
    sorted_ix = sorted(all_indices)
    if lost_height_mode == 'max_plus_50':
        if len(latencies) == 0:
            return 1000
        return max(latencies) + 50
    elif lost_height_mode == 'mean_jitter_plus_2std':
        mean_jitter = np.mean(jitters) if len(jitters) else 0
        std_latency = np.std(latencies) if len(latencies) else 0
        return mean_jitter + 2*std_latency
    elif lost_height_mode == 'avg_neighbor':
        sorted_packets = sorted([(i, e) for i, e in zip(all_indices, track.values())], key=lambda x: x[0])
        pos = None
        for i, (ix, elem) in enumerate(sorted_packets):
            if ix == idx:
                pos = i
                break
        prev_lat = next_lat = None
        for j in range(pos-1, -1, -1):
            if sorted_packets[j][1].isReceived():
                prev_lat = sorted_packets[j][1].latency
                break
        for j in range(pos+1, len(sorted_packets)):
            if sorted_packets[j][1].isReceived():
                next_lat = sorted_packets[j][1].latency
                break
        vals = []
        if prev_lat is not None: vals.append(prev_lat)
        if next_lat is not None: vals.append(next_lat)
        if vals: return np.mean(vals)
        return np.mean(latencies) if len(latencies) else 1000
    elif lost_height_mode == 'last10_mean':
        sorted_packets = sorted([(i, e) for i, e in zip(all_indices, packets)], key=lambda x: x[0])
        pos = None
        for i, (ix, elem) in enumerate(sorted_packets):
            if ix == idx:
                pos = i
                break
        received_latencies = []
        j = pos - 1
        while j >= 0 and len(received_latencies) < 10:
            if sorted_packets[j][1].isReceived():
                received_latencies.append(sorted_packets[j][1].latency)
            j -= 1
        if received_latencies:
            return np.mean(received_latencies)
        return np.mean(latencies) if len(latencies) else 1000
    elif lost_height_mode == 'last5_mean':
        sorted_packets = sorted([(i, e) for i, e in zip(all_indices, packets)], key=lambda x: x[0])
        pos = None
        for i, (ix, elem) in enumerate(sorted_packets):
            if ix == idx:
                pos = i
                break
        received_latencies = []
        j = pos - 1
        while j >= 0 and len(received_latencies) < 5:
            if sorted_packets[j][1].isReceived():
                received_latencies.append(sorted_packets[j][1].latency)
            j -= 1
        if received_latencies:
            return np.mean(received_latencies)
        return np.mean(latencies) if len(latencies) else 1000
    return 1000

# --- MAIN SCRIPT ---
data = {}
tracks = {}
cpuTrack = {}
names = {}

argParser = argparse.ArgumentParser(prog='plotMoqjsTimestamp.py',
    description='Program that allows to plot moq-js logger data',
    epilog='By Alessandro Bottisio')
argParser.add_argument('-f', '--file', required=False)
argParser.add_argument('-wpf', '--wshparsedfile', required=False)
argParser.add_argument('-sks', '--skipstart', required=False)
argParser.add_argument('-ske', '--skipend', required=False)
argParser.add_argument('-mh', '--maxheight', required=False)
argParser.add_argument('-cpu', '--cpulog', required=False)
argParser.add_argument('-shx', '--sharex', required=False)
argParser.add_argument('-lsl', '--logslow', required=False)
argParser.add_argument('-phd', '--pheader', required=False)
argParser.add_argument('-shl', '--showlost', required=False)
argParser.add_argument('-sf', '--savefile', required=False)
argParser.add_argument('-mts', '--min_tick_spacing', required=False, type=int, default=80,
    help="Spazio minimo in pixel tra le etichette dell'asse X (default 80)")
argParser.add_argument('-lsth', '--lost_height', choices=['1', 'infinite', 'max_plus_50', 'mean_jitter_plus_2std', 'avg_neighbor', 'last10_mean', 'last5_mean'],
    default='1', help="Come visualizzare i lost (1, infinite, max_plus_50, mean_jitter_plus_2std, avg_neighbor, last10_mean, last5_mean)")
args = argParser.parse_args()

min_tick_spacing = args.min_tick_spacing if hasattr(args, 'min_tick_spacing') else 80
lost_height_mode = args.lost_height

if args.file is not None and args.file != "":
    filename = args.file
    print("Opening moq-js log file", filename)
    f = open(filename, 'r')
else:
    print("Opening moq-js log file", 'log.txt')
    f = open('log.txt', 'r')

if args.wshparsedfile is not None and args.wshparsedfile != "":
    wshfilename = args.wshparsedfile
    wshfile = True
    print("Opening wireshark parsed moq-js data file", wshfilename)
    wshf = open(wshfilename, 'r')
else:
    wshfile = False

skip = 0
if args.skipstart is not None:
    skip = int(args.skipstart)
    if skip < 0 or math.isnan(skip):
        skip = 0

skipend = sys.maxsize
if args.skipend is not None:
    skipend = int(args.skipend)
    if skipend < 0 or math.isnan(skipend):
        skipend = sys.maxsize

maxheight = 0
if args.maxheight is not None:
    if type(args.maxheight) != int:
        if str(args.maxheight) == 'auto':
            maxheight = -1
        else:
            maxheight = int(args.maxheight)
            if maxheight < 0 or math.isnan(maxheight):
                maxheight = 0
    else:
        maxheight = int(args.maxheight)
        if maxheight < 0 or maxheight:
            maxheight = 0
cpulog = False
if args.cpulog == 'true': cpulog = True

sharex = False
if args.sharex == 'true': sharex = True

logSlow = False
if args.logslow == 'true': logSlow = True

header = 'false'
if args.pheader is not None: header = args.pheader

showLost = False
if args.showlost == 'true': showLost = True

saveFile = False
if args.savefile == 'true': saveFile = True

audio_row = -1
video_row = -1
skipping = True
cpuLogCount = 0
startTS = 0
packetCount = 0
last_ts_by_track = {}

for row in f:
    row = row.strip('\n').split(';')
    if row[0].isnumeric():
        name = row[0] + "-" + row[1] + "-" + row[2]
        track_id = row[0]
        elem_id = row[1] + "-" + row[2]
        if 4 < len(row) and row[4].isnumeric() and int(row[2]) > 0 and row[1].isnumeric() and (header == 'true' or (header == 'false' and int(row[1]) > 0) or (header == 'only' and int(row[1]) == 0)):
            if packetCount >= skip and packetCount <= skipend:
                skipping = False
            else:
                skipping = True
            if (not skipping) and ((audio_row == row[0] and packetCount >= skip) or (video_row == row[0] and (int(audio_row) > 0 or (int(audio_row) < 0 and packetCount >= skip)))):
                if track_id not in tracks:
                    tracks[track_id] = {}
                if(row[3] == 'sent'):
                    if startTS == 0:
                        startTS = int(row[4])
                    last_ts_by_track[track_id] = int(row[4])
                    if name in data:
                        data[name].setSenderTS(int(row[4]))
                        tracks[track_id][elem_id].setSenderTS(int(row[4]))
                    else:
                        data[name] = rowData(name, sender_ts=int(row[4]), color=None)
                        tracks[track_id][elem_id] = rowData(elem_id, sender_ts=int(row[4]), color=None)
                    if(5 < len(row) and row[5].isnumeric()):
                        data[name].setSenderJitter(int(row[5]))
                        tracks[track_id][elem_id].setSenderJitter(int(row[5]))
                elif(row[3] == 'received'):
                    if(name in data):
                        data[name].setReceiverTS(int(row[4]))
                        tracks[track_id][elem_id].setReceiverTS(int(row[4]))
                    else:
                        data[name] = rowData(name, receiver_ts=int(row[4]), color=None)
                        tracks[track_id][elem_id] = rowData(elem_id, receiver_ts=int(row[4]), color=None)
                    if(5 < len(row) and row[5].isnumeric()):
                        data[name].setReceiverJitter(int(row[5]))
                        tracks[track_id][elem_id].setReceiverJitter(int(row[5]))
                # Aggiorna colore solo se necessario
                if data[name].isTooOld():
                    data[name].setColor(COLORS["too_old"])
                elif data[name].isTooSlow():
                    data[name].setColor(COLORS["too_slow"])
                elif data[name].getColor() is None:
                    data[name].setColor((0.1, 0.1, 0.8, 1))
                if tracks[track_id][elem_id].isTooOld():
                    tracks[track_id][elem_id].setColor(COLORS["too_old"])
                elif tracks[track_id][elem_id].isTooSlow():
                    tracks[track_id][elem_id].setColor(COLORS["too_slow"])
                elif tracks[track_id][elem_id].getColor() is None:
                    tracks[track_id][elem_id].setColor((0.1, 0.1, 0.8, 1))
            if (audio_row == row[0] and int(audio_row) > 0) or (video_row == row[0] and int(video_row) < 0 and int(video_row) > 0): packetCount += 1

        elif(row[3] == 'too slow' and not skipping):
            ts = int(row[4]) if len(row) > 4 and row[4].isnumeric() else (last_ts_by_track.get(track_id, None)+5)
            if name not in data:
                data[name] = rowData(name, sender_ts=ts, color=COLORS["too_slow"], tooSlow=True)
            else:
                data[name].setColor(COLORS["too_slow"])
                data[name].setTooSlow(True)
            if track_id not in tracks:
                tracks[track_id] = {}
            if elem_id not in tracks[track_id]:
                tracks[track_id][elem_id] = rowData(elem_id, sender_ts=ts, color=COLORS["too_slow"], tooSlow=True)
            else:
                tracks[track_id][elem_id].setColor(COLORS["too_slow"])
                tracks[track_id][elem_id].setTooSlow(True)

        elif(row[3] == 'too old' and not skipping):
            ts = int(row[4]) if len(row) > 4 and row[4].isnumeric() else (last_ts_by_track.get(track_id, None)+5)
            if name not in data:
                data[name] = rowData(name, sender_ts=ts, color=COLORS["too_old"], tooOld=True)
            else:
                data[name].setColor(COLORS["too_old"])
                data[name].setTooOld(True)
            if track_id not in tracks:
                tracks[track_id] = {}
            if elem_id not in tracks[track_id]:
                tracks[track_id][elem_id] = rowData(elem_id, sender_ts=ts, color=COLORS["too_old"], tooOld=True)
            else:
                tracks[track_id][elem_id].setColor(COLORS["too_old"])
                tracks[track_id][elem_id].setTooOld(True)

        elif(row[3] == 'AUDIO'):
            names[row[0]] = 'Audio'
            audio_row = row[0]
        elif(row[3] == 'VIDEO'):
            names[row[0]] = 'Video'
            video_row = row[0]
    elif (not skipping) and cpulog and row[3] == 'CPU':
        color = (0, 0, 0, 1)
        if float(row[4]) > 50:
            color = (0.6, 0.2, 0.2, 1)
        else:
            color = (0.1, 0.1, 0.8, 1)
        cpuTrack[cpuLogCount] = rowData(cpuLogCount, value=float(row[4]), sender_ts=int(row[2]), color=color)
        cpuLogCount += 1

if wshfile:
    for row in wshf:
        row = row.strip('\n').split(';')
        if row[0].isnumeric():
            track = row[0]
            name = row[1] + "-" + row[2]
            if row[4].isnumeric() and row[0] in tracks and name in tracks[row[0]]:
                tracks[row[0]][name].retransmissions = int(row[4])

i = -1
lastTS = None
while lastTS is None and cpuLogCount + i > 0:
    lastTS = data[list(data)[i]].sender_ts
    i = i - 1
if lastTS is not None:
    cpuTrack = {k: v for k, v in cpuTrack.items() if (lastTS + 99 > v.sender_ts and v.sender_ts is not None)}
print("Tracks found: " + str(len(tracks)))

cnt_lost = sum(1 for d in data.values() if not d.isReceived() and not d.isTooOld() and not d.isTooSlow())
cnt_old = sum(1 for d in data.values() if d.tooOld)
cnt_slow = sum(1 for d in data.values() if d.tooSlow)
print("Totale pacchetti LOST:", cnt_lost)
print("Totale pacchetti TOO OLD:", cnt_old)
print("Totale pacchetti TOO SLOW:", cnt_slow)

# --- ASSE X COMUNE ---
all_x_floats = sorted(set([
    (elem.sender_ts - startTS) / 1000
    for track in tracks.values() for elem in track.values() if elem.sender_ts is not None
]))
all_x_labels = [str(round(x, 3)) for x in all_x_floats]
x_pos_map = {x: i for i, x in enumerate(all_x_floats)}

additional_axs = 0
if cpulog:
    additional_axs += 1
if wshfile:
    additional_axs += 1

# --- Calcola limiti per ogni traccia ---
latency_limits = {}
jitter_limits = {}
for track_id, track in tracks.items():
    latencies = [elem.latency for elem in track.values() if elem.isReceived() and elem.latency > 0]
    if latencies:
        if maxheight == -1:
            latency_ylim = np.mean(latencies) * 3
        else:
            latency_ylim = maxheight
        jitter_ylim = latency_ylim / 10
        if jitter_ylim > 20:
            jitter_ylim = 20
    else:
        latency_ylim = 10
        jitter_ylim = 2
    latency_limits[track_id] = latency_ylim
    jitter_limits[track_id] = jitter_ylim

latency_ax_idx = {}
jitter_ax_idx = {}

# --- PLOTTING ---
if len(tracks) == 0:
    print("No tracks found, program will exit")
    exit()
elif (len(tracks) == 1):
    n_plots = 2 + additional_axs
    if showLost:
        n_plots += 1
    fig, axs = plt.subplots(n_plots, figsize=(16, 8), sharex=True)
    fig.suptitle('moq-js latency test', fontsize=20)
    axs = np.atleast_1d(axs)
    maxRetransmissions = 0
    totalPackets = 0
    totalNotReceived = 0
    plotIdx = 0

    if showLost:
        x_c, y_lost, y_tooold, y_tooslow = build_cumulatives(tracks, startTS, data)
        x_c_idx = [x_pos_map[x] for x in x_c]
        axs[plotIdx].step(x_c_idx, y_lost, where='mid', color=COLORS["lost"], label='Lost')
        axs[plotIdx].step(x_c_idx, y_tooold, where='mid', color=COLORS["too_old"], label='Too old')
        axs[plotIdx].step(x_c_idx, y_tooslow, where='mid', color=COLORS["too_slow"], label='Too slow')
        axs[plotIdx].set_title("Cumulative anomaly packets")
        axs[plotIdx].set_ylabel('Cumulative\npackets', fontsize=12)
        axs[plotIdx].legend()
        plotIdx += 1

    # Latency
    axs[plotIdx].set_title("All packets")
    for key in names:
        if key.isnumeric():
            first_name = names[key]
            axs[plotIdx].set_ylabel(first_name + ' latency\n(ms)', fontsize=12)
            if (plotIdx + 1) < len(axs):
                axs[plotIdx + 1].set_ylabel(first_name + ' jitter\n(ms)(tx)', fontsize=12)

    for index, key in enumerate(tracks):
        latency_x = []
        latency_y = []
        latency_c = []
        jitter_x = []
        jitter_y = []
        jitter_c = []
        for elem in tracks[key].values():
            totalPackets += 1
            if elem.sender_ts is None:
                continue
            idx = x_pos_map[(elem.sender_ts - startTS) / 1000]
            if not elem.isReceived():
                if elem.isTooOld():
                    bar_color = COLORS["too_old"]
                elif elem.isTooSlow():
                    bar_color = COLORS["too_slow"]
                else:
                    bar_color = COLORS["lost"]
                if lost_height_mode == 'infinite':
                    axs[plotIdx].relim()
                    axs[plotIdx].autoscale_view()
                    ylim = axs[plotIdx].get_ylim()
                    height = ylim[1] * 0.98 if ylim[1] > 1 else 100
                elif lost_height_mode == '1':
                    height = 1
                else:
                    all_indices = [x_pos_map[(e.sender_ts - startTS) / 1000] for e in tracks[key].values() if e.sender_ts is not None]
                    height = simulated_latency_for_track(tracks[key], idx, all_indices, lost_height_mode)
                axs[plotIdx].bar(idx, height, color=bar_color)
                totalNotReceived += 1
                continue
            else:
                if elem.isTooOld():
                    bar_color = COLORS["too_old"]
                elif elem.isTooSlow():
                    bar_color = COLORS["too_slow"]
                elif elem.color is not None:
                    bar_color = elem.color
                else:
                    bar_color = (0.1, 0.1, 0.8, 1)
                latency_x.append(idx)
                latency_y.append(elem.latency)
                latency_c.append(bar_color)
                if (plotIdx + 1) < len(axs):
                    if elem.sender_jitter is None:
                        elem.setSenderJitter(0)
                    jitter_x.append(idx)
                    jitter_y.append(elem.sender_jitter)
                    jitter_c.append(bar_color)
        axs[plotIdx].bar(latency_x, latency_y, color=latency_c)
        if (plotIdx + 1) < len(axs):
            axs[plotIdx + 1].bar(jitter_x, jitter_y, color=jitter_c)
        # Salva posizione asse per limiti dopo
        latency_ax_idx[key] = plotIdx
        if (plotIdx + 1) < len(axs):
            jitter_ax_idx[key] = plotIdx + 1

    if wshfile:
        axs[-additional_axs].set_xlabel('Time in seconds', fontsize=12)
        axs[-additional_axs].set_ylabel('Number of retransmissions', fontsize=12)
    if cpulog:
        axs[-1].set_xlabel('Time in seconds', fontsize=12)
        axs[-1].set_ylabel('CPU usage\n(%)', fontsize=12)

    set_all_xticks(axs, all_x_floats, all_x_labels, min_tick_spacing_px=min_tick_spacing)
    axs[-1].set_xlabel("Time in seconds")
else:
    n_tracks = len(tracks)
    n_plots = n_tracks * 2 + 1 + additional_axs
    fig, axs = plt.subplots(n_plots, figsize=(18, 10), sharex=True)
    fig.suptitle('moq-js latency test', fontsize=20)
    axs = np.atleast_1d(axs)
    maxRetransmissions = 0
    totalPackets = 0
    totalNotReceived = 0
    plotIdx = 0

    if showLost:
        x_c, y_lost, y_tooold, y_tooslow = build_cumulatives(tracks, startTS, data)
        x_c_idx = [x_pos_map[x] for x in x_c]
        axs[0].step(x_c_idx, y_lost, where='mid', color=COLORS["lost"], label='Lost')
        axs[0].step(x_c_idx, y_tooold, where='mid', color=COLORS["too_old"], label='Too old')
        axs[0].step(x_c_idx, y_tooslow, where='mid', color=COLORS["too_slow"], label='Too slow')
        axs[0].set_ylabel('Cumulative\npackets', fontsize=12)
        axs[0].legend()
        plotIdx += 1
    else:
        axs[0].set_title("All packets")
        axs[0].set_ylabel('Latency\n(ms)', fontsize=12)
        latency_x = []
        latency_y = []
        latency_c = []
        for key, elem in data.items():
            if elem.sender_ts is not None:
                idx = x_pos_map[(elem.sender_ts - startTS) / 1000]
                if elem.isTooOld():
                    bar_color = COLORS["too_old"]
                elif elem.isTooSlow():
                    bar_color = COLORS["too_slow"]
                elif elem.color is not None:
                    bar_color = elem.color
                else:
                    bar_color = (0.1, 0.1, 0.8, 1)
                latency_x.append(idx)
                latency_y.append(elem.latency)
                latency_c.append(bar_color)
        axs[0].bar(latency_x, latency_y, color=latency_c)
        plotIdx += 1

    for index, key in enumerate(tracks):
        latency_x = []
        latency_y = []
        latency_c = []
        jitter_x = []
        jitter_y = []
        jitter_c = []
        for elem in tracks[key].values():
            totalPackets += 1
            if elem.sender_ts is None:
                continue
            idx = x_pos_map[(elem.sender_ts - startTS) / 1000]
            if not elem.isReceived():
                if elem.isTooOld():
                    bar_color = COLORS["too_old"]
                elif elem.isTooSlow():
                    bar_color = COLORS["too_slow"]
                else:
                    bar_color = COLORS["lost"]
                if lost_height_mode == 'infinite':
                    axs[plotIdx].relim()
                    axs[plotIdx].autoscale_view()
                    ylim = axs[plotIdx].get_ylim()
                    height = ylim[1] * 0.98 if ylim[1] > 1 else 100
                elif lost_height_mode == '1':
                    height = 1
                else:
                    all_indices = [x_pos_map[(e.sender_ts - startTS) / 1000] for e in tracks[key].values() if e.sender_ts is not None]
                    height = simulated_latency_for_track(tracks[key], idx, all_indices, lost_height_mode)
                axs[plotIdx].bar(idx, height, color=bar_color)
                totalNotReceived += 1
                continue
            else:
                if elem.isTooOld():
                    bar_color = COLORS["too_old"]
                elif elem.isTooSlow():
                    bar_color = COLORS["too_slow"]
                elif elem.color is not None:
                    bar_color = elem.color
                else:
                    bar_color = (0.1, 0.1, 0.8, 1)
                latency_x.append(idx)
                latency_y.append(elem.latency)
                latency_c.append(bar_color)
                if elem.sender_jitter is None:
                    elem.setSenderJitter(0)
                jitter_x.append(idx)
                jitter_y.append(elem.sender_jitter)
                jitter_c.append(bar_color)
        axs[plotIdx].bar(latency_x, latency_y, color=latency_c)
        axs[plotIdx + 1].bar(jitter_x, jitter_y, color=jitter_c)
        axs[plotIdx].set_ylabel(names[key] + '\nlatency (ms)', fontsize=12)
        axs[plotIdx + 1].set_ylabel(names[key] + ' tx\njitter (ms)', fontsize=12)
        # Salva posizione asse per limiti dopo
        latency_ax_idx[key] = plotIdx
        jitter_ax_idx[key] = plotIdx + 1
        plotIdx += 2

    if wshfile:
        axs[-additional_axs].set_xlabel('Time in seconds', fontsize=12)
        axs[-additional_axs].set_ylabel('Number of\nretransmissions', fontsize=12)
    if cpulog:
        axs[-1].set_xlabel('Time in seconds', fontsize=12)
        axs[-1].set_ylabel('CPU usage\n(%)', fontsize=12)

    set_all_xticks(axs, all_x_floats, all_x_labels, min_tick_spacing_px=min_tick_spacing)
    axs[-1].set_xlabel("Time in seconds")

# --- Applica limiti Y per traccia ---
for key in tracks:
    if key in latency_ax_idx:
        axs[latency_ax_idx[key]].set_ylim(top=latency_limits[key])
    if key in jitter_ax_idx:
        axs[jitter_ax_idx[key]].set_ylim(top=jitter_limits[key])

plt.subplots_adjust(left=0.07, right=0.975, hspace=0.85)
print("Total packets:", totalPackets, "\nTotal not received packets:", totalNotReceived)

def on_resize(event):
    set_all_xticks(axs, all_x_floats, all_x_labels, min_tick_spacing_px=min_tick_spacing)
    fig.canvas.draw_idle()

fig.canvas.mpl_connect('resize_event', on_resize)

if hasattr(args, "file") and args.file and saveFile:
    fig.set_size_inches(35, 20)
    base = os.path.basename(args.file).replace('.txt', '_cumuloss')
    plt.savefig(base + ".png")
    plt.savefig(base + ".svg")
    plt.close()
    print("Saved:", base + ".png and .svg")
    exit()
else:
    plt.show()
