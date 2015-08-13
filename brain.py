__author__ = 'malbert'

from dependencies import *

class Brain(object):

    def __init__(self,fileName,
                 dimt = 1000,
                 dimc = 2,
                 baseDataDir = '/data/malbert/quantification',
                 channels = [],
                 times = [],
                 registrationSliceStringSitk = None,
                 ):

        self.datashape = None
        self.dimt = dimt
        self.dimc = dimc
        self.debug = False
        self.fileName = fileName
        self.originalFile = None
        self.baseDataDir = baseDataDir
        self.dataDir = os.path.join(self.baseDataDir,os.path.basename(fileName))

        self.classifiers = dict()
        self.registrationSliceStringSitk = registrationSliceStringSitk

        # self.classChannels = dict()
        # self.classChannels['RawChannel'] = rawChannels
        # self.classChannels['SegmentationChannel'] = segmentationChannels
        # self.classChannels['RegistrationChannel'] = registrationChannels
        # self.classChannels['SkeletonizationChannel'] = skeletonizationChannels
        # self.classChannels['PredictionChannel'] = predictionChannels

        # self.classData = dict()

        self.nicknameDict = dict()

        self.channels = channels
        self.times = times
        # self.validTimes = validTimes
        # if self.validTimes is None:
        #     self.validTimes = [time for time in times]

        if not os.path.exists(self.dataDir): os.mkdir(self.dataDir)