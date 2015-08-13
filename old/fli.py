__author__ = 'malbert'


from dependencies import *
import multiprocessing

def getClosestDistancesOld(flimage,mask=None):
    flis = n.array(flimage.nonzero())
    if mask is None:
        maskp = n.array(n.mgrid[0:mask.shape[0],0:mask.shape[1],0:mask.shape[2]])
    else:
        maskp = mask.nonzero()

    maxMem = 2000000000 #2gb size
    stepSize = n.ceil(maxMem/maskp.shape[1])
    print maskp.shape[1]
    print stepSize
    results = n.zeros(maskp.shape[1],dtype=n.float32)
    for ipoints in range(0,maskp.shape[1],stepSize):
        print ipoints
        results[ipoints:ipoints+stepSize] = n.min(n.array([n.linalg.norm()]),0)



def getClosestDistances(b,im1,im2,mask):
    # pdb.set_trace()
    im1 = (beads.transformStackAndRef(b.registrationParams,im1,mask)*mask)>0
    im2 = (beads.transformStackAndRef(b.registrationParams,im2,mask)*mask)>0
    ims = (microglia.skeletonizeImage(im2)>0)

    mask = mask>0

    # pdb.set_trace()

    p1 = n.array(sitk.gafi(im1).nonzero()).swapaxes(0,1)
    p2 = n.array(sitk.gafi(ims).nonzero()).swapaxes(0,1)
    p3 = n.array(sitk.gafi(mask-im2).nonzero()).swapaxes(0,1)

    for idim in range(3):
        p1[:,2-idim] *= mask.GetSpacing()[idim]
        p2[:,2-idim] *= mask.GetSpacing()[idim]
        p3[:,2-idim] *= mask.GetSpacing()[idim]

    print 'using spacing %s for point distances' %b.spacing
    # pdb.set_trace()
    tree = spatial.cKDTree(p2)
    # pdb.set_trace()
    dists,inds = tree.query(p1,1,distance_upper_bound = n.max(im1.GetSize()))
    dists0,inds0 = tree.query(p3,1,distance_upper_bound = n.max(im1.GetSize()))

    control = sitk.gafi(mask-im2).astype(n.float)
    control[control.nonzero()] = dists0

    return dists,dists0,control,im1,im2