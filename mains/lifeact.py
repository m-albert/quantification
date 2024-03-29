__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

# filePath = prefix+'/data/malbert/data/dbspim/osmo/20151220_p2y12_45dpf_15s_3cells_Subset.czi'
filePath = prefix+'/data/malbert/data/dbspim/20160302_lifeact/20160302_3dpf_pu1_lifeact_15s_3_Subset.czi'
import zeissFusion as zf
# info = zf.getStackInfoFromCZI(filePath)
# spacing = info['spacing']
spacing = n.array([ 0.22845754,  0.22845754,  0.46888381])
greenOffset = n.array([0.5,1,0])*spacing

times = range(200)

bs = []

b = brain.Brain(filePath,
                dimc=2,
                times=times,
                baseDataDir=prefix+'/data/malbert/quantification',
                subDir = '20160302_lifeact',
                fileNameFormat='f%06d.h5',
                # spacing = n.array([info['spacing'][2]]*3),
                spacing = spacing,
                # spacing = n.array([0.6,0.6,0.4]),
                origin = n.zeros(3)
                )

descriptors.RawChannel(b,0,nickname='lact',hierarchy='lact',redo=False,
                       compression='jls',compressionOption=2)
descriptors.RawChannel(b,1,nickname='pu1',hierarchy='pu1',redo=False,
                       compression='jls',compressionOption=2)

registration.Transformation(b,b.lact,None,'lact_corr',redo=False,
                            offset=greenOffset,
                            compression='jls',compressionOption=2)

prediction.FilterSegmentation(b,b.pu1,'seg',threshold=-10,redo=False)
descriptors.IndependentChannel(b,b.seg,'objects',objects.Objects,redo=False)

descriptors.UnstructuredData(b,b.objects,'tracks_%s' %len(b.times),objects.Tracks,
                            minTrackLength = 20,
                             maxObjectDisplacementPerDimension=10,
                             redo=False)

# res = []
# res2 = []
# for time in times:
#     s=ar(b.seg[time])
#     pu1 = ar(b.pu1[time])
#     gcamp = ar(b.lact[time])
#     g = s*gcamp.astype(n.float)/(pu1+(pu1==0))
#     res.append(n.max(g,0))
#     res2.append(n.max(gcamp,0))


# track = 32
track = 23
seg = b.tracks_200['seg//%s' %track]
pu1 = b.tracks_200['pu1//%s' %track]
lact = b.tracks_200['lact_corr//%s' %track]
res3 = lact*seg/(pu1*seg+(seg==0).astype(n.float))



# res3 = pu1*seg/(lact*seg+(seg==0).astype(n.float))