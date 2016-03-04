__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

b = brain.Brain(prefix+'/data/malbert/data/dbspim/20151105_p2y12/20151105_p2y12_45dpf_zoom25_fastasposs_2_1.czi',
                dimc=1,
                # times=range(0,1),
                times=range(2),
                baseDataDir=prefix+'/data/malbert/quantification',
                subDir = '20151105_p2y12_45dpf_zoom25_fastasposs_2_1',
                fileNameFormat='f%06d.h5',
                spacing = n.array([ 0.09138302,  0.09138302,  0.39369837])
                )

descriptors.RawChannel(b,0,nickname='p2y12',hierarchy='p2y12',redo=False,
                       compression='jls',compressionOption=2)

descriptors.IndependentChannel(b,b.p2y12,'deconv',descriptors.FromFile,
                               filePattern='/data/malbert/data/dbspim/20151105_p2y12/deconv/20151105_p2y12_45dpf_zoom25_fastasposs_2_1_%(time)s%(wildcard)s.tif',
                               redo=False)

prediction.FilterSegmentation(b,b.p2y12,'seg_orig',redo=False)

registration.RegistrationParameters(b,b.p2y12,'intrareg',mode='intra')
registration.Transformation(b,b.p2y12,b.intrareg,'intraaligned',redo=False)

registration.Transformation(b,b.seg_orig,b.intrareg,'ms',
                            interpolation=sitk.sitkNearestNeighbor,
                            # mask=mask,
                            compression='jls',
                            compressionOption=0,
                            redo=False)

registration.GenericRegistration(b,b.p2y12,'generic',
                                 elastixStrings=[registration.elastixParameterTemplateStringNonRigidRigidityPenalty20,
                                 registration.elastixParameterTemplateStringNonRigidRigidityPenalty1],
                                 dilationRadius=2
                                 )


d = sitk.gifa(ar(b.deconv[0]))
d.SetSpacing(b.spacing)
dd = prediction.edgePotential(d)

positions = [[141,156,64]]
geoIn = prediction.initialEdges(dd,positions,radius=1)

geo = prediction.activeContours(geoIn,dd,1.,0.05,2)

# descriptors.IndependentChannel(b,b.ms,'objects',objects.Objects,redo=False)

#
# slices = tuple([slice(30,100),slice(600,900),slice(300,800)])


# slices = tuple([slice(30,100),slice(400,750),slice(700,900)])
# im1 = n.array(b.intraaligned[0])[slices]
# im2 = n.array(b.intraaligned[1])[slices]
# # im1 = n.array(b.p2y12[0])
# # im2 = n.array(b.p2y12[1])
#
# import zeissFusion as zf
#
# rim,rdefo = zf.nonRigidAlignment(sitk.gifa(im1),sitk.gifa(im2),zf.importsDict,[registration.elastixParameterTemplateStringRotation],'/tmp/test',initialTransformString=None)
# im,defo = zf.nonRigidAlignment(sitk.gifa(im1),rim,zf.importsDict,[registration.elastixParameterTemplateStringNonRigidRigidityPenalty],'/tmp/test',initialTransformString=None)
# # im,defo = zf.nonRigidAlignment(sitk.gifa(im1),sitk.gifa(im2),zf.importsDict,[registration.elastixParameterTemplateStringNonRigidTest],'/tmp/test',initialTransformString=None)
#
# im = sitk.Cast(im,3)
# rim = sitk.Cast(rim,3)
# adefo = sitk.gafi(defo)
# # adefo = adefo*500
# a=n.sqrt(n.sum([n.power(adefo[:,:,:,i],2) for i in range(3)],0))
# a = a*200
# sa = sitk.gifa(a.astype(n.uint16))

# import beads
# tifffile.imshow(n.array([[sitk.gafi(beads.scaleStack((b.spacing[2]/b.spacing)[::-1],sitk.gifa(n.array(b.p2y12[it])))),
#                           n.array(b.generic[it]['im0']),
#                           n.array(b.generic[it]['im1']),
#                           sitk.gafi(beads.scaleStack((b.spacing[2]/b.spacing)[::-1],sitk.gifa(n.array(b.ms[it]))))\
#                           *n.sqrt(n.sum([n.power((n.array(b.generic[it]['defo%s' %i]).astype(n.int32)-n.power(2,15))/1000.,2) for i in range(3)],0))
#                           # *(n.array(b.generic[it]['defo']).astype(n.int32)-n.power(2,15))/1000.
#                           ] for it in range(2)]),
#                 vmax=1000,
#                 norm=1,
#                 # projfunc=n.max
#                 )
#
# n.sqrt(n.sum([n.power((n.array(b.generic[it]['defo%s' %i]).astype(n.int32)-n.power(2,15))/1000.,2) for i in range(3)],0))
# import beads
# it = 1
# o1 = ar(b.deconv[it-1])
# # o1 = ar(b.p2y12[it-1])
# d = n.sqrt(n.sum([n.power((n.array(b.generic[it]['defo%s' %i]).astype(n.int32)-n.power(2,15))/1000.,2) for i in range(3)],0))
# d1 = prediction.segmentDeconv2(o1)
#
#
# m1 = (d1==103).astype(n.uint16)
# d1s = sitk.gafi(beads.scaleStack((b.spacing[2]/b.spacing)[::-1],sitk.gifa(m1)))
# # sitk.gafi(beads.scaleStack((b.spacing[2]/b.spacing)[::-1],sitk.gifa(d)))
#
# # r1 = sitk.gafi(beads.scaleStack((b.spacing[2]/b.spacing)[::-1],sitk.gifa(o1)))
# r1 = sitk.gafi(beads.scaleStack((b.spacing[2]/b.spacing)[::-1],sitk.gifa(ar(b.p2y12[it-1]))))
# # r2 = sitk.gafi(beads.scaleStack((b.spacing[2]/b.spacing)[::-1],sitk.gifa(ar(b.deconv[it]))))
# r2 = ar(b.generic[it]['im1'])
#
# tifffile.imshow([r1,r2],projfunc=n.max,projdim=0)
# tifffile.imshow(d1s*d,projfunc=n.max,projdim=0)
#
# tifffile.imshow([r1,r2],projfunc=n.max,projdim=1)
# tifffile.imshow(d1s*d,projfunc=n.max,projdim=1)
#
# tifffile.imshow([r1,r2],projfunc=n.max,projdim=2)
# tifffile.imshow(d1s*d,projfunc=n.max,projdim=2)

