
# join 2 dataframes to find *good* mixes without too long silence
import re
import numpy as np
import pandas as pd

v11dir = './'
unmixdbdir = '../../unmixdb/'
silencethresh = 4.0 # maximum allowed duration of silence in mix
trsilencethresh = 1.0 # maximum allowed duration of silence in track

def get_good (filecsv, chunkcsv, column, silencethres):

    files  = pd.read_csv(filecsv,  sep = '\t', index_col = 0)
    chunks = pd.read_csv(chunkcsv, sep = '\t', index_col = 0)
    badchunks = chunks.loc[chunks['duration'] > silencethresh]

    # left join to get all mixes on left, all silent chunks over threshold on right, keep only mixes without anything on right
    filterfiles = pd.merge(files, badchunks, how = 'left', on = column, indicator = 'check', left_index=False)

    # use indicator column from merge to select only columns for which no bad chunks existed (NULL in right half of join shows as NaN, is obfuscated by pandas)
    goodfiles = filterfiles.loc[filterfiles['check'] == 'left_only', column]

    return goodfiles, files, chunks


goodmixes,  mixes, mixchunks    = get_good(v11dir + 'allmixes.csv', v11dir + 'allmixsilencechunks.csv',    'mixname',   silencethresh)
goodtracks, tracks, trackchunks = get_good(v11dir + 'alltracks.csv', v11dir + 'alltracksilencechunks.csv', 'trackname', trsilencethresh)

# write list of good mixes and tracks to text files
goodmixes.to_csv(v11dir + f'unmixdb-v1.1-goodmixes-silence-less-than-{silencethresh:g}s.csv', columns = ['mixname'], header = False, index = False)
goodtracks.to_csv(v11dir + f'unmixdb-v1.1-goodtracks-silence-less-than-{silencethresh:g}s.csv', columns = ['trackname'], header = False, index = False)

print(f'num total mixes:  {len(mixes):4}, num good mixes  with less than {silencethresh}s of silence: {len(goodmixes):4}, num dropped mixes:  {len(mixes) - len(goodmixes):4}')
print(f'num total tracks: {len(tracks):4}, num good tracks with less than {silencethresh}s of silence: {len(goodtracks):4}, num dropped tracks: {len(tracks) - len(goodtracks):4}')
