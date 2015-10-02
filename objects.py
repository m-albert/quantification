__author__ = 'malbert'

from dependencies import *

class Objects(object):

    def __init__(self, minSize = 100, minSizeMaxSeparation = (1000,30)):
        print 'instanciating Objects'
        self.minSize = minSize
        self.minSizeMaxSeparation = minSizeMaxSeparation
        self.timepointClass = h5py.Group
        return

    # def fromFile(self,rootFileName,hierarchy):
    #     # return descriptors.H5Pointer(rootFileName,hierarchy)
    #     return True

    def fromFrame(self,frame,tmpFile,tmpHierarchy):

        print 'extracting objects...'

        # filePointer = rootFile.create_group(tmpString)

        labels,N = ndimage.label(frame)#,structure=n.ones((3,3,3)))
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
        filing.toH5_hl(flabels,tmpFile,hierarchy=os.path.join(tmpHierarchy,'labels'))

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


class Skeletons(object):

    def __init__(self, nDilations):
        print 'instanciating Skeletons'
        self.nDilations = nDilations
        # self.timepointClass = descriptors.H5Pointer
        self.timepointClass = h5py.Group
        return

    # def fromFile(self,rootFileName,hierarchy):
    #     return descriptors.H5Pointer(rootFileName,hierarchy)

    def fromFrame(self,frame,tmpFile,tmpHierarchy):

        print 'extracting skeletons...'
        # filePointer['nDilations'] = self.nDilations
        filing.toH5_hl(self.nDilations,tmpFile,hierarchy=os.path.join(tmpHierarchy,'nDilations'))

        nodeValueGroup = tmpFile[tmpHierarchy].create_group('nodeValues')
        skeletonCoordGroup = tmpFile[tmpHierarchy].create_group('skeletonCoords')
        # skeletonImageGroup = filePointer.create_group('skeletonImage')

        # flabels = n.zeros(frame['labels'].shape,dtype=frame['labels'].dtype)
        nObjects = n.array(frame['nObjects'])

        labels = sitk.gifa((n.array(frame['labels'])>0).astype(n.uint8))
        labels = sitk.BinaryFillhole(labels)
        # pdb.set_trace()
        for i in range(self.nDilations):
            labels = sitk.BinaryDilate(labels)
        for i in range(self.nDilations):
            labels = sitk.BinaryErode(labels)

        labels = sitk.BinaryFillhole(labels)

        skeletonIm = skeletonizeImage(labels)
        # pdb.set_trace()
        # filePointer['skeletonLabels'] = skeletonIm
        filing.toH5_hl(skeletonIm,tmpFile,hierarchy=os.path.join(tmpHierarchy,'skeletonLabels'))


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

    def __init__(self):
        print 'instanciating Hulls'
        # self.timepointClass = descriptors.H5Pointer
        self.timepointClass = h5py.Group
        return

    # def fromFile(self,rootFileName,hierarchy):
    #     return descriptors.H5Pointer(rootFileName,hierarchy)

    def fromFrame(self,frame,tmpFile,tmpHierarchy):

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
