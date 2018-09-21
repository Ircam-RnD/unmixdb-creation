#!/usr/bin/python
# arg: sound files...
# writes excerpts and cue files to current dir
# (before: run ircambeat, write file.beat.xml with analyse-all.sh)
# loads file.beat.xml
# trims file to ./file.excerpt40.mp3
# writes cut and cue to ./file.excerpt40.txt

import os
import sys
import xml.etree.ElementTree as et

# load ircambeat markers with namespace/format version ns
# @return beat markers array, measure markers array, bpm

def loadbeats(file, ns):

    e = et.parse(file)
    # et.dump(e)

    # parse segments, store highest (most detailed) level
    beats   = []
    measure = []
    for s in e.findall('{%s}segment' % ns):
        time = float(s.get('time'))
        beats.append(time)

        f = s.find('{%s}beattype' % ns)
        m = int(f.get('measure'))
        if m:   # append measure-starting beat marker to list
            measure.append(time)
    
    # get global info: bpm, duration
    g = e.find('{%s}global' %ns)
    duration = float(g.get('length'))
    tempo = g.find('{%s}tempo' %ns)
    bpm = float(tempo.get('bpm'))

    return beats, measure, bpm, duration

#
# main
#

for infile in sys.argv[1:]:
    stem     = os.path.splitext(infile)[0]  # includes path!
    xmlfile  = stem    + '.beat.xml'

    # out files without path, writes to current dir
    outbase  = os.path.basename(stem) + '.excerpt40'
    outfile  = outbase + '.mp3'
    txtfile  = outbase + '.txt'

    try:
        ns = "http://www.ircam.fr/musicdescription/1.4"
        beats, measures, bpm, duration = loadbeats(xmlfile, ns)

        # find second measure marker (tracks often start with silence, but beats are already marked), 
        # cut ~20s after first,
        cueinstart  = measures[1]
        cueinend    = measures[5]
        cutstart    = next(i for i in measures if i >= max(cueinstart + 20, cueinend + 10)) # cut beginning here

        # 5th last, cut in 20s before last
        cueoutstart = measures[-6]
        cueoutend   = measures[-2]
        cutend      = next(i for i in reversed(measures) if i <= min([cueoutstart - 10, duration - 20])) # cut end part here
        cutlen      = cutend - cutstart

        print(cueinstart, cueinend, cutstart, cutend, cueoutstart, cueoutend, "\n")

        # cut cutstart to cutend
        cutcmd  = "sox '%s' -r 44.1k '%s' trim 0 %f %f" % (infile, outfile, cutstart, cutend - cutstart)
        sys.stderr.write(cutcmd + "\n")
        os.system(cutcmd)

        # write info of excerpt in table format with header
        with open(txtfile, "w") as txt:
            header = ["filename", "bpm", "cueinstart", "cueinend", "cutpoint",
                          "joinpoint", "cueoutstart", "cueoutend", "duration"]
            data   = ['"'+os.path.basename(outfile)+'"', bpm, cueinstart, cueinend, cutstart,
                          cutend, cueoutstart - cutlen, cueoutend - cutlen, duration - cutlen]
            txt.write("\t".join(header) + "\n")
            txt.write("\t".join(str(x) for x in data) + "\n")

    except:
        sys.stderr.write("file not found: %s\n" % xmlfile)
