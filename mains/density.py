__author__ = 'malbert'

from matplotlib import cm,colors

# density = n.zeros(bs[0].ms[0].shape,dtype=n.float)
# common = n.zeros(bs[0].ms[0].shape+(3,),dtype=n.float)

segs = []
labels = n.zeros(bs[isample].ms[0].shape+(4,),dtype=n.float)
my_cm = n.append([[0,0,0,0]],cm.gist_rainbow(n.linspace(0,255,len(samples)).astype(n.uint16)),0)

for isample,sample in enumerate(samples):
    seg = (n.array(bs[isample].ms[0])>0).astype(n.uint16)
    segs.append(seg)
    labels = n.max([labels,my_cm[seg*(isample+1)]],0)
    # tmpDensity = sitk.gafi(imaging.gaussian3d(sitk.gifa((n.array(bs[isample].ms[0])>0).astype(n.uint16)),(20,20,10)))
    # tmpDensity = ndimage.gaussian_filter(n.array(bs[isample].ms[0])>0,(3,3,1.5))
    # density += tmpDensity
    # [ar(bs[i].ms[0]) for i in range(len(samples))]

sumlabels = n.array(labels)
# sumlabels = n.sum(labels[:,:,:,:,:3],0)
norm = n.sum(segs,0)
norm = norm + (norm==0)

meanlabels = imaging.sortAxes(imaging.sortAxes(sumlabels,[3,0,1,2])/norm,[1,2,3,0])

final = sitk.Cast(sitk.gifa(meanlabels*255),sitk.sitkVectorUInt8)

sitk.WriteImage(final,os.path.join(bs[0].dataDir,'results/all_microglia.tif'))

# fiji[:] = meanlabels[:,:,:,:3]*255
# my_cmap = colors.ListedColormap(n.append([0,0,0,0],cm.gist_rainbow(range(len(samples))), name='my_name')
