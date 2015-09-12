__author__ = 'malbert'


so = sitk.gifa(bs[0].p2y12[0])[800:1200,1000:1300,200:250]

sos = []
sigmas = n.linspace(1,3,5)
for k in sigmas:
    print k
    # soa = sitk.SmoothingRecursiveGaussian(so,k)
    soa = imaging.gaussian3d(so,(k,k,k*2.))
    # soa = imaging.gaussian3d(so,(k,k,k/2.))
    soa = sitk.Laplacian(soa)
    soa = sitk.gafi(soa)
    sos.append(soa)

sos = n.max(sos*sos[4]<-1)

[tifffile.imsave('/data/malbert/tmp/delme%s.tif' %i,n.abs(sos[i][200:]).astype(n.uint16)) for ii,i in enumerate(sigmas)]
# soa = sitk.gafi(so)

# res = n.abs(soa)*(soa<-10)


from mayavi import mlab
mlab.contour3d(soa[300:],contours=[-10])
mlab.contour3d(soa[:-30,500:1500,:1000],contours=[-10])
mlab.contour3d(sos[4],contours=[-2])


maskref = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/stack1.tif')
maskref.SetSpacing([4,4,2/0.55])
p=registration.getParamsFromElastix([reference,maskref],mode='affine')

tmask = registration.transformStack(p[1],maskref)
tref = sitk.Resample(reference,tmask)
tifffile.imshow(n.array([sitk.gafi(tref),sitk.gafi(tmask)]))

mask = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/manualotseg_final.tif')
mask.SetSpacing([4,4,2/0.55])

pmod = n.zeros(p[1].shape)
pmod[:] = p[1]
# pmod[11] += 40
trmask = registration.transformStack(pmod,mask)
tifffile.imshow(sitk.gafi(tref)*(1+sitk.gafi(trmask)))
# tifffile.imshow(n.array([sitk.gafi(tmask),sitk.gafi(mask)*10000]))



for i in range(9):
    bs[0].seg[1]-bs[0].seg[0]

ndimage.generic_filter_sum


reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/stack1.tif')