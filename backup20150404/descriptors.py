__author__ = 'malbert'

from dependencies import *

import shutil

config['relRawDataDir'] = "raw_ch%d"
config['rawDataFormat'] = "f%06d.h5"

config['hierarchy'] = 'DS1'


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

        if len(self.dataset.shape) < 2:
            returnData = n.array(self.dataset)
            #self.close()
            return returnData
        else:
            return self.dataset

    def __set__(self,value):
        raise(Exception('no setting possible!'))

    def __del__(self):
        print 'closing file %s' %self.filename
        self.close()
        return

    def close(self):
        del self.dataset
        if not self.file is None:
            self.file.close()
            self.file = None
        return

    def __getitem__(self,item):
        raise(Exception('shouldnt this go over the getitem of the parent?'))
        return self.__get__(self,H5Array)[item]


class ChannelData(object):

    # abstract class for channel image data, to be subclassed for
    # raw data, prediction, etc. by adding prepareTimepoints method
    # (and possibly more)

    def __init__(self,parent,channel):
        print 'instanciating original data descriptor for channel %s' %channel

        self.parent = parent
        self.channel = channel

        if not os.path.exists(self.dir):
            print 'creating %s' %(self.dir)
            os.mkdir(self.dir)

        self.timesDict = self.prepareTimepoints(self.parent.times)


    def __get__(self,instance,owner):
        raise(Exception('no getting possible!'))

    def __set__(self,instance,value):
        raise(Exception('no setting possible!'))

    def __getitem__(self,item):
        # pdb.set_trace()
        if type(item) in [int]:
            if not self.timesDict.has_key(item):
                self.timesDict[item] = self.prepareTimepoints([item])[item]
                # self.timesDict[item] = Stack(self.getFileName(item))
            return self.timesDict[item].__get__(self,self.timepointClass)
        elif type(item) == tuple and len(item) == 2:
            return self[item[0]][item[1]]
        elif type(item) == list or (type(item) == n.ndarray and len(item.shape) == 1):
            return Tupable([self[int(item[iitem])] for iitem in range(len(item))])

    def getFileName(self,time):

        return os.path.join(self.dir,self.fileNameFormat %time)

    def __len__(self):
        return len(self.parent.times)

class Tupable(object):
    def __init__(self,dataList):
        self.dataList = dataList
    def __len__(self): return len(self.dataList)
    def __getitem__(self,item):
        if type(item) in [tuple,list,type(n.ones(1))] and len(item)==2:
            return self.dataList[int(item[0])][int(item[1])]
        if type(item) == int:
            return self.dataList[int(item)]
        else: raise(Exception('wrong index'))



class ImageData(object):

    def __init__(self,parent,dataClass,*args,**kargs):

        # dataClass is raw, segmentation or...

        self.dataClass = dataClass

        self.parent = parent
        self.channelsDict = dict()

        self.parent.classData[dataClass.__name__] = self
        self.parent.__setattr__(self.dataClass.nickname,self)

        for ichannel,channel in enumerate(self.parent.classChannels[dataClass.__name__]):
            self.channelsDict[channel] = self.dataClass(self.parent,channel,*args,**kargs)

    def __get__(self,instance,owner):
        raise(Exception('no getting possible!'))

    def __set__(self,instance,value):
        raise(Exception('no setting possible!'))

    def __getitem__(self,item):
        if not (item in self.parent.channels):
            raise(Exception('trying to access channel %s, but allowed channels are %s' %(item,self.parent.classChannels[self.dataClass.__name__])))
        if self.channelsDict.has_key(item):
            return self.channelsDict[item]
        else:
            self.channelsDict[item] = self.dataClass(self.parent,item,*args,**kargs)
        return self.channelsDict[item]


class RawChannel(ChannelData):

    # class for handling original data
    # initial task: copy raw data to h5 files

    nickname = 'rawData'

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