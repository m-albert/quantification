__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

"""
xvfb-run --server-args="-screen 0 1024x768x24" ipython test.py
"""

# reference = descriptors.Image('/data/malbert/quantification/test0/test_reference.tif', spacing = [0.29,0.29,0.55])
# mask = descriptors.Image('/data/malbert/quantification/test0/test_mask.tif', spacing = [0.29,0.29,0.55])
# reference = descriptors.Image('/data/malbert/quantification/test0/test_reference_small.tif')
# mask = descriptors.Image('/data/malbert/quantification/test0/test_mask_small.tif')
reference = descriptors.Image(prefix+'/data/malbert/quantification/test0/test_reference_scaled.tif', spacing = [0.29*15,0.29*15,0.55*2])
mask = descriptors.Image(prefix+'/data/malbert/quantification/test0/test_mask_scaled.tif', spacing = [0.29*15,0.29*15,0.55*2])

bs = []
samples = range(2)
for isample in samples:

    b = brain.Brain(prefix+'/data/malbert/quantification/test%s' %isample,
                    dimc=1,
                    times=range(2),
                    baseDataDir=prefix+'/data/malbert/quantification',
                    subDir = 'test%s/test' %isample,
                    fileNameFormat='f%06d.h5',
                    spacing = [0.29*15,0.29*15,0.55*2]
                    )

    descriptors.RawChannel(b,0,nickname='p2y12',hierarchy='Data_scaled',redo=False)
    # registration.RegistrationParameters(b,b.p2y12,'intrareg',mode='intra',redo=True)
    # registration.RegistrationParameters(b,b.p2y12,'interreg',mode='inter',
    #                                     reference=reference,
    #                                     initialRegistration=b.intrareg,
    #                                     redo=True)
    # registration.Transformation(b,b.p2y12,b.interreg,'interaligned',redo=True)
    # registration.Transformation(b,b.p2y12,b.intrareg,'intraaligned',redo=True)
    # prediction.FilterSegmentation(b,b.interaligned,'seg',redo=True)
    # prediction.MaskedSegmentation(b,b.seg,mask,'ms',redo=True)
    # #
    # descriptors.IndependentChannel(b,b.ms,'objects',objects.Objects,redo=True)
    # descriptors.IndependentChannel(b,b.objects,'skeletons_0',objects.Skeletons,nDilations=0,redo=True)
    # descriptors.IndependentChannel(b,b.skeletons_0,'hulls',objects.Hulls,redo=True)

    registration.RegistrationParameters(b,b.p2y12,'intrareg',mode='intra')
    registration.RegistrationParameters(b,b.p2y12,'interreg',mode='inter',
                                        reference=reference,
                                        initialRegistration=b.intrareg)
    registration.Transformation(b,b.p2y12,b.interreg,'interaligned',redo=False)

    # prediction.FilterSegmentation(b,b.interaligned,'seg',redo=False)
    prediction.FilterSegmentation(b,b.p2y12,'seg_orig',redo=False)
    registration.Transformation(b,b.seg_orig,b.interreg,'ms',
                                interpolation=sitk.sitkNearestNeighbor,
                                mask=mask,
                                compression='jls',
                                compressionOption=0,
                                redo=False)

    # prediction.MaskedSegmentation(b,b.seg,mask,'ms',redo=False)
    # prediction.MaskedSegmentation(b,b.seg_orig,mask,'ms_orig',redo=False)

    descriptors.IndependentChannel(b,b.ms,'objects',objects.Objects,redo=False)

    # descriptors.IndependentChannel(b,b.objects,'skeletons_0',objects.Skeletons,nDilations=0,redo=False)
    # descriptors.IndependentChannel(b,b.skeletons_0,'hulls',objects.Hulls,redo=True)


    bs.append(b)

execfile('../movieScript.py')

# ims = []
# for ic in range(3):
#     tmp = []
#     for it in range(3):
#         o=filing.readH5('20150811_p2y12_4dpf_1min_%s.czi/all0/f%06d.h5' %(ic+1,it),hierarchy='DS1')#[280:300,880:900,880:900]
#         o = sitk.gafi(beads.scaleStack([2,15,15],sitk.gifa(o)))
#         filing.toH5(o,'/data/malbert/quantification/test%s/test/f%06d.h5' %(ic,it),hierarchy='Data_scaled')
#         tmp.append(o)
#     ims.append(tmp)
# #
# ref = sitk.gifa(ims[0][0])
# mask = n.zeros(ims[0][0].shape)
# mask[10:-10,10:-10,10:-10] = 1
# mask = sitk.gifa(mask.astype(n.uint16))
# sitk.WriteImage(ref,'/data/malbert/quantification/test0/test_reference_scaled.tif')
# sitk.WriteImage(mask,'/data/malbert/quantification/test0/test_mask_scaled.tif')

