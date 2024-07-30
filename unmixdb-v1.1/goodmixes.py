
# join 2 dataframes to find *good* mixes without too long silence
import re
import numpy as np
import pandas as pd

v11dir = './'
unmixdbdir = '../unmixdb/'
silencethresh = 4.0

files  = pd.read_csv(v11dir + 'files.csv',  sep = '\t', index_col = 0)
chunks = pd.read_csv(v11dir + 'chunks.csv', sep = '\t', index_col = 0)
badchunks = chunks.loc[chunks['duration'] > silencethresh]

# left join to get all mixes on left, all silent chunks over threshold on right, keep only mixes without anything on right
filterfiles = pd.merge(files, badchunks, how = 'left', on = 'mixname', indicator = 'check', left_index=False)

# use indicator column from merge to select only columns for which no bad chunks existed (NULL in right half of join shows as NaN, is obfuscated by pandas)
goodfiles = filterfiles.loc[filterfiles['check'] == 'left_only', 'mixname']

# clean up file prefix
pre = re.compile(unmixdbdir)
basefiles = goodfiles.apply(lambda x: pre.sub('', x))

# write list of good mixes to text file
basefiles.to_csv(v11dir + f'unmixdb-v1.1-goodmixes-silence-less-than-{silencethresh:g}s.csv', columns = ['mixname'], header = False, index = False)

print(f'num total mixes: {len(files)}, num good mixes with less than {silencethresh}s of silence: {len(basefiles)}, num dropped mixes: {len(files) - len(basefiles)}')
