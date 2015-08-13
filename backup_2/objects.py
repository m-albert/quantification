
__author__ = 'malbert'

from dependencies import *

class Object(object):
    def __init__(self):
        self.debug = False

        self.bbox = None                            # box containing relevant pixels
        self.coordinates = None                     # relative to bbox
        self.brain = None

        self.skeletonCoords = None
        self.skeletonNodes = None
        self.nodeValues = None

        self.center = None
        self.time = None
        self.size = None

def getObjectImage(obj,attribute='coordinates'):
    tmp = n.zeros(tuple([obj.bbox[i].stop-obj.bbox[i].start for i in range(3)]),dtype=n.uint8)
    if obj.__getattribute__(attribute) is None: raise(Exception('no skeleton computed yet'))
    tmp[obj.__getattribute__(attribute)] = 1
    return tmp

def extractObjects(brain,threshold=0.5,sizeThreshold=20,channel=0):
    print 'extracting objects...'
    snaps = []
    label = []
    for itime in range(brain.dimt):

        tmpSnaps = []
        tmpBin = (brain.segmentation[channel][itime] > threshold)
        labels,N = ndimage.label(tmpBin)#,structure=n.ones((3,3,3)))
        sizes = imaging.getSizes(labels)
        objects = ndimage.find_objects(labels)

        label.append(labels)

        for iobject in n.where(sizes>=sizeThreshold)[0]:

            newObject = Object()

            newObject.bbox = objects[iobject]
            #newObject.coordinates = n.nonzero(labels[newObject.bbox])
            newObject.coordinates = n.where(labels[newObject.bbox]==(iobject+1))

            newObject.time = itime
            newObject.size = sizes[iobject]
            newObject.center = n.array([n.mean([newObject.bbox[idim].start,newObject.bbox[idim].stop]) for idim in range(3)])
            newObject.brain = brain

            tmpSnaps.append(newObject)

        snaps.append(tmpSnaps)

    brain.objectSnaps[channel] = snaps
    brain.lastThreshold = threshold

    return label

def trackObjects(brain,channel=0,minTrackLength=5,maxObjectDisplacementPerDimension=10.,memory=0):
    print 'tracking objects...'

    indexing = misc.customIndex(2)

    objs = brain.objectSnaps[channel]
    indices = []
    times = []

    # normalize features
    sizes = n.array(misc.getAttributeFromAll(objs,'size'))
    sizeNormFactor = maxObjectDisplacementPerDimension/float(sizes.max())

    nfeatures = 4
    features = [[] for i in range(nfeatures)]
    for itime in range(brain.dimt):
        for iobjs in range(len(objs[itime])):
            times.append(objs[itime][iobjs].time)
            for ifeat in range(3):
                features[ifeat].append(objs[itime][iobjs].center[ifeat])
            features[-1].append(objs[itime][iobjs].size*sizeNormFactor)
            indices.append(indexing.encode([itime,iobjs]))

    print features[-1]

    maxObjectDisplacement = n.sqrt(maxObjectDisplacementPerDimension**2*nfeatures)
    print 'maxObjectDisplacement %s' %maxObjectDisplacement
    dataDict = dict()
    dataDict['frame'] = times
    pos_columns = []
    for ifeat in range(nfeatures):
        dataDict[str(ifeat)] = features[ifeat]
        pos_columns.append(str(ifeat))
    dataFrame = pandas.DataFrame(data=dataDict,index=indices)
    #pdb.set_trace()
    trackResults = trackpy.link_df(dataFrame,
                                   maxObjectDisplacement,
                                   pos_columns=pos_columns,
                                   retain_index=True,
                                   memory=memory)
    nParticles = int(n.array(trackResults.particle).max())
    tracks = []
    for itrack in range(nParticles):
        tmpInds = n.where(n.array(trackResults.particle) == itrack)[0]
        if not len(tmpInds) >= minTrackLength: continue
        tmpTrack = []
        tmpTotInds = n.array(trackResults.index)
        for tmpInd in tmpInds:
            tmpTime,tmpObj = indexing.decode(tmpTotInds[tmpInd])
            tmpTrack.append(objs[tmpTime][tmpObj])
        tracks.append(tmpTrack)

    brain.tracks[channel] = tracks

    return

def draw(brain,channel=0,objList=None,overSegmentation=True,colorDimension=1,cmap='rainbow',proj=None,attribute='coordinates',axOrder=[0,3,1,2]):
    if overSegmentation:
        #res = n.copy(brain.segmentation[channel])
        res = (brain.segmentation[channel]>0.5).astype(n.uint16)
    else:
        res = n.zeros(brain.segmentation[channel].shape,dtype=n.uint16)
    if objList is None:
        objList = brain.tracks[channel]
    for iobj in range(len(objList)):
        if not colorDimension: color = 1
        for iobjtime in range(len(objList[iobj])):
            if colorDimension == 1: color = iobj+2
            elif colorDimension == 2: color = iobjtime+2
            obj = objList[iobj][iobjtime]
            res[obj.time][obj.bbox][obj.__getattribute__(attribute)] = color
            #res[obj.time][obj.bbox] = color
    if proj is None:
        tifffile.imshow(misc.sortAxes(res,axOrder),interpolation='none',cmap=cmap)
    else:
        tifffile.imshow(n.max(misc.sortAxes(res,axOrder),proj+1),interpolation='none',cmap=cmap)
    return

def show(data,cmap='rainbow',proj=None):
    if proj is None:
        tifffile.imshow(misc.sortAxes(data,axOrder),interpolation='none',cmap=cmap)
    else:
        tifffile.imshow(n.max(misc.sortAxes(data,axOrder),proj+1),interpolation='none')
    return

def getImages(brain,channel=0,objList=None,overSegmentation=True,colorDimension=1,attribute='coordinates'):
    if overSegmentation:
        #res = n.copy(brain.segmentation[channel])
        res = (brain.segmentation[channel]>0.5).astype(n.uint16)
    else:
        res = n.zeros(brain.segmentation[channel].shape,dtype=n.uint16)
    if objList is None:
        objList = brain.tracks[channel]
    for iobj in range(len(objList)):
        if not colorDimension: color = 1
        for iobjtime in range(len(objList[iobj])):
            if colorDimension == 1: color = iobj+2
            elif colorDimension == 2: color = iobjtime+2
            obj = objList[iobj][iobjtime]
            res[obj.time][obj.bbox][obj.__getattribute__(attribute)] = color
    return res


def getDistanceToClosestPoint(b,sourcePoints,targetPoints):

    tree = spatial.cKDTree(sourcePoints) #3xN
    dist,inds = tree.query(sourcePoints,1,distance_upper_bound = n.sqrt(2*b.dimx**2))

    return dist