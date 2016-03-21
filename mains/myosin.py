__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

# filePath = prefix+'/data/malbert/data/dbspim/osmo/20151220_p2y12_45dpf_15s_3cells_Subset.czi'
filePath = prefix+'/data/malbert/data/dbspim/20160118_4dpf_myosin/20160118_myosin_pu1_4dpf_30s_2_Subset.czi'
import zeissFusion as zf
info = zf.getStackInfoFromCZI(filePath)
# spacing = n.array([])

times = range(120)
# times = range(1)

bs = []

b = brain.Brain(filePath,
                dimc=2,
                times=times,
                baseDataDir=prefix+'/data/malbert/quantification',
                subDir = '20160118_4dpf_myosin',
                fileNameFormat='f%06d.h5',
                # spacing = n.array([info['spacing'][2]]*3),
                spacing = info['spacing'],
                # spacing = n.array([0.6,0.6,0.4]),
                origin = n.zeros(3)
                )

descriptors.RawChannel(b,1,nickname='signal',hierarchy='signal',redo=False,
                       compression='jls',compressionOption=2)
descriptors.RawChannel(b,0,nickname='pu1',hierarchy='pu1',redo=False,
                       compression='jls',compressionOption=2)

prediction.FilterSegmentation(b,b.pu1,'seg',threshold=-10,redo=False)
descriptors.IndependentChannel(b,b.seg,'objects',objects.Objects,redo=False)

descriptors.UnstructuredData(b,b.objects,'tracks_%s' %len(b.times),objects.Tracks,
                            minTrackLength = 20,
                             maxObjectDisplacementPerDimension=10,
                             redo=False)

res = []
control = []
for time in times:
    seg = ar(b.seg[time])
    signal = ar(b.signal[time])
    pu1 = ar(b.pu1[time])
    res.append(signal*seg/(pu1*seg+(seg==0).astype(n.float)))
    control.append(seg/(pu1+1.))
res = n.array(res)
control=ar(control)


# res = []
# res2 = []
# for time in times:
#     s=ar(b.seg[time])
#     # s2=ar(b.seg_ia2[0])
#     pu1 = ar(b.pu1[time])
#     signal = ar(b.signal[time])
#     g = s*signal.astype(n.float)/(pu1+(pu1==0))
#     res.append(n.max(g,0))
#     res2.append(n.max(signal,0))

# track = 32
# seg = b.tracks_200['seg//32']
# pu1 = b.tracks_200['pu1//32']
# lact = b.tracks_200['lact//32']
# # res3 = lact*seg/(pu1*seg+(seg==0).astype(n.float))
# res3 = pu1*seg/(lact*seg+(seg==0).astype(n.float))