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

