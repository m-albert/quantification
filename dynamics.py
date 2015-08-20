__author__ = 'malbert'

from dependencies import *


class FilterSegmentation(descriptors.ChannelData):

    def __init__(self,parent,baseData,nickname,*args,**kargs):
        print 'creating filter segmentation of %s' %(baseData.nickname)

        self.baseData = baseData

        self.dir = self.baseData.dir
        self.fileNameFormat = self.baseData.fileNameFormat

        super(FilterSegmentation,self).__init__(parent,nickname,*args,**kargs)

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

        for itime,time in enumerate(toDoTimes):

            so = sitk.gifa(self.baseData[time])
            tmpRes = imaging.gaussian3d(so,(2,2,4.))
            tmpRes = sitk.Laplacian(tmpRes)
            tmpRes = sitk.Cast(tmpRes<-5,3)*sitk.Cast(sitk.Abs(tmpRes),3)
            tmpRes = sitk.gafi(tmpRes)

            tmpFile = h5py.File(self.baseData[time].file.filename)
            tmpFile[self.nickname] = tmpRes
            tmpFile.close()

            outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
                                    hierarchy=self.nickname)

        return outDict