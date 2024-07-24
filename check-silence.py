#!/python3

# check for long silent parts
import os
import glob
import soundfile
import librosa
import numpy as np
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

for sdir in setdirs:
    mixdir = sdir + '/mixes/'

    mp3list = glob.glob(mixdir + '*.mp3')

    n = 3
    m = np.ceil(len(mp3list) / n)
    print(len(mp3list), m, n)
    plt.figure(figsize=(20, m * 1.5))
    plt.tight_layout()

    for i, mp3name in enumerate(mp3list):
        y, sr = soundfile.read(mp3name)

        # to mono
        y = np.sum(y, axis=1)
        #print(y.shape)

        # Extract RMS, convert to dB (clip at -120dB)
        rms = np.squeeze(20 * np.log10(librosa.feature.rms(y=y, frame_length=winsize, hop_length=hopsize) + 1e-6))
        #print(rms.shape, min(rms), max(rms))
        plt.subplot(m, n, i + 1)
        plt.plot(np.squeeze(rms))
        plt.title(f'{i} ' + os.path.basename(mp3name))
    
        # find chunks <-70dB
        for start, count in find_runs(rms < -70):
            t   = start * hopsize / sr
            dur = ((count - 1) * hopsize + winsize)/ sr
            if dur > 1:
                print(f'{i:3} start {t: >5.1f} duration {dur: >5.1f}  {mp3name}')
                plt.axvspan(start, start + count, facecolor=(1, 0.1, 0.2, 0.7))
        
