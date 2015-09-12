__author__ = 'malbert'

from dependencies import *

import shutil

config['relRawDataDir'] = "raw_ch%d"
# config['relRawDataDir'] = "Stack_2_Channel_%d"

config['fileNameFormat'] = "f%06d.h5"
# config['fileNameFormat'] = "Cam_Right_%05d.h5"

config['rawHierarchy'] = 'DS1'
# config['rawHierarchy'] = 'Data'

config['unstructuredDataDir'] = "unstructured"


# def H5Array(filename):
#     return h5py.File(filename)[config['hierarchy']]

class H5Pointer(object):

    def __init__(self,fileName,hierarchy):
        self.fileName = fileName
        self.hierarchy = hierarchy

    def __get__(self,instance,owner):
        return h5py.File(self.fileName)[self.hierarchy]

# class H5Pointer(object):
#
#     def __init__(self,filename,hierarchy):
#         print 'instanciating stack for file %s' %filename
#         self.filename = filename
#         self.hierarchy = hierarchy
#         self.file = None
#         self.dataset = None
#         return
#
#     def __get__(self,instance,owner):
#         # open file only if needed
#
#         if self.file is None:
#             print 'opening file %s' %self.filename
#             self.file = h5py.File(self.filename)
#             if not self.hierarchy in self.file.keys(): raise(Exception('could not find dataset with name %s in file %s' %(self.hierarchy,self.filename)))
#             self.dataset = self.file[self.hierarchy]
#
#         if len(self.dataset.shape) < 2:
#             returnData = n.array(self.dataset)
#             self.close()
#             return returnData
#         else:
#             return self.dataset
#
#     def __set__(self,value):
#         raise(Exception('no setting possible!'))
#
#     def __del__(self):
#         print 'closing file %s' %self.filename
#         self.close()
#         return
#
#     def close(self):
#         self.dataset = None
#         if not self.file is None:
#             self.file.close()
#             self.file = None
#         return



class H5Array(object):

    # replace by simple h5py.File?

    def __init__(self,filename,hierarchy=config['rawHierarchy']):
        print 'instanciating stack for file %s' %filename
        self.filename = filename
        self.hierarchy = hierarchy
        self.file = None
        self.dataset = None
        return

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
        print 'closing file %s' %self.filename
        self.close()
        return

    def close(self):
        self.dataset = None
        if not self.file is None:
            self.file.close()
            self.file = None
        return

    def __getitem__(self,item):
        raise(Exception('shouldnt this go over the getitem of the parent?'))
        return self.__get__(self,H5Array)[item]


class Image(object):

    def __init__(self,fileName,spacing=None,shape=None,origin=None):
        self.fileName = fileName
        self.data = None
        self.spacing = spacing
        self.shape = shape
        self.origin = origin
        self.min = None
        self.max = None
        self.slices = None
        return

    def gi(self):
        tmpIm = self.gifa(self.data)
        tmpIm.SetSpacing(self.spacing)
        tmpIm.SetOrigin(self.origin)
        return tmpIm

    def ga(self):
        pass

    def __getattribute__(self,name):
        if not self.__dict__.has_key(name):
            raise(AttributeError)
        else:
            if self.data is None:
                print 'loading Image: %s' %self.fileName
                tmpImage = sitk.ReadImage(self.fileName)
                self.data = sitk.gafi(tmpImage)
                self.shape = n.array(self.data.GetSize())
                self.origin = n.array(self.data.GetOrigin())
                self.spacing = n.array(self.data.GetSpacing())

            if name in ['slices','minCoord','maxCoord'] and self.__dict__[name] is None:
                tmp = n.array(self.data.nonzero())
                self.minCoord = n.min(tmp,1)
                self.maxCoord = n.max(tmp,1)
                self.slices = tuple([slice(self.minCoord[i],self.maxCoord[i]) for i in range(3)])

        return self.__dict__[name]



class ChannelData(object):

    # abstract class for channel image data, to be subclassed for
    # raw data, prediction, etc. by adding prepareTimepoints method
    # (and possibly more)

    def __init__(self,parent,nickname,redo=False):
        print 'instanciating channel data in dir %s' %self.dir

        self.parent = parent
        self.nickname = nickname
        self.redo = redo

        if not self.__dict__.has_key('validTimes'):
            if self.__dict__.has_key('baseData'):
                self.validTimes = self.baseData.validTimes
            else:
                self.validTimes = self.parent.times

        if not parent.nicknameDict.has_key(nickname):
            parent.nicknameDict[nickname] = self
        else:
            raise(Exception('nickname already taken'))
        parent.__setattr__(nickname,self)

        if not self.__dict__.has_key('fileNameFormat'):
            self.fileNameFormat = config['fileNameFormat']

        if not os.path.exists(self.dir):
            print 'creating %s' %(self.dir)
            os.mkdir(self.dir)

        timepointsToPrepare = n.array(list(set(self.validTimes).intersection(set(self.parent.times))))
        timepointsToPrepare = list(timepointsToPrepare[n.argsort(timepointsToPrepare)])

        self.timesDict = self.prepareTimepoints(timepointsToPrepare,self.redo)


    def __get__(self,instance,owner):
        raise(Exception('no getting possible!'))

    def __set__(self,instance,value):
        raise(Exception('no setting possible!'))

    def __getitem__(self,item):
        item = int(item)
        if not self.timesDict.has_key(item):
            print '%s: preparing time %s' %(self.nickname,item)
            self.timesDict[item] = self.prepareTimepoints([item],self.redo)[item]
            # self.timesDict[item] = Stack(self.getFileName(item))
        # return self.timesDict[item].__get__(self,self.timepointClass)
        return self.timesDict[item].__get__(self,0)
        # return self.timesDict[item]#.__get__(self,self.timepointClass)
        if type(item) == tuple and len(item) == 2:
            return self[item[0]][item[1]]
        elif type(item) == list or (type(item) == n.ndarray and len(item.shape) == 1):
            tmpDict = dict()
            for iiitem,iitem in enumerate(item): tmpDict[int(iiitem)] = self[int(item[iiitem])]
            return Tupable(tmpDict)

    def __call__(self,itemValidIndex):
        if type(itemValidIndex) in [int]:
            item = int(self.validTimes[itemValidIndex])
            if not self.timesDict.has_key(item):
                print '%s: preparing time %s' %(self.nickname,item)
                self.timesDict[item] = self.prepareTimepoints([item],self.redo)[item]
                # self.timesDict[item] = Stack(self.getFileName(item))
            return self.timesDict[item].__get__(self,self.timepointClass)
        elif type(itemValidIndex) == tuple and len(itemValidIndex) == 2:
            #item[0] = self.validTimes[item[0]]
            return self[itemValidIndex[0]][itemValidIndex[1]]
        elif type(itemValidIndex) == list or (type(itemValidIndex) == n.ndarray and len(itemValidIndex.shape) == 1):
            #item = n.array(self.validTimes)[item]
            tmpDict = dict()
            for iiitem,iitem in enumerate(itemValidIndex): tmpDict[int(iiitem)] = self(int(iitem))
            return Tupable(tmpDict)

    # def __getitem__(self,item):
    #     if type(item) in [int]:
    #         if self.__dict__.has_key('validTimes'): item = int(self.validTimes[item])
    #         # pdb.set_trace()
    #         if not self.timesDict.has_key(item):
    #             print '%s: preparing time %s' %(self.nickname,item)
    #             self.timesDict[item] = self.prepareTimepoints([item],self.redo)[item]
    #             # self.timesDict[item] = Stack(self.getFileName(item))
    #         return self.timesDict[item].__get__(self,self.timepointClass)
    #     elif type(item) == tuple and len(item) == 2:
    #         if self.__dict__.has_key('validTimes'): item[0] = self.validTimes[item[0]]
    #         return self[item[0]][item[1]]
    #     elif type(item) == list or (type(item) == n.ndarray and len(item.shape) == 1):
    #         if self.__dict__.has_key('validTimes'): item = self.validTimes[item]
    #         tmpDict = dict()
    #         for iiitem,iitem in enumerate(range(len(item))): tmpDict[int(iitem)] = self[int(item[iiitem])]
    #         return Tupable(tmpDict)

    def getFileName(self,time):

        return os.path.join(self.dir,self.fileNameFormat %time)

    def __len__(self):
        return len(self.validTimes)

    def close(self,time):
        try:
            print 'closing'
            self.timesDict[int(time)].close()
        except:
            print 'could not close'

class IndependentChannel(ChannelData):

    # abstract class for channel image data, to be subclassed for
    # raw data, prediction, etc. by adding prepareTimepoints method
    # (and possibly more)

    def __init__(self,parent,baseData,nickname,processClass,redo=False,*args,**kargs):

        # no dir setting here?

        self.baseData = baseData
        self.dir = self.baseData.dir

        self.processObject = processClass(*args)
        # self.parent = parent
        self.nickname = nickname
        self.redo = redo

        super(IndependentChannel,self).__init__(parent,nickname,*args,**kargs)
        return

    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            tmpFile = h5py.File(self.baseData.getFileName(time))
            if self.nickname in tmpFile.keys():
                if redo:
                    del tmpFile[self.nickname]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    outDict[time] = self.processObject.fromFile(self.getFileName(time),hierarchy=self.nickname)
            else:
                toDoTimes.append(time)
            tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):

            tmpFile = h5py.File(self.baseData.getFileName(time))

            tmpPrefix = self.nickname+'_'

            for group in tmpFile.keys():
                if tmpPrefix in group: del tmpFile[group]

            tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])
            while tmpString in tmpFile.keys():
                tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])

            tmpGroup = tmpFile.create_group(tmpString)

            self.processObject.fromFrame(self.baseData[time],tmpGroup)

            tmpFile.move(tmpString,self.nickname)

            # outDict[time] = descriptors.H5Pointer(rootFile.filename,nickname)
            outDict[time] = self.processObject.timepointClass(self.baseData.getFileName(time),self.nickname)

            tmpFile.close()

        return outDict

class Tupable(object):

    def __init__(self,dataDict):
        self.dataDict = dataDict
        self.iterableKeys = []
        order = []
        for key in self.dataDict.keys():
            try:
                nkey = int(key)
                order.append(nkey)
                self.iterableKeys.append(key)
            except:
                continue

        order = n.argsort(order)
        self.iterableKeys = [self.iterableKeys[i] for i in order]

        self.current = 0
        self.highest = len(self.iterableKeys)-1

    def __iter__(self):
        return self
        #return self.dataDict[iterableKeys[self.current]]

    def next(self):
        if self.current > self.highest:
            raise StopIteration
        else:
            self.current += 1
            return self.dataDict[self.iterableKeys[self.current-1]]

    def __len__(self):
        keys = self.dataDict.keys()
        number = 0
        for key in keys:
            try:
                tmp = int(key)
                number += 1
            except: continue
        return number

    def __getitem__(self,item):
        try:
            item = int(item)
            return self.dataDict[int(item)]
        except:
            if type(item) in [tuple,list,n.ndarray] and len(item)==2:
                return self.dataDict[int(item[0])][int(item[1])]
            elif type(item) in [str]:
                return self.dataDict[item]
            raise(Exception('wrong index'))

    def sum(self):
        for ii,i in enumerate(self):
            if not ii: res = n.array(i)
            else: res += n.array(i)
        return res



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
            # self.channelsDict[item] = self.dataClass(self.parent,item,*args,**kargs)
            self.channelsDict[item] = self.dataClass(self.parent,item)
        return self.channelsDict[item]


class RawChannel(ChannelData):

    # class for handling original data
    # initial task: copy raw data to h5 files

    nickname = 'rawData'

    def __init__(self,parent,channel,nickname,*args,**kargs):
        print 'creating raw channel'
        self.dir = os.path.join(parent.dataDir,config['relRawDataDir'] %channel)
        self.timepointClass = H5Array
        self.channel = channel
        self.hierarchy = 'DS1'
        # self.hierarchy = 'Data' #malbert
        super(RawChannel,self).__init__(parent,nickname,*args,**kargs)
        self.parent.shape = self[self.parent.times[0]].shape
        return

    def prepareTimepoints(self,times,redo):
        print 'preparing timepoints %s' %times

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            tmpFile = h5py.File(self.getFileName(time))
            if self.hierarchy in tmpFile.keys():
                alreadyDoneTimes.append(time)
                outDict[time] = H5Array(self.getFileName(time))
            else:
                toDoTimes.append(time)
            tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):
            print "preparing channel %01d time %06d" %(self.channel,time)
            if not os.path.exists(self.parent.fileName):
                raise(Exception('file doesnt exist: %s' %self.parent.fileName))
            if self.parent.fileName[-4:] == '.czi':
                if os.path.exists(self.parent.fileName[:-4]+'(1).czi'): masterFile = True
                else: masterFile = False
                if masterFile:
                    if not time: tmpFileName = self.parent.fileName
                    else: tmpFileName = self.parent.fileName[:-4]+'(%s).czi' %time
                    tmpData = czifile.imread(tmpFileName).squeeze()
                else:
                    if self.parent.originalFile is None: self.parent.originalFile = czifile.CziFile(self.parent.fileName)
                    # subset format:
                    #pdb.set_trace()
                    if self.parent.dimc > 1:
                        tmpData = self.parent.originalFile.asarray_general([[self.channel],[time]],[2,3])
                    else:
                        tmpData = self.parent.originalFile.asarray_general([[time]],[3])

            else: raise(Exception('check load format'))

            if not os.path.exists(self.getFileName(time)):
                filing.toH5(tmpData,self.getFileName(time),hierarchy=self.hierarchy)
            else:
                tmpFile = h5py.File(self.getFileName(time))
                tmpFile[self.hierarchy] = tmpData
                tmpFile.close()

            outDict[time] = H5Array(self.getFileName(time))

        return outDict


class UnstructuredData(object):

    # abstract class for unstructured data, to be subclassed
    # by adding prepare() method, data to pickle

    def __init__(self,parent,nickname,redo=False):
        print 'instanciating unstructured data at file %s' %self.fileName

        self.parent = parent
        self.nickname = nickname
        self.redo = redo

        if not parent.nicknameDict.has_key(nickname):
            parent.nicknameDict[nickname] = self
        else:
            raise(Exception('nickname already taken'))
        parent.__setattr__(nickname,self)

        if not self.__dict__.has_key('fileName'):
            raise(Exception('unstructured data class needs filename'))
        else:
            self.fileName = os.path.join(self.parent.dataDir,config['unstructuredDataDir'],self.fileName)

        if not os.path.exists(os.path.dirname(self.fileName)):
            print 'creating %s' %(os.path.dirname(self.fileName))
            os.mkdir(os.path.dirname(self.fileName))

        self.data = self.prepare(self.redo)


    def __get__(self,instance,owner):
        raise(Exception('no getting possible!'))

    def __set__(self,instance,value):
        raise(Exception('no setting possible!'))