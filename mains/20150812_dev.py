__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

reference = descriptors.Image(prefix+'/data/malbert/atlas/references/50dpf_af_gfp/20150812/output/stack1.tif',
                              shape=(1920, 1920, 319),spacing=[0.29,0.29,0.55])
mask = descriptors.Image(prefix+'/data/malbert/atlas/references/50dpf_af_gfp/20150812/output/reference_mask.tif',
                                shape=(1920, 1920, 319),spacing=[0.29,0.29,0.55])

# reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/stack1.tif')
# reference = sitk.ReadImage('/data/malbert/atlas/references/50dpf_af_gfp/20150812/output/stack1.tif')
# mask = sitk.ReadImage('/data/malbert/atlas/references/50dpf_af_gfp/20150812/output/reference_scaled448_mask.tif')
# mask.SetSpacing([4,4,8])
# mask = sitk.Resample(mask,reference)
# reference.SetSpacing([4,4,2./0.55])
samples = [1,2,5,6,7,8,9,10,11] # samples 0812 5dpf

bs = []
for isample,sample in enumerate(samples):
    b = brain.Brain(prefix+'/data/malbert/data/dbspim/20150810_p2y12/20150812_p2y12_50dpf/20150812_p2y12_5dpf_1min_%s.czi' %sample,
                    dimc=1,
                    times=range(10),
                    baseDataDir=prefix+'/data/malbert/quantification',
                    subDir = '20150812_p2y12_5dpf_1min_%s.czi' %sample,
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
    # descriptors.IndependentChannel(b,b.skeletons_0,'hulls',objects.Hulls,redo=False)

    bs.append(b)

# execfile('density.py')
# execfile('../movieScript.py')

for ib,b in enumerate(bs):
    tmp = n.array(bs[ib].interaligned[0])[mask.slices]
    obj = n.array(bs[ib].objects[0]['labels'])
    lab = n.array(bs[ib].ms[0])
    for i in range(3):
        sitk.WriteImage(sitk.gifa([tmp,obj,lab][i].astype(n.uint16)),'%s/results/clicking/brain_%s_%s.tif' %(bs[0].dataDir,ib,i))



# q = n.sum([(n.array(bs[i].hulls[0]['labels'])>0).astype(n.uint16) for i in range(len(bs))],0).astype(n.float)
# q = [n.max(n.array(bs[0].hulls[it]['labels']),0) for it in range(len(b.times))]
# projs = []
# for dim in range(3):
#     projs.append(n.max(q,dim))

w = sitk.gafi(gm)[mask.slices]
w = w*(w>0.1)
w=sitk.Cast(sitk.gifa(w),6)

for ivideo in range(8):
    v = []
    for it in range(10):
        print it
        v.append(sitk.gafi(sitk.Cast(sitk.gifa(n.array(bs[ivideo].interaligned[it])[mask.slices]),6)*w).astype(n.uint16))

    res = n.array([n.max(i,0) for i in v])
    sitk.WriteImage(sitk.gifa(res),'/home/malbert/delme/p2y12_wholebrain_4dpf_10timepoints_%s.tif' %ivideo)