#!/bin/sh

IFS=$'\n' # prevent word splitting on spaces
ircambeat=/Users/schwarz/src/ircamsummary/build/bin/ircambeat
tmp=/tmp/analyse-$$.wav

for file in $*; do
  out="${file%.*}"
  mpg123 -w $tmp "$file"  &&  $ircambeat -c --meter 22 -i $tmp -o "$out".beat.xml
  rm $tmp
done
