__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *


# reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/stack1.tif')

reference = descriptors.Image(prefix+'/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/stack1.tif',
                         shape=(1920, 1920, 317),spacing=[0.29,0.29,0.55])
mask = descriptors.Image(prefix+'/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/reference_mask.tif',
                         shape=(1920, 1920, 317),spacing=[0.29,0.29,0.55])

# reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/stack1.tif')
# mask = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/reference_scaled448_mask.tif')
# mask.SetSpacing([4,4,8])
# mask = sitk.Resample(mask,reference)
# rreference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/reference.tif')
# reference.SetSpacing([4,4,2./0.55])
# samples = [1,2,3,5,9,10]
# samples = [11,12,13,15,16]
# samples = [1,2,3,5,9,10,11,12,13,15,16] # 11
# samples = [1,2,3,5,9,11,12,13,16] # 11, without indicies 5 and -2 which conflict with mask

samples = [1,3,5,9,11,12,13,16] # 11, without indicies 5 and -2 which conflict with mask, 2 is in neuropil
# samples = [13] # 11, without indicies 5 and -2 which conflict with mask, 2 is in neuropil

bs = []
for isample,sample in enumerate(samples):
    b = brain.Brain(prefix+'/data/malbert/data/dbspim/20150810_p2y12/20150811_p2y12_40dpf/20150811_p2y12_4dpf_1min_%s.czi' %sample,
                    dimc=1,
                    times=range(10),

                    baseDataDir=prefix+'/data/malbert/quantification',
                    subDir = prefix+'20150811_p2y12_4dpf_1min_%s.czi' %sample,
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
    # descriptors.UnstructuredData(b,b.objects,'tracks_%s' %len(b.times),objects.Tracks,redo=False)

    # descriptors.IndependentChannel(b,b.objects,'skeletons_0',objects.Skeletons,nDilations=3,redo=False)

    bs.append(b)

# for ib,b in enumerate(bs):
#     tmp = n.array(bs[ib].interaligned[0])[mask.slices]
#     obj = n.array(bs[ib].objects[0]['labels'])
#     lab = n.array(bs[ib].ms[0])
#     for i in range(3):
#         sitk.WriteImage(sitk.gifa([tmp,obj,lab][i].astype(n.uint16)),'%s/results/clicking/brain_%s_%s.tif' %(bs[0].dataDir,ib,i))




# execfile('density.py')
# execfile('../movieScript.py')

# q = n.sum([(n.array(bs[i].objects[0]['labels'])>0).astype(n.uint16) for i in range(len(bs))],0).astype(n.float)
# projs = []
# for dim in range(3):
#     projs.append(n.max(q,dim))
#
# sg = sitk.gifa(q)
# sg.SetSpacing(b.spacing)
# newSize = n.array(b.spacing)/n.array([b.spacing[0],b.spacing[0],b.spacing[0]])*n.array(sg.GetSize()).astype(n.uint32)
# ref = sitk.gifa(n.zeros(tuple(newSize)[::-1]))
# ref.SetSpacing((b.spacing[0],b.spacing[0],b.spacing[0]))
# res = sitk.Resample(sg,ref)
# # res = sitk.Resample(sg,newSize,sitk.Transform(),sitk.sitkLinear,(0,0,0),(b.spacing[0],b.spacing[0],b.spacing[0]))
# res = sitk.gafi(res)
# projs2 = []
# for dim in range(3):
#     tmp = n.max(res,dim)
#     # if not dim:
#     #     tmp = tmp.swapaxes(0,1)
#     projs2.append(tmp)
# for dim in range(3):
#     misc.imsave("%s/results/overlay_proj%s.png" %(bs[0].dataDir,dim),projs2[dim])