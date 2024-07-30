
# join 2 dataframes to find *good* mixes without too long silence
import glob
import re
import numpy as np
import pandas as pd
from tqdm import tqdm

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


# load all mix label files, scan "start" with track name, write dataframe with mixname, trackname, trackpos

def load_labels (mixname, prefix):

    # find label file name from mp3 mixname
    ext = re.compile('\.mp3$')
    labelfile = ext.sub('.labels.txt', mixname) 

    pre = re.compile(prefix)
    mixbase = pre.sub('', mixname)

    lab = pd.read_csv(labelfile, sep = '\t', index_col = None, header = None)
    trstart = lab.loc[lab[3] == 'start']    # keep only lines with 'start' command

    # rename 2 cols, remove others
    trstart = trstart.rename(columns={4: 'trackname', 2: 'trackpos'}).drop(columns = [0, 1, 3])
    trstart.insert(0, 'mixname', [ mixbase ] * len(trstart))
    return trstart


# problem: some labels have no mp3!!! labelfiles = glob.glob(unmixdbdir + 'mixotic-set*/mixes/*.labels.txt')
mixfiles = glob.glob(unmixdbdir + 'mixotic-set*/mixes/*.mp3')

mix_to_track = pd.DataFrame([ ], columns = ['mixname', 'trackpos', 'trackname'])

for mixname in tqdm(mixfiles):
    new = load_labels(mixname, unmixdbdir)
    mix_to_track = pd.concat([mix_to_track, new], ignore_index=True)

print(mix_to_track)

mix_to_track.to_csv  (path_or_buf='mixtotrack.csv', sep='\t')
mix_to_track.to_json (path_or_buf='mixtotrack.json', orient='records')

