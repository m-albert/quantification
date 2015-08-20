__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

# samples = [1,2,4,5,9]#,10,13,14,15,16]
samples = [10,13,14,15,16]
reference = sitk.ReadImage('/data/malbert/atlas/references/65dpf_af_gfp/20150810/output/stack1.tif')
# samples = [1,2,4,5,9,10,13,14,15,16]
# samples = [10,13,14,15,16]



bs = []
for isample,sample in enumerate(samples):
    b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150810_p2y12_65dpf/20150809_p2y12_6dpf_1min_3_%s.czi' %sample,
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