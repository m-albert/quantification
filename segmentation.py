__author__ = 'malbert'

from dependencies import *

config['segmentationPath'] = 'segmentation'

class Segmentation(descriptors.ChannelData):

    # class for handling segmentation data
    # initial task: threshold and connected components
    # relies on parent having prediction channel
    nickname = 'segmentation'

    def __init__(self,parent,baseData,nickname,threshold = 0.5, sizeThresholds = [20,n.power(10,7)],*args,**kargs):
        print 'creating segmentation \"%s\" of basedata %s' %(nickname,baseData.nickname)

        self.baseData = baseData
        # self.baseData = parent.classData[baseDataClass.__name__]
        self.timepointClass = ObjectGroup

        self.dir = self.baseData.dir
        self.fileNameFormat = self.baseData.fileNameFormat
        # self.dir = parent.classData[baseDataClass.__name__][channel].dir

        self.threshold = threshold
        self.sizeThresholds = sizeThresholds

        super(Segmentation,self).__init__(parent,nickname,*args,**kargs)

    def getLabels(self,shape,objDict,attribute='coordinates'):

        # pdb.set_trace()
        res = n.zeros(shape,dtype=n.uint16)
        for iobj in objDict.keys():
            try:
                iobj = int(iobj)
            except:
                continue

            obj = objDict[str(iobj)]
            bbox = tuple([slice(i[0],i[1]) for i in obj['bbox']])
            res[bbox][tuple(obj[attribute])] = iobj
        return res

    def labels(self,times,absTime=False):
        if absTime:
            return descriptors.Tupable(dict(zip(times,[i['labels'] for i in self[times]])))
        else:
            return descriptors.Tupable(dict(zip(times,[i['labels'] for i in self(times)])))


    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            tmpFile = h5py.File(self.baseData.getFileName(time))
            if config['segmentationPath'] in tmpFile.keys():
                if redo:
                    del tmpFile[config['segmentationPath']]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    outDict[time] = self.timepointClass(self.getFileName(time))
            else:
                toDoTimes.append(time)
            tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)


        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):
            print "segmenting (connected component and size filter) %s time %06d" %(self.baseData.nickname,time)

            tmpFile = h5py.File(self.baseData[time].file.filename)
            tmpGroupGroup = tmpFile.create_group(config['segmentationPath'])

            tmpBin = (n.array(self.baseData[time]) > self.threshold)
            labels,N = ndimage.label(tmpBin)#,structure=n.ones((3,3,3)))
            sizes = imaging.getSizes(labels)
            objects = ndimage.find_objects(labels)

            validObjects = list(set(n.where(sizes>=self.sizeThresholds[0])[0]).intersection(set(n.where(sizes<self.sizeThresholds[1])[0])))
            for iiobject,iobject in enumerate(validObjects):

                tmpObjectGroup = tmpGroupGroup.create_group(str(iiobject))

                bbox = objects[iobject]
                tmpObjectGroup['bbox'] = n.array([[i.start,i.stop] for i in bbox]).astype(n.uint16)
                #newObject.coordinates = n.nonzero(labels[newObject.bbox])
                tmpObjectGroup['coordinates'] = n.array(n.where(labels[bbox]==(iobject+1)))

                tmpObjectGroup['size'] = sizes[iobject]
                tmpObjectGroup['time'] = time
                tmpObjectGroup['center'] = n.array([n.mean([bbox[idim].start,bbox[idim].stop]) for idim in range(3)])


            tmpGroupGroup['labels'] = self.getLabels(tmpBin.shape,tmpGroupGroup)

            tmpFile.close()

            outDict[time] = self.timepointClass(self.baseData.getFileName(time))

        return outDict


class ObjectGroup(object):

    # replace by simple h5py.File?

    def __init__(self,filename):
        print 'instanciating object group for file %s' %filename

        self.filename = filename
        self.file = None

        # self.summaryTupable = self.__get__(self,ObjectGroup)
        self.summaryTupable = None
        return

    def __get__(self,instance,owner):

        if self.summaryTupable is None:

            if self.file is None:
                self.file = h5py.File(self.filename)

            returnDict = dict()
            tmpGroup = self.file[config['segmentationPath']]
            for iobj in tmpGroup.keys():
                try:
                    iobj = int(iobj)
                except:
                    continue
                tmpObject = Object()
                tmpObject.bbox = tuple([slice(i[0],i[1]) for i in tmpGroup[str(iobj)]['bbox']])
                tmpObject.coordinates = tmpGroup[str(iobj)]['coordinates']
                tmpObject.center = n.array(tmpGroup[str(iobj)]['center'])
                tmpObject.size = n.array(tmpGroup[str(iobj)]['size'])
                tmpObject.time = n.array(tmpGroup[str(iobj)]['time'])

                returnDict[int(iobj)] = tmpObject
            returnDict['labels'] = tmpGroup['labels']

            self.summaryTupable = descriptors.Tupable(returnDict)

        return self.summaryTupable


        # return self.file[config['segmentationPath']]
        # tmpGroup = self.file[config['segmentationPath']]
        # tmpObject = Object()
        # tmpObject.bbox = tuple([slice(i[0],i[1]) for i in n.array(tmpGroup['bbox'])])
        # tmpObject.coordinates = n.array(tmpGroup['coordinates'])
        # tmpObject.size = n.array(tmpGroup['size'])
        # tmpObject.center = n.array(tmpGroup['center'])
        #
        # return tmpObject

    def __getitem__(self,item):

        return self.__get__(self,self,ObjectGroup)[str(item)]

    def __set__(self,value):
        raise(Exception('no setting possible!'))

    def __del__(self):
        # make sure file is closed correctly
        self.close()
        print 'closing file %s' %self.filename
        del self.file

    def close(self):
        if not self.file is None:
            self.file.close()
        return

class Object(object):
    def __init__(self):
        self.debug = False

        self.bbox = None                            # box containing relevant pixels
        self.coordinates = None                     # relative to bbox

        # self.skeletonCoords = None
        # self.skeletonNodes = None
        # self.nodeValues = None

        self.center = None
        self.size = None
        self.time = None


class ActiveContourSegmentationOld(object):

    # to use with descriptors.IndependentChannel

    def __init__(self,parent, minSize = 100):
        print 'active contour segmentation'
        self.minSize = minSize
        # self.minSizeMaxSeparation = minSizeMaxSeparation
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

        # pdb.set_trace()
        sImg = sitk.gifa(frame)
        sImg.SetSpacing(self.parent.spacing)
        sImg = stacking.scale(sImg,scaling=None)

        # sitImg = sitk.Cast(sitk.ReadImage('/home/malbert/misc/test/3dexample_iso.tif'),6)
        # img = sitk.gafi(sitImg)
        # sitImg.SetSpacing([0.09,0.09,0.39])
        # sitImg.SetSpacing([0.39,0.39,0.39])

        gImg = sitk.SmoothingRecursiveGaussian(sImg,0.3)
        lImg = sitk.Laplacian(gImg)
        lImg = sitk.gafi(lImg)
        lImg = n.abs(lImg*(lImg<-1000))

        sImg,N = ndimage.label(lImg>1000)

        sImg = sImg.astype(n.uint16)
        sImg = imaging.sizeFilter(sImg,minSize=self.minSize)
        # sizes = imaging.getSizes(sImg)
        # pdb.set_trace()
        # validSizes = n.array([0]+n.where(sizes>self.minSize)[0])
        # sImg = validSizes[sImg]
        print 'found %s labels to process with active contours' %n.max(sImg)

        bImg = (sImg > 0).astype(n.uint16)
        gI = 1 / (1+lImg**2)


        mgac = morphsnakes.MorphGAC(gI, smoothing=1, threshold=0.1, balloon=-0.6)
        # mgac = morphsnakes.MorphACWE(gI, smoothing=1, lambda1=1, lambda2=1)
        mgac.levelset = getHullsIm(sImg)
        morphsnakes.evolve(mgac, num_iters=30)
        # ac,N = ndimage.label(mgac.levelset)

        # ac = ac.astype(n.uint16)
        print 'segmentation: laplace OR ac'
        labels = (bImg+mgac.levelset)
        # labels = (labels/labels).astype(n.uint16)
        labels,N = ndimage.label(labels)
        labels = imaging.sizeFilter(labels,minSize=self.minSize)
        labels = labels.astype(n.uint16)
        N = n.max(labels)
        print '%s labels are left after combining active contours and laplace' %N
        # pdb.set_trace()
        findObjects = ndimage.find_objects(labels)
        sizes = imaging.getSizes(labels)

        filing.toH5_hl(self.minSize,tmpFile,hierarchy=os.path.join(tmpHierarchy,'minSize'))

        bboxs,minCoordinates,coordinatess,osizes,centers,surfaces = [],[],[],[],[],[]
        for obj in range(N):

            # print 'processing object %s' %iobject

            # objectGroup = objectsGroup.create_group(str(iobject))
            # volume = objects.vtk_volume(objLabels)
            bbox = findObjects[obj]
            objLabels = (labels[bbox]==(obj+1)).astype(n.uint16)
            # pdb.set_trace()
            surface = objects.vtk_surface(objLabels,spacing=self.parent.spacing[::-1])
            coordinates = n.array(n.where(objLabels)).swapaxes(0,1)
            size = sizes[obj]
            center = n.array([n.mean([bbox[idim].start,bbox[idim].stop]) for idim in range(3)])
            minCoordinate = n.array([bbox[i].start for i in range(3)])

            bboxs.append(bbox)
            minCoordinates.append(minCoordinate)
            coordinatess.append(coordinates)
            osizes.append(size)
            centers.append(center)
            surfaces.append(surface)

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
        surfaces = n.array(surfaces)

        # pdb.set_trace()

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

        # filePointer['sizes'] = osizes
        filing.toH5_hl(surfaces,tmpFile,hierarchy=os.path.join(tmpHierarchy,'surfaces'))

        # filePointer['centers'] = centers
        filing.toH5_hl(centers,tmpFile,hierarchy=os.path.join(tmpHierarchy,'centers'))

        coordinatesGroup = tmpFile[tmpHierarchy].create_group('coordinates')
        for i in range(len(coordinatess)):
            # coordinatesGroup[str(i)] = coordinatess[i]
            filing.toH5_hl(coordinatess[i],tmpFile,hierarchy=os.path.join(tmpHierarchy,os.path.join('coordinates',str(i))))

        # return descriptors.H5Pointer(rootFile.filename,nickname)
        return

class ActiveContourSegmentation(object):

    # to use with descriptors.IndependentChannel

    def __init__(self,parent, minSize = 100):
        print 'active contour segmentation'
        self.minSize = minSize
        # self.minSizeMaxSeparation = minSizeMaxSeparation
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

        # pdb.set_trace()
        sImg = sitk.gifa(frame)
        sImg.SetSpacing(self.parent.spacing)
        sImg = stacking.scale(sImg,scaling=None)

        # sitImg = sitk.Cast(sitk.ReadImage('/home/malbert/misc/test/3dexample_iso.tif'),6)
        # img = sitk.gafi(sitImg)
        # sitImg.SetSpacing([0.09,0.09,0.39])
        # sitImg.SetSpacing([0.39,0.39,0.39])

        gImg = sitk.SmoothingRecursiveGaussian(sImg,0.3)
        lImg = sitk.Laplacian(gImg)
        lImg = sitk.gafi(lImg)
        lImg = n.abs(lImg*(lImg<-1000))

        sImg,N = ndimage.label(lImg>1000)

        sImg = sImg.astype(n.uint16)
        sImg = imaging.sizeFilter(sImg,minSize=self.minSize)
        # sizes = imaging.getSizes(sImg)
        # pdb.set_trace()
        # validSizes = n.array([0]+n.where(sizes>self.minSize)[0])
        # sImg = validSizes[sImg]
        print 'found %s labels to process with active contours' %n.max(sImg)

        bImg = (sImg > 0).astype(n.uint16)
        gI = 1 / (1+lImg**2)


        mgac = morphsnakes.MorphGAC(gI, smoothing=1, threshold=0.1, balloon=-0.6)
        # mgac = morphsnakes.MorphACWE(gI, smoothing=1, lambda1=1, lambda2=1)
        mgac.levelset = getHullsIm(sImg)
        morphsnakes.evolve(mgac, num_iters=30)
        # ac,N = ndimage.label(mgac.levelset)

        # ac = ac.astype(n.uint16)
        print 'segmentation: laplace OR ac'
        labels = (bImg+mgac.levelset)
        # labels = (labels/labels).astype(n.uint16)
        labels,N = ndimage.label(labels)
        labels = imaging.sizeFilter(labels,minSize=self.minSize)
        labels = labels.astype(n.uint16)
        N = n.max(labels)
        print '%s labels are left after combining active contours and laplace' %N
        # pdb.set_trace()
        findObjects = ndimage.find_objects(labels)
        sizes = imaging.getSizes(labels)

        filing.toH5_hl(self.minSize,tmpFile,hierarchy=os.path.join(tmpHierarchy,'minSize'))

        bboxs,minCoordinates,coordinatess,osizes,centers,surfaces = [],[],[],[],[],[]
        for obj in range(N):

            # print 'processing object %s' %iobject

            # objectGroup = objectsGroup.create_group(str(iobject))
            # volume = objects.vtk_volume(objLabels)
            bbox = findObjects[obj]
            objLabels = (labels[bbox]==(obj+1)).astype(n.uint16)
            # pdb.set_trace()
            surface = objects.vtk_surface(objLabels,spacing=self.parent.spacing[::-1])
            coordinates = n.array(n.where(objLabels)).swapaxes(0,1)
            size = sizes[obj]
            center = n.array([n.mean([bbox[idim].start,bbox[idim].stop]) for idim in range(3)])
            minCoordinate = n.array([bbox[i].start for i in range(3)])

            bboxs.append(bbox)
            minCoordinates.append(minCoordinate)
            coordinatess.append(coordinates)
            osizes.append(size)
            centers.append(center)
            surfaces.append(surface)

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
        surfaces = n.array(surfaces)

        # pdb.set_trace()

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

        # filePointer['sizes'] = osizes
        filing.toH5_hl(surfaces,tmpFile,hierarchy=os.path.join(tmpHierarchy,'surfaces'))

        # filePointer['centers'] = centers
        filing.toH5_hl(centers,tmpFile,hierarchy=os.path.join(tmpHierarchy,'centers'))

        coordinatesGroup = tmpFile[tmpHierarchy].create_group('coordinates')
        for i in range(len(coordinatess)):
            # coordinatesGroup[str(i)] = coordinatess[i]
            filing.toH5_hl(coordinatess[i],tmpFile,hierarchy=os.path.join(tmpHierarchy,os.path.join('coordinates',str(i))))

        # return descriptors.H5Pointer(rootFile.filename,nickname)
        return

def getHullsIm(im):
    labels,N = ndimage.label(im)
    sizes = imaging.getSizes(labels)
    res = n.zeros_like(im)
    for ilabel in range(N):
        if sizes[ilabel] > 100:
            res += getHullIm(labels==(ilabel+1))
    res = res/(res+(res==0))
    return res


def getHullIm(im):

    delall = spatial.Delaunay(n.array(im.nonzero()).swapaxes(0,1))

    chullpoints = delall.points[n.unique(delall.convex_hull)]
    delhull = spatial.Delaunay(chullpoints)

    all=n.array(n.where(im<n.inf)).swapaxes(0,1)
    pointsinhull = delhull.find_simplex(all)>=0
    hullim = pointsinhull.reshape(im.shape)

    return hullim