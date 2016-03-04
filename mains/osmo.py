__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

filePath = prefix+'/data/malbert/data/dbspim/osmo/20151220_p2y12_45dpf_15s_3cells_Subset.czi'
import zeissFusion as zf
info = zf.getStackInfoFromCZI(filePath)

bs = []

b = brain.Brain(filePath,
                dimc=1,
                times=range(140),
                baseDataDir=prefix+'/data/malbert/quantification',
                subDir = 'osmo2',
                fileNameFormat='f%06d.h5',
                spacing = n.array([info['spacing'][2]]*3),
                # spacing = n.array([0.6,0.6,0.4]),
                origin = n.zeros(3)
                )

descriptors.RawChannel(b,0,nickname='p2y12',hierarchy='p2y12',originalSpacing=info['spacing'],redo=False,
                       compression='jls',compressionOption=2)
descriptors.IndependentChannel(b,b.p2y12,'deconv',descriptors.FromFile,
                               # filePattern='/data/malbert/data/dbspim/20151105_p2y12/deconv/20151105_p2y12_45dpf_zoom25_fastasposs_2_1_%(time)s%(wildcard)s.tif',
                               filePattern='/home/malbert/mnt/hrm/malbert/huygens_dst/20151220/20151220_p2y12_45dpf_15s_%(time)04d_%(wildcard)s_hrm.tif',
                               fileSpacing=info['spacing'],
                               compression='jls',
                               compressionOption=2,
                               redo=False)

descriptors.IndependentChannel(b,b.deconv,'seg',segmentation.ActiveContourSegmentation,
                               minSize = 500,
                               redo=False)

descriptors.UnstructuredData(b,b.seg,'tracks_%s' %len(b.times),objects.Tracks,
                             maxObjectDisplacementPerDimension=10,
                             redo=False)
# prediction.FilterSegmentation(b,b.p2y12,'seg_orig',threshold = -1, redo=True)
# o = prediction.segmentFromFilter(ar(b.seg_orig[0]))
# prediction.Prediction(b,b.p2y12,'ilastik', redo=False)

# sig = ar(b.p2y12[0])
# sig = sitk.gifa(sig)
# d=sitk.SignedMaurerDistanceMap(sitk.gifa(o)>0)
# da = sitk.gafi(d)
# # m=ndimage.minimum_filter(sitk.gafi(d),size=(20,100,100))
# # minima = (m==da)*(m<-5)
# # markers,N = ndimage.label(minima)
# markers = n.zeros(da.shape,dtype=n.uint16)
# markers = sitk.gifa(markers)
# markers[300,680,47] = 2
# markers[0,0,0] = 1
# w=sitk.MorphologicalWatershedFromMarkers(-d,sitk.Cast(markers,3))
#
#
# e=o[47,550:-1,150:400]>0
# markers = n.zeros(e.shape)
# markers[110,150] = 2
# markers[0,0] = 1
# d=ndimage.morphology.distance_transform_edt(n.invert(e))
# w = watershed(d,markers)

from skimage.morphology import watershed
from skimage import feature

# sig = b.p2y12[0][40:55,550:-1,150:400]
# sig = sig.astype(n.int64)
# e=o[40:55,550:-1,150:400]>0
# d=ndimage.morphology.distance_transform_edt(n.invert(e))
#
#
# sigm = ndimage.gaussian_filter(sig.astype(n.float),(0.5,1,1))
# markermask = feature.peak_local_max(-sigm+sigm.max(),exclude_border=True,indices=False,
#                                     min_distance=1,footprint=n.ones((5,40,40)))
# markers,N = ndimage.label(markermask)
# w = watershed(sigm,markers)
