# unmixdb-creation
Python and shell scripts to generate UnmixDB, a dataset for MIR on DJ mixes, published at https://zenodo.org/record/1422385

Dataset Name:	UnmixDB: A Dataset for DJ-Mix Information Retrieval

Version:	1
Date:		20-09-2018
Description:	A collection of automatically generated DJ mixes with ground truth, based on creative-commons-licensed freely available and redistributable electronic dance tracks.
Authors:	Diemo Schwarz, Dominique Fourer
Contact email:	schwarz@ircam.fr

Publication: Please cite as [https://zenodo.org/records/1422385/files/schwarz-fourer-ismir2018late-breaking-unmixdb.pdf]([Diemo Schwarz, Dominique Fourer, UnmixDB: A Dataset for DJ-Mix Information Retrieval, ISMIR late-breaking session, Paris, 2018])

Reuse of data:	The dataset has been created from a subset of Creative-Commons licensed tracks and mixes of the mixotic mix collection, based on the curational work described in [Reinhard Sonnleitner, Andreas Arzt, and Gerhard Widmer. Landmark-based audio fingerprinting for DJ mix monitoring. In Proceedings of the International Symposium on Music Information Retrieval (ISMIR), New York, NY, 2016]


# VERSION HISTORY
20-09-2018	v1	first publication

# DOCUMENTATION

In order to evaluate the DJ mix analysis and reverse engineering methods described above, we created a dataset of excerpts of open licensed dance tracks and automatically generated mixes based on these.

We use track excerpts because of the runtime and memory requirements, especially for the DTW, which is of quadratic memory complexity. We could not have scaled the dataset up to the many playlists and variants when using full tracks.

Each excerpt contains about 20s of the beginning and 20s of the end of the source track. However, the exact choice is made taking into account the metric structure of the track. The cue-in region, where the fade-in will happen, is placed on the second beat marker starting a new measure (as analysed by the IrcamBeat), and lasts for 4 measures.  The cue-out region ends with the 2nd to last measure marker. We assure at least 20s for the beginning and end parts by extending them accordingly. The cut points where they are spliced together is again placed on the start of a measure, such that no artefacts due to beat discontinuity are introduced.

Each mix is based on a playlist that mixes 3 track excerpts beat-synchronously, such that the middle track is embedded in a realistic context of beat-aligned linear cross fading to the other tracks.
The first track's BPM is used as the seed tempo onto which the other tracks are adapted.

Each playlist of 3 tracks is mixed 12 times with combinations of 4 variants of effects and 3 variants of time scaling using the treatments of the sox open source command-line program [http://sox.sourceforge.net].

The UnmixDB dataset contains the ground truth for the source tracks and mixes in ASCII label format with tab-separated columns starttime, endtime, label.
For each mix, the start, end, and cue points of the constituent tracks are given, along with their BPM  and speed factors.
Additionally, the song excerpts are accompanied by their cue region and tempo information.

This figure shows the data flow and file types of the UnmixDB dataset used by the python scripts in this repository:

![The data flow and file types of the UnmixDB dataset](./unmixdb-creation.png)

Our DJ mix dataset is based on the curatorial work of Sonnleitner et. al. 2016, who collected Creative-Commons licensed source tracks of 10 free dance music mixes from Mixotic. We used their collected tracks to produce our track excerpts, but regenerated artificial mixes with perfectly accurate ground truth.
