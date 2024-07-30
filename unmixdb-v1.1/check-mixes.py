#!pythonw

# check for long silent parts in mixes
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
files  = pd.DataFrame([], columns = ['mixname', 'sr', 'samples'])
chunks = pd.DataFrame([], columns = ['mixname', 'start', 'length', 'duration'])

for sdir in setdirs:
    mixdir = sdir + '/mixes/'
    mp3list = glob.glob(mixdir + '*.mp3')
    print(f'----- checking {len(mp3list)} mixes in {mixdir}')

    # get matrix of all files rfi, all silent chunks res
    rfi, res = find_silence(mp3list, -70, prefix = unmixdbdir)
    
    # convert to dataframes: 
    # file with mixname, sr, duration in samples 
    newf      = pd.DataFrame(rfi, columns = ['mixname', 'sr', 'samples'])
    newchunks = pd.DataFrame(res, columns = ['mixname', 'start', 'length', 'duration'])

    # append and save
    files  = pd.concat([files,  newf],      ignore_index=True)
    chunks = pd.concat([chunks, newchunks], ignore_index=True)

    # write after each setdir, just in case...
    files.to_csv  (path_or_buf='allmixes.csv', sep='\t')
    chunks.to_csv (path_or_buf='allmixsilencechunks.csv', sep='\t')
    files.to_json (path_or_buf='allmixes.json', orient='records')
    chunks.to_json(path_or_buf='allmixsilencechunks.json', orient='records')
