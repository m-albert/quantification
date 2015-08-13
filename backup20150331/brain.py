__author__ = 'malbert'

from dependencies import *

class Brain(object):

    def __init__(self,fileName,
                 scaleFactors = [1.,1.,1.],
                 baseDataDir = '/data/malbert/quantification'):

        self.scaleFactors = n.array(scaleFactors).astype(n.float64)
        self.debug = False

        self.fileName = fileName
        self.baseDataDir = baseDataDir
        self.dataDir = os.path.join(self.baseDataDir,
                os.path.basename(fileName)+'_scaleFactors_%s_%s_%s' %tuple(self.scaleFactors))
        self.segmentationDir = os.path.join(self.dataDir,'segmentation')
        if not os.path.exists(self.dataDir): os.mkdir(self.dataDir)
        if not os.path.exists(self.segmentationDir): os.mkdir(self.segmentationDir)

        self.data = []
        self.segmentation = []
        self.classifiers = []
        self.objectSnaps = []
        self.lastThreshold = 0
        self.transform = None
        self.registrationParams = None

        self.spacing = n.array([1.,1.,1.])

        self.dimc,self.dimt,self.dimx,self.dimy,self.dimz = [0,0,0,0,0]
        #loadData(self)

def initialize(brain):
    # initial methods
    #prepareIlastikSamples(brain)
    brain.objectSnaps = [[] for i in range(brain.dimc)]
    brain.tracks = [[] for i in range(brain.dimc)]
    brain.segmentation = [[] for i in range(brain.dimc)]
    # brain.classifiers = ['' for i in range(brain.dimc)]
    return

def prepareIlastikSamples(brain):
    #pdb.set_trace()
    didPrepare = False
    for ic in range(brain.dimc):
        for isample in [0,1]:
            tmpFile = os.path.join(brain.dataDir,'ilastiktraining_channel%s_%s.h5' %(ic,isample))
            if not os.path.exists(tmpFile):
                filing.arrayToH5(brain.data[ic][[0,-1][isample]],tmpFile)
                didPrepare = True
    # if didPrepare: raise(Exception('train ilastik'))
    return didPrepare

def segment(brain):
    print 'segmenting...'
    #if len(brain.segmentation) == brain.dimc: return
    #elif len(brain.segmentation): raise(Exception('strange segmentation array'))
    segmentationFiles = [os.path.join(brain.dataDir,'segmentation_channel%s.h5' %ic) for ic in range(brain.dimc)]
    for ic in range(brain.dimc):
        if brain.classifiers[ic] == '':
            print 'no classifier for channel %s, continuing...' %ic
            continue
        #segmentationFiles.append()
        if os.path.exists(segmentationFiles[ic]):
            brain.segmentation[ic] = filing.readH5(segmentationFiles[ic])
        else:
            brain.segmentation[ic] = ilastiking.runIlastik(brain.data[ic],brain.classifiers[ic],outLabelIndex=1)
            filing.arrayToH5Raw(brain.segmentation[ic],segmentationFiles[ic])
    brain.segmentation = n.array(brain.segmentation)
    return

def segmentSequential(brain,times):
    print 'segmenting...'
    #if len(brain.segmentation) == brain.dimc: return
    #elif len(brain.segmentation): raise(Exception('strange segmentation array'))
    segmentationFiles = []
    for ic in range(brain.dimc):
        segmentationFiles.append(os.path.join(brain.dataDir,'segmentation_channel%s.h5' %ic))
        if os.path.exists(segmentationFiles[ic]):
            brain.segmentation[ic] = filing.readH5(segmentationFiles[ic])
        else:
            segs = []
            for it in times:
                tmpFile = segmentationFiles[ic][:-3]+'_%03d.h5' %it
                #pdb.set_trace()
                if os.path.exists(tmpFile):
                    tmpSeg = filing.readH5(tmpFile)
                else:
                    tmpSeg = ilastiking.runIlastik([brain.data[ic][it]],brain.classifiers[ic],outLabelIndex=1)[0]
                    filing.arrayToH5Raw(tmpSeg,segmentationFiles[ic][:-3]+'_%03d.h5' %it)
                segs.append(tmpSeg)
            brain.segmentation[ic] = n.array(segs)
            filing.arrayToH5Raw(brain.segmentation[ic],segmentationFiles[ic])
    brain.segmentation = n.array(brain.segmentation)
    return

def segmentNew(brain,channels=None):
    print 'segmenting...'
    if len(brain.segmentation) == brain.dimc: return
    elif len(brain.segmentation): raise(Exception('strange segmentation array'))
    if channels is None: channels = range(brain.dimc)
    segmentationFile = os.path.join(brain.dataDir,'segmentation_channel%s.h5')
    for ic,channel in enumerate(channels):
        if os.path.exists(segmentationFile %channel):
            brain.segmentation[channel] = filing.readH5(segmentationFile %channel)
        else:
            brain.segmentation[channel] = ilastiking.runIlastik(brain.data[channel],brain.classifiers[channel],outLabelIndex=1)
            filing.arrayToH5Raw(brain.segmentation[channel],segmentationFile %channel)
    return

def loadData(brain):
    print 'loading data...'
    # order = [c,t,x,y,z]
    fileName = brain.fileName
    scaledFileName = os.path.join(brain.dataDir,'scaledData.h5')
    if os.path.exists(scaledFileName):
        brain.data = filing.readH5(scaledFileName,hierarchy='DS1')
    else:
        if fileName[-3:] == 'lsm':
            im = tifffile.imread(fileName).astype(n.uint16)
            dimx,dimy,dimz,dimt,dimc = 3,4,1,0,2
            im = misc.sortAxes(im,[dimc,dimt,dimx,dimy,dimz])
        if fileName[-3:] == '.h5':
            im = filing.readH5Image(fileName).astype(n.uint16)
        if fileName[-3:] == 'czi':
            import czifile
            #pdb.set_trace()
            im = czifile.imread(fileName)
            if len(im.shape) == 7:
                im = im[0,:,:,:,:,:,0]
            elif len(im.shape) == 11:
                im = im[0,0,0,0,0,:,:,:,:,:,0]
            else: raise(Exception('look at czi file shape'))
            brain.spacing = zf.getStackInfoFromCZI(fileName)['spacing']
            #pdb.set_trace()
        #pdb.set_trace()
        if (brain.scaleFactors[0] == 1) and ((brain.scaleFactors[1] == 1) and (brain.scaleFactors[2] == 1)):
            print 'no scaling'
        else:
            print 'scaling data by factors %s' %brain.scaleFactors
            scaledData = []
            for ic in range(im.shape[0]):
                tmpC = []
                #for it in range(im.shape[1]):
                # print 'only taking 30!'
                for it in range(im.shape[1]):
                    tmpC.append(sitk.gafi(beads.scaleStack(1/brain.scaleFactors[::-1],sitk.gifa(im[ic][it]))))
                scaledData.append(n.array(tmpC))
            im = n.array(scaledData)
        brain.data = n.array(im)
        filing.arrayToH5Raw(brain.data,scaledFileName)
    brain.dimc,brain.dimt,brain.dimx,brain.dimy,brain.dimz = brain.data.shape
    return


# def registerToReference(brain,refImage,channel=1):
#     infoDict = dict()
#     infoDict['spacing'] = n.array([1.,1.,1.])
#     infoDict['']
#     zf.elastixParameterTemplateStringAffineBeforeNonRigid
#     regSample = sitk.gifa(brain.data[channel][0])
#     # transform = register(refImage,regSample)
#     return

def getParamsFromElastix(b,refImage,channel=0):#,affineOrRigidOrSimilarity=2):

    transformFile = 'transformParamsSimilarity3.pc'

    paramsPath = os.path.join(b.dataDir,transformFile)
    if os.path.exists(paramsPath):
        finalParams = pickle.load(open(paramsPath))
        print finalParams
        b.registrationParams = finalParams
        return

    movImage = sitk.gifa(b.data[channel][0])
    movImage.SetSpacing(b.spacing)
    movImage = sitk.Resample(movImage,refImage)
    # if not(scaleParams is None):
    #     scaleParams = n.array(scaleParams)
    #     movImage = beads.scaleStack(scaleParams[::-1],movImage)
    #     movImage.SetSpacing(b.spacing*scaleParams)
    # else: movImage.SetSpacing(b.spacing)

    params = [1.,0,0,0,1,0,0,0,1,0,0,0]
    fiPath = os.path.join(tmpDir,'tmpFixedImage.mhd')
    sitk.WriteImage(refImage,fiPath)

    # finalParams = [[1.,0,0,0,1,0,0,0,1,0,0,0]]
    for iim in range(1,2):

        miPath = os.path.join(tmpDir,'tmpMovingImage.mhd')
        sitk.WriteImage(movImage,miPath)

        paramDict = dict()

        paramDict['el'] = elastixPath
        parameterPath = os.path.join(tmpDir,'elastixParameters.txt')
        initialTransformPath = os.path.join(tmpDir,'elastixInitialTransform.txt')
        paramDict['out'] = tmpDir
        extras.createInitialTransformFile(n.array([1,1,1.]),params,elastixInitialTransformTemplateString,initialTransformPath)
        #if affineOrRigid: parameterTemplateString = elastixParameterTemplateStringAffine
        #else: parameterTemplateString = elastixParameterTemplateStringRotation
        # parameterTemplateString = elastixParameterTemplateStringAffine#
        parameterTemplateString = elastixParameterOTAtlas
        # parameterTemplateString = elastixParameterTemplateStringRotation
        extras.createParameterFile(n.array([1,1,1.]),initialTransformPath,parameterTemplateString,parameterPath)
        paramDict['params'] = parameterPath
        paramDict['f1'] = fiPath
        paramDict['f2'] = miPath
        paramDict['initialTransform'] = initialTransformPath

        # run elastix
        cmd = ('%(el)s -f %(f1)s -m %(f2)s -p %(params)s -t0 %(initialTransform)s -out %(out)s' %paramDict).split(' ')
        print "\n\nCalling elastix for image based registration with arguments:\n\n %s\n\n" %cmd
        subprocess.Popen(cmd).wait()

        outFile = os.path.join(paramDict['out'],'TransformParameters.0.txt')
        # read output parameters from elastix output file
        rawOutParams = open(outFile).read()

        outParams = rawOutParams.split('\n')[2][:-1].split(' ')[1:]
        outParams = n.array([float(i) for i in outParams])
        outCenterOfRotation = rawOutParams.split('\n')[19][:-1].split(' ')[1:]
        outCenterOfRotation = n.array([float(i) for i in outCenterOfRotation])
        if len(outParams)==6:
            tmp = transformations.euler_matrix(outParams[0],outParams[1],outParams[2])
            affineOutParams = n.zeros(12)
            affineOutParams[:9] = tmp[:3,:3].flatten()
            affineOutParams[-3:] = n.array([outParams[3],outParams[4],outParams[5]])
        elif len(outParams)==12:
            affineOutParams = outParams
        # elif len(outParams)==7:
        #     tmp = transformations.compose_matrix(scale=n.array([outParams[6]]*3),
        #                                          angles=n.array([outParams[0],outParams[1],outParams[2]]),
        #                                          translate=n.array([outParams[3],outParams[4],outParams[5]]))
        #     affineOutParams = n.zeros(12)
        #     pdb.set_trace()
        #     affineOutParams[:9] = tmp[:3,:3].flatten()
        #     affineOutParams[-3:] = tmp[:3,3]
        elif len(outParams)==7:
            angles = transformations.euler_from_quaternion([n.sqrt(1-n.sum([n.power(outParams[i],2) for i in range(3)])),
                                                            outParams[0],outParams[1],outParams[2]])
            tmp = transformations.compose_matrix(#scale=n.array([outParams[6]]*3),
                                                 angles=angles)
                                                 #translate=n.array([outParams[3],outParams[4],outParams[5]]))
            affineOutParams = n.zeros(12)
            # pdb.set_trace()
            affineOutParams[:9] = tmp[:3,:3].flatten()*outParams[6]
            affineOutParams[-3:] = n.array([outParams[3],outParams[4],outParams[5]])

        else: raise(Exception('unable to interpret parameters'))

        totalTranslate = affineOutParams[-3:] - n.dot(affineOutParams[:9].reshape((3,3)),outCenterOfRotation) + outCenterOfRotation
        affineOutParams = n.concatenate([affineOutParams[:9],totalTranslate],0)
        lastParams = fusion.composeAffineTransformations([affineOutParams,params])

        finalParams = lastParams

    finalParams = n.array(finalParams)
    pickle.dump(finalParams,open(paramsPath,'w'))
    b.registrationParams = finalParams
    return

def transform(b,data,refIm=None):
    if data.dtype == n.bool:
        data = data.astype(n.uint8)
    tmpData = sitk.gifa(data)
    tmpData.SetSpacing(b.spacing)
    return sitk.gafi(beads.transformStackAndRef(b.registrationParams,tmpData,refIm))


elastixParameterTemplateStringAffine = """
// Description: affine
(RequiredRatioOfValidSamples 0.05)

(Transform "AffineTransform")
//(Transform "SimilarityTransform")

(GradientMagnitudeTolerance 1e-7)
(NumberOfResolutions 3)

//(ImagePyramidSchedule  8 8 2  4 4 1  2 2 1 )
(ImagePyramidSchedule  10 10 10  4 4 4  2 2 2)

//ImageTypes
(FixedInternalImagePixelType "float")
(FixedImageDimension 3)
(MovingInternalImagePixelType "float")
(MovingImageDimension 3)
(UseDirectionCosines "false")

//Components
(Registration "MultiResolutionRegistration")
(FixedImagePyramid "FixedRecursiveImagePyramid")
//(Registration "MultiMetricMultiResolutionRegistration")
(MovingImagePyramid "MovingRecursiveImagePyramid")
(Interpolator "BSplineInterpolator")
(Metric "AdvancedMattesMutualInformation")

(Optimizer "QuasiNewtonLBFGS")
//(Optimizer ConjugateGradient)

(ResampleInterpolator "FinalBSplineInterpolator")
(Resampler "DefaultResampler")

(ErodeMask "false" )

(HowToCombineTransforms "Compose")
(AutomaticTransformInitialization "false")
(AutomaticScalesEstimation "true")
//(AutomaticTransformInitializationMethod "CenterOfGravity" )

(WriteTransformParametersEachIteration "false")
(WriteResultImage "true")
(CompressResultImage "false")
(ShowExactMetricValue "false")

(ImageSampler "Full")

//Order of B-Spline interpolation used in each resolution level:
(BSplineInterpolationOrder 1)

(FixedImageBSplineInterpolationOrder 1)
(MovingImageBSplineInterpolationOrder 1)

//Order of B-Spline interpolation used for applying the final deformation:
(FinalBSplineInterpolationOrder 1)

//Default pixel value for pixels that come from outside the picture:
(DefaultPixelValue 0)

//(MaximumStepLength 4.0)
(ResultImagePixelType "short")
(ResultImageFormat "mhd")
"""

elastixInitialTransformTemplateString = """
(Transform "AffineTransform")
(NumberOfParameters 12)

(HowToCombineTransforms "Compose")

(InitialTransformParametersFileName "NoInitialTransform")

// Image specific
(FixedImageDimension 3)
(MovingImageDimension 3)
(FixedInternalImagePixelType "short")
(MovingInternalImagePixelType "short")
//(UseDirectionCosines "false")



(CenterOfRotationPoint 0 0 0)
"""


elastixParameterTemplateStringRotation = """
// Description: affine

(RequiredRatioOfValidSamples 0.05)

(Transform "EulerTransform")
(GradientMagnitudeTolerance 1e-7)
(NumberOfResolutions 3)

//(ImagePyramidSchedule  8 8 2  4 4 1  2 2 1 )
(ImagePyramidSchedule   10 10 10 4 4 4 2 2 2)

//ImageTypes
(FixedInternalImagePixelType "short")
(FixedImageDimension 3)
(MovingInternalImagePixelType "short")
(MovingImageDimension 3)
(UseDirectionCosines "false")

//Components
(Registration "MultiResolutionRegistration")
(FixedImagePyramid "FixedRecursiveImagePyramid")
//(Registration "MultiMetricMultiResolutionRegistration")
(MovingImagePyramid "MovingRecursiveImagePyramid")
(Interpolator "BSplineInterpolator")
(Metric "AdvancedMattesMutualInformation")
//(Metric "AdvancedKappaStatistic")
//(Metric0Weight 1.0) (Metric1Weight 1.0)
//(Metric "AdvancedMeanSquares")
//(Optimizer "AdaptiveStochasticGradientDescent")


(Optimizer "QuasiNewtonLBFGS")
//(Optimizer ConjugateGradient)

//(StopIfWolfeNotSatisfied "false")

(ResampleInterpolator "FinalBSplineInterpolator")
(Resampler "DefaultResampler")
//(Resampler "CUDAResampler")
//(CenterOfRotationPoint 0.0 0.0 0.0)

(ErodeMask "false" )

(HowToCombineTransforms "Compose")
(AutomaticTransformInitialization "false")
(Scales 10000 10000 10000 1 1 1)
//(Scales 1000 1000 1000 1 1 1)
(AutomaticScalesEstimation "false")
//(AutomaticTransformInitializationMethod "CenterOfGravity" )

(WriteTransformParametersEachIteration "false")
(WriteResultImage "true")
(CompressResultImage "false")
//(WriteResultImageAfterEachResolution "true")
(ShowExactMetricValue "false")

//Maximum number of iterations in each resolution level:
//(MaximumNumberOfIterations 500)

//Number of grey level bins in each resolution level:
(NumberOfHistogramBins 64)
//(FixedLimitRangeRatio 0.0)
//(MovingLimitRangeRatio 0.0)
//(FixedKernelBSplineOrder 3)
//(MovingKernelBSplineOrder 3)

//Number of spatial samples used to compute the mutual information in each resolution level:
//(ImageSampler "RandomCoordinate")
//(ImageSampler "RandomSparseMask")
(ImageSampler "Full")
//(SampleGridSpacing 1)
//(NumberOfSpatialSamples 5000)
//(NewSamplesEveryIteration "true")
//(CheckNumberOfSamples "true")
//(MaximumNumberOfSamplingAttempts 10)

//Order of B-Spline interpolation used in each resolution level:
(BSplineInterpolationOrder 1)

(FixedImageBSplineInterpolationOrder 1)
(MovingImageBSplineInterpolationOrder 1)

//Order of B-Spline interpolation used for applying the final deformation:
(FinalBSplineInterpolationOrder 1)

//Default pixel value for pixels that come from outside the picture:
(DefaultPixelValue 0)

//(MaximumStepLength 4.0)
(ResultImagePixelType "short")
(ResultImageFormat "mhd")
"""

elastixParameterOTAtlas = """

// Description
// Stage: affine
//
// Author:      Roy van Pelt
// Affiliation: Eindhoven University of Technology
// Year:        2013

// ********** Image Types

(FixedInternalImagePixelType "float")
(FixedImageDimension 3)
(MovingInternalImagePixelType "float")
(MovingImageDimension 3)


// ********** Components

(Registration "MultiResolutionRegistration")
(FixedImagePyramid "FixedRecursiveImagePyramid")
(MovingImagePyramid "MovingRecursiveImagePyramid")
(Interpolator "BSplineInterpolator")
//(Metric "AdvancedMattesMutualInformation")
(Metric "NormalizedMutualInformation")
(Optimizer "AdaptiveStochasticGradientDescent")
(ResampleInterpolator "FinalBSplineInterpolator")
(Resampler "DefaultResampler")
(Transform "SimilarityTransform")


// ********** Pyramid

// Total number of resolutions
(NumberOfResolutions 4)
(ImagePyramidSchedule 16 16 4 8 8 2 4 4 1 2 2 1)


// ********** Transform

(AutomaticScalesEstimation "true")
(AutomaticTransformInitialization "true")
(AutomaticTransformInitializationMethod "CenterOfGravity")
(HowToCombineTransforms "Compose")


// ********** Optimizer

// Maximum number of iterations in each resolution level:
//(MaximumNumberOfIterations 300 200 100 50)

(MaximumNumberOfIterations 2000 1000 500 250)
//(MaximumNumberOfIterations 600 400 200 100)

//(MaximumNumberOfIterations 5000 2500 1000 500)

(AutomaticParameterEstimation "true")
(UseAdaptiveStepSizes "true")
(NumberOfHistogramBins 64 64 64)
(NumberOfFixedHistogramBins 64 64 64)
(NumberOfMovingHistogramBins 64 64 64)

//(NumberOfGradientMeasurements 0)
//(NumberOfJacobianMeasurements 4056)
(NumberOfBandStructureSamples 10)
//(MaximumStepLength 2.29829)
(SigmoidInitialTime 0 0 0)

// ********** Several

(WriteTransformParametersEachIteration "false")
(WriteTransformParametersEachResolution "false")
(WriteResultImageAfterEachResolution "false")
(WritePyramidImagesAfterEachResolution "false")
(WriteResultImageAfterEachIteration "false")
(ShowExactMetricValue "false")
(ErodeFixedMask "false" "false" "false")
(ErodeMovingMask "false" "false" "false")
(UseDirectionCosines "false")
(FixedLimitRangeRatio 0.01 0.01 0.01)
(MovingLimitRangeRatio 0.01 0.01 0.01)
(UseFastAndLowMemoryVersion "true")

// ********** ImageSampler

//Number of spatial samples used to compute the mutual information in each resolution level:
(ImageSampler "RandomCoordinate")
(CheckNumberOfSamples "false" "false" "false")
(NumberOfSpatialSamples 2048 4096 4096 4096)
(NumberOfSamplesForSelfHessian 10000)
(NumberOfSamplesForExactGradient 10000)
(NewSamplesEveryIteration "true")
(UseRandomSampleRegion "false")
(MaximumNumberOfSamplingAttempts 0 0 0)
(RequiredRatioOfValidSamples 0.25)


// ********** Interpolator and Resampler

//Order of B-Spline interpolation used in each resolution level:
(BSplineInterpolationOrder 1 1 1 1)
(FixedImageBSplineInterpolationOrder 1 1 1 1)
(MovingImageBSplineInterpolationOrder 1 1 1 1)
(FixedKernelBSplineOrder 3 3 3 3)
(MovingKernelBSplineOrder 3 3 3 3)

//Order of B-Spline interpolation used for applying the final deformation:
(FinalBSplineInterpolationOrder 3)

//Default pixel value for pixels that come from outside the picture:
(DefaultPixelValue 0)

(WriteResultImage "true")
(CompressResultImage "false")

// The pixel type and format of the resulting deformed moving image
(ResultImagePixelType "float")
(ResultImageFormat "mhd")
"""