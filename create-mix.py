#!/usr/bin/python
# args: [<timescale method>] [effect] <mix output name> <list of soundfile cue txt to mix...>
# TODO: timescale method:
#   none
#   resample (sox: speed)
#   stretch  (sox: tempo using WSOLA)
#   supervp
#
# effect:
#   none
#   bass
#   compressor
#   distortion
#
# loads file.txt cue data written by create-excerpts.py
# writes mix of sound files,
# if option is set, first and last are cut at cutpoint

# call as
# cd data/unmixdb/excerpts/set123/refsongs
# =2/create-mix.py ../mixes/3.wav `ls *.txt | head -3`

"""
creates commandline for sox:

sox -m "|sox in1 -p trim cueinstart1 fade cueinlen1 (cueoutstart1 - cueinstart1) cueoutlen1" \
       "|sox in2 -p trim cueinstart2 fade cueinlen2 (cueoutstart2 - cueinstart2) cueoutlen2 speed 1 pad (cueoutstart1 - cueinstart1)" out

tips: -p option treats command as an input pipe to another SoX command

### create clicktrack test mix:
cd '/Users/schwarz/Documents/projects/ABC DJ/data/unmixdb/test/clicktracks/refsongs'
../../../../../src-git/unmixing/create-mix-base/create-mix.py ../mixes/clickmix.wav clicktrack-120bpm+0.5s.txt clicktrack-110bpm+0.5s.txt clicktrack-135bpm+0.5s.txt

### test with clicktracks:
cd '/Users/schwarz/Documents/projects/ABC DJ/src-git/player proto'
../unmixing/create-mix-base/create-mix.py clickmix.wav clicktrack-120bpm+0.5s.txt clicktrack-110bpm+0.5s.txt clicktrack-135bpm+0.5s.txt

### test with excerpts:

cd /Users/schwarz/src/test/audiofiles

cueinstart1=0.1
cueinend1=0.3
cueinlen1=`echo $cueinend1 - $cueinstart1 | bc -l`
cueoutstart1=0.5
cueoutend1=0.7
cueoutlen1=`echo $cueoutend1 - $cueoutstart1 | bc -l`
rawlen1=`echo $cueoutstart1 - $cueinstart1 | bc -l`
fadeoutstop1=`echo $cueoutend1 - $cueinstart1 | bc -l`

cueinstart2=0.1
cueinend2=0.3
cueinlen2=`echo $cueinend2 - $cueinstart2 | bc -l`
cueoutstart2=0.5
cueoutend2=0.7
cueoutlen2=`echo $cueoutend2 - $cueoutstart2 | bc -l`
rawlen2=`echo $cueoutstart2 - $cueinstart2 | bc -l`
fadeoutstop2=`echo $cueoutend2 - $cueinstart2 | bc -l`

in1=sweep-saw.wav
in2=sound-then-zeros.aif
out=out.wav

sox $in1 out1.wav trim $cueinstart1 fade t $cueinlen1 $fadeoutstop1 $cueoutlen1
sox $in2 out2.wav trim $cueinstart2 fade t $cueinlen2 $fadeoutstop2 $cueoutlen2
sox $in2 out2pad.wav trim $cueinstart2 fade t $cueinlen2 $fadeoutstop2 $cueoutlen2 speed 1 pad $rawlen1
sox -m "|sox $in1 -p trim $cueinstart1 fade t $cueinlen1 $fadeoutstop1 $cueoutlen1" \
       "|sox $in2 -p trim $cueinstart2 fade t $cueinlen2 $fadeoutstop2 $cueoutlen2 speed 1 pad $rawlen1" $out
"""

import os
import sys
import argparse

def read_table_as_dict(filename):
    
    scalarify = True    # if num. data lines == 1, use values directly as scalars
    dict = {}
    table = []
    with open(filename, 'r') as f:
        count = 0
        for line in f:
            if count < 1:
                # header defines keys
                keys = line.split()
                for i in range(0,len(keys)): table.append([])
            else:
                # data line
                values = line.split()
                for i in range(0, len(values)): # append to individual arrays
                    # todo: handle quoted strings, check #values with #keys
                    try:
                        v = float(values[i])
                    except:
                        v = values[i]
                    table[i].append(v)

            count += 1

    # convert table to dict
    for i in range(0, len(keys)):
        dict[keys[i]] = table[i] if scalarify and len(table[i]) > 1 else table[i][0]

    return dict

# map options to sox args
def timescale(sel, speed):
    
    timescale = {
        'none': '', # reset ground truth speed to 1 when no time scaling is used
        'resample': 'speed %.17f',
        'stretch':  'tempo -m %.17f', # sox tempo effect using WSOLA
        'supervp':  'TODO'
        }

    if sel == 'none':
        speed = 1

    try:
        sc = (timescale[sel] % speed);
    except:
        sc = ''  # don't care about missing %
            
    return (speed, sc)

def effect(sel):
    effect = {
        'none': '',
        'bass': 'bass +6 gain -l -3',   # 6dB low-shelving biquad filter below 100Hz
        'compressor': 'compand 0.3,1 6:-70,-60,-20 -5 -90 0.2', # 3:1 soft-knee compressor above -60 dB, 0.2 lookahead, -5 makeup gain
        'distortion': 'overdrive'
    }
    return effect[sel]

#
# main
#

parser = argparse.ArgumentParser()
parser.add_argument("timescale",  nargs = '?', default = 'resample')
parser.add_argument("effect",     nargs = '?', default = 'none')
parser.add_argument("mixname",    nargs = 1)
parser.add_argument("filenames",  nargs = '+')
args = parser.parse_args()

outfilename = args.mixname[0];
outlabelname = os.path.splitext(outfilename)[0] + '.labels.txt'
infilenames = args.filenames;

count = 1
offset = 0
command = 'sox -m '
tracks = [] # mix events: list of tuples (count, offset, [ array of tuples (start, dur, event)])

for infile in infilenames:

    # read txt file with cue info:
    # filename bpm cueinstart cueinend cutpoint joinpoint cueoutstart cueoutend duration
    cues = read_table_as_dict(infile)

    # collect mix and cue data
    if count == 1:
        # first file: start without fade in / cut at middle if option is set
        cueinstart = cues["cueinstart"]
        bpm = cues["bpm"]   # take bpm from first track
        tracks.append((count, offset, 1, [(0, 0, 'bpm', bpm)]))    # add first marker with global bpm 
        prefix = ''
    else:
        prefix = '       '

    cueinstart  = cues["cueinstart"]
    cueinlen    = cues["cueinend"]    - cues["cueinstart"]
    cueoutlen   = cues["cueoutend"]   - cues["cueoutstart"]
    rawlen      = cues["cueoutstart"] - cues["cueinstart"]
    fadeoutstop = cues["cueoutend"]   - cues["cueinstart"]
    speed       = bpm / cues['bpm']     # warp to first file's speed

    # generate sox input command to mix
    (speed, ts) = timescale(args.timescale, speed)
    fx = effect(args.effect)
    soxspec = 'sox %s -r 44.1k %s trim %.17f fade t %.17f %.17f %.17f '+ts+' '+fx+' pad %.17f'
    command += (prefix + '"|' + soxspec + '"\\\n') % (cues["filename"], '-p', cueinstart, cueinlen, fadeoutstop, cueoutlen, offset)

    # debug: write faded input track
    # os.system(soxspec % (cues["filename"], cues["filename"] + '.fade.wav', cueinstart, cueinlen, fadeoutstop, cueoutlen, speed, offset))

    # store mix ground truth for labels file:
    tracks.append((count, offset, speed, 
                  [(-cueinstart,                   0,         'start', cues['filename']),
                   (-cueinstart,                   0,         'speed', speed),
                   (0,                             cueinlen,  'fadein'),
                   (cues['cutpoint'] - cueinstart, 0,         'cutpoint'),
                   (fadeoutstop - cueoutlen,       cueoutlen, 'fadeout'),
                   (cues['duration'] - cueinstart, 0,         'stop', cues['filename'])
                  ]))

    offset += rawlen / speed  # advance through mix
    count  += 1

# end for all files

# prepare labels
labels = []
for tr in tracks:
    (track, offset, speed, events) = tr
    for ev in events:
        labels.append((offset + ev[0] / speed, offset + (ev[0] + ev[1]) / speed, track, ev[2], ev[3] if len(ev) > 3 else ''))

# sort by time
labels.sort(key = lambda ev: ev[0])

# write mix ground truth to labels file:
with open(outlabelname, "w") as labelfile:
    for lab in labels:
        # <starttime> <endtime> <track> <command> [<param>]
        labelfile.write('%.17f\t%.17f\t%d\t%s\t%s\n' % lab)

# generate sox command to mix
command += " '%s'" % outfilename
print(command)
os.system(command)
