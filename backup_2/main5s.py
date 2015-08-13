from dependencies import *

inFile = '/data/malbert/data/dbspim/20141109_35dpf_1_1mic_5s/20141109_35dpf_1_1mic_5s_Subset.czi'
#outFile = inFile[:-4]+'_aligned_to80.h5'
#outFileRed = inFile[:-4]+'_aligned_to80_red.h5'

b = brain.Brain('/data/malbert/data/dbspim/20141109_35dpf_1_1mic_5s/20141109_35dpf_1_1mic_5s_Subset.czi'
                ,scaleFactors=[1.,1,1])

b.classifiers = ['/data/malbert/quantification/20141109_35dpf_1_1mic_5s_Subset.czi_scaleFactors_1.0_1.0_1.0_channel0.h5']

b.spacing = n.array([ 0.19361037,  0.19361037,  0.5       ])[::-1]

brain.loadData(b)

b.dimt = 2

brain.initialize(b)

#brain.segmentSequential(b,range(0,b.dimt,3))
#brain.segmentSequential(b,range(1,b.dimt,3))
#brain.segmentSequential(b,range(2,b.dimt,3))
brain.segmentSequential(b,range(b.dimt))

objects.extractObjects(b,threshold=0.5,channel=0,sizeThreshold=500)
objects.trackObjects(b,channel=0,minTrackLength=1,maxObjectDisplacementPerDimension=30)

microglia.getSkeletons(b.tracks,nDilations=1)
misc.applyFunctionToAll(b.tracks,microglia.getSkeletonNodes)

# microglia.getSkeletons(b.tracks[0][:4],nDilations=0)
# misc.applyFunctionToAll(b.tracks[0][:4],microglia.getSkeletonNodes)

# microglia.getSkeletons(b.tracks,nDilations=1)
# misc.applyFunctionToAll(b.tracks,microglia.getSkeletonNodes)

# objects.draw(b,0,proj=0)

#micros = misc.applyFunctionToAll(b.tracks[0],microglia.getSkeleton)

