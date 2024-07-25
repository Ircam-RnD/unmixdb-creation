#!/python3

# check for long silent parts
import os
import glob
import soundfile
import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# CONFIG:
# set this to where your unmixdb has been downloaded
unmixdbdir = '../unmixdb/'
winsize = 4096
hopsize = 4096


def find_runs (cond):
    _, i, c = np.unique(np.r_[[0], cond[:-1] != cond[1:]].cumsum(),
                    return_index = 1,                   
                    return_counts = 1)

    for index, count in zip(i, c):
        if cond[index]:
            yield index, count

# main loop over mix dirs
setdirs = glob.glob(unmixdbdir + 'mixotic-set*-excerpts')

# output dataframes
files  = pd.DataFrame([], columns = ['mixname', 'sr', 'samples'])
chunks = pd.DataFrame([], columns = ['mixname', 'start', 'length', 'duration'])

for sdir in setdirs:
    mixdir = sdir + '/mixes/'
    mp3list = glob.glob(mixdir + '*.mp3')
    print(f'----- checking {len(mp3list)} mixes in {mixdir}')

    n = 3
    m = np.ceil(len(mp3list) / n)
    #print(len(mp3list), m, n)
    #plt.figure(figsize=(20, m * 1.5))
    #plt.tight_layout()

    # result matrix columns: 
    # silence framestartsamp, silence framenumsamps, silence in seconds
    res = [ ]
    rfi = [ ]
    
    for i, mp3name in enumerate(mp3list):
        y, sr = soundfile.read(mp3name)

        # to mono
        y = np.sum(y, axis=1)
        #print(y.shape)

        rfi.append([mp3name, sr, len(y)])

        # Extract RMS, convert to dB (clip at -120dB)
        rms = np.squeeze(20 * np.log10(librosa.feature.rms(y=y, frame_length=winsize, hop_length=hopsize) + 1e-6))
        #print(rms.shape, min(rms), max(rms))
        #plt.subplot(m, n, i + 1)
        #plt.plot(np.squeeze(rms))
        #plt.title(f'{i} ' + os.path.basename(mp3name))
    
        # find chunks <-70dB
        for start, count in find_runs(rms < -70):
            sstart = start * hopsize
            sdur   = (count - 1) * hopsize + winsize
            tstart = sstart / sr
            tdur   = sdur / sr
        
            # append to result matrix 
            res.append([ mp3name, sstart, sdur, tdur ])
        
            if tdur > 1:
                print(f'{i:3} start {tstart: >5.1f} duration {tdur: >5.1f}  {mp3name}')
                # plt.axvspan(start, start + count, facecolor=(1, 0.1, 0.2, 0.7))

    
    # convert to dataframes: 
    # file with mixname, sr, duration in samples 
    newf      = pd.DataFrame(rfi, columns = ['mixname', 'sr', 'samples'])
    newchunks = pd.DataFrame(res, columns = ['mixname', 'start', 'length', 'duration'])

    # append and save
    files  = pd.concat([files,  newf],      ignore_index=True)
    chunks = pd.concat([chunks, newchunks], ignore_index=True)
    
    files.to_csv(path_or_buf='files.csv', sep='\t')
    chunks.to_csv(path_or_buf='chunks.csv', sep='\t')
    files.to_json(path_or_buf='files.json', orient='records')
    chunks.to_json(path_or_buf='chunks.json', orient='records')
