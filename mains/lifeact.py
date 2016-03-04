__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

# filePath = prefix+'/data/malbert/data/dbspim/osmo/20151220_p2y12_45dpf_15s_3cells_Subset.czi'
filePath = prefix+'/data/malbert/data/dbspim/20160302_lifeact/20160302_3dpf_pu1_lifeact_15s_3_Subset.czi'
import zeissFusion as zf
info = zf.getStackInfoFromCZI(filePath)

bs = []

b = brain.Brain(filePath,
                dimc=2,
                times=range(600),
                baseDataDir=prefix+'/data/malbert/quantification',
                subDir = '20160302_lifeact',
                fileNameFormat='f%06d.h5',
                # spacing = n.array([info['spacing'][2]]*3),
                spacing = info['spacing'],
                # spacing = n.array([0.6,0.6,0.4]),
                origin = n.zeros(3)
                )

descriptors.RawChannel(b,0,nickname='lact',hierarchy='lact',redo=False,
                       compression='jls',compressionOption=2)
descriptors.RawChannel(b,1,nickname='pu1',hierarchy='pu1',redo=False,
                       compression='jls',compressionOption=2)

prediction.FilterSegmentation(b,b.pu1,'seg',threshold=-10,redo=True)
descriptors.IndependentChannel(b,b.seg,'objects',objects.Objects,redo=False)

descriptors.UnstructuredData(b,b.objects,'tracks_%s' %len(b.times),objects.Tracks,
                             maxObjectDisplacementPerDimension=10,
                             redo=False)
