__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

import time
time.sleep(500)

# samples = [1,2,3,5,9,10]
# samples = [11,12,13,15,16]
# samples = [1,2,3,5,9,10,11,12,13,15,16]
# samples = [1,2,4,5,9,10,13,14,15,16]
samples = [1,2,5,6,7,8,9,10,11] # samples 0812 5dpf
bs = []
for isample,sample in enumerate(samples):
    # b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150811_p2y12_40dpf/20150811_p2y12_4dpf_1min_%s.czi' %sample,
    #                 dimc=1,
    #                 times=range(5)
    #                 )
    b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150812_p2y12_50dpf/20150812_p2y12_5dpf_1min_%s.czi' %sample,
                    dimc=1,
                    times=range(10)
                    )
    descriptors.RawChannel(b,0,'p2y12')
    # sitk.WriteImage(sitk.gifa(b.p2y12[0]),'/data/malbert/atlas/references/45dpf_af_gfp/20150811/atlasData/atlas0_%03d.mhd' %(isample+1))
    sitk.WriteImage(sitk.gifa(b.p2y12[0]),'/data/malbert/atlas/references/50dpf_af_gfp/20150812/atlasData/atlas0_%03d.mhd' %(isample+1))


# rename
targets = [1,2,3,4,5]
names = [7,8,9,10,11]
for j in range(1,5):
    target = targets[j]
    name = names[j]
    os.system("ln -s 20150818_p2y12_50dpf_1min_%s.czi 20150812_p2y12_5dpf_1min_%s.czi" %(target,name))
    for i in range(9):
        os.system("ln -s 20150818_p2y12_50dpf_1min_%s\(%s\).czi 20150812_p2y12_5dpf_1min_%s\(%s\).czi" %(target,i+1,name,i+1))

# create mask

so=reference
tmpRes = sitk.SmoothingRecursiveGaussian(so,2)
tmpRes = sitk.Laplacian(tmpRes)
tmpRes = sitk.Cast(tmpRes<-5,3)#*sitk.Cast(sitk.Abs(tmpRes),3)
tmpRes = sitk.gafi(tmpRes)

tmpRes,N = ndimage.label(tmpRes)
tmpRes = imaging.mySizeFilter(tmpRes,5000,1000000000000)
s = imaging.getSizes(tmpRes)
skinind = n.argmax(s)
nskin = (tmpRes!=(skinind+1))

nskinlabel,N = ndimage.label(nskin)




# find mask
tmpRes = sitk.SmoothingRecursiveGaussian(sitk.Cast(so,7),20)
tmpRes = sitk.Laplacian(tmpRes)
# tmpRes = sitk.Cast(tmpRes<-5,3)#*sitk.Cast(sitk.Abs(tmpRes),3)
tmpRes = sitk.gafi(tmpRes)


img = sitk.gifa((n.abs(tmpRes*(tmpRes<0))*1000).astype(n.uint16)[250])
# img = registration.scaleStack([2,4,4],img)
# img.SetSpacing([4,4,2])

marker_img = sitk.gifa(n.zeros((10,10)).astype(n.uint16))
marker_img = sitk.Resample(marker_img,img)
shape = n.array(marker_img.GetSize())
# pts = [[10,10,10],[1000,1000,250]]
margins = [50,100,150,200]
pts = [[1000,1000]]
ptinds = [1]
for imargin,margin in enumerate(margins):
    pts += [[margin,margin],[margin,shape[1]-margin],[shape[0]-margin,shape[1]-margin],[shape[0]-margin,margin],
           # [shape[0]-margin,margin+10],[shape[0]-margin+10,margin+10]
           ]
    ptinds += range(imargin*4+1,(imargin+1)*4+1)
    # ptinds += list(n.arange(imargin*len(margins)+2,(imargin+1)*len(margins)+2))

for ipt,pt in enumerate(pts):
    idx = img.TransformPhysicalPointToIndex(pt)
    marker_img[idx] = ptinds[ipt]

ws = sitk.MorphologicalWatershedFromMarkers(img, marker_img, markWatershedLine=True, fullyConnected=False)
tifffile.imshow(sitk.gafi(ws))
# tifffile.imshow(sitk.gafi((sitk.LabelOverlay(img, ws, opacity=.2))))





tmp = n.abs(tmpRes*(tmpRes<0))
drange = 10
tmp = sitk.gifa(tmp)
tmp = sitk.Cast(tmp<drange,6)*tmp+sitk.Cast(10*(tmp>=drange),6)
tmp = tmp*(n.power(2,16)/drange)
img = sitk.Cast(tmp,3)


# img = sitk.gifa((tmpRes>500).astype(n.uint16))
# img = sitk.gifa(tmpRes.astype(n.uint16))
scale = [10,10,5]
img = registration.scaleStack(scale[::-1],img)
img.SetSpacing([int(i) for i in scale])

marker_img = sitk.gifa(n.zeros((10,10,10)).astype(n.uint16))
marker_img = sitk.Resample(marker_img,img)
# shape = n.array(marker_img.GetSize())
# shape = tmpRes.shape[::-1]
# margins = [50,100,150,200]
margins = [200]
z = 200
pts = [[1000,1000,z]]
ptinds = [1]
for imargin,margin in enumerate(margins):
    pts += [[margin,margin,z],[margin,shape[1]-margin,z],[shape[0]-margin,shape[1]-margin,z],[shape[0]-margin,margin,z]]
    ptinds += range(imargin*4+2,(imargin+1)*4+2)
    # ptinds += list(n.arange(imargin*len(margins)+2,(imargin+1)*len(margins)+2))

for ipt,pt in enumerate(pts):
    idx = img.TransformPhysicalPointToIndex(pt)
    marker_img[idx] = ptinds[ipt]

ws = sitk.MorphologicalWatershedFromMarkers(img, marker_img, markWatershedLine=True, fullyConnected=False)
tifffile.imshow(sitk.gafi(ws))
# tifffile.imshow(sitk.gafi((sitk.LabelOverlay(img, ws, opacity=.2))))





tmpRes2 = sitk.SmoothingRecursiveGaussian(so,20)
tmpRes2 = sitk.gafi(tmpRes2)


times = range(10)
diffs = n.zeros(bs[0].seg[0].shape)
mic = n.zeros(bs[0].seg[0].shape)
for i in range(len(samples)):
    for t in times:
        this = n.array(bs[i].seg[t])
        mic += this
        if t < times[-1]:
            next = n.array(bs[i].seg[t+1])
            diffs += n.abs((next>0).astype(n.int8)-(this>0).astype(n.int8))