__author__ = 'malbert'

import sys
sys.path.append('..')
from dependencies import *

# @sys.settrace
# def trace_debug(frame, event, arg):
#     if event == 'call':
#         # print (set(globals()) - basestuff)
#         if frame.f_code.co_name in (set(globals()) - basestuff):
#             print ("calling %r on line %d, vars: %r" %
#                     (frame.f_code.co_name,
#                      frame.f_lineno,
#                      frame.f_locals,
#                      # arg,
#                      ))
#             return trace_debug
#     elif event == "return":
#         print "returning", arg

basestuff = set(globals())

class MockBrain(object):

    def __init__(self,fileName,
                 dimt = 1000,
                 baseDataDir = '/data/malbert/quantification',
                 channels = [],
                 times = [],
                 validTimes = None,
                 rawChannels = [],
                 predictionChannels = [],
                 segmentationChannels = [],
                 registrationChannels = [],
                 skeletonizationChannels = [],

                 registrationSliceStringSitk = None,
                 ):

        self.dimt = dimt
        self.debug = False
        self.fileName = fileName
        self.originalFile = None
        self.baseDataDir = baseDataDir
        self.dataDir = os.path.join(self.baseDataDir,os.path.basename(fileName))

        self.classifiers = dict()
        self.registrationSliceStringSitk = registrationSliceStringSitk

        self.classChannels = dict()
        self.classChannels['RawChannel'] = rawChannels
        self.classChannels['SegmentationChannel'] = segmentationChannels
        self.classChannels['RegistrationChannel'] = registrationChannels
        self.classChannels['SkeletonizationChannel'] = skeletonizationChannels
        self.classChannels['PredictionChannel'] = predictionChannels

        self.classData = dict()

        self.channels = channels
        self.times = times
        self.validTimes = validTimes
        if self.validTimes is None:
            self.validTimes = [time for time in times]

        if not os.path.exists(self.dataDir): os.mkdir(self.dataDir)




def testStackAccess():
    s = descriptors.H5Array('teststack.h5')
    assert(len(s.__get__(s,descriptors.H5Array).shape)==3)
    del s
    return True


def testRawChannelData(b):

    b.mic = descriptors.RawChannel(b,1)
    b.gcamp = descriptors.RawChannel(b,0)

    return True

def testPredictionChannelData(b):

    b.segmic = prediction.Prediction(b,b.mic)

    return True

def testSegmentationChannelData(b):

    descriptors.ImageData(b,segmentation.SegmentationChannel,prediction.PredictionChannel)

    return True

def testRegistrationChannelData(b):

    descriptors.ImageData(b,registration.RegistrationParamsChannel)

    return True


if __name__=="__main__":
    b = MockBrain('/data/malbert/data/dbspim/20150317/20150317_45dpf_pu1_gcamp6s_right_15s_Subset.czi',
                dimt = 1000,
                channels = [1,0],
                times = range(2),
                rawChannels = [0,1],
                predictionChannels = [1],
                segmentationChannels = [1],
                registrationChannels = [0],
                registrationSliceStringSitk = ":,:,60:90:2"
                )


    testStackAccess()
    testRawChannelData(b)

    # b.classifiers[1] =
    testPredictionChannelData(b)
    # testSegmentationChannelData(b)
    # testRegistrationChannelData(b)
    # b.times = range(100)
    # tifffile.imshow(b.data[0])
