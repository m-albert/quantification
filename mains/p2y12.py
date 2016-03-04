__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

b = brain.Brain(prefix+'/data/malbert/data/dbspim/20150502_45dpf_p2y12_fast_Subset.czi',
                dimc=1,
                # times=range(0,1),
                times=range(100),
                baseDataDir=prefix+'/data/malbert/quantification',
                subDir = 'p2y12_20150502',
                fileNameFormat='f%06d.h5',
                )

descriptors.RawChannel(b,0,nickname='p2y12',hierarchy='p2y12',redo=False,
                       compression='jls',compressionOption=2)

prediction.FilterSegmentation(b,b.p2y12,'seg_orig',redo=False)

registration.RegistrationParameters(b,b.p2y12,'intrareg',mode='intra')
registration.Transformation(b,b.p2y12,b.intrareg,'intraaligned',redo=False)

# prediction.FilterSegmentation(b,b.interaligned,'seg',redo=False)
registration.Transformation(b,b.seg_orig,b.intrareg,'ms',
                            interpolation=sitk.sitkNearestNeighbor,
                            # mask=mask,
                            compression='jls',
                            compressionOption=0,
                            redo=False)


# descriptors.IndependentChannel(b,b.seg_orig,'robjects',objects.Objects,redo=False)
# descriptors.UnstructuredData(b,b.robjects,'rtracks_%s' %len(b.times),objects.Tracks,redo=False)
# #
# descriptors.IndependentChannel(b,b.robjects,'rskeletons_3',objects.Skeletons,nDilations=3,redo=False)


descriptors.IndependentChannel(b,b.seg_orig,'objects',objects.Objects,redo=False)
descriptors.UnstructuredData(b,b.objects,'tracks_%s' %len(b.times),objects.Tracks,redo=False)
#
# descriptors.IndependentChannel(b,b.objects,'skeletons_3',objects.Skeletons,nDilations=3,redo=False)

# iobj=32
itrack=5
# o=[(b.p2y12[time][objects.bbox(b.objects[time]['bboxs'][iobj-1])]).astype(n.uint16) for time in range(10)]
#
# l=[(b.objects[time]['labels'][objects.bbox(b.objects[time]['bboxs'][iobj-1])]==iobj).astype(n.uint16) for time in range(10)]
# t=[(b.objects[time]['labels'][objects.bbox(b.objects[time]['bboxs'][iobj-1])]==iobj).astype(n.uint16) for time,obj in n.array(b.tracks_10['tracks'][str(itrack)])]

# t=[]
# for ittrack in range(len(b.tracks_100)):
#     time = b.tracks_100[str(ittrack)]
#     obj = b.tracks_100[str(ittrack)]
#     tmp = b.objects[time]['labels'][objects]
# t=[(b.objects[time]['labels'][objects.bbox(b.objects[b.tracks_100[itrack][ittime][0]]['bboxs'][b.tracks_100[itrack][ittime][1]])]==b.tracks_100[itrack][ittime][1]).astype(n.uint16) for ittime in range(10)]

# import segment_surface
#
# # q = n.array()
#
# q=(b.p2y12[time][objects.bbox(b.objects[time]['bboxs'][iobj-1])]==iobj).astype(n.uint16)