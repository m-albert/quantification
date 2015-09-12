__author__ = 'malbert'

from dependencies import *


class Objects(object):

    def __init__(self, minSize = 100, minSizeMaxSeparation = (1000,30)):
        print 'instanciating Objects'
        self.minSize = minSize
        self.minSizeMaxSeparation = minSizeMaxSeparation
        self.timepointClass = descriptors.H5Pointer
        return

    def fromFile(self,rootFileName,hierarchy):
        return descriptors.H5Pointer(rootFileName,hierarchy)
        # tmpFile = h5py.File(rootFileName)
        # return tmpFile[hierarchy]

    def fromFrame(self,frame,filePointer):

        print 'extracting objects...'

        # filePointer = rootFile.create_group(tmpString)

        labels,N = ndimage.label(frame)#,structure=n.ones((3,3,3)))
        sizes = imaging.getSizes(labels)
        objects = ndimage.find_objects(labels)

        # pdb.set_trace()
        filePointer['minSize'] = self.minSize
        validSizes1 = n.where(sizes>=self.minSizeMaxSeparation[0])[0]
        validSizes2 = n.array(list(set(n.where(sizes<self.minSizeMaxSeparation[0])[0]).intersection(set(n.where(sizes>=self.minSize)[0]))))
        # filePointer['nObjects'] = len(validSizes)
        # objectsGroup = filePointer.create_group('objects')

        bboxs,minCoordinates,coordinatess,osizes,centers = [],[],[],[],[]
        for iobject,obj in enumerate(validSizes1):

            print 'processing object %s' %iobject

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

        for iobject,obj in enumerate(validSizes2):
            bbox = objects[obj]
            coordinates = n.array(n.where(labels[bbox]==(obj+1))).swapaxes(0,1)
            size = sizes[obj]
            center = n.array([n.mean([bbox[idim].start,bbox[idim].stop]) for idim in range(3)])
            minCoordinate = n.array([bbox[i].start for i in range(3)])

            # distances = n.sqrt(n.sum(n.power((coordinatess+minCoordinates)-center,2),-1))
            absCoordinatess = n.array([coordinatess[i]+minCoordinates[i] for i in range(len(coordinatess))])
            distances = n.array([n.min(n.sqrt(n.sum(n.power(absCoordinatess[i]-center,2),-1)) for i in range(len(coordinatess)))])
            if n.min(distances) < self.minSizeMaxSeparation[1]: continue
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
            flabels[tuple(bboxs[iobj])][tuple(coordinatess[iobj].swapaxes(0,1))] = iobj

        filePointer['labels'] = flabels

        filePointer['nObjects'] = len(bboxs)
        filePointer['bboxs'] = n.array([[[bboxs[j][i].start,bboxs[j][i].stop] for i in range(3)] for j in range(len(bboxs))])
        filePointer['minCoordinates'] = minCoordinates
        filePointer['sizes'] = osizes
        filePointer['centers'] = centers
        coordinatesGroup = filePointer.create_group('coordinates')
        for i in range(len(coordinatess)):
            coordinatesGroup[str(i)] = coordinatess[i]

        # return descriptors.H5Pointer(rootFile.filename,nickname)
        return

    # from sklearn.cluster import MeanShift, estimate_bandwidth

def combineBboxes(bbox1,bbox2,coordinates1,coordinates2):
    minCoordinate1 = n.array([bbox1[i].start for i in range(3)])
    minCoordinate2 = n.array([bbox2[i].start for i in range(3)])
    maxCoordinate1 = n.array([bbox1[i].stop for i in range(3)])
    maxCoordinate2 = n.array([bbox2[i].stop for i in range(3)])
    minCoordinateN = n.min([minCoordinate1,minCoordinate2],0)
    maxCoordinateN = n.max([maxCoordinate1,maxCoordinate2],0)
    nbbox = tuple([slice(minCoordinateN[i],maxCoordinateN[i]) for i in range(3)])
    offset1 = minCoordinateN-minCoordinate1
    offset2 = minCoordinateN-minCoordinate2
    coordinatesN = n.append(coordinates1+offset1,coordinates2+offset2,0)
    centerN = n.array([n.mean([nbbox[idim].start,nbbox[idim].stop]) for idim in range(3)])
    return nbbox,minCoordinateN,coordinatesN,centerN


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

def find_centers(X, K):
    # Initialize to K random centers
    oldmu = n.random.sample(X, K)
    mu = n.random.sample(X, K)
    while not has_converged(mu, oldmu):
        oldmu = mu
        # Assign all points in X to clusters
        clusters = cluster_points(X, mu)
        # Reevaluate centers
        mu = reevaluate_centers(oldmu, clusters)
    return(mu, clusters)

def bounding_box(X):
    xmin, xmax = min(X,key=lambda a:a[0])[0], max(X,key=lambda a:a[0])[0]
    ymin, ymax = min(X,key=lambda a:a[1])[1], max(X,key=lambda a:a[1])[1]
    return (xmin,xmax), (ymin,ymax)

def gap_statistic(X):
    (xmin,xmax), (ymin,ymax) = bounding_box(X)
    # Dispersion for real distribution
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
            for n in range(len(X)):
                Xb.append([n.random.uniform(xmin,xmax),
                          n.random.uniform(ymin,ymax)])
            Xb = n.array(Xb)
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