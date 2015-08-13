__author__ = 'malbert'

from dependencies import *

config['relSkeletonizationDataDir'] = "seg_ch%d"
config['skeletonizationDataFormat'] = "f%06d_Probabilities.h5"

class SkeletonizationChannel(descriptors.ChannelData):

    def __init__(self,parent,channel):
        print 'creating skeletonization channel'

        self.dir = parent.rawData[channel].dir
        self.fileNameFormat = parent.rawData[channel].fileNameFormat

        self.nickname = 'skeleton'


        self.timepointClass = Skeleton

        super(SkeletonizationChannel,self).__init__(parent,channel)

    def prepareTimepoints(self,times):
        print 'preparing timepoints %s' %times

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            if config['registrationPath'] in self.parent.rawData[self.channel][time].file.keys():
                alreadyDoneTimes.append(time)
                outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=config['registrationPath'])
            else:
                toDoTimes.append(time)

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        tmpImage = sitk.gifa(self.parent.rawData[self.channel][0])
        if not (self.parent.registrationSliceStringSitk is None):
            exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

        outFileRef = os.path.join(tmpDir,'refImage.mhd')
        outFileRefRaw = os.path.join(tmpDir,'refImage.raw')
        sitk.WriteImage(tmpImage,outFileRef)

        for itime,time in enumerate(toDoTimes):
            print "registering channel %01d time %06d" %(self.channel,time)

            tmpImage = sitk.gifa(self.parent.rawData[self.channel][time])
            if not (self.parent.registrationSliceStringSitk is None):
                exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

            inputList = [outFileRef,tmpImage]

            tmpParams = imaging.getParamsFromElastix(inputList,
                              initialParams=None,
                              tmpDir=tmpDir,
                              mode='similarity',
                              masks=None)

            tmpParams = n.array(tmpParams[1]).astype(n.float64)

            tmpFile = h5py.File(self.parent.rawData[self.channel][time].file.filename)
            tmpFile[config['registrationPath']] = tmpParams
            tmpFile.close()

            outDict[time] = descriptors.H5Array(self.parent.rawData[self.channel][time].file.filename,
                                    hierarchy=config['registrationPath'])

        os.remove(outFileRef)
        os.remove(outFileRefRaw)
        return outDict


class Skeleton(object):

    # replace by simple h5py.File?

    def __init__(self,filename,hierarchy=config['hierarchy']):
        print 'instanciating stack for file %s' %filename
        self.filename = filename
        self.hierarchy = hierarchy
        self.file = None
        self.dataset = None

    def __get__(self,instance,owner):
        # open file only if needed

        if self.file is None:
            print 'opening file %s' %self.filename
            self.file = h5py.File(self.filename)
            if not self.hierarchy in self.file.keys(): raise(Exception('could not find dataset with name %s in file %s' %(self.hierarchy,self.filename)))
            self.dataset = self.file[self.hierarchy]

        if len(self.dataset.shape) < 2:
            returnData = n.array(self.dataset)
            self.close()
            return returnData
        else:
            return self.dataset

    def __set__(self,value):
        raise(Exception('no setting possible!'))

    def __del__(self):
        # make sure file is closed correctly
        del self.dataset
        if not self.file is None:
            self.file.close()
        print 'closing file %s' %self.filename
        del self.file

    def __getitem__(self,item):
        raise(Exception('shouldnt this go over the getitem of the parent?'))
        return self.__get__(self,H5Array)[item]

    def close(self):
        del self.dataset
        self.file.close()
        self.file = None
        return
