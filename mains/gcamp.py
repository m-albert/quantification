__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

"""
xvfb-run --server-args="-screen 0 1024x768x24" ipython test.py
"""
reference = descriptors.Image(prefix+'/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/stack1.tif',
                         shape=(1920, 1920, 317),spacing=[0.29,0.29,0.55])
mask = descriptors.Image(prefix+'/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/reference_mask.tif',
                         shape=(1920, 1920, 317),spacing=[0.29,0.29,0.55])

bs = []
samples = range(1)
for isample in samples:

    b = brain.Brain(prefix+'/data/malbert/data/dbspim/20150317/20150317_45dpf_pu1_gcamp6s_right_15s_Subset.czi',
                    dimc=2,
                    times=range(2),
                    baseDataDir=prefix+'/data/malbert/quantification',
                    subDir = 'gcamp_20151002',
                    fileNameFormat='f%06d.h5',
                    spacing = n.array([ 0.38711306,  0.38711306,  1.        ]),
                    )

    descriptors.RawChannel(b,0,nickname='gcamp',hierarchy='gcamp',redo=False)
    descriptors.RawChannel(b,1,nickname='pu1',hierarchy='pu1',redo=False)

    registration.RegistrationParameters(b,b.gcamp,'intrareg',mode='intra')
    registration.RegistrationParameters(b,b.gcamp,'interreg',mode='inter',
                                        reference=reference,
                                        initialRegistration=b.intrareg,
                                        redo = True)
    registration.Transformation(b,b.gcamp,b.interreg,'interaligned',redo=True)

    bs.append(b)

# execfile('../movieScript.py')