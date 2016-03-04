__author__ = 'malbert'

import weighted_kde
from imports import *

from dependencies import *
from scipy.stats import multivariate_normal
from scipy import stats


def getDensity(points,mask,bandwidth=25.,scales=n.array([4.,4,2])):

    bandwidth = float(bandwidth)

    # pdb.set_trace()
    mean = n.mean(points,1)
    # meanx = mean[0]

    # points[0] = (-2)*(points[0]-meanx) + points[0]

    m=mask.ga()[mask.slices]
    print 'reducing mask!'
    # m[:100] = 0
    mscaled = sitk.gafi(beads.scaleStack(scales[::-1]/mask.spacing[::-1],sitk.gifa(m)))

    # mscaled =

    amscaled = mscaled.swapaxes(0,2)


    # bounds = n.array(m.shape)[::-1]*mask.spacing/scales
    bounds = amscaled.shape


    x,y,z = n.mgrid[0:bounds[0],0:bounds[1],0:bounds[2]]
    x_grid = n.array([x.flatten(),y.flatten(),z.flatten()])

    gkde = weighted_kde.gaussian_kde(points,bw_method=bandwidth)

    diag = n.array([bandwidth,bandwidth,bandwidth])
    gkde.covariance = n.diag(diag)
    gkde.inv_cov = n.diag(1/diag)

    dens = gkde.evaluate(x_grid)
    dens = dens.reshape(x.shape)*amscaled

    dens = dens/n.sum(dens)
    # pdb.set_trace()

    # pdb.set_trace()

    kernel = multivariate_normal.pdf(x_grid.swapaxes(0,1),n.array(x.shape)/2.,gkde.covariance).reshape(x.shape)
    kk = kernel>(kernel.max()/10.)
    kbounds = n.array(kk.nonzero())
    kmin = n.min(kbounds,1)
    kmax = n.max(kbounds,1)
    kernel = kernel[kmin[0]:kmax[0],kmin[1]:kmax[1],kmin[2]:kmax[2]]

    print 'calculating weightmap'
    weightmap = sitk.Convolution(sitk.Cast(sitk.gifa(mscaled),6),sitk.Cast(sitk.gifa(kernel),6),
                                 boundaryCondition=sitk.ConvolutionImageFilter.ZERO_PAD)

    kernelsum = n.sum(kernel)
    nweightmap = sitk.gafi(weightmap)
    weights = kernelsum/ndimage.map_coordinates(nweightmap,points[::-1,:],mode='nearest')


    wgkde = weighted_kde.gaussian_kde(points,bw_method=bandwidth,weights=weights)
    wgkde.covariance = gkde.covariance
    wgkde.inv_cov = gkde.inv_cov

    wdens = wgkde.evaluate(x_grid)
    wdens = wdens.reshape(x.shape)*amscaled

    wdens = wdens/n.sum(wdens)

    xs = n.array(amscaled.nonzero())
    probs = wdens[amscaled.nonzero()]
    probs = probs/n.sum(probs)
    # tifffile.imshow(n.array([dpens,wdens]),vmin=1,projfunc=n.max,projdim=2)
    return wdens,dens,xs,probs


def getNNDists(points,neighs=1):
    tree = spatial.cKDTree(points)
    dists = n.mean(tree.query(points,neighs+1)[0][:,1:neighs+1],axis=1)
    return dists

def flatten(l):
    iterator = flatgen(l)
    return n.array([i for i in iterator])

def flatgen(l):
    import collections
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def drawWithMinDistance(xs,pdf,N,minDistance):
    res = []
    while len(res) != N:
        # print len(res)
        # pdb.set_trace()
        tmp = pdf.rvs(size=1)[0]
        if len(res):
            dists = n.linalg.norm(xs[res]-xs[tmp],axis=1)
            # neighs = 3
            # tree = spatial.cKDTree(xs[res])
            # dists = n.mean(tree.query([xs[tmp]],neighs+1)[0][:,1:neighs+1],1)
            if n.min(dists)>=minDistance: res.append(tmp)
        else:
            res.append(tmp)
    # pdb.set_trace()
    return res

def getDens(positions,xs,prob,minDistance=20/3.,
            # zmin=100*0.55/3.
            zmin=0
            ):

    N = 1
    bandwidth=0.2
    pdf = stats.rv_discrete(values=n.array([range(len(xs)),prob]))
    dists,rpoints,rdists = [],[],[]
    for isample in samples:
        tmp,tmpDists = [],[]
        indices = n.where(positions[isample].swapaxes(0,1)[:,2]>=zmin)[0]
        dists.append(getNNDists(positions[isample].swapaxes(0,1))[indices])
        for iN in range(N):
            # tmpXs,tmpDist = distsWithMinDistance(xs,pdf,len(positions[isample][0]),minDistance=5)
            tmpXs = xs[drawWithMinDistance(xs,pdf,len(positions[isample][0]),minDistance=minDistance)]
            indices = n.where(tmpXs[:,2]>=zmin)[0]
            # pdb.set_trace()
            tmp.append(tmpXs[indices])
            tmpDist = getNNDists(tmpXs)
            tmpDists.append(tmpDist[indices])
        rdists.append(tmpDists)
        rpoints.append(tmp)

    # x_grid = n.linspace(0, flatten([rdists,dists]).max(), 1000)
    x_grid = n.linspace(0, 30., 1000)
    rkde = stats.gaussian_kde(flatten(rdists),bw_method=bandwidth)
    skde = stats.gaussian_kde(flatten(dists),bw_method=bandwidth)

    rdens = rkde.evaluate(x_grid)
    sdens = skde.evaluate(x_grid)

    rdens = rdens/n.sum(rdens)
    sdens = sdens/n.sum(sdens)

    return x_grid,rdens,sdens,rpoints,[i.swapaxes(0,1) for i in positions]

if __name__ == "__main__":

    scales = n.array([3,3,3])
    iterations = 10

    res = []
    res2 = []

    mask = descriptors.Image(prefix+'/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/reference_mask.tif',
                             shape=(1920, 1920, 317),spacing=[0.29,0.29,0.55])
    positions = []
    samples = range(8)
    for isample in samples:
        tmp = pandas.read_excel('/data/malbert/quantification/imaris/4dpf/brain_%s_2.xls' %isample)
        x,y,z = n.array([n.array(tmp['Detailed'][1:]),n.array(tmp['Unnamed: 1'][1:]),n.array(tmp['Unnamed: 2'][1:])]).astype(n.float)
        positions.append((n.array([x,y,z]).swapaxes(0,1)/1000.*mask.spacing/scales).swapaxes(0,1))

    points = n.array([[],[],[]])
    for isample in samples:
        points = n.append(points,positions[isample],1)

    res.append(getDensity(points,mask,scales=scales))
    # res2.append(getDens(positions,res[0][2].swapaxes(0,1),res[0][3]))

    tmpIters = []
    for iteration in range(iterations):
        tmpIters.append(getDens(positions,res[0][2].swapaxes(0,1),res[0][3],minDistance=n.linspace(15/3.,20/3.,iterations)[iteration]))
    res2.append(tmpIters)

    # mask = descriptors.Image(prefix+'/data/malbert/atlas/references/50dpf_af_gfp/20150812/output/reference_mask.tif',
    #                                 shape=(1920, 1920, 319),spacing=[0.29,0.29,0.55])
    # positions = []
    # samples = range(9)
    # for isample in samples:
    #     tmp = pandas.read_excel('/data/malbert/quantification/imaris/5dpf/brain_%s_2.xls' %isample)
    #     x,y,z = n.array([n.array(tmp['Detailed'][1:]),n.array(tmp['Unnamed: 1'][1:]),n.array(tmp['Unnamed: 2'][1:])]).astype(n.float)
    #     positions.append((n.array([x,y,z]).swapaxes(0,1)/1000.*mask.spacing/scales).swapaxes(0,1))
    #
    # points = n.array([[],[],[]])
    # for isample in samples:
    #     points = n.append(points,positions[isample],1)
    #
    # res.append(getDensity(points,mask,scales=scales))
    # tmpIters = []
    # for iteration in range(iterations):
    #     tmpIters.append(getDens(positions,res[1][2].swapaxes(0,1),res[1][3],minDistance=n.linspace(15/3.,20/3.,iterations)[iteration]))
    # res2.append(tmpIters)
    #
    # mask = descriptors.Image(prefix+'/data/malbert/atlas/references/65dpf_af_gfp/20150810/output/reference_mask.tif',
    #                               shape=(1920, 1920, 365),spacing=[0.29,0.29,0.55])
    # positions = []
    # samples = range(10)
    # for isample in samples:
    #     tmp = pandas.read_excel('/data/malbert/quantification/imaris/6dpf/brain_%s_2.xls' %isample)
    #     x,y,z = n.array([n.array(tmp['Detailed'][1:]),n.array(tmp['Unnamed: 1'][1:]),n.array(tmp['Unnamed: 2'][1:])]).astype(n.float)
    #     positions.append((n.array([x,y,z]).swapaxes(0,1)/1000.*mask.spacing/scales).swapaxes(0,1))
    #
    # points = n.array([[],[],[]])
    # for isample in samples:
    #     points = n.append(points,positions[isample],1)
    #
    # res.append(getDensity(points,mask,scales=scales))
    #
    # tmpIters = []
    # for iteration in range(iterations):
    #     tmpIters.append(getDens(positions,res[2][2].swapaxes(0,1),res[2][3],minDistance=n.linspace(15/3.,20/3.,iterations)[iteration]))
    # res2.append(tmpIters)



for i in range(1):

    fig, ax = subplots(1, 1, figsize=(7,5))

    # ax.plot(res2[i][0][0]*3,n.mean([res2[i][iteration][1] for iteration in range(iterations)],0),'r')
    # ax.plot(res2[i][0][0]*3,n.mean([res2[i][iteration][2] for iteration in range(iterations)],0),'g')
    #
    # ax.set_title('%s dpf' %(i+4))
    # ax.set_xlabel('nn distance in um')
    # ax.set_ylabel('probability distribution')

    exp_random = n.mean([n.average(res2[i][iteration][0],weights=res2[i][iteration][1])*scales[0] for iteration in range(iterations)])
    exp_std_random = n.std([n.average(res2[i][iteration][0],weights=res2[i][iteration][1])*scales[0] for iteration in range(iterations)])
    exp_data = n.average(res2[i][0][0],weights=res2[i][0][2])*scales[0]
    print '%s dpf: nn distance expectancy: random %s data %s, error %s' %(4+i,exp_random,exp_data,exp_std_random)


    # ax.plot(x_grid,res2[i][0],'r')
    # ax.plot(x_grid,res2[i][1],'g')

# c,r = [],[]
# for isample in range(len(samples)):
#     for ipos,pos in enumerate(positions[isample].swapaxes(0,1)):
#         r.append(res2[-1][5][isample][0][ipos])
#         c.append(pos)
# ndimage.gaussian_filter((res[i][0]*n.power(10,9)).astype(n.uint16).swapaxes(0,2)[::-1,:,:],1)
# for i in range(3):
#     tmp = ndimage.gaussian_filter((res[i][0]*n.power(10,9)).astype(n.uint16).swapaxes(0,2)[::-1,:,:],1)
#     sitk.WriteImage(sitk.gifa(tmp),'/data/malbert/results/distribution/density3d_%sdpf_2.tif' %(i+4))


# ax.plot(res2[i][0][0]*3,n.mean([res2[i][iteration][1] for iteration in range(iterations)],0),'r')
# ax.plot(res2[i][0][0]*3,n.mean([res2[i][iteration][2] for iteration in range(iterations)],0),'g')
#
# ax.set_title('%s dpf' %(i+4))
# ax.set_xlabel('nn distance in um')
# ax.set_ylabel('probability distribution')


import matplotlib as mpl
mpl.rcParams['lines.linewidth'] = 2

mpl.rcParams['lines.color'] = 'white'
mpl.rcParams['patch.edgecolor'] = 'white'

mpl.rcParams['text.color'] = 'white'

mpl.rcParams['axes.facecolor'] = 'black'
mpl.rcParams['axes.edgecolor'] = 'white'
mpl.rcParams['axes.labelcolor'] = 'white'

mpl.rcParams['xtick.color'] = 'white'
mpl.rcParams['ytick.color'] = 'white'

mpl.rcParams['grid.color'] = 'white'

mpl.rcParams['figure.facecolor'] = 'black'
mpl.rcParams['figure.edgecolor'] = 'black'

mpl.rcParams['savefig.facecolor'] = 'black'
mpl.rcParams['savefig.edgecolor'] = 'black'


q=getDens(positions,res[0][2].swapaxes(0,1),res[0][3],minDistance=n.linspace(15/3.,20/3.,iterations)[iteration])
ran = q[3][3][0]
p = q[4][3]

fig, ax = subplots(1, 1, figsize=(12,8))
size=100
s1 = ax.scatter(ran[:,0]*3,-ran[:,1]*3+(ran[:,1]*3).max(),c='r',label='sampled from density pdf',s=size)
s2 = ax.scatter(p[:,0]*3,-p[:,1]*3+(p[:,1]*3).max(),c='g',label='microglia positions',s=size)
ax.legend(loc='upper left')

savefig("/data/malbert/results/distribution/scatter.png",bbox_inches='tight')

fig, ax = subplots(1, 1, figsize=(7,5))

ax.plot(res2[i][0][0]*3,n.mean([res2[i][iteration][1] for iteration in range(iterations)],0),'r')
ax.plot(res2[i][0][0]*3,n.mean([res2[i][iteration][2] for iteration in range(iterations)],0),'g')
savefig("/data/malbert/results/distribution/histogram.png",bbox_inches='tight')
