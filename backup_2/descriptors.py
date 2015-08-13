__author__ = 'malbert'

from dependencies import *

import shutil

config['relRawDataDir'] = "raw_ch%d"
config['rawDataFormat'] = "f%06d.h5"
config['relSegmentationDataDir'] = "seg_ch%d"
config['segmentationDataFormat'] = "f%06d_Probabilities.h5"

config['ilastikCommand'] = ilastiking.runIlastikNew

config['hierarchy'] = 'DS1'
config['registrationPath'] = 'registrationParameters'


# def H5Array(filename):
#     return h5py.File(filename)[config['hierarchy']]

class H5Array(object):

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


class ChannelData(object):

    # abstract class for channel image data, to be subclassed for
    # raw data, segmentation, etc. by adding prepareTimepoints method
    # (and possibly more)

    def __init__(self,parent,channel):
        print 'instanciating original data descriptor for channel %s' %channel

        self.parent = parent
        self.channel = channel

        if not os.path.exists(self.dir):
            print 'creating %s' %(self.dir)
            os.mkdir(self.dir)

        # for itime,time in enumerate(self.parent.times):
        #     self.timesDict[time] = self.prepareStack(self.getFileName(time))

        self.timesDict = self.prepareTimepoints(self.parent.times)


    def __get__(self,instance,owner):
        raise(Exception('no getting possible!'))

    def __set__(self,instance,value):
        raise(Exception('no setting possible!'))

    def __getitem__(self,item):
        if not type(item) == tuple:
            if not self.timesDict.has_key(item):
                self.timesDict[item] = self.prepareTimepoints([item])[item]
                # self.timesDict[item] = Stack(self.getFileName(item))
            return self.timesDict[item].__get__(self,self.timepointClass)
        elif len(item) == 2:
            return self[item[0]][item[1]]

    def getFileName(self,time):

        return os.path.join(self.dir,self.fileNameFormat %time)

    def __len__(self):
        return len(self.parent.times)


class ImageData(object):

    def __init__(self,parent,dataClass):

        # dataClass is raw, segmentation or...

        self.dataClass = dataClass

        self.parent = parent
        self.channelsDict = dict()

        for ichannel,channel in enumerate(self.parent.classChannels[dataClass.__name__]):
            self.channelsDict[channel] = self.dataClass(self.parent,channel)

    def __get__(self,instance,owner):
        raise(Exception('no getting possible!'))

    def __set__(self,instance,value):
        raise(Exception('no setting possible!'))

    def __getitem__(self,item):
        if not (item in self.parent.channels):
            raise(Exception('trying to access channel %s, but allowed channels are %s' %(item,self.parent.classChannels[dataClass.__name__])))
        if self.channelsDict.has_key(item):
            return self.channelsDict[item]
        else:
            self.channelsDict[item] = self.dataClass(self.parent,item)
        return self.channelsDict[item]


class RawChannel(ChannelData):

    # class for handling original data
    # initial task: copy raw data to h5 files

    def __init__(self,parent,channel):
        print 'creating raw channel'
        self.dir = os.path.join(parent.dataDir,config['relRawDataDir'] %channel)
        self.fileNameFormat = config['rawDataFormat']
        self.timepointClass = H5Array

        super(RawChannel,self).__init__(parent,channel)

    def prepareTimepoints(self,times):
        print 'preparing timepoints %s' %times

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            if os.path.exists(self.getFileName(time)):
                alreadyDoneTimes.append(time)
                outDict[time] = H5Array(self.getFileName(time))
            else:
                toDoTimes.append(time)

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):
            print "preparing channel %01d time %06d" %(self.channel,time)
            if self.parent.fileName[-4:] == '.czi':
                if self.parent.originalFile is None: self.parent.originalFile = czifile.CziFile(self.parent.fileName)
                # subset format:
                #pdb.set_trace()
                tmpData = self.parent.originalFile.asarray_general([[self.channel],[time]],[2,3])

            else: raise(Exception('check load format'))

            filing.toH5(tmpData,self.getFileName(time),hierarchy=config['hierarchy'])
            outDict[time] = H5Array(self.getFileName(time))

        return outDict

class SegmentationChannel(ChannelData):

    # class for handling segmentation data
    # initial task: run ilastik
    # relies on parent having classifiers dict

    def __init__(self,parent,channel):
        print 'creating seg channel'

        # if not (channel in parent.segmentationChannels):
        #     #raise(Exception('Channel %s not marked for segmentation' %channel))
        #     print 'Ommitting channel %s since it is not marked for segmentation' %channel
        #     return

        self.timepointClass = H5Array

        self.dir = os.path.join(parent.dataDir,config['relSegmentationDataDir'] %channel)
        if not os.path.exists(self.dir): os.mkdir(self.dir)
        self.fileNameFormat = config['segmentationDataFormat']

        if parent.classifiers.has_key(channel):
            self.classifier = parent.classifiers[channel]
        else:

            self.trainingSamplesDir = os.path.join(self.dir,'training')
            if not os.path.exists(self.trainingSamplesDir): os.mkdir(self.trainingSamplesDir)

            classifierPath = os.path.join(self.trainingSamplesDir,'classifier_ch%s.ilp' %channel)
            if not os.path.exists(classifierPath):
                print 'preparing ilastik training samples based on times %s' %parent.times

                shutil.copyfile('/home/malbert/quantification/classifier_template_ch%s.ilp' %channel,classifierPath)

                # produce training samples
                timepoints = len(parent.times)
                timepoints = [itp*(timepoints/4) for itp in range(4)]
                for itime,time in enumerate(timepoints):
                    samplePath = os.path.join(self.trainingSamplesDir,'sample%02d.h5' %itime)
                    if os.path.exists(samplePath): os.remove(samplePath)
                    os.link(parent.rawData[channel][time].file.filename,samplePath)

                raise(Exception('train ilastik for channel %s using copied project at %s!' %(channel,classifierPath)))

        super(SegmentationChannel,self).__init__(parent,channel)


    def prepareTimepoints(self,times):
        print 'preparing timepoints %s' %times

        outDict = dict()

        alreadyDoneTimes, toDoTimes, toDoStacks = [],[],[]
        for itime,time in enumerate(times):
            if os.path.exists(self.getFileName(time)):
                alreadyDoneTimes.append(time)
                outDict[time] = H5Array(self.getFileName(time))
            else:
                toDoTimes.append(time)
                toDoStacks.append(self.parent.rawData[self.channel][time])

        if not len(toDoTimes): return outDict

        outFiles = config['ilastikCommand'](toDoStacks,self.classifier,outLabelIndex=1,outDir=self.dir)

        for ifile,f in enumerate(outFiles):
            tmpOutFileName = os.path.join(self.dir,outFiles[ifile].file.filename)
            outFiles[ifile].file.close()
            outDict[toDoTimes[ifile]] = H5Array(tmpOutFileName)

        return outDict


class RegistrationChannel(object):

    def __init__(self):
        self.timepointClass = RegistrationParameters
        print 'la'

    def prepareTimepoints(self,times):

        return

