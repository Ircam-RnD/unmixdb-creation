# unmixdb-creation
Python and shell scripts to generate UnmixDB, a dataset for MIR on DJ mixes, published at https://zenodo.org/record/1422385

Dataset Name:	UnmixDB: A Dataset for DJ-Mix Information Retrieval

Version:	1
Date:		20-09-2018
Description:	A collection of automatically generated DJ mixes with ground truth, based on creative-commons-licensed freely available and redistributable electronic dance tracks.
Authors:	Diemo Schwarz, Dominique Fourer
Contact email:	schwarz@ircam.fr

Publication: Please cite as [[Diemo Schwarz, Dominique Fourer, UnmixDB: A Dataset for DJ-Mix Information Retrieval, ISMIR late-breaking session, Paris, 2018]](https://zenodo.org/records/1422385/files/schwarz-fourer-ismir2018late-breaking-unmixdb.pdf)

Reuse of data:	The dataset has been created from a subset of Creative-Commons licensed tracks and mixes of the mixotic mix collection, based on the curational work described in [Reinhard Sonnleitner, Andreas Arzt, and Gerhard Widmer. Landmark-based audio fingerprinting for DJ mix monitoring. In Proceedings of the International Symposium on Music Information Retrieval (ISMIR), New York, NY, 2016]


# VERSION HISTORY
20-09-2018	v1		first publication
26-10-2024	v1.1	correction: define subset of mixes without long silences

# DOCUMENTATION

See also the article [[Diemo Schwarz, Dominique Fourer, UnmixDB: A Dataset for DJ-Mix Information Retrieval, ISMIR late-breaking session, Paris, 2018]](https://zenodo.org/records/1422385/files/schwarz-fourer-ismir2018late-breaking-unmixdb.pdf).

In order to evaluate the DJ mix analysis and reverse engineering methods described above, we created a dataset of excerpts of open licensed dance tracks and automatically generated mixes based on these.

We use track excerpts because of the runtime and memory requirements, especially for the DTW, which is of quadratic memory complexity. We could not have scaled the dataset up to the many playlists and variants when using full tracks.

Each excerpt contains about 20s of the beginning and 20s of the end of the source track. However, the exact choice is made taking into account the metric structure of the track. The cue-in region, where the fade-in will happen, is placed on the second beat marker starting a new measure (as analysed by the IrcamBeat), and lasts for 4 measures.  The cue-out region ends with the 2nd to last measure marker. We assure at least 20s for the beginning and end parts by extending them accordingly. The cut points where they are spliced together is again placed on the start of a measure, such that no artefacts due to beat discontinuity are introduced.

Each mix is based on a playlist that mixes 3 track excerpts beat-synchronously, such that the middle track is embedded in a realistic context of beat-aligned linear cross fading to the other tracks.
The first track's BPM is used as the seed tempo onto which the other tracks are adapted.

Each playlist of 3 tracks is mixed 12 times with combinations of 4 variants of effects and 3 variants of time scaling using the treatments of the sox open source command-line program [http://sox.sourceforge.net].

The UnmixDB dataset contains the ground truth for the source tracks and mixes in the `.labels.txt` files. 
Additionally, the song excerpts are accompanied by their cue region and tempo information in the `.cue.txt` files (see below).

This figure shows the data flow and file types of the UnmixDB dataset used by the python scripts in this repository:

![The data flow and file types of the UnmixDB dataset](./unmixdb-creation.png)

# File Formats

The ground truth for the source tracks and mixes in the `.labels.txt` files are in ASCII label format (as used in the _Audacity_ audio editor) with tab-separated columns _starttime, endtime, track, label, parameters_.

Example:

```
-2.27415963589999981	-2.27415963589999981	1	start	"07_Sr_Click_-_Tibetan_-_Antiritmo024.excerpt40.mp3"
-2.27415963589999981	-2.27415963589999981	1	speed	1
 0.00000000000000000	 0.00000000000000000	1	bpm	127.937802416
 0.00000000000000000	 7.61034013609999960	1	fadein	
20.73541950110000087	20.73541950110000087	1	cutpoint	
28.73608979710000000	28.73608979710000000	2	start	"08_Banding_-_Eula_-_Antiritmo024.excerpt40.mp3"
28.73608979710000000	28.73608979710000000	2	speed	1.015
32.00870748290000023	38.99791383219999830	1	fadeout	
32.00870748290000023	39.39265306109999898	2	fadein	
41.50416235950000043	41.50416235950000043	1	stop	"07_Sr_Click_-_Tibetan_-_Antiritmo024.excerpt40.mp3"
52.31455782300000124	52.31455782300000124	2	cutpoint	
60.81445714400000213	60.81445714400000213	3	start	"01_Choenyi_-_PA_To_M_-_Antiritmo024.excerpt40.mp3"
60.81445714400000213	60.81445714400000213	3	speed	0.956
63.49496598630000221	70.87891156450000096	2	fadeout	
63.49496598630000221	70.52480725610000434	3	fadein	
73.69862947960000099	73.69862947960000099	2	stop	"08_Banding_-_Eula_-_Antiritmo024.excerpt40.mp3"
83.64988662120001095	83.64988662120001095	3	cutpoint	
94.89414965970000537	102.45224489779999999	3	fadeout	
104.62124172450000970	104.62124172450000970	3	stop	"01_Choenyi_-_PA_To_M_-_Antiritmo024.excerpt40.mp3"
```

Here, the start/end time is in seconds, the track column determines which of the source tracks are concerned, the label determines the type of information given, followed by an optional parameter column.
For each mix, the start, end, and cue points of the constituent tracks are given, along with their BPM  and speed factors.
The meanings of the labels and parameters are:

| Label   | Parameter		  | Definition |
|---------|-------------------|------------|
| start   | _filename_		  | (virtual) start time of track in mix	|
| speed   | _speed factor_	  | playback speed factor of the referenced track at that point in time	|
| bpm     | _beats per minute_ | source tempo of the track	|
| fadein  |					  | track fades in between start and end time	|
| fadeout |					  | track fades out between start and end time	|
| stop    | _filename_		  | end time of track in mix	|
| cutpoint |				  | marker where the track excerpts were spliced 	|

Additionally, the song excerpts are accompanied by their cue region and tempo information in the `.cue.txt` files with a tab-separated header line giving the names of the columns, and one row of tab-separated data.

Example:

```
filename	bpm	cueinstart	cueinend	cutpoint	joinpoint	cueoutstart	cueoutend	duration
"04_Vizar_-_Ghosts_-_Antiritmo018.excerpt40.mp3"	122.11588408	2.3786494318	9.7625950101	22.5451800441	309.381279817	33.8591029466	41.7248625838	43.7173696146
```

## Version unmixdb-v1.1

Version 1 of unmixdb has a few mixes that weren't generated correctly and contain missing tracks (silent parts of ~20s length).  Additionally, some tracks start or end with a few seconds of silence.  As this can perturb alignment and unmixing algorithms, unmixdb v1.1 defines a subset of _good_ mixes.
In directory `unmixdb-v1.1`, the text file `unmixdb-v1.1-goodmixes-silence-less-than-4s.csv` contains a list of mixes with not longer than 4s of silence (where RMS is < -70dB).

Creation:
1. The script `check-silence.py` analyses the RMS of all mixes and writes tables `files` and `chunks` (silent segments).
2. The script `goodmixes.py` filters out mixes with silence above a given threshold and writes `unmixdb-v1.1-goodmixes-silence-less-than-4s`.

# Acknowledgements

Our DJ mix dataset is based on the curatorial work of Sonnleitner et. al. 2016, who collected Creative-Commons licensed source tracks of 10 free dance music mixes from Mixotic. We used their collected tracks to produce our track excerpts, but regenerated artificial mixes with perfectly accurate ground truth.

This dataset was created within the [ABC_DJ project](https://abcdj.eu/) which has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 688122.
