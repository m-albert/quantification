__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

"""
xvfb-run --server-args="-screen 0 1024x768x24" ipython test.py
"""

refspacing = n.array([0.29,0.29,0.55])
refshape = n.array([1920, 1920, 317])
reforigin = n.array([-0.5*refspacing[0]*refshape[0],-0.5*refspacing[1]*refshape[1],-refspacing[2]*refshape[2]])
# reforigin = -(0.5*(refspacing[0]*refshape[0]+refspacing[1]*refshape[1])+refspacing[2]*refshape[2])

reference = descriptors.Image(prefix+'/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/stack1.tif',
                         shape=refshape,spacing=refspacing,
                         origin=reforigin)
# mask = descriptors.Image(prefix+'/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/reference_mask.tif',
#                          shape=refshape,spacing=refspacing,
#                          origin=reforigin)
mask = descriptors.Image(prefix+'/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/reference_mask_x_0_640_z_0_61.tif',
                         shape=refshape,spacing=refspacing,
                         origin=reforigin)

sampleshape = n.array([658,850,134])
samplespacing = n.array([ 0.38711306,  0.38711306,  1.        ])
sampleorigin = n.array([0,-0.5*samplespacing[1]*sampleshape[1],-samplespacing[2]*sampleshape[2]])
greenOffset = n.array([0,-10,0])*samplespacing

bs = []
samples = range(1)
times = range(200)
for isample in samples:

    b = brain.Brain(prefix+'/data/malbert/data/dbspim/20150317/20150317_45dpf_pu1_gcamp6s_right_15s_Subset.czi',
                    dimc=2,
                    # times=range(0,1),
                    times=times,
                    baseDataDir=prefix+'/data/malbert/quantification',
                    subDir = 'gcamp_20151002',
                    fileNameFormat='f%06d.h5',
                    spacing = samplespacing,
                    origin = sampleorigin
                    )

    descriptors.RawChannel(b,0,nickname='gcamp',hierarchy='gcamp',redo=False,
                           compression='jls',compressionOption=2)
    descriptors.RawChannel(b,1,nickname='pu1',hierarchy='pu1',redo=False,
                           compression='jls',compressionOption=2)

    prediction.FilterSegmentation(b,b.pu1,'seg_orig',threshold=-50,redo=False)
    # prediction.FilterSegmentation(b,b.pu1,'seg_orig2',threshold=-50,redo=True)

    registration.RegistrationParameters(b,b.gcamp,'intrareg',mode='intra')
    registration.RegistrationParameters(b,b.gcamp,'interreg',mode='inter',
                                        reference=reference,
                                        initialRegistration=b.intrareg,
                                        redo = False)

    registration.Transformation(b,b.gcamp,b.interreg,'interaligned',
                                mask=mask,
                                redo=False,
                                offset=greenOffset,
                                compression='jls',compressionOption=2)
    registration.Transformation(b,b.pu1,b.interreg,
                                'pu1_ia',
                                mask=mask,
                                redo=False,
                                compression='jls',compressionOption=2)

    registration.Transformation(b,b.seg_orig,b.interreg,
                                'seg_ia',
                                mask=mask,
                                redo=False,
                                interpolation=sitk.sitkNearestNeighbor,
                                compression='jls')

    descriptors.IndependentChannel(b,b.seg_ia,'objects',objects.Objects,redo=False)
    # descriptors.UnstructuredData(b,b.objects,'tracks_%s' %len(b.times),objects.Tracks,redo=True)

    # ims = []
    # for itrack in range(b.__dict__['tracks_%s' %len(times)]['nTracks']):
    #     tmpIms = b.__dict__['tracks_%s' %len(times)]['interaligned//%s' %itrack]
    #     ims.append(tmpIms)

    # o=b.tracks_200['pu1_ia//1']

    # o = b.tracks_11['interaligned//10']
    # activity.Signal(b,b.interaligned,'signal',filterSize=2,redo=False)

    # descriptors.IndependentChannel(b,b.seg_ia,'distance_masks',activity.DistanceMasks,nDilations=20,
    #                                signal=b.signal,mask=mask,
    #                                redo=False)

    bs.append(b)

# track = 7
# res = []
# for time in range(len(b.tracks_200['%s' %track])):
#     tmpO = (o[time]==0).astype(n.float)
#     tmp = ar(ims[track][time])/(tmpO+o[time].astype(n.float))
#     res.append(tmp)

# times 200 tracks: 1,7

res = []
res2 = []
for time in times:
    s=ar(b.seg_ia[time])
    # s2=ar(b.seg_ia2[0])

    pu1 = ar(b.pu1_ia[time])
    gcamp = ar(b.interaligned[time])
    g = s*gcamp.astype(n.float)/(pu1+(pu1==0))
    res.append(n.max(g,0))
    res2.append(n.max(gcamp,0))
# g2 = s2*gcamp.astype(n.float)/(pu1+(pu1==0))


# label = 3
# bbs = [objects.bbox(b.objects[it]['bboxs'][label]) for it in b.times]
# refbbox = bbs[len(b.times)/2]
# c = n.array([b.seg_ia[it][refbbox] for it in b.times])
# g = n.array([b.interaligned[it][refbbox] for it in b.times])
# neurons = n.array([n.invert(c.astype(n.bool)).astype(n.uint16)*g])
# micro = n.array([c*g])
# sneurons = n.sum(n.sum(n.sum(neurons,-1),-1),-1)
# smicro = n.sum(n.sum(n.sum(micro,-1),-1),-1)
# occupied = n.sum(n.sum(n.sum(c,-1),-1),-1)/float(n.product(c[0].shape))

# execfile('../movieScript.py')