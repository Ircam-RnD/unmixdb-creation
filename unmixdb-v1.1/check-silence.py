import soundfile
import librosa
import numpy as np
import matplotlib.pyplot as plt

def find_runs (cond):
    _, i, c = np.unique(np.r_[[0], cond[:-1] != cond[1:]].cumsum(),
                    return_index = 1,                   
                    return_counts = 1)

    for index, count in zip(i, c):
        if cond[index]:
            yield index, count

# returns:  
# array rfiles ['filename', 'sr', 'samples']: all files
# array res    ['filename', 'start', 'length', 'duration']: all silent chunks
# prefix will be removed from file names

def rfiles, res = find_silence (mp3list, thresh, prefix = '', winsize = 4096, hopsize = 4096, plot = False):

    # to clean up file prefix
    pre = re.compile(prefix)

    res    = [ ]
    rfiles = [ ]
    
    for i, mp3name in enumerate(mp3list):
        y, sr = soundfile.read(mp3name)
        basepath = pre.sub('', mp3name) # path with prefix removed

        # to mono
        y = np.sum(y, axis=1)

        rfiles.append([basepath, sr, len(y)])

        # Extract RMS, convert to dB (clip at -120dB)
        rms = np.squeeze(20 * np.log10(librosa.feature.rms(y=y, frame_length=winsize, hop_length=hopsize) + 1e-6))
        #print(rms.shape, min(rms), max(rms))
        if plot:
            plt.subplot(m, n, i + 1)
            plt.plot(np.squeeze(rms))
            plt.title(f'{i} ' + os.path.basename(mp3name))
    
        # find chunks <-70dB
        for start, count in find_runs(rms < thresh):
            sstart = start * hopsize
            sdur   = (count - 1) * hopsize + winsize
            tstart = sstart / sr
            tdur   = sdur / sr
        
            # append to result matrix 
            res.append([ basepath, sstart, sdur, tdur ])
        
            if tdur > 1:
                print(f'{i:3} start {tstart: >5.1f} duration {tdur: >5.1f}  {basepath}')
                if plot:
                    plt.axvspan(start, start + count, facecolor=(1, 0.1, 0.2, 0.7))

    return rfiles, res
