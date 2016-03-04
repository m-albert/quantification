__author__ = 'malbert'

from dependencies import *

class Objects(object):

    def __init__(self,parent, minSize = 100, minSizeMaxSeparation = (1000,30)):
        print 'instanciating Objects'
        self.minSize = minSize
        self.minSizeMaxSeparation = minSizeMaxSeparation
        self.timepointClass = h5py.Group
        self.parent = parent
        return

    # def fromFile(self,rootFileName,hierarchy):
    #     # return descriptors.H5Pointer(rootFileName,hierarchy)
    #     return True

    def fromFrame(self,time,frame,tmpFile,tmpHierarchy):

        print 'extracting objects...'

        # filePointer = rootFile.create_group(tmpString)
        tmpGroup = tmpFile.create_group(tmpHierarchy)

        labels,N = ndimage.label(frame)#,structure=n.ones((3,3,3)))
        labels = labels.astype(n.uint16)
        sizes = imaging.getSizes(labels)
        objects = ndimage.find_objects(labels)

        # pdb.set_trace()
        # filePointer['minSize'] = self.minSize
        filing.toH5_hl(self.minSize,tmpFile,hierarchy=os.path.join(tmpHierarchy,'minSize'))

        validSizes1 = n.where(sizes>=self.minSizeMaxSeparation[0])[0]
        validSizes2 = n.array(list(set(n.where(sizes<self.minSizeMaxSeparation[0])[0]).intersection(set(n.where(sizes>=self.minSize)[0]))))
        # filePointer['nObjects'] = len(validSizes)
        # objectsGroup = filePointer.create_group('objects')

        bboxs,minCoordinates,coordinatess,osizes,centers = [],[],[],[],[]
        for iobject,obj in enumerate(validSizes1):

            # print 'processing object %s' %iobject

            # objectGroup = objectsGroup.create_group(str(iobject))

            bbox = objects[obj]
            coordinates = n.array(n.where(labels[bbox]==(obj+1))).swapaxes(0,1)
            size = sizes[obj]
            center = n.array([n.mean([bbox[idim].start,bbox[idim].stop]) for idim in range(3)])
            minCoordinate = n.array([bbox[i].start for i in range(3)])

            bboxs.append(bbox)
            minCoordinates.append(minCoordinate)
            coordinatess.append(coordinates)
            osizes.append(size)
            centers.append(center)

            # objectGroup['bbox'] = n.array([[bbox[i].start,bbox[i].stop] for i in range(3)])
            # objectGroup['minCoordinate'] = n.array([bbox[i].start for i in range(3)])
            # objectGroup['coordinates'] = coordinates
            # objectGroup['size'] = size
            # objectGroup['center'] = center

        bboxs = n.array(bboxs)
        minCoordinates = n.array(minCoordinates)
        coordinatess = n.array(coordinatess)
        osizes = n.array(osizes)
        centers = n.array(centers)

        # pdb.set_trace()

        for iobject,obj in enumerate(validSizes2):
            bbox = objects[obj]
            coordinates = n.array(n.where(labels[bbox]==(obj+1))).swapaxes(0,1)
            size = sizes[obj]
            center = n.array([n.mean([bbox[idim].start,bbox[idim].stop]) for idim in range(3)])
            minCoordinate = n.array([bbox[i].start for i in range(3)])

            # distances = n.sqrt(n.sum(n.power((coordinatess+minCoordinates)-center,2),-1))
            absCoordinatess = n.array([coordinatess[i]+minCoordinates[i] for i in range(len(coordinatess))])
            distances = n.array([n.min(n.sqrt(n.sum(n.power(absCoordinatess[i]-center,2),-1)) for i in range(len(coordinatess)))])
            if n.min(distances) > self.minSizeMaxSeparation[1]: continue
            else:
                targetObject = n.argmin(distances)
                distances = spatial.distance.cdist(minCoordinate + coordinates,
                                                   minCoordinates[targetObject] + coordinatess[targetObject])
                sourceCoord = n.argmin(n.min(distances,1))
                targetCoord = n.argmin(distances[sourceCoord])

                nbbox,nminCoordinate,ncoordinates,ncenter = combineBboxes(bbox,bboxs[targetObject],coordinates,coordinatess[targetObject])

                sourceCoord = ncoordinates[sourceCoord]
                targetCoord = ncoordinates[len(coordinates)+targetCoord]

                # connect objects
                x0, y0, z0 = sourceCoord
                x1, y1, z1 = targetCoord
                length = int(n.linalg.norm(targetCoord-sourceCoord))
                # length = int(n.hypot(x1-x0, y1-y0, z1-z0))
                x, y, z = n.linspace(x0, x1, length), n.linspace(y0, y1, length), n.linspace(z0, z1, length)
                addCoordinates = n.array([x.astype(n.int), y.astype(n.int), z.astype(n.int)]).swapaxes(0,1)
                pdb.set_trace()
                ncoordinates = n.append(ncoordinates,addCoordinates,0)

                # replace old object by new one
                bboxs[targetObject] = nbbox
                minCoordinates[targetObject] = nminCoordinate
                coordinatess[targetObject] = ncoordinates
                osizes[targetObject] = len(ncoordinates)
                centers[targetObject] = ncenter


        # produce final labels image

        flabels = n.zeros(labels.shape,dtype=labels.dtype)
        for iobj in range(len(bboxs)):
            flabels[tuple(bboxs[iobj])][tuple(coordinatess[iobj].swapaxes(0,1))] = iobj+1

        # filePointer['labels'] = flabels
        filing.toH5_hl(flabels,tmpFile,hierarchy=os.path.join(tmpHierarchy,'labels'),compression='jls')

        # filePointer['nObjects'] = len(bboxs)
        filing.toH5_hl(len(bboxs),tmpFile,hierarchy=os.path.join(tmpHierarchy,'nObjects'))

        tmpBboxs = n.array([[[bboxs[j][i].start,bboxs[j][i].stop] for i in range(3)] for j in range(len(bboxs))])
        # filePointer['bboxs'] = n.array([[[bboxs[j][i].start,bboxs[j][i].stop] for i in range(3)] for j in range(len(bboxs))])
        filing.toH5_hl(tmpBboxs,tmpFile,hierarchy=os.path.join(tmpHierarchy,'bboxs'))

        # filePointer['minCoordinates'] = minCoordinates
        filing.toH5_hl(minCoordinates,tmpFile,hierarchy=os.path.join(tmpHierarchy,'minCoordinates'))

        # filePointer['sizes'] = osizes
        filing.toH5_hl(osizes,tmpFile,hierarchy=os.path.join(tmpHierarchy,'sizes'))

        # filePointer['centers'] = centers
        filing.toH5_hl(centers,tmpFile,hierarchy=os.path.join(tmpHierarchy,'centers'))

        coordinatesGroup = tmpFile[tmpHierarchy].create_group('coordinates')
        for i in range(len(coordinatess)):
            # coordinatesGroup[str(i)] = coordinatess[i]
            filing.toH5_hl(coordinatess[i],tmpFile,hierarchy=os.path.join(tmpHierarchy,os.path.join('coordinates',str(i))))

        # return descriptors.H5Pointer(rootFile.filename,nickname)
        return

class Tracks(object):

    def __init__(self,parent,minTrackLength=2,maxObjectDisplacementPerDimension=10.,memory=0):
        self.minTrackLength = minTrackLength
        self.maxObjectDisplacementPerDimension = maxObjectDisplacementPerDimension
        self.memory = memory
        self.parent = parent
        return

    def fromBaseData(self,baseData,tmpFile,tmpHierarchy):

        print 'tracking objects...'

        # tmpFile[tmpHierarchy]['objects'] = baseData.hierarchy

        indexing = misc.customIndex(2)

        indices = []
        times = []

        # normalize features
        sizes = n.array([n.array(baseData[time]['sizes']) for time in baseData.times])
        sizeMax = n.max([n.median(sizes[isize]) for isize in range(len(sizes))])
        sizeNormFactor = self.maxObjectDisplacementPerDimension/float(sizeMax)

        nfeatures = 4
        features = [[] for i in range(nfeatures)]
        for time in baseData.times:
            for iobj in range(n.array(baseData[time]['nObjects'])):
                times.append(time)
                for ifeat in range(3):
                    features[ifeat].append(baseData[time]['centers'][iobj][ifeat])
                features[-1].append(baseData[time]['sizes'][iobj]*sizeNormFactor)
                indices.append(indexing.encode([time,iobj]))

        print features[-1]
        features = n.array(features)

        maxObjectDisplacement = n.sqrt(self.maxObjectDisplacementPerDimension**2*nfeatures)
        print 'maxObjectDisplacement %s' %maxObjectDisplacement
        dataDict = dict()
        dataDict['frame'] = times
        pos_columns = []
        for ifeat in range(nfeatures):
            dataDict[str(ifeat)] = features[ifeat]
            pos_columns.append(str(ifeat))
        # pos_columns = n.arange(nfeatures)
        dataFrame = pandas.DataFrame(dataDict,index=indices)
        # pdb.set_trace()
        trackResults = trackpy.link_df(dataFrame,
                                       maxObjectDisplacement,
                                       pos_columns=pos_columns,
                                       retain_index=True,
                                       memory=self.memory)
        # pdb.set_trace()
        nParticles = int(n.array(trackResults.particle).max())
        tracks = []
        for itrack in range(nParticles+1):
            tmpInds = n.where(n.array(trackResults.particle) == itrack)[0]
            if not len(tmpInds) >= self.minTrackLength: continue
            tmpTrack = []
            tmpTotInds = n.array(trackResults.index)
            for tmpInd in tmpInds:
                tmpTime,tmpObj = indexing.decode(tmpTotInds[tmpInd])
                # tmpTrack.append(objs[tmpTime][tmpObj])
                tmpTrack.append([tmpTime,tmpObj])
            tracks.append(tmpTrack)

        tmpGroup = tmpFile[tmpHierarchy].create_group('tracks')
        for itrack in range(len(tracks)):
            filing.toH5_hl(tracks[itrack],tmpFile,hierarchy=os.path.join(tmpHierarchy,'tracks/%s' %itrack))
        filing.toH5_hl(len(tracks),tmpFile,hierarchy=os.path.join(tmpHierarchy,'tracks/nTracks'))

        tmpGroup = tmpFile[tmpHierarchy].create_group('labels')
        labelDicts = n.array([n.zeros(int(n.array(baseData[time]['nObjects']))+1,dtype=n.uint16) for time in baseData.times])
        for itrack in range(len(tracks)):
            for itime in range(len(tracks[itrack])):
                trackObj = tracks[itrack][itime]
                labelDicts[list(baseData.times).index(trackObj[0])][trackObj[1]+1] = itrack+1

        print 'calculating labels'
        filing.toH5_hl(n.array(baseData.times),tmpFile,hierarchy=os.path.join(tmpHierarchy,'times'))
        for itime,time in enumerate(baseData.times):
            print 'label time %s' %time
            labels = labelDicts[itime][n.array(baseData[time]['labels'])]
            filing.toH5_hl(labels,tmpFile,hierarchy=os.path.join(tmpHierarchy,'labels/%s' %time),compression='jls')
        return

    def getTimePoint(self,tmpFile,tmpHierarchy,time):
        # pdb.set_trace()
        return tmpFile[tmpHierarchy]['labels'][str(time)]

    def getLength(self,tmpFile,tmpHierarchy):
        return len(n.array(tmpFile[tmpHierarchy]['times']))
        # return n.array(n.array(tmpFile[tmpHierarchy]['tracks']['nTracks']))[0]

    def getString(self,tmpFile,tmpHierarchy,string,baseData,**kargs):

        if string == 'nTracks':
            return n.array(tmpFile[tmpHierarchy]['tracks']['nTracks'])[0]

        elif '/' in string:
            """
            base,hierarchy,string = 'base_hierarchy_string'
            """
            # pdb.set_trace()
            split = string.split('/')
            string = split[-1]
            if len(split) == 3:
                base,hierarchy = split[:2]
            else: raise(Exception('wrong string'))
            # elif len(split) == 2:
            #     base,hierarchy = split[0],None
            # string = string[2:]
            times = n.array(tmpFile[tmpHierarchy]['tracks'][string])[:,0]
            objs = n.array(tmpFile[tmpHierarchy]['tracks'][string])[:,1]
            res=[]
            shapes,minCoords = [],[]
            pdb.set_trace()
            for itime,time in enumerate(times):
                # pdb.set_trace()
                # if tmpBbox
                tmpBbox = bbox(baseData[time]['bboxs'][objs[itime]])
                # if len(kargs.keys()):
                #     if 'hierarchy' in kargs.keys():
                #         tmpImage = kargs['base'][kargs['hierarchy']][str(time)]
                #     else:
                #         tmpImage = kargs['base'][time]
                # else:
                if not len(base) and len(hierarchy):
                    tmpImage = tmpFile[tmpHierarchy][hierarchy][str(time)][tmpBbox]
                elif len(base) and not len(hierarchy):
                    # get baseData evaluated at objects coordinates
                    tmpCoords = n.array(baseData[time]['coordinates'][str(objs[itime])])
                    # pdb.set_trace()
                    tmpData = self.parent.__dict__[base][time][tmpBbox]
                    tmpImage = n.zeros(tmpData.shape,dtype=tmpData.dtype)
                    tmpImage[tuple(tmpCoords.swapaxes(0,1))] = tmpData[tuple(tmpCoords.swapaxes(0,1))]
                    # tmpImage = tmpFile[base][time]
                elif len(base) and len(hierarchy):
                    # get other baseData hierarchy values like surface or size
                    # tmpImage = self.parent.__dict__[base][hierarchy][str(time)][tmpBbox]
                    tmpImage = self.parent.__dict__[base][time][hierarchy][objs[itime]]
                else:
                    tmpImage = tmpFile[tmpHierarchy]['labels'][str(time)][tmpBbox]
                    tmpImage = tmpImage/tmpImage.max()
                # tmp = tmpImage[tmpBbox]
                res.append(tmpImage)
                shapes.append(tmpImage.shape)
                minCoords.append(n.array(baseData[time]['minCoordinates'][objs[itime]]))

            if (len(base) and len(hierarchy)): return res
            minCoords = n.array(minCoords).astype(n.uint16)
            maxCoord = n.max(n.array(shapes+minCoords),0)
            minCoord = n.min(n.array(minCoords),0)
            maxShape = n.array(maxCoord-minCoord).astype(n.uint16)
            nres = n.zeros((len(times),)+tuple(maxShape),dtype=n.uint16)
            for itime,time in enumerate(times):
                #nres[itime,0:shapes[itime][0],0:shapes[itime][1],0:shapes[itime][2]] = res[itime]

                minIndex = n.round(minCoords[itime])-minCoord
                maxIndex = minIndex+shapes[itime]

                nres[(itime,)+tuple(slice(start,stop) for start,stop in zip(minIndex,maxIndex))] = res[itime]

            return nres
        else:
            return n.array(tmpFile[tmpHierarchy]['tracks'][string])

def getTracks(tmpGroup):
    nTracks = n.array(tmpGroup['nTracks'])
    tracks = []
    for itrack in range(nTracks):
        tracks.append(list(n.array(tmpGroup[str(itrack)])))
    return tracks

class Skeletons(object):

    def __init__(self,parent, nDilations):
        print 'instanciating Skeletons'
        self.nDilations = nDilations
        # self.timepointClass = descriptors.H5Pointer
        self.timepointClass = h5py.Group
        self.parent = parent
        return

    # def fromFile(self,rootFileName,hierarchy):
    #     return descriptors.H5Pointer(rootFileName,hierarchy)

    def fromFrame(self,time,frame,tmpFile,tmpHierarchy):
        tmpGroup = tmpFile.create_group(tmpHierarchy)
        print 'extracting skeletons...'
        # filePointer['nDilations'] = self.nDilations
        filing.toH5_hl(self.nDilations,tmpFile,hierarchy=os.path.join(tmpHierarchy,'nDilations'))

        nodeValueGroup = tmpFile[tmpHierarchy].create_group('nodeValues')
        skeletonCoordGroup = tmpFile[tmpHierarchy].create_group('skeletonCoords')
        # skeletonImageGroup = filePointer.create_group('skeletonImage')

        # flabels = n.zeros(frame['labels'].shape,dtype=frame['labels'].dtype)
        nObjects = n.array(frame['nObjects'])

        labels = sitk.gifa((n.array(frame['labels'])>0).astype(n.uint8))
        # labels = fillHole2d(labels)
        labels = dilateAndErode(labels,self.nDilations)
        # labels = sitk.BinaryFillhole(labels)
        # pdb.set_trace()
        # for i in range(self.nDilations):
        #     labels = sitk.BinaryDilate(labels)
        # for i in range(self.nDilations):
        #     labels = sitk.BinaryErode(labels)

        # labels = sitk.BinaryFillhole(labels)
        labels = fillHole2d(labels)

        skeletonIm = skeletonizeImage(labels)
        # pdb.set_trace()
        # filePointer['skeletonLabels'] = skeletonIm
        filing.toH5_hl(skeletonIm.astype(n.uint16),tmpFile,hierarchy=os.path.join(tmpHierarchy,'skeletonLabels'),compression='jls')


        for iobj in range(nObjects):
            # print 'processing object %s' %iobj

            tmpBbox = bbox(n.array(frame['bboxs'][iobj]))
            tmpCoords = skeletonIm[tmpBbox].nonzero()
            tmpNodeValues = skeletonIm[tmpBbox][tmpCoords]

            nodeValueGroup[str(iobj)] = tmpNodeValues
            skeletonCoordGroup[str(iobj)] = n.array(tmpCoords).swapaxes(0,1)

        tmpFile[tmpHierarchy]['labels'] = frame['labels']
        tmpFile[tmpHierarchy]['nObjects'] = frame['nObjects']
        tmpFile[tmpHierarchy]['minCoordinates'] = frame['minCoordinates']

        return

class Hulls(object):

    def __init__(self,parent):
        print 'instanciating Hulls'
        # self.timepointClass = descriptors.H5Pointer
        self.timepointClass = h5py.Group
        self.parent = parent
        return

    # def fromFile(self,rootFileName,hierarchy):
    #     return descriptors.H5Pointer(rootFileName,hierarchy)

    def fromFrame(self,time,frame,tmpFile,tmpHierarchy):
        tmpGroup = tmpFile.create_group(tmpHierarchy)
        print 'extracting convex hulls...'

        verticesGroup = tmpFile[tmpHierarchy].create_group('nodeValues')

        nObjects = n.array(frame['nObjects'])
        labels = n.array(frame['labels'])
        minCoordinates = n.array(frame['minCoordinates'])

        # totVertices = []
        radius = 5
        x,y,z = n.mgrid[0:2*radius,0:2*radius,0:2*radius]
        tmpIndices = n.where(n.sum(n.power(x,2)+n.power(y,2)+n.power(z,2))<=(radius*radius))
        pattern = n.zeros((2*radius,2*radius,2*radius))
        pattern[tmpIndices] = nObjects + 1
        for iobj in range(nObjects):

            points = n.array(frame['skeletonCoords'][str(iobj)])

            ch = spatial.ConvexHull(points)
            vertices = points[ch.vertices]
            verticesGroup[str(iobj)] = vertices
            # pdb.set_trace()
            for vertex in vertices:
                tmpSlices = tuple(slice(int(minCoordinates[iobj][i]+vertex[i]-radius),
                                        int(minCoordinates[iobj][i]+vertex[i]+radius)) for i in range(3))
                # labels[tmpSlices] = pattern
                labels[tmpSlices] = nObjects+1
            # totVertices.append(vertices)

        # filePointer['labels'] = labels
        filing.toH5_hl(labels,tmpFile,hierarchy=os.path.join(tmpHierarchy,'labels'))

        return

def fillHole2d(im):
    wasSitk = False
    if type(im) == sitk.Image:
        im = sitk.gafi(im).astype(n.uint16)
        wasSitk = True

    def perform(image):
        res = n.array([ndimage.binary_fill_holes(i) for i in image]).astype(image.dtype)
        # fill = res-image
        # objects = ndimage.measurements.find_objects(fill)
        # sizes = imaging.getSizes(fill)
        # for iobj in range(len(objects)):
        #     tmpSlice = list(objects[iobj])
        #     len1 = tmpSlice[1].stop-tmpSlice[1].start
        #     len2 = tmpSlice[2].stop-tmpSlice[2].start
        #     tmpSlice[0] = slice(tmpSlice[0].start-n.mean([len1,len2])/2.,tmpSlice[0].stop+n.mean([len1,len2])/2.)
        #     tmpSlice = tuple(tmpSlice)
        #     shape = res[tmpSlice].shape
        #     center = shape/2
        #     x,y,z = n.mgrid[0:shape[0],0:shape[1],0:shape[2]]
        #     ((x-center[0])**2+(y-center[1])**2+(z-center[2])**2)<
        #     ellipse[n.where(ellipse)]

        return res

    res = perform(im)
    res = perform(res.swapaxes(0,1)).swapaxes(0,1)
    res = perform(res.swapaxes(0,2)).swapaxes(0,2)
    res = perform(res)
    res = perform(res.swapaxes(0,1)).swapaxes(0,1)
    res = perform(res.swapaxes(0,2)).swapaxes(0,2)

    if wasSitk:
        res = sitk.gifa(res)
    return res

# def fillHolePlus(im):
#     wasSitk = False
#     if type(im) == sitk.Image:
#         im = sitk.gafi(im).astype(n.uint16)
#         wasSitk = True
#
#     res = fillHole2d(im)
#
#     # fills = res-im
#
#     labels,N = ndimage.measurements.find_objects(fills)
#     for
#
#     res = fillHole2d(res)
#
#     if wasSitk:
#         res = sitk.gifa(res)
#     return res

def dilateAndErode(im,N):
    if not N: return im
    wasNumpy = False
    if type(im) == n.ndarray:
        im = sitk.gifa(im)
        wasNumpy = True

    for i in range(N):
        im = sitk.BinaryDilate(im)
    for i in range(N):
        im = sitk.BinaryErode(im)

    if wasNumpy:
        im = sitk.gafi(im)
    return im



def skeletonizeImage(im):

    tmpString = 'skeletonization_'+str(n.random.randint(0,1000000000000000,1)[0])
    tmpFolder = os.path.join(tmpDir,tmpString)
    os.mkdir(tmpFolder)

    filePath = os.path.join(tmpFolder,'tmp%09d.tif' %0)
    sitk.WriteImage(sitk.Cast(im,sitk.sitkUInt8),filePath)

    cmd = ("%s %s %s" %(fijiPath,os.path.join(projectDir,'skeletonize.py'),tmpFolder)).split(" ")
    subprocess.Popen(cmd).wait()

    res = sitk.gafi(sitk.ReadImage(filePath)/255).astype(n.uint8)
    # pdb.set_trace()
    os.remove(filePath)
    os.rmdir(tmpFolder)

    kernel = n.ones((3,3,3))
    kernel[1,1,1] = 0
    res = ndimage.convolve(res,kernel,mode='constant')*res

    return res

def getSkeletonNodes(im,coords=None):
    if coords is None:
        coords = n.array(im.nonzero())

    kernel = n.ones((3,3,3))
    kernel[1,1,1] = 0
    im = ndimage.convolve(im,kernel,mode='constant')
    nodeValues = im[tuple(coords)]
    return nodeValues

def getSkeletonNodesOld(im,coords=None):

    shape = im.shape

    if coords is None:
        coords = n.array(im.nonzero())

    convBox = n.ones((3,3,3))
    convIndices = n.array(convBox.nonzero()) - 1
    nodeValues = n.zeros(len(coords[0]))
    for icoord in range(len(coords[0])):
        tmpCoord = coords[:,icoord]
        tmpIndices = convIndices + tmpCoord.reshape((3,1))
        nodeValues[icoord] = n.sum(ndimage.map_coordinates(im,tmpIndices))-1
        # nodeValues[icoord] = n.sum(im[tuple(tmpIndices)])-1

    # pdb.set_trace()
    validNodeValues = [1,3,4,5,6,7]
    # skeletonNodes = coords[:,n.min([n.abs(nodeValues-validNodeValues[i]) for i in range(len(validNodeValues))],0)==0]
    nodeValues[n.min([n.abs(nodeValues-validNodeValues[i]) for i in range(len(validNodeValues))],0)!=0] = 0
    return nodeValues


def combineBboxes(bbox1,bbox2,coordinates1,coordinates2):
    minCoordinate1 = n.array([bbox1[i].start for i in range(3)])
    minCoordinate2 = n.array([bbox2[i].start for i in range(3)])
    maxCoordinate1 = n.array([bbox1[i].stop for i in range(3)])
    maxCoordinate2 = n.array([bbox2[i].stop for i in range(3)])
    minCoordinateN = n.min([minCoordinate1,minCoordinate2],0)
    maxCoordinateN = n.max([maxCoordinate1,maxCoordinate2],0)
    pdb.set_trace()
    nbbox = tuple([slice(minCoordinateN[i],maxCoordinateN[i]) for i in range(3)])
    offset1 = minCoordinateN-minCoordinate1
    offset2 = minCoordinateN-minCoordinate2
    coordinatesN = n.append(coordinates1-offset1,coordinates2-offset2,0)
    centerN = n.array([n.mean([nbbox[idim].start,nbbox[idim].stop]) for idim in range(3)])
    return nbbox,minCoordinateN,coordinatesN,centerN


def bbox(ar):
    return tuple(slice(ar[i][0],ar[i][1]) for i in range(3))


def cluster_points(X, mu):
    clusters  = {}
    for x in X:
        bestmukey = min([(i[0], n.linalg.norm(x-mu[i[0]])) \
                    for i in enumerate(mu)], key=lambda t:t[1])[0]
        try:
            clusters[bestmukey].append(x)
        except KeyError:
            clusters[bestmukey] = [x]
    return clusters

def reevaluate_centers(mu, clusters):
    newmu = []
    keys = sorted(clusters.keys())
    for k in keys:
        newmu.append(n.mean(clusters[k], axis = 0))
    return newmu

def has_converged(mu, oldmu):
    return (set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu]))

def find_centers2(X, K):
    # Initialize to K random centers
    oldmu = random.sample(X, K)
    mu = random.sample(X, K)
    while not has_converged(mu, oldmu):
        oldmu = mu
        # Assign all points in X to clusters
        clusters = cluster_points(X, mu)
        # Reevaluate centers
        mu = reevaluate_centers(oldmu, clusters)
    return(mu, clusters)

def find_centers3(X,k,spacing=[2,1,1]):
    spacing = n.array(spacing)
    X = X*spacing
    centers,distortion = cluster.vq.kmeans(X,k)
    X = X/spacing
    cd = []
    for c in centers:
        cd.append(n.linalg.norm(X-c,axis=1))
    # pdb.set_trace()
    cd = n.array(cd)
    cd = n.argmin(cd,0)
    res = []
    for i in range(k):
        res.append(X[n.where(cd==i)[0]])
    return(centers,res)

def find_centers(X,k,spacing=[2,1,1]):
    from sklearn.cluster import AgglomerativeClustering
    spacing = n.array(spacing)
    X = X*spacing
    cl = AgglomerativeClustering(n_clusters=k)
    cl.fit(X)
    cd = cl.labels_
    X = X/spacing
    res = []
    for i in range(k):
        res.append(X[n.where(cd==i)[0]])
    return([n.mean(res[i],0) for i in range(k)],res)

# def bounding_box(X):
#     xmin, xmax = min(X,key=lambda a:a[0])[0], max(X,key=lambda a:a[0])[0]
#     ymin, ymax = min(X,key=lambda a:a[1])[1], max(X,key=lambda a:a[1])[1]
#     return (xmin,xmax), (ymin,ymax)

# def gap_statisticOrig(X):
#     (xmin,xmax), (ymin,ymax) = bounding_box(X)
#     # Dispersion for real distribution
#     ks = range(1,5)
#     Wks = n.zeros(len(ks))
#     Wkbs = n.zeros(len(ks))
#     sk = n.zeros(len(ks))
#     for indk, k in enumerate(ks):
#         mu, clusters = find_centers(X,k)
#         Wks[indk] = n.log(Wk(mu, clusters))
#         # Create B reference datasets
#         B = 10
#         BWkbs = n.zeros(B)
#         for i in range(B):
#             Xb = []
#             for bla in range(len(X)):
#                 Xb.append([random.uniform(xmin,xmax),
#                           random.uniform(ymin,ymax)])
#             Xb = n.array(Xb)
#             mu, clusters = find_centers(Xb,k)
#             BWkbs[i] = n.log(Wk(mu, clusters))
#         Wkbs[indk] = sum(BWkbs)/B
#         sk[indk] = n.sqrt(sum((BWkbs-Wkbs[indk])**2)/B)
#     sk = sk*n.sqrt(1+1/B)
#     return(ks, Wks, Wkbs, sk)

def gap_statistic3(X,objects,N=100):
    maxCoord = n.max(X,0)
    # (xmin,xmax), (ymin,ymax) = bounding_box(X)
    # Dispersion for real distribution
    X = X[n.random.choice(n.arange(len(X)),size=N)]
    ks = range(1,10)
    Wks = n.zeros(len(ks))
    Wkbs = n.zeros(len(ks))
    sk = n.zeros(len(ks))
    for indk, k in enumerate(ks):
        mu, clusters = find_centers(X,k)
        Wks[indk] = n.log(Wk(mu, clusters))
        # Create B reference datasets
        B = 10
        BWkbs = n.zeros(B)
        for i in range(B):
            Xb = []
            for bla in range(len(X)):
                Xb.append([random.uniform(0,maxCoord[0]),random.uniform(0,maxCoord[1]),random.uniform(0,maxCoord[2])])
            Xb = n.array(Xb)
            mu, clusters = find_centers(Xb,k)
            BWkbs[i] = n.log(Wk(mu, clusters))
        Wkbs[indk] = sum(BWkbs)/B
        sk[indk] = n.sqrt(sum((BWkbs-Wkbs[indk])**2)/B)
    sk = sk*n.sqrt(1+1/B)
    return(ks, Wks, Wkbs, sk)

def gap_statistic2(X,objects,N=100):
    # (xmin,xmax), (ymin,ymax) = bounding_box(X)
    # Dispersion for real distribution
    X = X[n.random.choice(n.arange(len(X)),size=N)]
    ks = range(1,5)
    Wks = n.zeros(len(ks))
    Wkbs = n.zeros(len(ks))
    sk = n.zeros(len(ks))
    for indk, k in enumerate(ks):
        mu, clusters = find_centers(X,k)
        Wks[indk] = n.log(Wk(mu, clusters))
        # Create B reference datasets
        B = n.array(objects['nObjects'])
        BWkbs = n.zeros(B)
        for i in range(B):
            Xb = []
            coords = n.array(objects['coordinates'][str(i)])
            Xb = coords[n.random.choice(n.arange(len(coords)),size=N)]
            # for bla in range(len(X)):
            #     Xb.append([random.uniform(xmin,xmax),
            #               random.uniform(ymin,ymax)])
            # Xb = n.array(Xb)
            mu, clusters = find_centers(Xb,k)
            BWkbs[i] = n.log(Wk(mu, clusters))
        Wkbs[indk] = sum(BWkbs)/B
        sk[indk] = n.sqrt(sum((BWkbs-Wkbs[indk])**2)/B)
    sk = sk*n.sqrt(1+1/B)
    return(ks, Wks, Wkbs, sk)

def Wk(mu, clusters):
    K = len(mu)
    return sum([n.linalg.norm(mu[i]-c)**2/(2*len(c)) \
               for i in range(K) for c in clusters[i]])

# from objects import Wk,gap_statistic
#
# wkbs = []
# npoints = 100
# for iobj in range(n.array(bs[0].objects[0]['nObjects'])):
#     print iobj
#     coords = n.array(bs[0].objects[0]['coordinates'][str(iobj)])
#     coords = coords[n.random.choice(n.arange(len(coords)),size=npoints)]
#     wkbs.append(n.log(Wk([n.mean(coords,0)],[coords])))
#
# mwkbs = n.mean(wkbs)

# def main():
#     # Generate some data with anisotropic cells...
#     # x,y,and z will range from -2 to 2, but with a
#     # different (20, 15, and 5 for x, y, and z) number of steps
#     x,y,z = np.mgrid[-2:2:20j, -2:2:15j, -2:2:5j]
#     r = np.sqrt(x**2 + y**2 + z**2)
#
#     dx, dy, dz = [np.diff(it, axis=a)[0,0,0] for it, a in zip((x,y,z),(0,1,2))]
#
#     # Your actual data is a binary (logical) array
#     max_radius = 1.5
#     data = (r <= max_radius).astype(np.int8)
#
#     ideal_volume = 4.0 / 3 * max_radius**3 * np.pi
#     coarse_volume = data.sum() * dx * dy * dz
#     est_volume = vtk_volume(data, (dx, dy, dz), (x.min(), y.min(), z.min()))
#
#     coarse_error = 100 * (coarse_volume - ideal_volume) / ideal_volume
#     vtk_error = 100 * (est_volume - ideal_volume) / ideal_volume
#
#     print 'Ideal volume', ideal_volume
#     print 'Coarse approximation', coarse_volume, 'Error', coarse_error, '%'
#     print 'VTK approximation', est_volume, 'Error', vtk_error, '%'

def vtk_volume(data, spacing=(1,1,1), origin=(0,0,0)):
    data = data.astype(n.int8)
    from tvtk.api import tvtk
    data[data == 0] = -1
    grid = tvtk.ImageData(spacing=spacing, origin=origin)
    grid.point_data.scalars = data.T.ravel() # It wants fortran order???
    grid.point_data.scalars.name = 'scalars'
    grid.dimensions = data.shape

    iso = tvtk.ImageMarchingCubes(input=grid)
    mass = tvtk.MassProperties(input=iso.output)
    return mass.volume

def vtk_surface(data, spacing=(1,1,1), origin=(0,0,0)):
    data = data.astype(n.int8)
    from tvtk.api import tvtk
    data[data == 0] = -1
    grid = tvtk.ImageData(spacing=spacing, origin=origin)
    grid.point_data.scalars = data.T.ravel() # It wants fortran order???
    grid.point_data.scalars.name = 'scalars'
    grid.dimensions = data.shape

    iso = tvtk.ImageMarchingCubes(input=grid)
    mass = tvtk.MassProperties(input=iso.output)
    return mass.surface_area