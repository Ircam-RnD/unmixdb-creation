#!/usr/bin/python
#
# makemixes n outbase <sourcefile cue txt>...
#
# create all subsequences of n mixes out of list of sourcefiles
# named outbase-i.mp3
#
# run as:
# cd data/unmixdb/excerpts/set123/refsongs
# ../../../../unmixing/create-mix-base/makemixes.py 3 ../mixes/set123mix3 *.txt

import os
import sys
from math import *

scriptdir = os.path.dirname(__file__)
mix = '"%s/create-mix.py"' % scriptdir # needs to be in same dir

mixlen = int(sys.argv[1])
outbase = sys.argv[2]
sourcefiles = sys.argv[3:]
numfiles = len(sourcefiles)

# generate all subsequences of length n with wraparound
seq = []
for i in range(0, numfiles):
    seq.append(map(lambda x: x % numfiles, range(i, i+mixlen)))

variants = [('none', 'none'), ('none', 'bass'), ('none', 'compressor'), ('none', 'distortion'),
            ('resample', 'none'), ('resample', 'bass'), ('resample', 'compressor'), ('resample', 'distortion'),
            ('stretch', 'none'), ('stretch', 'bass'), ('stretch', 'compressor'), ('stretch', 'distortion')]

print('------- mixing %d files into %d sequences of length %d in %d variants (tatal: %d)\n' % (numfiles, len(seq), mixlen, len(variants), len(seq) * len(variants)))
#print(seq)

# call create-mix on all subsequences
for ind in range(0, len(seq)):
    for var in variants:
        mixname = '%s-%s-%s-%02d.mp3' % (outbase, var[0], var[1], ind)
        cmd = ' '.join([mix, var[0], var[1], mixname] + [sourcefiles[s] for s in seq[ind]])
        print(cmd)
        os.system(cmd)
