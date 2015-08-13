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
        self.timepointClass = descriptors.H5Array

        self.dir = self.baseData.dir

        self.trainingSamplesDir = os.path.join(self.dir,'training')
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
                outDict[time] = descriptors.H5Array(self.getFileName(time))
            else:
                toDoTimes.append(time)
                toDoStacks.append(self.baseData[time])

        if not len(toDoTimes): return outDict

        # pdb.set_trace()
        outFiles = config['ilastikCommand'](toDoStacks,self.classifier,outLabelIndex=1,outDir=self.dir)

        for ifile,f in enumerate(outFiles):
            tmpOutFileName = os.path.join(self.dir,outFiles[ifile].file.filename)
            outFiles[ifile].file.close()
            outDict[toDoTimes[ifile]] = descriptors.H5Array(tmpOutFileName)

        return outDict