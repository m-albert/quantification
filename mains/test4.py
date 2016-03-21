__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

filePath = prefix+'/data/malbert/data/dbspim/20151219_p2y12_35dpf_15s_7cells_Subset1.czi'
import zeissFusion as zf
info = zf.getStackInfoFromCZI(filePath)

times = range(2)

bs = []

b = brain.Brain(filePath,
                dimc=1,
                # times=range(231),
                times=times,
                baseDataDir=prefix+'/data/malbert/quantification',
                subDir = '20151219_p2y12_35dpf_15s_7cells_Subset1_test',
                fileNameFormat='f%06d.h5',
                spacing = n.array([info['spacing'][2]]*3),
                # spacing = n.array([0.6,0.6,0.4]),
                origin = n.zeros(3)
                )

# descriptors.RawChannel(b,0,nickname='p2y12',hierarchy='p2y12',originalSpacing=info['spacing'],redo=False,
#                        compression='jls',compressionOption=2)
descriptors.IndependentChannel(b,None,'deconv',descriptors.FromFile,
                               # filePattern='/data/malbert/data/dbspim/20151105_p2y12/deconv/20151105_p2y12_45dpf_zoom25_fastasposs_2_1_%(time)s%(wildcard)s.tif',
                               filePattern='/home/malbert/mnt/hrm/malbert/huygens_dst/20151219/20151219_p2y12_35dpf_15s_7cells_Subset1_%(time)04d_%(wildcard)s_hrm.tif',
                               fileSpacing=info['spacing'],
                               compression='jls',
                               compressionOption=2,
                               redo=False)

# descriptors.IndependentChannel(b,b.deconv,'seg',segmentation.ActiveContourSegmentation,
#                                minSize = 500,
#                                redo=False)

registration.RegistrationParameters(b,b.deconv,'intrareg',mode='intra',redo=False)

registration.Transformation(b,b.deconv,b.intrareg,'deconv_ia',
                            # mask=mask,
                            redo=False,
                            # offset=greenOffset,
                            compression='jls',compressionOption=2)