__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *


# reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/stack1.tif')
reference = sitk.ReadImage('/data/malbert/atlas/references/50dpf_af_gfp/20150812/output/stack1.tif')
# reference.SetSpacing([4,4,2./0.55])
# samples = [1,2,5,6,7,8,9,10,11] # samples 0812 5dpf
samples = [1,2,5,6,7] # samples 0812 5dpf
# samples = [8,9,10,11] # samples 0812 5dpf

bs = []
for isample,sample in enumerate(samples):
    b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150812_p2y12_50dpf/20150812_p2y12_5dpf_1min_%s.czi' %sample,
                    dimc=1,
                    times=range(10)
                    )
    descriptors.RawChannel(b,0,'p2y12')
    registration.RegistrationParameters(b,b.p2y12,'intrareg',mode='intra')
    registration.RegistrationParameters(b,b.p2y12,'interreg',mode='inter',
                                        reference=reference,
                                        initialRegistration=b.intrareg)
    registration.Transformation(b,b.p2y12,b.interreg,'interaligned',redo=False)
    registration.Transformation(b,b.p2y12,b.intrareg,'intraaligned',redo=False)

    prediction.FilterSegmentation(b,b.interaligned,'seg')

    bs.append(b)
