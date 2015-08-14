__author__ = 'malbert'

from dependencies import *

# config['registrationPath'] = 'registrationParameters'
# config['registeredPath'] = 'registered'

class RegistrationParameters(descriptors.ChannelData):

    nickname = 'registrationParams'

    def __init__(self,parent,baseData,nickname,
                 reference=None,
                 initialRegistration=None,
                 singleRegistrationTime=None,
                 *args,**kargs):

        print 'creating registration channel'

        self.baseData = baseData

        self.dir = self.baseData.dir
        self.fileNameFormat = self.baseData.fileNameFormat

        self.validTimes = range(parent.dimt)

        self.reference = reference
        self.initialRegistration = initialRegistration
        self.singleRegistrationTime = singleRegistrationTime

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
            else:
                toDoTimes.append(time)
            tmpFile.close()

            # self.baseData.close(time)

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        tmpImage = sitk.gifa(self.baseData[0])
        if not (self.parent.registrationSliceStringSitk is None):
            exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

        outFileRef = os.path.join(tmpDir,'refImage.mhd')
        outFileRefRaw = os.path.join(tmpDir,'refImage.raw')
        sitk.WriteImage(tmpImage,outFileRef)

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

            if self.singleRegistrationTime is None or time == self.singleRegistrationTime:

                print "registering basedata %s time %06d" %(self.baseData.nickname,time)

                # process reference image
                if self.reference is None:
                    tmpImage = sitk.gifa(self.baseData[time])
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

                inputList = [outFileRef,tmpImage]

                tmpParams = imaging.getParamsFromElastix(inputList,
                                  initialParams=initialParams,
                                  tmpDir=tmpDir,
                                  mode='similarity',
                                  masks=None)

                tmpParams = n.array(tmpParams[1]).astype(n.float64)

            else:
                if self.singleRegistrationTime != 0: raise(Exception('the two references need to be the same!'))
                relParams = self.timesDict[str(time)]
                if initialParams is None:
                    tmpParams = relParams
                else:
                    tmpParams = composeAffineTransformations([initialParams,relParams])


            tmpFile = h5py.File(self.baseData[time].file.filename)
            tmpFile[self.nickname] = tmpParams
            tmpFile.close()

            outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
                                    hierarchy=config[self.nickname])

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
            changedParams = n.zeros(12)
            changedParams[:] = tmpParams
            if not (self.offset is None):
                changedParams[9:] += self.offset
            tmpRes = transformStackAndRef(changedParams,tmpIm,refIm)

            if not (self.mask is None):
                tmpRes = tmpRes*mask

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