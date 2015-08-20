__author__ = 'malbert'


__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *
import multiprocessing

# reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/stack1.tif')
reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/stack1.tif')
# reference.SetSpacing([4,4,2./0.55])
# samples = [1,2,3,5,9,10]
samples = [11,12,13,15,16]
# samples = [1,2,3,5,9,10,11,12,13,15,16]

bs = []
for isample,sample in enumerate(samples):
    b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150811_p2y12_40dpf/20150811_p2y12_4dpf_1min_%s.czi' %sample,
                    dimc=1,
                    times=range(5)
                    )
    bs.append([b])

def main(inp):
    b = inp[0]
    descriptors.RawChannel(b,0,'p2y12')
    registration.RegistrationParameters(b,b.p2y12,'intrareg',mode='intra')
    registration.RegistrationParameters(b,b.p2y12,'interreg',mode='inter',
                                        reference=reference,
                                        initialRegistration=b.intrareg)
    registration.Transformation(b,b.p2y12,b.interreg,'interaligned',redo=False)
    registration.Transformation(b,b.p2y12,b.intrareg,'intraaligned',redo=False)
    inp[0] = b
    return

p = multiprocessing.Pool(5)
p.map(main,bs)