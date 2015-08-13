__author__ = 'malbert'

from dependencies import *

config['segmentationPath'] = 'segmentation'

class SegmentationChannel(descriptors.ChannelData):

    # class for handling segmentation data
    # initial task: threshold and connected components
    # relies on parent having prediction channel
    nickname = 'segmentation'

    def __init__(self,parent,channel,baseData):
        print 'creating seg channel %s' %channel

        self.baseData = baseData
        # self.baseData = parent.classData[baseDataClass.__name__]
        self.timepointClass = ObjectGroup

        self.dir = parent.classData[baseDataClass.__name__][channel].dir
        # self.dir = parent.classData[baseDataClass.__name__][channel].dir
        self.fileNameFormat = parent.classData[baseDataClass.__name__][channel].fileNameFormat

        self.threshold = 0.5
        self.sizeThreshold = 20

        super(SegmentationChannel,self).__init__(parent,channel)


    def prepareTimepoints(self,times):
        print 'preparing timepoints %s' %times

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            if config['segmentationPath'] in self.baseData[self.channel][time].file.keys():
                alreadyDoneTimes.append(time)
                # pdb.set_trace()
                outDict[time] = ObjectGroup(self.getFileName(time))
            else:
                toDoTimes.append(time)

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):
            print "segmenting (connected component and size filter) channel %01d time %06d" %(self.channel,time)

            tmpFile = h5py.File(self.baseData[self.channel][time].file.filename)
            tmpGroupGroup = tmpFile.create_group(config['segmentationPath'])

            # pdb.set_trace()
            tmpBin = (n.array(self.baseData[self.channel][time]) > self.threshold)
            labels,N = ndimage.label(tmpBin)#,structure=n.ones((3,3,3)))
            sizes = imaging.getSizes(labels)
            objects = ndimage.find_objects(labels)

            for iobject in n.where(sizes>=self.sizeThreshold)[0]:

                tmpObjectGroup = tmpGroupGroup.create_group(str(iobject))

                bbox = objects[iobject]
                tmpObjectGroup['bbox'] = n.array([[i.start,i.stop] for i in bbox]).astype(n.uint16)
                #newObject.coordinates = n.nonzero(labels[newObject.bbox])
                tmpObjectGroup['coordinates'] = n.array(n.where(labels[bbox]==(iobject+1)))

                tmpObjectGroup['size'] = sizes[iobject]
                tmpObjectGroup['center'] = n.array([n.mean([bbox[idim].start,bbox[idim].stop]) for idim in range(3)])
                # del tmpGroupGroup
                # raise(Exception())
            tmpFile.close()

            outDict[time] = ObjectGroup(self.baseData[self.channel][time].file.filename)

        return outDict


class ObjectGroup(object):

    # replace by simple h5py.File?

    def __init__(self,filename):
        print 'instanciating object group for file %s' %filename

        self.filename = filename
        self.file = None

    def __get__(self,instance,owner):
        if self.file is None:
            self.file = h5py.File(self.filename)

        tmpGroup = self.file[config['segmentationPath']]
        tmpObject = Object()
        tmpObject.bbox = tuple([slice(i[0],i[1]) for i in n.array(tmpGroup['bbox'])])
        tmpObject.coordinates = n.array(tmpGroup['coordinates'])
        tmpObject.size = n.array(tmpGroup['size'])
        tmpObject.center = n.array(tmpGroup['center'])

        return tmpObject

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