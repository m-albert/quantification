__author__ = 'malbert'

from dependencies import *

config['slidingWindowMeanPath'] = 'slidingWindowMean%s'
config['signalPath'] = 'signal_windowsize%s'


class SlidingWindowMean(descriptors.ChannelData):

    def __init__(self,parent,baseData,nickname,filterSize=2,*args,**kargs):
        print 'creating sliding window mean of %s with filterSize %s' %(baseData.nickname,filterSize)

        self.baseData = baseData
        self.filterSize = filterSize
        self.hierarchy = nickname
        self.validTimes = parent.times

        super(SlidingWindowMean,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = h5py.Dataset

        return

    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            tmpFile = self.parent[time]
            if self.nickname in tmpFile.keys():
                if redo:
                    del tmpFile[self.nickname]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    outDict[time] = True
            else:
                toDoTimes.append(time)

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

            # tmpFile = h5py.File(self.baseData.getFileName(time))
            # tmpFile[self.hierarchy] = tmpRes
            # tmpFile.close()

            # pdb.set_trace()
            filing.toH5_hl(tmpRes.astype(n.float),self.parent[time],hierarchy=self.hierarchy)
                        # compression='jls',compressionOption=0)

            # outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
            #                         hierarchy=self.hierarchy)
            outDict[time] = True

        return outDict



class Signal(descriptors.ChannelData):

    def __init__(self,parent,baseData,nickname,filterSize=5,factor=1000,*args,**kargs):
        print 'creating sliding window mean of %s with filterSize %s' %(baseData.nickname,filterSize)

        self.baseData = baseData
        self.filterSize = filterSize
        self.hierarchy = nickname
        self.validTimes = parent.times
        self.factor = factor

        super(Signal,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = h5py.Dataset

        return

    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            tmpFile = self.parent[time]
            if self.nickname in tmpFile.keys():
                if redo:
                    del tmpFile[self.nickname]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    outDict[time] = True
            else:
                toDoTimes.append(time)

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
            tmpDiff = self.baseData[time]-tmpRes.astype(n.float)
            tmpSignal = tmpDiff*(tmpDiff>0).astype(n.uint8)/tmpRes
            tmpSignal[tmpRes==0] = 0

            # tmpFile = h5py.File(self.baseData.getFileName(time))
            # tmpFile[self.hierarchy] = tmpSignal

            # pdb.set_trace()
            filing.toH5_hl((tmpSignal*self.factor).astype(n.uint16),self.parent[time],hierarchy=self.hierarchy,
                           compression='jls',compressionOption=2)

            outDict[time] = True

        return outDict

class DistanceMasks(object):

    def __init__(self,signal,mask,nDilations=20):
        print 'instanciating Hulls'
        self.nDilations = nDilations
        self.segmentation = segmentation
        self.signal = signal
        self.mask = mask
        # self.timepointClass = descriptors.H5Pointer
        self.timepointClass = h5py.Group
        return

    # def fromFile(self,rootFileName,hierarchy):
    #     return descriptors.H5Pointer(rootFileName,hierarchy)

    def fromFrame(self,time,frame,tmpFile,tmpHierarchy):
        tmpGroup = tmpFile.create_group(tmpHierarchy)
        seg = n.array(frame)
        print 'distance masks...'
        tmpFile[tmpHierarchy].create_group('masks')
        masks = getDistanceMasks(n.array(seg),self.mask.ga()[self.mask.slices],nDilations=self.nDilations)
        for idil in range(self.nDilations):
            filing.toH5_hl(masks[idil],tmpFile,hierarchy=os.path.join(tmpHierarchy,'masks/%s' %idil),compression='jls')
        s = n.array([n.sum(masks[idil]*n.array(self.signal[time]).astype(n.float))/n.sum(masks[idil]) for idil in range(self.nDilations)])
        filing.toH5_hl(s,tmpFile,hierarchy=os.path.join(tmpHierarchy,'signal'))

        return


def mymean(x,y):
    tmp = x.mean()
    for ii in range(len(y)): y[ii]=tmp


def getDistanceMasks(microglia,mask,nDilations=10):
    microglia = sitk.gifa((n.array(microglia)!=0).astype(n.uint16))
    # nDilations = 2
    dilations = []
    tmp = microglia
    for idil in range(nDilations):
        print 'dilation %s from %s' %(idil+1,nDilations)
        tmp = sitk.BinaryDilate(tmp)
        tmp = sitk.BinaryFillhole(tmp)
        dilations.append(tmp)
    for idil in range(len(dilations))[::-1]:
        # pdb.set_trace()
        if idil:
            dilations[idil] = sitk.gafi(dilations[idil]-dilations[idil-1])*mask
        else:
            dilations[idil] = sitk.gafi(dilations[idil]-microglia)*mask
        # dilations[idil] = sitk.gafi(dilations[idil])*mask

    return dilations

