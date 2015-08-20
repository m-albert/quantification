__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *


# samples = [1,2,3,5,9,10]
# samples = [11,12,13,15,16]
# samples = [1,2,3,5,9,10,11,12,13,15,16]
samples = [1,2,4,5,9,10,13,14,15,16]
bs = []
for isample,sample in enumerate(samples):
    # b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150811_p2y12_40dpf/20150811_p2y12_4dpf_1min_%s.czi' %sample,
    #                 dimc=1,
    #                 times=range(5)
    #                 )
    b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150810_p2y12_65dpf/20150809_p2y12_6dpf_1min_3_%s.czi' %sample,
                    dimc=1,
                    times=range(1)
                    )
    descriptors.RawChannel(b,0,'p2y12')
    # sitk.WriteImage(sitk.gifa(b.p2y12[0]),'/data/malbert/atlas/references/45dpf_af_gfp/20150811/atlasData/atlas0_%03d.mhd' %(isample+1))
    sitk.WriteImage(sitk.gifa(b.p2y12[0]),'/data/malbert/atlas/references/65dpf_af_gfp/20150810/atlasData/atlas0_%03d.mhd' %(isample+1))