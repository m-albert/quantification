from dependencies import *

b = brain.Brain('/home/malbert/mnt/peri/People/Shinya/Imaging_raw/2014/20140623_MG_secA5_WT_3dpf/'
          '20140623_MG_secA5_WT_3dpf_LSM780_2014_06_23__14_29_58.lsm')
b.classifiers = ['/data/malbert/quantification/20140623_MG_secA5_WT_3dpf_LSM780_2014_06_23__14_29_58_scale030310_channel0.h5',
                 '/data/malbert/quantification/20140623_MG_secA5_WT_3dpf_LSM780_2014_06_23__14_29_58_scale030310_channel1.h5']

brain.initialize(b)
brain.segment(b)
#objects.extractObjects(b,threshold=0.5,channel=0)
objects.extractObjects(b,threshold=0.8,channel=1,sizeThreshold=40)
#objects.trackObjects(b,channel=0,minTrackLength=5,maxObjectDisplacementPerDimension=10)
objects.trackObjects(b,channel=1,minTrackLength=5,maxObjectDisplacementPerDimension=10)
objects.draw(b,1,proj=0)
#objects.draw(b,1,b.objectSnaps[1])
#objects.show(b.segmentation[1])

micros = misc.applyFunctionToAll(b.tracks[1],microglia.getSkeleton)