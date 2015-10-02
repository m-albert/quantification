__author__ = 'malbert'

from dependencies import *

config['relPredictionDataDir'] = "pred_ch%d"
config['predictionFileNameFormat'] = "f%06d_Probabilities.h5"
config['ilastikCommand'] = ilastiking.runIlastikNew
# config['predictionPath'] = 'prediction'


class Prediction(descriptors.ChannelData):

    # class for handling prediction data
    # initial task: run ilastik
    # relies on parent having classifiers dict

    nickname = 'prediction'

    def __init__(self,parent,baseData,nickname,*args,**kargs):
        print 'creating prediction channel'

        # if not (channel in parent.predictionChannels):
        #     #raise(Exception('Channel %s not marked for prediction' %channel))
        #     print 'Ommitting channel %s since it is not marked for prediction' %channel
        #     return

        self.fileNameFormat = config['predictionFileNameFormat']
        self.baseData = baseData
        self.timepointClass = h5py.Dataset
        self.hierarchy = nickname

        # self.dir = self.baseData.dir

        self.trainingSamplesDir = os.path.join(self.dataDir,'training')
        if not os.path.exists(self.trainingSamplesDir): os.mkdir(self.trainingSamplesDir)


        classifierPath = os.path.join(self.trainingSamplesDir,'classifier.ilp')
        # pdb.set_trace()
        if parent.classifiers.has_key(self.baseData.nickname):
            # self.classifier = parent.classifiers[self.baseData.nickname]
            self.classifier = classifierPath
            super(Prediction,self).__init__(parent,nickname,*args,**kargs)

        else:

            if not os.path.exists(classifierPath):
                print 'preparing ilastik training samples based on times %s' %parent.times

                shutil.copyfile('/home/malbert/quantification/classifier_template.ilp',classifierPath)

                # produce training samples
                timepoints = len(parent.times)
                timepoints = [itp*(timepoints/4) for itp in range(4)]
                for itime,time in enumerate(timepoints):
                    samplePath = os.path.join(self.trainingSamplesDir,'sample%02d.h5' %itime)
                    if os.path.exists(samplePath): os.remove(samplePath)
                    os.link(self.baseData[time].file.filename,samplePath)

            raise(Exception('train ilastik for basedata %s using copied project at %s!' %(self.baseData.nickname,classifierPath)))



    def prepareTimepoints(self,times,redo):

        # pdb.set_trace()

        outDict = dict()

        alreadyDoneTimes, toDoTimes, toDoStacks = [],[],[]
        for itime,time in enumerate(times):
            if os.path.exists(self.getFileName(time)):
                alreadyDoneTimes.append(time)
                # outDict[time] = descriptors.H5Array(self.getFileName(time))
            else:
                toDoTimes.append(time)
                toDoStacks.append(self.baseData[time])

        if not len(toDoTimes): return outDict

        # pdb.set_trace()
        outFiles = config['ilastikCommand'](toDoStacks,self.classifier,outLabelIndex=1,outDir=self.parent.dataDir)

        for ifile,f in enumerate(outFiles):
            tmpOutFileName = os.path.join(self.parent.dataDir,outFiles[ifile].file.filename)
            outFiles[ifile].file.close()
            # outDict[toDoTimes[ifile]] = descriptors.H5Array(tmpOutFileName)

        return outDict



class FilterSegmentation(descriptors.ChannelData):

    def __init__(self,parent,baseData,nickname,*args,**kargs):
        print 'creating filter segmentation of %s' %(baseData.nickname)

        self.baseData = baseData
        self.hierarchy = nickname
        # self.dir = self.baseData.dir
        # self.fileNameFormat = self.baseData.fileNameFormat

        super(FilterSegmentation,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = h5py.Dataset


    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            # tmpFile = h5py.File(self.baseData.getFileName(time))
            tmpFile = self.parent[time]
            if self.nickname in tmpFile.keys():
                if redo:
                    del tmpFile[self.nickname]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    # outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=self.nickname)
                    outDict[time] = True
            else:
                toDoTimes.append(time)
            #tmpGroup.file.close()
            # tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):

            so = sitk.gifa(self.baseData[time])
            # tmpRes = imaging.gaussian3d(so,(2,2,4.))
            tmpRes = sitk.SmoothingRecursiveGaussian(so,2)
            tmpRes = sitk.Laplacian(tmpRes)
            tmpRes = sitk.Cast(tmpRes<-5,3)#*sitk.Cast(sitk.Abs(tmpRes),3)
            tmpRes = sitk.gafi(tmpRes)

            tmpRes,N = ndimage.label(tmpRes)
            tmpRes = imaging.mySizeFilter(tmpRes,5000,1000000000000)

            # filing.toH5(tmpRes.astype(n.uint16),self.baseData[time].file.filename,hierarchy=self.nickname,
            #             compression='jls',compressionOption=0)
            filing.toH5_hl(tmpRes.astype(n.uint16),self.parent[time],hierarchy=self.hierarchy,
                        compression='jls',compressionOption=0)

            # tmpFile = h5py.File(self.baseData[time].file.filename)
            # tmpFile[self.nickname] = tmpRes
            # tmpFile.close()

            # outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
            #                         hierarchy=self.nickname)
            outDict[time] = True

        return outDict


class MaskedSegmentation(descriptors.ChannelData):

    def __init__(self,parent,baseData,mask,nickname,*args,**kargs):
        print 'creating mask of %s' %(baseData.nickname)

        self.baseData = baseData
        self.mask = mask
        self.hierarchy = nickname
        # self.mask = sitk.gafi(mask)
        # tmp = n.array(self.mask.nonzero())
        # self.maskMin = n.min(tmp,1)
        # self.maskMax = n.max(tmp,1)
        # self.slices = tuple([slice(self.maskMin[i],self.maskMax[i]) for i in range(3)])

        # self.dir = self.baseData.dir
        self.fileNameFormat = parent.fileNameFormat

        super(MaskedSegmentation,self).__init__(parent,nickname,*args,**kargs)

        self.timepointClass = h5py.Dataset


    def prepareTimepoints(self,times,redo):

        outDict = dict()

        alreadyDoneTimes, toDoTimes = [],[]
        for itime,time in enumerate(times):
            # tmpFile = h5py.File(self.baseData.getFileName(time))
            tmpFile = self.parent[time]
            if self.nickname in tmpFile.keys():
                if redo:
                    del tmpFile[self.nickname]
                    toDoTimes.append(time)
                else:
                    alreadyDoneTimes.append(time)
                    # outDict[time] = descriptors.H5Array(self.getFileName(time),hierarchy=self.nickname)
                    outDict[time] = True
            else:
                toDoTimes.append(time)
            #tmpGroup.file.close()
            # tmpFile.close()

        print 'already prepared: %s\nto prepare: %s\n' %(alreadyDoneTimes,toDoTimes)

        if not len(toDoTimes): return outDict

        for itime,time in enumerate(toDoTimes):

            tmpRes = self.baseData[time][self.mask.slices]*self.mask.ga()[self.mask.slices]

            # filing.toH5(tmpRes.astype(n.uint16),self.baseData[time].file.filename,hierarchy=self.nickname,
            #             compression='jls',compressionOption=0)
            filing.toH5_hl(tmpRes.astype(n.uint16),self.parent[time],hierarchy=self.hierarchy,
                        compression='jls',compressionOption=0)

            # tmpFile = h5py.File(self.baseData[time].file.filename)
            # tmpFile[self.nickname] = tmpRes
            # tmpFile.close()

            # outDict[time] = descriptors.H5Array(self.baseData.getFileName(time),
            #                         hierarchy=self.nickname)
            outDict[time] = True

        return outDict