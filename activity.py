__author__ = 'malbert'

__author__ = 'malbert'

from dependencies import *

config['slidingWindowMeanPath'] = 'slidingWindowMean%s'
config['signalPath'] = 'signal_windowsize%s'


class SlidingWindowMean(descriptors.ChannelData):

    def __init__(self,parent,baseData,nickname,filterSize=2,*args,**kargs):
        print 'creating sliding window mean of %s with filterSize %s' %(baseData.nickname,filterSize)


        self.baseData = baseData
        self.filterSize = filterSize

        self.hierarchy = config['slidingWindowMeanPath'] %filterSize

        self.dir = self.baseData.dir
        self.fileNameFormat = self.baseData.fileNameFormat

        super(SlidingWindowMean,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = descriptors.H5Array


    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            tmpFile = h5py.File(self.baseData.getFileName(time))
            if self.hierarchy in tmpFile.keys():
                if redo:
                    del tmpFile[self.hierarchy]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=self.hierarchy)
            else:
                toDoTimes.append(time)
            #tmpGroup.file.close()
            tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        firstEndProcessed = False
        for itime,time in enumerate(toDoTimes):
            factor = 1./(2*self.filterSize+1)
            if n.sum(self.validTimes<time) <= self.filterSize:
                if not itime:
                    tmpTimes = [self.validTimes[i] for i in range(2*self.filterSize+1)]
                    tmpImages = [self.baseData[i] for i in tmpTimes]
                    tmpRes = n.zeros_like(tmpImages[0])
                    for iim in range(2*self.filterSize+1):
                        tmpRes += factor*n.array(tmpImages[iim])

            elif n.sum(self.validTimes>time) < self.filterSize:
                if not firstEndProcessed:
                    tmpTimes = self.validTimes[-2*self.filterSize-1:]
                    #tmpTimes = [self.validTimes[i] for i in range(dataLen-2*self.filterSize+1,dataLen)]
                    tmpImages = [self.baseData[i] for i in tmpTimes]
                    tmpRes = n.zeros_like(tmpImages[0])
                    for iim in range(2*self.filterSize+1):
                        tmpRes += factor*n.array(tmpImages[iim])
                firstEndProcessed = True

            else:
                currIndex = n.where(n.array(self.validTimes)==time)[0][0]
                if not itime:
                    tmpTimes = n.array(self.validTimes)[currIndex- self.filterSize:currIndex + 1+ self.filterSize]
                    tmpImages = [self.baseData[i] for i in tmpTimes]
                    tmpRes = n.zeros_like(tmpImages[0])
                    for iim in range(2*self.filterSize+1):
                        tmpRes += factor*n.array(tmpImages[iim])
                else:
                    new = self.validTimes[currIndex+self.filterSize]
                    old = self.validTimes[currIndex-self.filterSize-1]
                    tmpRes += factor*n.array(self.baseData[new])
                    tmpRes -= factor*n.array(self.baseData[old])

            tmpFile = h5py.File(self.baseData.getFileName(time))
            tmpFile[self.hierarchy] = tmpRes
            tmpFile.close()

            outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
                                    hierarchy=self.hierarchy)

        return outDict

class Signal(descriptors.ChannelData):

    def __init__(self,parent,baseData,nickname,filterSize=5,*args,**kargs):
        print 'creating sliding window mean of %s with filterSize %s' %(baseData.nickname,filterSize)


        self.baseData = baseData
        self.filterSize = filterSize

        self.hierarchy = config['signalPath'] %filterSize

        self.dir = self.baseData.dir
        self.fileNameFormat = self.baseData.fileNameFormat

        super(Signal,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = descriptors.H5Array


    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            tmpFile = h5py.File(self.baseData.getFileName(time))
            if self.hierarchy in tmpFile.keys():
                if redo:
                    del tmpFile[self.hierarchy]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=self.hierarchy)
            else:
                toDoTimes.append(time)
            #tmpGroup.file.close()
            tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        firstEndProcessed = False
        for itime,time in enumerate(toDoTimes):
            print "calculating signal of basedata %s with filterSize %s, time %06d" %(self.baseData.nickname,self.filterSize,time)

            factor = 1./(2*self.filterSize+1)
            if n.sum(self.validTimes<time) <= self.filterSize:
                if not itime:
                    tmpTimes = [self.validTimes[i] for i in range(2*self.filterSize+1)]
                    tmpImages = [n.array(self.baseData[i]) for i in tmpTimes]
                    tmpRes = n.zeros_like(tmpImages[0])
                    for iim in range(2*self.filterSize+1):
                        tmpRes += factor*tmpImages[iim]

            elif n.sum(self.validTimes>time) < self.filterSize:
                if not firstEndProcessed:
                    tmpTimes = self.validTimes[-2*self.filterSize-1:]
                    #tmpTimes = [self.validTimes[i] for i in range(dataLen-2*self.filterSize+1,dataLen)]
                    tmpImages = [n.array(self.baseData[i]) for i in tmpTimes]
                    tmpRes = n.zeros_like(tmpImages[0])
                    for iim in range(2*self.filterSize+1):
                        tmpRes += factor*tmpImages[iim]
                firstEndProcessed = True

            else:
                currIndex = n.where(n.array(self.validTimes)==time)[0][0]
                # if 1:
                # pdb.set_trace()
                if not itime or not times[itime-1]==self.validTimes[currIndex-1]:
                    tmpTimes = n.array(self.validTimes)[currIndex- self.filterSize:currIndex+1+self.filterSize]
                    tmpImages = [n.array(self.baseData[i]) for i in tmpTimes]
                else:
                    new = self.validTimes[currIndex+self.filterSize]
                    # old = self.validTimes[currIndex-self.filterSize-1]
                    tmpImages = tmpImages[1:]+[n.array(self.baseData[new])]

                tmpRes = n.zeros_like(tmpImages[0])
                for iim in range(2*self.filterSize+1):
                    tmpRes += factor*tmpImages[iim]
                # else:
                #     # pdb.set_trace()
                #     new = self.validTimes[currIndex+self.filterSize]
                #     old = self.validTimes[currIndex-self.filterSize-1]
                #     tmpRes += factor*n.array(self.baseData[new])
                #     tmpRes -= factor*n.array(self.baseData[old])
                #
                #     print 'debug: ',time,old,new

            # tmpRes[tmpRes==0] = 1
            tmpSignal = n.abs(self.baseData[time]-tmpRes.astype(n.float))/tmpRes
            tmpSignal[tmpRes==0] = 0

            tmpFile = h5py.File(self.baseData.getFileName(time))
            tmpFile[self.hierarchy] = tmpSignal
            tmpFile.close()
            # pdb.set_trace()
            outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
                                    hierarchy=self.hierarchy)

        return outDict



def mymean(x,y):
    tmp = x.mean()
    for ii in range(len(y)): y[ii]=tmp