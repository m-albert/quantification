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