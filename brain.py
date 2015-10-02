__author__ = 'malbert'

from dependencies import *

# config['fileNameFormat'] = "f%06d.h5"

class Brain(object):

    def __init__(self,fileName,
                 dimt = 1000,
                 dimc = 2,
                 baseDataDir = '/data/malbert/quantification',
                 subDir = '%s' %timestamp,
                 channels = [],
                 times = [],
                 registrationSliceStringSitk = None,
                 spacing = None,
                 origin = None,
                 fileNameFormat = "f%06d.h5",
                 ):

        self.fileNameFormat = fileNameFormat

        if spacing is None:
            self.spacing = n.array([1,1,1.])
        else:
            self.spacing = spacing
        if origin is None:
            self.origin = n.zeros(3)
        else:
            self.origin = origin

        self.datashape = None
        self.dimt = dimt
        self.dimc = dimc
        self.debug = False
        self.fileName = fileName
        self.originalFile = None
        self.baseDataDir = baseDataDir
        self.subDir = subDir
        self.dataDir = os.path.join(self.baseDataDir,self.subDir)

        self.classifiers = dict()
        self.registrationSliceStringSitk = registrationSliceStringSitk

        self.nicknameDict = dict()

        self.channels = channels
        self.times = times

        if not os.path.exists(self.dataDir): os.mkdir(self.dataDir)

        self.fileDict = dict()

        for itime,time in enumerate(self.times):
            self.fileDict[time] = h5py.File(os.path.join(self.dataDir,self.fileNameFormat) %time)

        return

    def __getitem__(self,time):
        if time in self.fileDict.keys():
            return self.fileDict[time]
        else:
            if os.path.exists(os.path.join(self.dataDir,self.fileNameFormat) %time):
                self.fileDict[time] = h5py.File(os.path.join(self.dataDir,self.fileNameFormat) %time)
            else:
                raise(Exception('timepoint %s not initialized yet' %time))


