__author__ = 'malbert'

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

im1 = n.array(b.p2y12[0])
im2 = n.array(b.p2y12[1])

import zeissFusion as zf

im,defo = zf.nonRigidAlignment(sitk.gifa(im1),sitk.gifa(im2),zf.importsDict,[zf.elastixParameterTemplateStringNonRigidRigidityPenalty],'/tmp/test',initialTransformString=None)