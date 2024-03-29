__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *


# reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/stack1.tif')
reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/stack1.tif')
mask = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/reference_scaled448_mask.tif')
mask.SetSpacing([4,4,8])
mask = sitk.Resample(mask,reference)
# rreference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/reference.tif')
# reference.SetSpacing([4,4,2./0.55])
# samples = [1,2,3,5,9,10]
# samples = [11,12,13,15,16]
samples = [1,2,3,5,9,10,11,12,13,15,16]

bs = []
for isample,sample in enumerate(samples):
    b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150811_p2y12_40dpf/20150811_p2y12_4dpf_1min_%s.czi' %sample,
                    dimc=1,
                    times=range(2)
                    )
    descriptors.RawChannel(b,0,'p2y12')
    registration.RegistrationParameters(b,b.p2y12,'intrareg',mode='intra')
    registration.RegistrationParameters(b,b.p2y12,'interreg',mode='inter',
                                        reference=reference,
                                        initialRegistration=b.intrareg)
    registration.Transformation(b,b.p2y12,b.interreg,'interaligned',redo=False)
    registration.Transformation(b,b.p2y12,b.intrareg,'intraaligned',redo=False)

    prediction.FilterSegmentation(b,b.interaligned,'seg')
    prediction.MaskedSegmentation(b,b.seg,mask,'ms',redo=False)

    descriptors.IndependentChannel(b.ms,'objects',objects.Objects)

    bs.append(b)
