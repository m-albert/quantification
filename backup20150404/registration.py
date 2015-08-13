__author__ = 'malbert'

from dependencies import *

config['registrationParamsPath'] = 'registrationParameters'

class RegistrationParamsChannel(descriptors.ChannelData):

    nickname = 'registrationParams'

    def __init__(self,parent,channel):
        print 'creating registration channel'

        self.dir = parent.rawData[channel].dir
        self.fileNameFormat = parent.rawData[channel].fileNameFormat

        self.timepointClass = descriptors.H5Array

        super(RegistrationParamsChannel,self).__init__(parent,channel)

    def prepareTimepoints(self,times):
        print 'preparing timepoints %s' %times

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            if config['registrationParamsPath'] in self.parent.rawData[self.channel][time].file.keys():
                alreadyDoneTimes.append(time)
                outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=config['registrationParamsPath'])
            else:
                toDoTimes.append(time)

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if len(toDoTimes):

            tmpImage = sitk.gifa(self.parent.rawData[self.channel][0])
            if not (self.parent.registrationSliceStringSitk is None):
                exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

            outFileRef = os.path.join(tmpDir,'refImage.mhd')
            outFileRefRaw = os.path.join(tmpDir,'refImage.raw')
            sitk.WriteImage(tmpImage,outFileRef)

            for itime,time in enumerate(toDoTimes):
                print "registering channel %01d time %06d" %(self.channel,time)

                tmpImage = sitk.gifa(self.parent.rawData[self.channel][time])
                if not (self.parent.registrationSliceStringSitk is None):
                    exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

                inputList = [outFileRef,tmpImage]

                tmpParams = imaging.getParamsFromElastix(inputList,
                                  initialParams=None,
                                  tmpDir=tmpDir,
                                  mode='similarity',
                                  masks=None)

                tmpParams = n.array(tmpParams[1]).astype(n.float64)

                tmpFile = h5py.File(self.parent.rawData[self.channel][time].file.filename)
                tmpFile[config['registrationParamsPath']] = tmpParams
                tmpFile.close()

                outDict[time] = descriptors.H5Array(self.parent.rawData[self.channel][time].file.filename,
                                        hierarchy=config['registrationParamsPath'])

            os.remove(outFileRef)
            os.remove(outFileRefRaw)

        return outDict


class RegisteredChannel(descriptors.ChannelData):

    nickname = 'registrationParams'

    def __init__(self,parent,channel):
        print 'creating registration channel'

        self.dir = parent.rawData[channel].dir
        self.fileNameFormat = parent.rawData[channel].fileNameFormat

        self.timepointClass = descriptors.H5Array

        super(RegistrationParamsChannel,self).__init__(parent,channel)

    def prepareTimepoints(self,times):
        print 'preparing timepoints %s' %times

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            if config['registrationParamsPath'] in self.parent.rawData[self.channel][time].file.keys():
                alreadyDoneTimes.append(time)
                outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=config['registrationParamsPath'])
            else:
                toDoTimes.append(time)

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        tmpImage = sitk.gifa(self.parent.rawData[self.channel][0])
        if not (self.parent.registrationSliceStringSitk is None):
            exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

        outFileRef = os.path.join(tmpDir,'refImage.mhd')
        outFileRefRaw = os.path.join(tmpDir,'refImage.raw')
        sitk.WriteImage(tmpImage,outFileRef)

        for itime,time in enumerate(toDoTimes):
            print "registering channel %01d time %06d" %(self.channel,time)

            tmpImage = sitk.gifa(self.parent.rawData[self.channel][time])
            if not (self.parent.registrationSliceStringSitk is None):
                exec('tmpImage = tmpImage[%s]' %self.parent.registrationSliceStringSitk)

            inputList = [outFileRef,tmpImage]

            tmpParams = imaging.getParamsFromElastix(inputList,
                              initialParams=None,
                              tmpDir=tmpDir,
                              mode='similarity',
                              masks=None)

            tmpParams = n.array(tmpParams[1]).astype(n.float64)

            tmpFile = h5py.File(self.parent.rawData[self.channel][time].file.filename)
            tmpFile[config['registrationParamsPath']] = tmpParams
            tmpFile.close()

            outDict[time] = descriptors.H5Array(self.parent.rawData[self.channel][time].file.filename,
                                    hierarchy=config['registrationParamsPath'])

        os.remove(outFileRef)
        os.remove(outFileRefRaw)
        return outDict