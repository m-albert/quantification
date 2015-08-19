__author__ = 'malbert'

from dependencies import *

# config['registrationPath'] = 'registrationParameters'
# config['registeredPath'] = 'registered'

class RegistrationParameters(descriptors.ChannelData):

    nickname = 'registrationParams'

    def __init__(self,parent,baseData,nickname,

                 mode = 'intra',
                 reference = 0,
                 initialRegistration=None,
                 *args,**kargs):

        print 'creating registration channel with nickname %s' %nickname

        self.baseData = baseData

        self.dir = self.baseData.dir
        self.fileNameFormat = self.baseData.fileNameFormat

        self.validTimes = range(parent.dimt)

        self.reference = reference
        self.initialRegistration = initialRegistration
        self.mode = mode

        self.relShape = None

        super(RegistrationParameters,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = descriptors.H5Array


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
                    outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=self.nickname)
                    if self.mode == 'inter' and not time:
                    # if self.singleRegistrationTime is None or self.singleRegistrationTime == time:
                        self.relParams = outDict[time].__get__(outDict[time],outDict[time])
                        if type(self.reference) == sitk.Image:
                            self.relShape = n.array(self.reference.GetSize())
                        elif type(self.reference) == n.array:
                            self.relShape = n.array(self.reference.shape)[::-1]
                    if self.mode == 'intra' and time == self.reference:
                        self.relShape = n.array(self.baseData[self.reference].shape)[::-1]

            else:
                toDoTimes.append(time)
            tmpFile.close()

            # self.baseData.close(time)

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        # process reference image
        if type(self.reference) == int:
            tmpImage = sitk.gifa(self.baseData[self.parent.times[self.reference]])
        elif type(self.reference) == sitk.Image:
            tmpImage = self.reference
        elif type(self.reference) == n.array:
            tmpImage = sitk.gifa(self.reference)
        elif type(self.reference) == str:
            tmpImage = sitk.ReadImage(self.reference)
        else:
            raise(Exception('check reference image argument'))

        if not (self.parent.registrationSliceStringSitk is None):
            exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

        outFileRef = os.path.join(tmpDir,'refImage.mhd')
        outFileRefRaw = os.path.join(tmpDir,'refImage.raw')
        sitk.WriteImage(tmpImage,outFileRef)

        # pdb.set_trace()

        for itime,time in enumerate(toDoTimes):

            # process initial params
            if self.initialRegistration is None:
                initialParams = None
            elif type(self.initialRegistration) == type(RegistrationParameters):
                initialParams = n.array(self.initialRegistration[time])
            elif len(self.initialRegistration) != 12 and len(self.initialRegistration[times[0]]) == 12:
                initialParams = self.initialRegistration[time]
            elif len(self.initialRegistration) == 12:
                initialParams = self.initialRegistration
            else:
                raise(Exception('check initialRegistration argument: %s' %self.initialRegistration))

            if self.mode == 'intra':
                if time == self.reference:
                    tmpParams = n.array([1.,0,0,0,1,0,0,0,1,0,0,0])
                else:
                    if self.relShape is None: self.relShape == self.baseData[0].shape[::-1]
                    tmpImage = sitk.gifa(self.baseData[time])
                    if not (self.parent.registrationSliceStringSitk is None):
                        exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

                    closestTime = alreadyDoneTimes[n.argmin(n.abs(n.array(alreadyDoneTimes)-time))]
                    tmpObject = outDict[closestTime]
                    tmpInitialParams = [[1.,0,0,0,1,0,0,0,1,0,0,0],tmpObject.__get__(tmpObject,tmpObject)]
                    print 'taking tp %s as initial (intra) parameters for tp %s' %(closestTime,time)

                    inputList = [outFileRef,tmpImage]
                    mode = 'rigid'
                    tmpParams = getParamsFromElastix(inputList,
                                      initialParams=tmpInitialParams,
                                      tmpDir=tmpDir,
                                      mode=mode,
                                      masks=None)
                    tmpParams = n.array(tmpParams[1]).astype(n.float64)

            elif self.mode == 'inter':
                if not time:
                    if self.relShape is None: self.relShape == n.array(tmpImage.GetSize())

                    tmpImage = sitk.gifa(self.baseData[time])
                    if not (self.parent.registrationSliceStringSitk is None):
                        exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

                    if initialParams is None: tmpInitialParams = None
                    else: tmpInitialParams = [[1.,0,0,0,1,0,0,0,1,0,0,0],initialParams]

                    inputList = [outFileRef,tmpImage]
                    mode = 'similarity'
                    tmpParams = getParamsFromElastix(inputList,
                                      initialParams=tmpInitialParams,
                                      tmpDir=tmpDir,
                                      mode=mode,
                                      masks=None)
                    tmpParams = n.array(tmpParams[1]).astype(n.float64)
                    self.relParams = tmpParams
                else:
                    if initialParams is None:
                        tmpParams = self.relParams
                    else:
                        tmpParams = composeAffineTransformations([initialParams,self.relParams])


            tmpFile = h5py.File(self.baseData[time].file.filename)
            tmpFile[self.nickname] = tmpParams
            tmpFile.close()

            outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),hierarchy=self.nickname)
            alreadyDoneTimes.append(time)

            self.baseData.close(time)

        os.remove(outFileRef)
        os.remove(outFileRefRaw)
        return outDict


class Transformation(descriptors.ChannelData):

    def __init__(self,parent,baseData,paramsData,nickname,mask=None,filterTimes=None,offset=None,*args,**kargs):
        print 'creating transformation channel of %s using %s and mask %s' %(baseData.nickname,paramsData.nickname,mask)

        self.baseData = baseData
        self.paramsData = paramsData
        self.mask = mask
        self.filterTimes = filterTimes
        self.offset = offset

        if not (filterTimes is None):
            params = n.array([self.paramsData[itime] for itime in range(parent.dimt)])
            s=n.sum(n.abs(params[0,9:]-params[:,9:]),1)#*n.std(params[:,:][:,9:],0),1)
            midLine = ndimage.filters.percentile_filter(s,50,20,mode='constant')
            diffs = s-midLine
            goodIndices = n.where(n.array(n.abs(diffs)<3*n.std(diffs[n.where(n.abs(diffs)<n.std(diffs))])))[0]
            self.validTimes = goodIndices
        else:
            self.validTimes = parent.times

        self.dir = self.baseData.dir
        self.fileNameFormat = self.baseData.fileNameFormat

        super(Transformation,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = descriptors.H5Array


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
                    outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=self.nickname)
            else:
                toDoTimes.append(time)
            #tmpGroup.file.close()
            tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        refIm = sitk.gifa(self.baseData[0])
        if not (self.mask is None):
            mask = sitk.Cast(self.mask,refIm.GetPixelID())

        for itime,time in enumerate(toDoTimes):
            print "transforming basedata %s with params %s, time %06d" %(self.baseData.nickname,self.paramsData.nickname,time)

            tmpIm = sitk.gifa(self.baseData[time])
            tmpParams = n.array(self.paramsData[time])
            # pdb.set_trace()
            changedParams = n.zeros(12)
            changedParams[:] = tmpParams
            if not (self.offset is None):
                changedParams[9:] += self.offset
            tmpRes = transformStackAndRef(changedParams,tmpIm,refIm)

            if not (self.mask is None):
                tmpRes = tmpRes*mask

            tmpRes = tmpRes[0:self.paramsData.relShape[0],0:self.paramsData.relShape[1],0:self.paramsData.relShape[2]]
            tmpRes.SetSpacing((1,1,1.))
            tmpRes.SetOrigin((0,0,0.))
            tmpRes = sitk.gafi(tmpRes)

            tmpFile = h5py.File(self.baseData[time].file.filename)
            tmpFile[self.nickname] = tmpRes
            tmpFile.close()

            outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
                                    hierarchy=self.nickname)

        return outDict

def transformStackAndRef(p,stack,refStack):
    # can handle composite transformations (len(p)%12)
    newim = transformStack(p,stack)
    if not (refStack is None):
        newim = sitk.Resample(newim,refStack)
    return newim

def transformStack(p,stack,outShape=None,outSpacing=None,outOrigin=None):
    # can handle composite transformations (len(p)%12)
    # 20140326: added outOrigin option
    numpyarray = False
    if type(stack)==n.ndarray:
        numpyarray = True
        stack = sitk.GetImageFromArray(stack)
    transf = sitk.Transform(3,8)
    if not (p is None):
        for i in range(len(p)/12):
            transf.AddTransform(sitk.Transform(3,6))
        #p = n.array(p)
        #p = n.concatenate([p[:9].reshape((3,3))[::-1,::-1].flatten(),p[9:][::-1]])
        transf.SetParameters(n.array(p,dtype=n.float64))
    if outShape is None: shape = stack.GetSize()
    else:
        shape = n.ceil(n.array(outShape))
        shape = [int(i) for i in shape]
    if outSpacing is None: outSpacing = stack.GetSpacing()
    else: outSpacing = n.array(outSpacing)
    if outOrigin is None: outOrigin = stack.GetOrigin()
    else: outOrigin = n.array(outOrigin)
    print stack.GetSize(),shape
    #pdb.set_trace()
    newim = sitk.Resample(stack,shape,transf,sitk.sitkLinear,outOrigin,outSpacing)
    if numpyarray:
        newim = sitk.GetArrayFromImage(newim)
    return newim

def composeAffineTransformations(paramsList):
    """
    compose parameters from subsequent affine transformations given in list paramsList
    """
    currentParams = n.array([1,0,0,0,1,0,0,0,1,0,0,0])
    for params in paramsList:
        params = n.array(params)
        tmpMatrix = n.dot(currentParams[:9].reshape((3,3)),params[:9].reshape((3,3)))
        tmpTrans = n.dot(currentParams[:9].reshape((3,3)),params[9:])+currentParams[9:]
        currentParams = n.concatenate([tmpMatrix.flatten(),tmpTrans],0)
    return currentParams

def createParameterFile(spacing,initialTransformFile,template,outPath):
    spacingString = '\n\n(Spacing %s %s %s)\n\n' %tuple(spacing)
    initString = '\n\n(InitialTransformParametersFileName \"%s\")\n\n' %initialTransformFile
    template = initString +spacingString+ template
    outFile = open(outPath,'w')
    outFile.write(template)
    outFile.close()
    return

def createInitialTransformFile(spacing,params,template,outPath):
    spacingString = '\n\n(Spacing %s %s %s)\n' %tuple(spacing)
    paramsString = '\n\n(TransformParameters %s %s %s %s %s %s %s %s %s %s %s %s)\n\n' %tuple(params)
    template = paramsString + spacingString + template
    outFile = open(outPath,'w')
    outFile.write(template)
    outFile.close()
    return

def getParamsFromElastix(images,initialParams=None,
                         elastixPath='/home/malbert/software/fusion/dependencies_linux/elastix_linux64_v4.7/bin/elastix',
                         tmpDir='/data/malbert/tmp',mode='similarity',
                         masks=None):

    """
    mode: can be one of 'affine','rigid' or 'similarity'
    """
    os.environ['LD_LIBRARY_PATH'] = os.path.join(os.path.dirname(os.path.dirname(elastixPath)),'lib')

    wroteFixed = False
    wroteMoving = False

    if initialParams is None:
        params = [[1.,0,0,0,1,0,0,0,1,0,0,0]]*len(images)
    else:
        params = initialParams

    if type(images[0]) == sitk.Image:

        fiPath = os.path.join(tmpDir,'tmpFixedImage.mhd')
        sitk.WriteImage(images[0],fiPath)
        wroteFixed = True

    elif type(images[0]) == str:
        fiPath = images[0]

    else:
        raise(Exception('check input'))


    finalParams = [[1.,0,0,0,1,0,0,0,1,0,0,0]]
    for iim in range(1,len(images)):

        if type(images[iim]) == sitk.Image:

            sitk.WriteImage(images[iim],os.path.join(tmpDir,'tmpMovingImage.mhd'))
            miPath = os.path.join(tmpDir,'tmpMovingImage.mhd')
            wroteMoving = True

        elif type(images[iim]) == str:
            miPath = images[iim]

        else:
            raise(Exception('check input'))


        paramDict = dict()

        paramDict['el'] = elastixPath
        parameterPath = os.path.join(tmpDir,'elastixParameters.txt')
        initialTransformPath = os.path.join(tmpDir,'elastixInitialTransform.txt')
        paramDict['out'] = tmpDir
        createInitialTransformFile(n.array([1,1,1.]),params[iim],elastixInitialTransformTemplateString,initialTransformPath)
        if mode == 'affine':
            parameterTemplateString = elastixParameterTemplateString
        elif mode == 'rigid':
            parameterTemplateString = elastixParameterTemplateStringRotation
        elif mode == 'similarity':
            parameterTemplateString = elastixParameterTemplateStringSimilarity
        else:
            raise(Exception('check registration mode'))

        createParameterFile(n.array([1,1,1.]),initialTransformPath,parameterTemplateString,parameterPath)
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
        lastParams = composeAffineTransformations([affineOutParams,params[iim]])

        finalParams.append(lastParams)

        # if masks is not None: os.remove(miMaskPath)
    if wroteFixed:
        os.remove(fiPath)
        os.remove(fiPath[:-3]+'raw')
    if wroteMoving:
        os.remove(miPath)
        os.remove(miPath[:-3]+'raw')

    finalParams = n.array(finalParams)
    return finalParams


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

elastixParameterTemplateString = """
// Description: affine

(RequiredRatioOfValidSamples 0.05)

(Transform "AffineTransform")
//(GradientMagnitudeTolerance 1e-7)
(NumberOfResolutions 2)

//(ImagePyramidSchedule  8 8 2  4 4 1  2 2 1 )
(ImagePyramidSchedule  4 4 4  2 2 2)

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


(Optimizer "AdaptiveStochasticGradientDescent")
//(Optimizer "QuasiNewtonLBFGS")
//(Optimizer ConjugateGradient)

//(StopIfWolfeNotSatisfied "false")

(ResampleInterpolator "FinalBSplineInterpolator")
(Resampler "DefaultResampler")
//(Resampler "CUDAResampler")
//(CenterOfRotationPoint 0.0 0.0 0.0)

(ErodeMask "false" )

(HowToCombineTransforms "Compose")
(AutomaticTransformInitialization "true")
//(Scales 10000 10000000 10000000 10000000 10000 10000000 10000000 10000000 10000 1 1000 1)
//(Scales 1000 1000 1000 1 1 1)
(AutomaticScalesEstimation "true")
//(AutomaticTransformInitializationMethod "CenterOfGravity" )

(WriteTransformParametersEachIteration "false")
(WriteResultImage "false")
(CompressResultImage "false")
//(WriteResultImageAfterEachResolution "true")
(ShowExactMetricValue "false")

//Maximum number of iterations in each resolution level:
//(MaximumNumberOfIterations 500)

//Number of grey level bins in each resolution level:
(NumberOfHistogramBins 32)
//(FixedLimitRangeRatio 0.0)
//(MovingLimitRangeRatio 0.0)
//(FixedKernelBSplineOrder 3)
//(MovingKernelBSplineOrder 3)

//Number of spatial samples used to compute the mutual information in each resolution level:
(ImageSampler "RandomCoordinate")
//(ImageSampler "RandomSparseMask")
//(ImageSampler "Full")
//(SampleGridSpacing 2)
(NumberOfSpatialSamples 2048)
(NewSamplesEveryIteration "true")
(CheckNumberOfSamples "true")
(MaximumNumberOfIterations 500 200)
//(MaximumNumberOfSamplingAttempts 10)

//Order of B-Spline interpolation used in each resolution level:
(BSplineInterpolationOrder 1)

(FixedImageBSplineInterpolationOrder 1)
(MovingImageBSplineInterpolationOrder 1)

//Order of B-Spline interpolation used for applying the final deformation:
(FinalBSplineInterpolationOrder 1)

//Default pixel value for pixels that come from outside the picture:
(DefaultPixelValue 200)

//(MaximumStepLength 4.0)
(ResultImagePixelType "short")
(ResultImageFormat "mhd")
"""

elastixParameterTemplateStringRotation = """
// Description: affine

(RequiredRatioOfValidSamples 0.05)

(Transform "EulerTransform")
//(GradientMagnitudeTolerance 1e-6)
(NumberOfResolutions 3)

//(ImagePyramidSchedule  8 8 2  4 4 1  2 2 1 )
//(ImagePyramidSchedule 8 8 4 4 4 2 2 2 1)
(FixedImagePyramidSchedule 8 8 4 4 4 2 2 2 1)
(MovingImagePyramidSchedule 8 8 4 4 4 2 2 2 1)

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


(Optimizer "AdaptiveStochasticGradientDescent")
//(Optimizer "QuasiNewtonLBFGS")
//(Optimizer ConjugateGradient)

//(StopIfWolfeNotSatisfied "false")

(ResampleInterpolator "FinalBSplineInterpolator")
(Resampler "DefaultResampler")
//(Resampler "CUDAResampler")
//(CenterOfRotationPoint 0.0 0.0 0.0)

(ErodeMask "false" )

(HowToCombineTransforms "Compose")
(AutomaticTransformInitialization "true")
//(Scales 10000 10000000 10000000 10000000 10000 10000000 10000000 10000000 10000 1 1000 1)
//(Scales 1000 1000 1000 1 1 1)
(AutomaticScalesEstimation "true")
//(AutomaticTransformInitializationMethod "CenterOfGravity" )

(WriteTransformParametersEachIteration "false")
(WriteResultImage "false")
(CompressResultImage "false")
//(WriteResultImageAfterEachResolution "true")
(ShowExactMetricValue "false")

//Maximum number of iterations in each resolution level:
(MaximumNumberOfIterations 500 250 100)

//Number of grey level bins in each resolution level:
(NumberOfHistogramBins 32)
//(FixedLimitRangeRatio 0.0)
//(MovingLimitRangeRatio 0.0)
//(FixedKernelBSplineOrder 3)
//(MovingKernelBSplineOrder 3)

//Number of spatial samples used to compute the mutual information in each resolution level:
(ImageSampler "RandomCoordinate")
//(ImageSampler "RandomSparseMask")
//(ImageSampler "Full")
//(SampleGridSpacing 2)
(NumberOfSpatialSamples 2048)
(NewSamplesEveryIteration "true")
(CheckNumberOfSamples "true")
//(MaximumNumberOfIterations 500 100)
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

elastixParameterTemplateStringSimilarity = """

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
(Metric "AdvancedMattesMutualInformation")
//(Metric "NormalizedMutualInformation")
(Optimizer "AdaptiveStochasticGradientDescent")
//(Optimizer "QuasiNewtonLBFGS")
(ResampleInterpolator "FinalBSplineInterpolator")
(Resampler "DefaultResampler")
(Transform "SimilarityTransform")
//(GradientMagnitudeTolerance 1e-6)


// ********** Pyramid

// Total number of resolutions
//(NumberOfResolutions 4)
(NumberOfResolutions 4)
//(ImagePyramidSchedule 16 16 4 8 8 2 4 4 1 2 2 1)
(ImagePyramidSchedule 16 16 8 8 8 4 4 4 2 1 1 1)
//(FixedImagePyramidSchedule 4 4 2 2 2 1 1 1 1)
//(MovingImagePyramidSchedule 8 8 4 4 4 2 2 2 1)


// ********** Transform

(AutomaticScalesEstimation "true")
(AutomaticTransformInitialization "true")
//(AutomaticTransformInitializationMethod "CenterOfGravity")
(HowToCombineTransforms "Compose")


// ********** Optimizer

// Maximum number of iterations in each resolution level:
(MaximumNumberOfIterations 2000 1000 500 250)

(AutomaticParameterEstimation "true")
(UseAdaptiveStepSizes "true")
(NumberOfHistogramBins 64)
(NumberOfFixedHistogramBins 64)
(NumberOfMovingHistogramBins 64)

//(NumberOfGradientMeasurements 0)
//(NumberOfJacobianMeasurements 4056)
//(NumberOfBandStructureSamples 10)
//(MaximumStepLength 2.29829)
//(SigmoidInitialTime 0 0 0)

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
(NumberOfSpatialSamples 4096)
//(NumberOfSamplesForSelfHessian 10000)
//(NumberOfSamplesForExactGradient 10000)
(NewSamplesEveryIteration "true")
(UseRandomSampleRegion "false")
(MaximumNumberOfSamplingAttempts 0)
//(ImageSampler "Full")
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

(WriteResultImage "false")
(CompressResultImage "false")

// The pixel type and format of the resulting deformed moving image
(ResultImagePixelType "float")
(ResultImageFormat "mhd")
"""