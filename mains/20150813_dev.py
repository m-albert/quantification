__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *


reference = descriptors.Image(prefix+'/data/malbert/atlas/references/65dpf_af_gfp/20150810/output/stack1.tif',
                              shape=(1920, 1920, 365),spacing=[0.29,0.29,0.55])
mask = descriptors.Image(prefix+'/data/malbert/atlas/references/65dpf_af_gfp/20150810/output/reference_mask.tif',
                              shape=(1920, 1920, 365),spacing=[0.29,0.29,0.55])

# samples = [1,2,4,5,9]#,10,13,14,15,16]
# samples = [10,13,14,15,16]
# reference = sitk.ReadImage('/data/malbert/atlas/references/65dpf_af_gfp/20150810/output/stack1.tif')
# mask = sitk.ReadImage('/data/malbert/atlas/references/65dpf_af_gfp/20150810/output/reference_scaled448_mask.tif')
# mask.SetSpacing([4,4,8])
# mask = sitk.Resample(mask,reference)
# samples = [1,2,4,5,9,10,13,14,15,16]
samples = [1,2,4,5,9,10,13,14,15,16] # for #14 field of view is too small
# samples = [14]

bs = []
for isample,sample in enumerate(samples):
    b = brain.Brain(prefix+'/data/malbert/data/dbspim/20150810_p2y12/20150810_p2y12_65dpf/20150809_p2y12_6dpf_1min_3_%s.czi' %sample,
                    dimc=1,
                    times=range(1),
                    baseDataDir=prefix+'/data/malbert/quantification',
                    subDir = '20150809_p2y12_6dpf_1min_3_%s.czi' %sample,
                    fileNameFormat='f%06d.h5',
                    spacing = [0.29,0.29,0.55]
                    )
    descriptors.RawChannel(b,0,nickname='p2y12',redo=False)
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

    descriptors.IndependentChannel(b,b.objects,'skeletons_0',objects.Skeletons,nDilations=3,redo=False)
    # descriptors.IndependentChannel(b,b.skeletons_0,'hulls',objects.Hulls,redo=True)

    bs.append(b)

for ib,b in enumerate(bs):
    tmp = n.array(bs[ib].interaligned[0])[mask.slices]
    obj = n.array(bs[ib].objects[0]['labels'])
    lab = n.array(bs[ib].ms[0])
    for i in range(3):
        sitk.WriteImage(sitk.gifa([tmp,obj,lab][i].astype(n.uint16)),'%s/results/clicking/brain_%s_%s.tif' %(bs[0].dataDir,ib,i))



# execfile('density.py')
# execfile('../movieScript.py')
#
# q = n.sum([(n.array(bs[i].objects[0]['labels'])>0).astype(n.uint16) for i in range(len(bs))],0).astype(n.float)
# projs = []
# for dim in range(3):
#     projs.append(n.max(q,dim))