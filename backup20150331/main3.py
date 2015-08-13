from dependencies import *

inFile = '/data/malbert/data/dbspim/20141214_gcamp_pu1_30s/20141214_gcamp_pu1_ot_30sec_Subset.czi'
outFile = inFile[:-4]+'_aligned_to80.h5'
outFileRed = inFile[:-4]+'_aligned_to80_red.h5'

b = brain.Brain('gcamp6s_pu1'
                ,scaleFactors=[1.,1,1])

b.classifiers = ['/data/malbert/quantification/gcamp6s_pu1_scaleFactors_1.0_1.0_1.0.h5']

b.spacing = array([2., 0.38711306,  0.38711306])

#b.data = n.array([filing.readH5(outFileRed,hierarchy='DS1')[:80,25:90,200:1000,40:1200]])
#b.data = n.log(b.data)*5000
#b.data = b.data.astype(n.uint16)

#b.dimc,b.dimt,b.dimx,b.dimy,b.dimz = b.data.shape

b.dimc,b.dimt,b.dimx,b.dimy,b.dimz = (1,80,800,1160,65)

brain.initialize(b)

# brain.segmentSequential(b,range(2,b.dimt,3))
brain.segment(b)

# b.segmentation =

objects.extractObjects(b,threshold=0.5,channel=0,sizeThreshold=500)
objects.trackObjects(b,channel=0,minTrackLength=3,maxObjectDisplacementPerDimension=30)

microglia.getSkeletons(b.objectSnaps)
misc.applyFunctionToAll(b.objectSnaps,microglia.getSkeletonNodes)

microglia.getSkeletons(b.tracks[0][:4],nDilations=0)
misc.applyFunctionToAll(b.tracks[0][:4],microglia.getSkeletonNodes)

# microglia.getSkeletons(b.tracks,nDilations=1)
# misc.applyFunctionToAll(b.tracks,microglia.getSkeletonNodes)

# objects.draw(b,0,proj=0)

#micros = misc.applyFunctionToAll(b.tracks[0],microglia.getSkeleton)