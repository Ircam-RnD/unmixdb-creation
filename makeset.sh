#!/bin/sh -x
#
# create a whole set in current dir: excerpts and mixes
#
# cd setdir
# makeset.sh fulltrackdir setname n

IFS=$'\n' # prevent word splitting on spaces
fulltrackdir=$1
setname=$2
n=$3
bin=`dirname "$0"`

mkdir mixes
mkdir refsongs
cd refsongs

$bin/create-excerpt.py "$fulltrackdir"/*.mp3 "$fulltrackdir"/*/*.mp3 "$fulltrackdir"/*/*/*.mp3

$bin/makemixes.py $n ../mixes/${setname}mix${n} *.txt
