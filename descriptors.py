__author__ = 'malbert'

from dependencies import *

import shutil

config['relRawDataDir'] = "all%d"
# config['relRawDataDir'] = "Stack_2_Channel_%d"

# config['fileNameFormat'] = "Cam_Right_%05d.h5"

config['rawHierarchy'] = 'DS1'
# config['rawHierarchy'] = 'Data'

config['unstructuredDataDir'] = "unstructured"


# def H5Array(filename):
#     return h5py.File(filename)[config['hierarchy']]

class DelayedKeyboardInterrupt(object):
    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self.handler)

    def handler(self, signal, frame):
        self.signal_received = (signal, frame)
        logging.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)

# class H5Pointer(object):
#
#     def __init__(self,fileName,hierarchy):
#         self.fileName = fileName
#         self.hierarchy = hierarchy
#
#     def __get__(self,instance,owner):
#         return h5py.File(self.fileName)[self.hierarchy]

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



# class H5Array(object):
#
#     # replace by simple h5py.File?
#
#     def __init__(self,filename,hierarchy=config['rawHierarchy']):
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
#
#     def __getitem__(self,item):
#         raise(Exception('shouldnt this go over the getitem of the parent?'))
#         # return self.__get__(self,H5Array)[item]
#         return

def imageFormat(imType):
    # forces sitk.Image format on simple functions
    # assumptions:
    #   image is first in list of input arguments
    #   output is just an image
    def wrap(f):
        def wrapped_f(*args,**kargs):
            # pdb.set_trace()
            args = list(args)
            if type(args[0]) == sitk.Image:
                wasSitk = True
                if imType == n.ndarray:
                    args[0] = sitk.gafi(args[0])
            elif type(args[0]) == n.ndarray:
                wasSitk = False
                if imType == sitk.Image:
                    args[0] = sitk.gifa(args[0])

            args = tuple(args)
            result = f(*args,**kargs)

            if type(result) == sitk.Image and not wasSitk:
                result = sitk.gafi(result)
            if type(result) == n.ndarray and wasSitk:
                result = sitk.gifa(result)
            return result
        return wrapped_f
    return wrap

class ToLoad(object):
    def __init__(self, var, func):
        self.var  = var
        self.func = func

    # style note: try to avoid overshadowing built-ins (e.g. type)
    def __get__(self, obj, cls):
            internal = getattr(obj, '_'+self.var)
            if internal is None:
                value = getattr(obj, self.func)()
                setattr(obj, '_'+self.var, value)
                return value
            else:
                return internal

class Image(object):

    image = ToLoad('image', '_load_image')
    shape = ToLoad('shape', '_load_shape')
    origin = ToLoad('origin', '_load_origin')
    spacing = ToLoad('spacing', '_load_spacing')
    minCoord = ToLoad('minCoord', '_load_minCoord')
    maxCoord = ToLoad('maxCoord', '_load_maxCoord')
    slices = ToLoad('slices', '_load_slices')

    def __init__(self,fileName,spacing=None,shape=None,origin=None):

        # image meta data does not get set from sitk.ReadImage!

        self.fileName = fileName

        self._spacing = spacing
        self._shape = shape
        self._origin = origin

        self._image = None
        self._minCoord = None
        self._maxCoord = None
        self._slices = None
        return

    def gi(self):
        self.image.SetSpacing(self.spacing)
        self.image.SetOrigin(self.origin)
        return self.image

    def ga(self):
        return sitk.gafi(self.image)
        pass

    def GetSize(self):
        return self.shape[::-1]

    def _load_image(self):
        return sitk.ReadImage(self.fileName)

    def _load_spacing(self):
        if self._spacing == None:
            return n.array(self.image.GetSpacing())
        else:
            return self._spacing

    def _load_shape(self):
        if self._shape is None:
            return n.array(self.image.GetSize())
        else:
            return self._shape

    def _load_origin(self):
        if self._origin is None:
            return n.array(self.image.GetOrigin())
        else:
            return self._origin

    def _loadMaskStuff(self):
        tmp = self.ga().nonzero()
        self.minCoord = n.min(tmp,1)
        self.maxCoord = n.max(tmp,1)
        self.slices = tuple([slice(self.minCoord[i],self.maxCoord[i]) for i in range(3)])
        return

    def _load_minCoord(self):
        self._loadMaskStuff()
        return self.minCoord

    def _load_maxCoord(self):
        self._loadMaskStuff()
        return self.maxCoord

    def _load_slices(self):
        self._loadMaskStuff()
        return self.slices

    def __getattr__(self,name):
        try:
            res = getattr(self.ga(),name)
            return res
        except:
            raise(Exception('couldnt get attribute %s from numpy array' %name))
            return

    # def __getattribute__(self,name):
    #     pdb.set_trace()
    #     if name == 'i': return object.__getattribute__(self,'gi')()
    #     if name == 'a': return object.__getattribute__(self,'ga')()
    #     if not object.__getattribute__(self,'__dict__').has_key(name):
    #         raise(AttributeError)
    #     else:
    #         if not object.__getattribute__(self,'data') is None:
    #             print 'loading Image: %s' %object.__getattribute__(self,'fileName')
    #             tmpImage = sitk.ReadImage(object.__getattribute__(self,'fileName'))
    #             self.data = sitk.gafi(tmpImage)
    #             self.shape = n.array(object.__getattribute__(self,'data').GetSize())
    #             self.origin = n.array(object.__getattribute__(self,'data').GetOrigin())
    #             self.spacing = n.array(object.__getattribute__(self,'data').GetSpacing())
    #
    #         if name in ['slices','minCoord','maxCoord'] and object.__getattribute__(self,name) is None:
    #             tmp = n.array(object.__getattribute__(self,'data').nonzero())
    #             self.minCoord = n.min(tmp,1)
    #             self.maxCoord = n.max(tmp,1)
    #             self.slices = tuple([slice(object.__getattribute__(self,'minCoord')[i],object.__getattribute__(self,'maxCoord')[i]) for i in range(3)])
    #
    #     return object.__getattribute__(self,name)

def safeHierarchy(tmpFile,baseHierarchy):
    candidates = []
    maxIndex = len(baseHierarchy)
    for hier in tmpFile.keys():
        if hier[:maxIndex] == baseHierarchy:
            candidates.append(hier)


    if baseHierarchy in tmpFile.keys():
        print 'la'

    return



class ChannelData(object):

    # abstract class for channel image data, to be subclassed for
    # raw data, prediction, etc. by adding prepareTimepoints method
    # (and possibly more)

    def __init__(self,parent,nickname,redo=False,compression=None,compressionOption=None):
        print 'instanciating channel data with nickname %s' %nickname

        self.parent = parent
        self.nickname = nickname
        self.redo = redo

        self.compression = compression
        self.compressionOption = compressionOption

        self.spacing = parent.spacing
        self.origin = parent.origin
        self.times = self.parent.times

        if not self.__dict__.has_key('validTimes'):
            if self.__dict__.has_key('baseData') and not(self.baseData is None):
                self.validTimes = self.baseData.validTimes
            else:
                self.validTimes = self.parent.times

        if not parent.nicknameDict.has_key(nickname):
            parent.nicknameDict[nickname] = self
        else:
            raise(Exception('nickname already taken'))
        parent.__setattr__(nickname,self)

        # if not self.__dict__.has_key('fileNameFormat'):
        #     self.fileNameFormat = config['fileNameFormat']

        # if not os.path.exists(self.dir):
        #     print 'creating %s' %(self.dir)
        #     os.mkdir(self.dir)

        timepointsToPrepare = n.array(list(set(self.validTimes).intersection(set(self.parent.times))))
        timepointsToPrepare = list(timepointsToPrepare[n.argsort(timepointsToPrepare)])

        self.timesDict = {}
        for itime,time in enumerate(timepointsToPrepare):
            self.timesDict[time] = self.prepareTimepoints([time],self.redo)[time]
        # self.timesDict = self.prepareTimepoints(timepointsToPrepare,self.redo)


    def __get__(self,instance,owner):
        raise(Exception('no getting possible!'))

    def __set__(self,instance,value):
        raise(Exception('no setting possible!'))

    def __getitem__(self,item):
        item = int(item)
        # pdb.set_trace()
        if not self.timesDict.has_key(item):
            print '%s: preparing time %s' %(self.nickname,item)
            self.timesDict[item] = self.prepareTimepoints([item],self.redo)[item]
        # return self.timesDict[item].__get__(self,0)
        return self.parent[item][self.hierarchy]

        # if type(item) == tuple and len(item) == 2:
        #     return self[item[0]][item[1]]
        # elif type(item) == list or (type(item) == n.ndarray and len(item.shape) == 1):
        #     tmpDict = dict()
        #     for iiitem,iitem in enumerate(item): tmpDict[int(iiitem)] = self[int(item[iiitem])]
        #     return Tupable(tmpDict)

    def __call__(self,itemValidIndex):
        if type(itemValidIndex) in [int]:
            item = int(self.validTimes[itemValidIndex])
            if not self.timesDict.has_key(item):
                print '%s: preparing time %s' %(self.nickname,item)
                self.timesDict[item] = self.prepareTimepoints([item],self.redo)[item]
            return self.timesDict[item].__get__(self,self.timepointClass)
        elif type(itemValidIndex) == tuple and len(itemValidIndex) == 2:
            return self[itemValidIndex[0]][itemValidIndex[1]]
        elif type(itemValidIndex) == list or (type(itemValidIndex) == n.ndarray and len(itemValidIndex.shape) == 1):
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

    # def getFileName(self,time):
    #
    #     return os.path.join(self.parent.dataDir,self.parent.fileNameFormat %time)

    def __len__(self):
        return len(self.validTimes)

    # def close(self,time):
    #     try:
    #         print 'closing'
    #         self.timesDict[int(time)].close()
    #     except:
    #         print 'could not close'

class IndependentChannelOld(ChannelData):

    def __init__(self,parent,baseData,nickname,processClass,redo=False,*args,**kargs):

        # no dir setting here?

        self.baseData = baseData
        # self.dir = self.baseData.dir

        self.processObject = processClass(parent,*args,**kargs)
        # if hasattr(self.processObject(),'groupOrImage'):
        #     self.groupOrImage = True
        # else: self.groupOrImage = False

        # self.parent = parent
        self.nickname = nickname
        self.hierarchy = nickname
        self.redo = redo

        super(IndependentChannel,self).__init__(parent,nickname,redo=self.redo)
        return

    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            # tmpFile = h5py.File(self.baseData.getFileName(time))
            tmpFile = self.parent[time]
            if self.nickname in tmpFile.keys():
                if redo:
                    del tmpFile[self.nickname]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    # outDict[time] = self.processObject.fromFile(self.getFileName(time),hierarchy=self.nickname)
                    outDict[time] = True
            else:
                toDoTimes.append(time)
            # tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):

            with DelayedKeyboardInterrupt():

                # tmpFile = h5py.File(self.baseData.getFileName(time))
                tmpFile = self.parent[time]

                tmpPrefix = self.nickname+'_'

                # for group in tmpFile.keys():
                #     if tmpPrefix in group: del tmpFile[group]

                tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])
                while tmpString in tmpFile.keys():
                    tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])

                # if self.groupOrImage:
                #     tmpGroup = tmpFile.create_group(tmpString)

                # self.processObject.fromFrame(self.baseData[time],tmpGroup)
                if not (self.baseData is None):
                    self.processObject.fromFrame(time,self.baseData[time],tmpFile,tmpString)
                else: self.processObject.fromFrame(time,None,tmpFile,tmpString)

                tmpFile.move(tmpString,self.hierarchy)

                # outDict[time] = descriptors.H5Pointer(rootFile.filename,nickname)
                # outDict[time] = self.processObject.timepointClass(self.baseData.getFileName(time),self.nickname)
                outDict[time] = True

                # tmpGroup = None
                # tmpFile.close()

        return outDict

class IndependentChannel(ChannelData):

    def __init__(self,parent,baseData,nickname,processClass,redo=False,*args,**kargs):

        # no dir setting here?

        self.baseData = baseData
        # self.dir = self.baseData.dir

        self.processObject = processClass(parent,*args,**kargs)
        # if hasattr(self.processObject(),'groupOrImage'):
        #     self.groupOrImage = True
        # else: self.groupOrImage = False

        # self.parent = parent
        self.nickname = nickname
        self.hierarchy = nickname
        self.redo = redo

        super(IndependentChannel,self).__init__(parent,nickname,redo=self.redo)
        return

    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            # tmpFile = h5py.File(self.baseData.getFileName(time))
            tmpFile = self.parent[time]
            if self.nickname in tmpFile.keys():
                if redo:
                    del tmpFile[self.nickname]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    # outDict[time] = self.processObject.fromFile(self.getFileName(time),hierarchy=self.nickname)
                    outDict[time] = True
            else:
                toDoTimes.append(time)
            # tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):

            with DelayedKeyboardInterrupt():

                # tmpFile = h5py.File(self.baseData.getFileName(time))
                tmpFile = self.parent[time]
                if self.nickname in tmpFile.keys():
                    if redo:
                        print 'preparing %s: redoing time %s' %(self.nickname,time)
                        del tmpFile[self.nickname]
                    else:
                        print 'preparing %s: found prepared time %s' %(self.nickname,time)
                        outDict[time] = True
                        continue

                tmpPrefix = self.nickname+'_'

                tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])
                while tmpString in tmpFile.keys():
                    tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])

                # if self.groupOrImage:
                #     tmpGroup = tmpFile.create_group(tmpString)

                # self.processObject.fromFrame(self.baseData[time],tmpGroup)
                if not (self.baseData is None):
                    self.processObject.fromFrame(time,self.baseData[time],tmpFile,tmpString)
                else: self.processObject.fromFrame(time,None,tmpFile,tmpString)

                tmpFile.move(tmpString,self.hierarchy)

                # outDict[time] = descriptors.H5Pointer(rootFile.filename,nickname)
                # outDict[time] = self.processObject.timepointClass(self.baseData.getFileName(time),self.nickname)
                outDict[time] = True

                # tmpGroup = None
                # tmpFile.close()

        return outDict

class DependentChannel(ChannelData):

    def __init__(self,parent,baseData,nickname,processClass,redo=False,*args,**kargs):

        # no dir setting here?

        self.baseData = baseData
        # self.dir = self.baseData.dir

        self.processObject = processClass(self,parent,*args,**kargs)
        # if hasattr(self.processObject(),'groupOrImage'):
        #     self.groupOrImage = True
        # else: self.groupOrImage = False

        # self.parent = parent
        self.nickname = nickname
        self.hierarchy = nickname
        self.redo = redo

        super(DependentChannel,self).__init__(parent,nickname,redo=self.redo)
        return

    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            # tmpFile = h5py.File(self.baseData.getFileName(time))
            tmpFile = self.parent[time]
            if self.nickname in tmpFile.keys():
                if redo:
                    del tmpFile[self.nickname]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    # outDict[time] = self.processObject.fromFile(self.getFileName(time),hierarchy=self.nickname)
                    outDict[time] = True
            else:
                toDoTimes.append(time)
            # tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):

            with DelayedKeyboardInterrupt():

                # tmpFile = h5py.File(self.baseData.getFileName(time))
                tmpFile = self.parent[time]
                if self.nickname in tmpFile.keys():
                    if redo:
                        print 'preparing %s: redoing time %s' %(self.nickname,time)
                        del tmpFile[self.nickname]
                    else:
                        print 'preparing %s: found prepared time %s' %(self.nickname,time)
                        outDict[time] = True
                        continue

                tmpPrefix = self.nickname+'_'

                tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])
                while tmpString in tmpFile.keys():
                    tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])

                # if self.groupOrImage:
                #     tmpGroup = tmpFile.create_group(tmpString)

                # self.processObject.fromFrame(self.baseData[time],tmpGroup)
                if not (self.baseData is None):
                    self.processObject.fromFrame(time,self.baseData[time],tmpFile,tmpString)
                else: self.processObject.fromFrame(time,None,tmpFile,tmpString)

                tmpFile.move(tmpString,self.hierarchy)

                # outDict[time] = descriptors.H5Pointer(rootFile.filename,nickname)
                # outDict[time] = self.processObject.timepointClass(self.baseData.getFileName(time),self.nickname)
                outDict[time] = True

                # tmpGroup = None
                # tmpFile.close()

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

    def __init__(self,parent,channel,nickname,hierarchy=None,relRawDataDir=None,originalSpacing=None,*args,**kargs):
        print 'creating raw channel'
        # if not relRawDataDir is None:
        #     self.dir = os.path.join(parent.dataDir,relRawDataDir)
        # else: self.dir = os.path.join(parent.dataDir,config['relRawDataDir'] %channel)
        if not hierarchy is None:
            self.hierarchy = hierarchy
        else: self.hierarchy = config['rawHierarchy']

        self.timepointClass = h5py.Dataset
        self.channel = channel
        self.originalSpacing = originalSpacing
        # self.hierarchy = 'DS1'
        # self.hierarchy = 'Data' #malbert
        super(RawChannel,self).__init__(parent,nickname,*args,**kargs)
        self.parent.shape = self[self.parent.times[0]].shape
        return

    def prepareTimepoints(self,times,redo):
        print 'preparing timepoints %s' %times

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            # tmpFile = h5py.File(self.getFileName(time))
            tmpFile = self.parent[time]
            if self.hierarchy in tmpFile.keys() and not redo:
                alreadyDoneTimes.append(time)
                # outDict[time] = H5Array(self.getFileName(time),hierarchy=self.hierarchy)
                outDict[time] = True
            elif self.hierarchy in tmpFile.keys() and redo:
                del tmpFile[self.hierarchy]
                toDoTimes.append(time)
            else:
                toDoTimes.append(time)

            # tmpFile.close()

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

            if tmpData.max() == 0:
                if itime: tmpData = n.array(self.parent[toDoTimes[itime-1]][self.hierarchy])
            else:
                tmpData = interpolateEmptyPlanes(tmpData)

            # if not os.path.exists(self.getFileName(time)):
            #     filing.toH5(tmpData,self.getFileName(time),hierarchy=self.hierarchy)
            # else:
                # tmpFile = h5py.File(self.getFileName(time))
            tmpFile = self.parent[time]

            if not self.originalSpacing is None:
                tmpData = sitk.gifa(tmpData)
                tmpData.SetSpacing(self.originalSpacing)
                tmpData = stacking.space(tmpData,spacing=self.parent.spacing)
                tmpData = sitk.gafi(tmpData)

            filing.toH5_hl(tmpData,tmpFile,hierarchy=self.hierarchy)

            # tmpFile[self.hierarchy] = tmpData
                # tmpFile.close()

            # outDict[time] = H5Array(self.getFileName(time),hierarchy=self.hierarchy)
            outDict[time] = True

        return outDict

def interpolateEmptyPlanes(ar):

    shape = ar.shape
    profile = n.max(n.max(ar,-1),-1)>0

    # cut ends
    start = n.argmax(profile)
    stop = len(profile)-1-n.argmax(profile[::-1])
    # profile = profile[start:stop]


    empties = n.where(profile==0)[0]
    nonempties = n.where(profile!=0)[0]

    for plane in empties:
        if plane <= start or plane >= stop: continue
        prevInd = n.argmax(nonempties[n.where(nonempties<plane)])
        prev = nonempties[prevInd]
        after = nonempties[prevInd+1]
        print plane,prev,after

        z = n.array([0,1])
        y = n.linspace(0,shape[1]-1,shape[1])
        x = n.linspace(0,shape[2]-1,shape[2])

        interp = interpolate.RegularGridInterpolator((z,y,x),n.array([ar[prev],ar[after]]))

        ys,xs = n.mgrid[0:shape[1],0:shape[2]]
        ys = ys.flatten()
        xs = xs.flatten()
        zs = n.ones(len(xs))*(float(plane-prev)/(after-prev))

        newim = interp(n.array([zs,ys,xs]).swapaxes(0,1)).reshape((shape[1],shape[2]))
        ar[plane] = newim

    return ar


class UnstructuredData(object):

    # abstract class for unstructured data, to be subclassed
    # by adding prepare() method, data to pickle

    def __init__(self,parent,baseData,nickname,processClass,fileName=None,redo=False,*args,**kargs):

        self.parent = parent
        self.nickname = nickname
        self.redo = redo
        self.hierarchy = self.nickname
        self.processClass = processClass
        self.processObject = self.processClass(parent,*args,**kargs)
        self.baseData = baseData
        self.times = parent.times

        if not parent.nicknameDict.has_key(nickname):
            parent.nicknameDict[nickname] = self
        else:
            raise(Exception('nickname already taken'))
        parent.__setattr__(nickname,self)

        if fileName is None:
            self.fileName = os.path.join(self.parent.dataDir,self.processClass.__name__+'.h5')
        else:
            self.fileName = os.path.join(self.parent.dataDir,fileName+'.h5')

        print 'instanciating unstructured data at file %s' %self.fileName


        self.file = h5py.File(self.fileName)

        self.data = self.prepare(self.redo)


    def __get__(self,instance,owner):
        raise(Exception('no getting possible!'))

    def __set__(self,instance,value):
        raise(Exception('no setting possible!'))

    def prepare(self,redo):

        if self.hierarchy in self.file.keys():
            if not redo:
                return
            else:
                del self.file[self.hierarchy]

        with DelayedKeyboardInterrupt():

            tmpFile = self.file

            tmpPrefix = self.nickname+'_'
            tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])
            while tmpString in tmpFile.keys():
                tmpString = tmpPrefix + str(n.random.randint(0,1000000000000000,1)[0])

            tmpGroup = tmpFile.create_group(tmpString)

            self.processObject.fromBaseData(self.baseData,tmpFile,tmpString)

            tmpFile.move(tmpString,self.hierarchy)

        return

    def __getitem__(self,item,**kargs):
        if type(item) == int:

            if not (item in self.times):
                raise(Exception('requested time %s not available in unstructured data with times %s' %(item,self.times)))

            try:
                res = self.processObject.getTimePoint(self.file,self.hierarchy,item)
            except:
                raise(Exception('problem getting timepoint'))
        elif type(item) == str:
            res = self.processObject.getString(self.file,self.hierarchy,item,self.baseData,**kargs)
        else:
            raise(Exception('wrong argument to __getitem__: %s' %item))

        return res

    def __len__(self):

        try:
            res = self.processObject.getLength(self.file,self.hierarchy)
        except:
            raise(Exception('problem getting length'))

        return res

class FromFile(object):

    def __init__(self,parent, filePattern, fileSpacing=None, compression='jls',compressionOption=0):
        print 'instanciating FromFile for %s' %filePattern
        self.filePattern = filePattern
        self.fileSpacing = fileSpacing
        self.parent = parent
        self.compression = compression
        self.compressionOption = compressionOption
        # self.timeOffset = timeOffset
        return

    def fromFrame(self,time,frame,tmpFile,tmpHierarchy):

        tmpDict = dict()
        tmpDict['time'] = time
        tmpDict['wildcard'] = '.*'

        listDir = os.listdir(os.path.dirname(self.filePattern))
        tmpRe = re.compile(self.filePattern %tmpDict)
        found = 0
        for fileName in listDir:
            fileName = os.path.join(os.path.dirname(self.filePattern),fileName)
            if not tmpRe.match(fileName) is None:
                found = 1
                break

        if not found: raise(Exception('could not find file for timepoint %s' %time))

        sImage = sitk.ReadImage(fileName)
        if not self.fileSpacing is None:
            sImage.SetSpacing(self.fileSpacing)
            sImage = stacking.space(sImage,spacing=self.parent.spacing)
        tmpImage = sitk.gafi(sImage)

        filing.toH5_hl(tmpImage.astype(n.uint16),tmpFile,hierarchy=tmpHierarchy,
                       compression=self.compression,compressionOption=self.compressionOption)

        return