__author__ = 'malbert'

from dependencies import *

config['registrationPath'] = 'registrationParameters'
config['registeredPath'] = 'registered'

class RegistrationParameters(descriptors.ChannelData):

    nickname = 'registrationParams'

    def __init__(self,parent,baseData,nickname,*args,**kargs):
        print 'creating registration channel'

        self.baseData = baseData

        self.dir = self.baseData.dir
        self.fileNameFormat = self.baseData.fileNameFormat

        self.validTimes = range(parent.dimt)

        super(RegistrationParameters,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = descriptors.H5Array


    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            tmpFile = h5py.File(self.baseData.getFileName(time))
            # if config['registrationPath'] in self.baseData[time].file.keys():
            if config['registrationPath'] in tmpFile.keys():
                if redo:
                    del tmpFile[config['registrationPath']]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=config['registrationPath'])
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
            print "registering basedata %s time %06d" %(self.baseData.nickname,time)

            tmpImage = sitk.gifa(self.baseData[time])
            if not (self.parent.registrationSliceStringSitk is None):
                exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

            inputList = [outFileRef,tmpImage]

            tmpParams = imaging.getParamsFromElastix(inputList,
                              initialParams=None,
                              tmpDir=tmpDir,
                              mode='similarity',
                              masks=None)

            tmpParams = n.array(tmpParams[1]).astype(n.float64)

            tmpFile = h5py.File(self.baseData[time].file.filename)
            tmpFile[config['registrationPath']] = tmpParams
            tmpFile.close()

            outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
                                    hierarchy=config['registrationPath'])

            self.baseData.close(time)

        os.remove(outFileRef)
        os.remove(outFileRefRaw)
        return outDict


class Transformation(descriptors.ChannelData):

    def __init__(self,parent,baseData,paramsData,nickname,mask=None,filterTimes=True,offset=None,*args,**kargs):
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

        self.dir = self.baseData.dir
        self.fileNameFormat = self.baseData.fileNameFormat

        super(Transformation,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = descriptors.H5Array


    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            tmpFile = h5py.File(self.baseData.getFileName(time))
            if config['registeredPath'] in tmpFile.keys():
                if redo:
                    del tmpFile[config['registeredPath']]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=config['registeredPath'])
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
            tmpRes = beads.transformStackAndRef(changedParams,tmpIm,refIm)

            if not (self.mask is None):
                tmpRes = tmpRes*mask

            tmpRes = sitk.gafi(tmpRes)

            tmpFile = h5py.File(self.baseData[time].file.filename)
            tmpFile[config['registeredPath']] = tmpRes
            tmpFile.close()

            outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
                                    hierarchy=config['registeredPath'])

        return outDict


