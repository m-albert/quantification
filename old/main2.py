from dependencies import *

b = brain.Brain('/home/malbert/mnt/peri/People/Shinya/Imaging_raw/2014/20140623_MG_secA5_WT_3dpf/'
          '20140623_MG_secA5_WT_3dpf_LSM780_2014_06_23__14_29_58.lsm',scaleFactors=[1.,1,1])
b.classifiers = ['/data/malbert/quantification/20140623_MG_secA5_WT_3dpf_LSM780_2014_06_23__14_29_58_scale030310_channel0.h5',
                 '/data/malbert/quantification/20140623_MG_secA5_WT_3dpf_LSM780_2014_06_23__14_29_58_scale101010_channel1.h5']

brain.loadData(b)
brain.initialize(b)

#
brain.segment(b)
objects.extractObjects(b,threshold=0.5,channel=1,sizeThreshold=200)
objects.trackObjects(b,channel=1,minTrackLength=3,maxObjectDisplacementPerDimension=30)
objects.draw(b,1,proj=0)

micros = misc.applyFunctionToAll(b.tracks[1],microglia.getSkeleton)