#!/usr/bin/python
#
# makemixes n outpath/outbase <sourcefile cue txt in current dir>...
#
# create all subsequences of n mixes out of list of sourcefiles (in current dir)
# named outbase-i.mp3
#
# for example, run as:
# cd data/unmixdb/excerpts/set123/refsongs
# .../unmixdb-creation/makemixes.py 3 ../mixes/set123mix3 *.txt

import os
import sys
from math import *

scriptdir = os.path.dirname(__file__)
mixcmd = '"%s/create-mix.py"' % scriptdir # needs to be in same dir

mixlen = int(sys.argv[1])
outbase = sys.argv[2]
sourcefiles = sys.argv[3:]
numfiles = len(sourcefiles)

# generate all subsequences of length n with wraparound
seq = []
for i in range(0, numfiles):
    seq.append(map(lambda x: x % numfiles, range(i, i+mixlen)))

# list of pairs of time scale method, effect
variants = [('none', 'none'), ('none', 'bass'), ('none', 'compressor'), ('none', 'distortion'),
            ('resample', 'none'), ('resample', 'bass'), ('resample', 'compressor'), ('resample', 'distortion'),
            ('stretch', 'none'), ('stretch', 'bass'), ('stretch', 'compressor'), ('stretch', 'distortion')]

print('------- mixing %d files into %d sequences of length %d in %d variants (tatal: %d)\n' % (numfiles, len(seq), mixlen, len(variants), len(seq) * len(variants)))
#print(seq)

# call create-mix on all subsequences
for ind in range(0, len(seq)):
    for var in variants:
        ts = var[0]
        fx = var[1]
        mixname = '%s-%s-%s-%02d.mp3' % (outbase, ts, fx, ind)
        cmd = ' '.join([mixcmd, ts, fx, mixname] + [(("'%s'") % sourcefiles[s]) for s in seq[ind]])
        print(cmd)
        os.system(cmd) # call create-mix.py
