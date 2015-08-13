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
                 registrationSliceStringSitk = None,
                 ):

        self.datashape = None
        self.dimt = dimt
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


if __name__=="__main__":
    b = MockBrain('/data/malbert/data/dbspim/20150317/20150317_45dpf_pu1_gcamp6s_right_15s_Subset.czi',
                dimt = 1000,
                channels = [1,0],
                times = range(100),
                registrationSliceStringSitk = ":,:,60:90:2"
                )

    mask = sitk.ReadImage('/data/malbert/quantification/20150317_45dpf_pu1_gcamp6s_right_15s_Subset.czi/mask_000000.tif')

    descriptors.RawChannel(b,1,'mic')
    descriptors.RawChannel(b,0,'gcamp')
    b.classifiers['mic'] = 1

    prediction.Prediction(b,b.mic,'predmic')

    registration.RegistrationParameters(b,b.gcamp,'registrationParams')

    registration.Transformation(b,b.predmic,b.registrationParams,mask=mask,nickname='regpredmic',redo=False,offset=n.array([0,11.,0]))
    registration.Transformation(b,b.gcamp,b.registrationParams,mask=mask,nickname='reggcamp',redo=False)

    # activity.SlidingWindowMean(b,b.reggcamp,filterSize=5,nickname='refreggcamp',redo=True)
    activity.Signal(b,b.reggcamp,filterSize=5,nickname='signal',redo=False)

    segmentation.Segmentation(b,b.regpredmic,'segregpredmic',redo=False,threshold=0.5,sizeThreshold=100)

    # tracking.Track(b,b.segregpredmic(range(100)),'tracksegmic',redo=True)

    # execfile('analyse3.py')
