#!pythonw

# check for long silent parts in tracks
import glob
import pandas as pd
from check_silence import find_runs, find_silence

# CONFIG:
# set this to where your unmixdb has been downloaded
unmixdbdir = '../../unmixdb/'

# main loop over mix dirs
setdirs = glob.glob(unmixdbdir + 'mixotic-set*-excerpts')
print(f'Starting to analyse {len(setdirs)} setdirs: {setdirs}')

# output dataframes
files  = pd.DataFrame([], columns = ['trackname', 'sr', 'samples'])
chunks = pd.DataFrame([], columns = ['trackname', 'start', 'length', 'duration'])

for sdir in setdirs:
    mixdir  = sdir + '/refsongs/'
    mp3list = glob.glob(mixdir + '*.mp3')
    print(f'----- checking {len(mp3list)} tracks in {mixdir}')

    # get matrix of all files rfi, all silent chunks res
    rfi, res = find_silence(mp3list, -70, prefix = unmixdbdir)
    
    # convert to dataframes: 
    # file with trackname, sr, duration in samples 
    newf      = pd.DataFrame(rfi, columns = ['trackname', 'sr', 'samples'])
    newchunks = pd.DataFrame(res, columns = ['trackname', 'start', 'length', 'duration'])

    # append and save
    files  = pd.concat([files,  newf],      ignore_index=True)
    chunks = pd.concat([chunks, newchunks], ignore_index=True)

    # write after each setdir, just in case...
    files.to_csv  (path_or_buf='alltracks.csv', sep='\t')
    chunks.to_csv (path_or_buf='alltracksilencechunks.csv', sep='\t')
    files.to_json (path_or_buf='alltracks.json', orient='records')
    chunks.to_json(path_or_buf='alltracksilencechunks.json', orient='records')
