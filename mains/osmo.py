__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

filePath = prefix+'/data/malbert/data/dbspim/osmo/20151220_p2y12_45dpf_15s_3cells_Subset.czi'
import zeissFusion as zf
info = zf.getStackInfoFromCZI(filePath)

times = range(140)

bs = []

b = brain.Brain(filePath,
                dimc=1,
                # times=range(231),
                times=times,
                baseDataDir=prefix+'/data/malbert/quantification',
                subDir = 'osmo',
                fileNameFormat='f%06d.h5',
                spacing = n.array([info['spacing'][2]]*3),
                # spacing = n.array([0.6,0.6,0.4]),
                origin = n.zeros(3)
                )

descriptors.RawChannel(b,0,nickname='p2y12',hierarchy='p2y12',originalSpacing=info['spacing'],
                       redo=False,
                       compression='jls',compressionOption=2)
descriptors.IndependentChannel(b,b.p2y12,'deconv',descriptors.FromFile,
                               # filePattern='/data/malbert/data/dbspim/20151105_p2y12/deconv/20151105_p2y12_45dpf_zoom25_fastasposs_2_1_%(time)s%(wildcard)s.tif',
                               # filePattern='/home/malbert/mnt/hrm/malbert/huygens_dst/20151220/20151220_p2y12_45dpf_15s_%(time)04d_%(wildcard)s_hrm.tif',
                               filePattern='/home/malbert/mnt/hrm/malbert/huygens_dst/20151220/20151220_p2y12_45dpf_15s_3cells_Subset_%(time)04d_%(wildcard)s_hrm.tif',
                               fileSpacing=info['spacing'],
                               compression='jls',
                               compressionOption=2,
                               redo=False)

descriptors.IndependentChannel(b,b.deconv,'seg',segmentation.ActiveContourSegmentation,
                               minSize = 500,
                               redo=False)

registration.RegistrationParameters(b,b.p2y12,'intrareg',mode='intra')

registration.Transformation(b,b.deconv,b.intrareg,'deconv_ia',
                            # mask=mask,
                            redo=False,
                            # offset=greenOffset,
                            compression='jls',compressionOption=2)

descriptors.IndependentChannel(b,b.deconv_ia,'seg_ia',segmentation.ActiveContourSegmentation,
                               minSize = 500,
                               redo=False)

descriptors.DependentChannel(b,b.seg_ia,'structseg',segmentation.StructuralSegmentation,
                               minSize = 100,
                               propagation = False,
                               redo=False)

# descriptors.UnstructuredData(b,b.seg,'tracks_%s' %len(b.times),objects.Tracks,
#                              maxObjectDisplacementPerDimension=10,
#                              redo=False)
#
# descriptors.UnstructuredData(b,b.seg_ia,'ia_tracks_%s' %len(b.times),objects.Tracks,
#                              maxObjectDisplacementPerDimension=10,
#                              redo=False)





# bla = []
# for i in times: bla.append((ar(b.ia_tracks_140[i])==1).astype(n.uint16))
# bla = ar(bla)
# bla[:,:,120:150,97] = 0
# bla[:,:,138,97:100] = 0
#
# sc = measurement.separateCell(bla[:94])
#
# import vtkutils,processing,sitk2vtk
#
# times = range(sc.shape[0])
# cs = [[],[]]
# for iobj,obj in enumerate([1,2]):
#     for time in range(sc.shape[0]):
#     # for time in [34]:
#         print time
#         im = sitk.gifa((sc[time]==obj).astype(n.uint16))
#         vtkimg = sitk2vtk.sitk2vtk(im)
#         mesh = vtkutils.extractSurface(vtkimg,0.5)
#         c = processing.CalculateCurvatures(mesh)
#         cs[iobj].append(c)
#
# ms = [[n.mean(cs[iobj][time]) for time in times] for iobj in range(2)]
# ss = [[n.std(cs[iobj][time]) for time in times] for iobj in range(2)]







    # curvatures.append(tmpc)
# curvatures = n.array(curvatures)
# vs,ss,cs = measurement.plotSeparateCell(sc)

# bla,s = [],[]
# for i in times[:1]:
#     tmp = (ar(b.ia_tracks_140[i])==1).astype(n.uint16)
#     bla.append(tmp)
#     toSkel0 = sitk.gifa(tmp)
#     toSkel = objects.dilateAndErode(toSkel0,5)
#     skel = objects.skeletonizeImage(toSkel)
#     s.append(skel)
#
# bla=ar(bla)
# s=ar(s)
#
# surf = bla[0]-ndimage.binary_erosion(bla[0])
# w = sitk.gafi(sitk.SignedDanielssonDistanceMap(sitk.gifa(s[0])))
# q=w*surf

    # sitk.