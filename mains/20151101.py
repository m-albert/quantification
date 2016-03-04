__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *


reference = descriptors.Image(prefix+'/data/malbert/atlas/references/35dpf_af_gfp/20151101/output/stack1.tif',
                         shape=(1920, 1920, 317),spacing=[0.29,0.29,0.55])
# mask = descriptors.Image(prefix+'/data/malbert/atlas/references/35dpf_af_gfp/20151101/output/reference_mask.tif',
#                          shape=(1920, 1920, 317),spacing=[0.29,0.29,0.55])
samples = [1,3,4,5,7]#,8,9,10,11,12]
# samples = [8,9,10,11,12]


bs = []
for isample,sample in enumerate(samples):
    b = brain.Brain(prefix+'/data/malbert/data/dbspim/20151101_p2y12/20151101_p2y12_35dpf_1min_%s.czi' %sample,
                    dimc=1,
                    times=range(10),
                    baseDataDir=prefix+'/data/malbert/quantification',
                    subDir = prefix+'20151101_p2y12_35dpf_1min_%s.czi' %sample,
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
    # registration.Transformation(b,b.seg_orig,b.interreg,'ms',
    #                             interpolation=sitk.sitkNearestNeighbor,
    #                             mask=mask,
    #                             compression='jls',
    #                             compressionOption=0,
    #                             redo=False)

    # descriptors.IndependentChannel(b,b.ms,'objects',objects.Objects,redo=False)

    # descriptors.UnstructuredData(b,b.objects,'tracks_%s' %len(b.times),objects.Tracks,redo=False)

    # descriptors.IndependentChannel(b,b.objects,'skeletons_0',objects.Skeletons,nDilations=3,redo=False)

    bs.append(b)


# for isample,sample in enumerate([1,3,4,5,7,8,9,10,11,12]):
#     o = sitk.gifa(czifile.imread('/data/malbert/data/dbspim/20151101_p2y12/20151101_p2y12_35dpf_1min_%s.czi' %sample).squeeze())
#     # o = sitk.ReadImage('/data/malbert/data/dbspim/20151101_p2y12/20151101_p2y12_35dpf_1min_%s.czi' %sample)
#     sitk.WriteImage(o,'/data/malbert/atlas/references/35dpf_af_gfp/20151101/atlasData/atlas0_%03d.mhd' %(isample+1))