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

        self.trainingSamplesDir = os.path.join(parent.dataDir,'training')
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

    def __init__(self,parent,baseData,nickname,threshold=-50,*args,**kargs):
        print 'creating filter segmentation of %s' %(baseData.nickname)

        self.baseData = baseData
        self.hierarchy = nickname
        self.threshold = threshold
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
            tmpRes = laplaceFilter(so,gauss=[2,2,1],thresh=self.threshold)
            # tmpRes = segmentLaplace(so,thresh=self.threshold,nErode = 2,nDilate = 10)
            tmpRes = sitk.gafi(tmpRes)
            # tmpRes = imaging.gaussian3d(so,(2,2,4.))


            # tmpRes = sitk.SmoothingRecursiveGaussian(so,2)
            # tmpRes = sitk.Laplacian(tmpRes)
            # tmpRes = sitk.Cast(tmpRes<-5,3)#*sitk.Cast(sitk.Abs(tmpRes),3)
            # tmpRes = sitk.gafi(tmpRes)



            #tmpRes,N = ndimage.label(tmpRes)
            #tmpRes = imaging.mySizeFilter(tmpRes,5000,1000000000000)

            # filing.toH5(tmpRes.astype(n.uint16),self.baseData[time].file.filename,hierarchy=self.nickname,
            #             compression='jls',compressionOption=0)
            # filing.toH5_hl(tmpRes.astype(n.uint16),self.parent[time],hierarchy=self.hierarchy,
            #             compression='jls',compressionOption=0)
            filing.toH5_hl(tmpRes.astype(n.uint16),self.parent[time],hierarchy=self.hierarchy,
                           )

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

@descriptors.imageFormat(sitk.Image)
def laplaceFilterOld(so,gauss=2,thresh=-5):
    tmpRes = sitk.SmoothingRecursiveGaussian(so,gauss)
    tmpRes = sitk.Laplacian(tmpRes)
    tmpRes = sitk.Cast(tmpRes<thresh,3)#*sitk.Cast(sitk.Abs(tmpRes),3)
    # tmpRes = sitk.gafi(tmpRes)
    return tmpRes

@descriptors.imageFormat(sitk.Image)
def laplaceFilter(so,gauss=[2,2,1.],thresh=-5):
    tmpRes = imaging.gaussian3d(so,gauss)
    # tmpRes = sitk.SmoothingRecursiveGaussian(so,gauss)
    tmpRes = sitk.Laplacian(tmpRes)
    tmpRes = sitk.Cast(tmpRes<thresh,3)#*sitk.Cast(sitk.Abs(tmpRes),3)
    # tmpRes = sitk.gafi(tmpRes)
    return tmpRes

@descriptors.imageFormat(sitk.Image)
def segmentIntensity(im,thresh=500,nErode=1,nDilate=3):

    im = im>thresh
    # im = sitk.gifa(im.astype(n.uint16))
    # im = sitk.BinaryErode(im,1)
    # im = sitk.BinaryDilate(im,1)
    # im = sitk.BinaryDilate(im,nDil)
    # im = sitk.BinaryErode(im,nDil)

    im = imaging.sitk2d(im,sitk.BinaryErode,nErode)
    im = imaging.sitk2d(im,sitk.BinaryDilate,nErode)
    im = imaging.sitk2d(im,sitk.BinaryDilate,nDilate)
    im = imaging.sitk2d(im,sitk.BinaryErode,nDilate)

    im = sitk.gafi(im)
    l,N = ndimage.label(im)
    l = sitk.gifa(l.astype(n.uint16))

    return l

@descriptors.imageFormat(sitk.Image)
def segmentLaplace(im,gauss=[2,2,2],thresh=-50,nErode=1,nDilate=3):

    # pdb.set_trace()
    im = laplaceFilter(im,gauss,thresh)
    # im = sitk.BinaryErode(im,nErode)
    # im = sitk.BinaryDilate(im,nErode)
    # im = sitk.BinaryDilate(im,nDilate)
    # im = sitk.BinaryErode(im,nDilate)

    im = imaging.sitk2d(im,sitk.BinaryErode,nErode)
    im = imaging.sitk2d(im,sitk.BinaryDilate,nErode)
    im = imaging.sitk2d(im,sitk.BinaryDilate,nDilate)
    im = imaging.sitk2d(im,sitk.BinaryErode,nDilate)

    # im = imaging.sitk2d(im,sitk.BinaryFillhole)

    im = sitk.gafi(im)
    l,N = ndimage.label(im)
    l = sitk.gifa(l.astype(n.uint16))

    return l


@descriptors.imageFormat(sitk.Image)
def segmentFromFilter(im,gauss=[2,2,1],nErode=2,nDilate=2):

    im = im>0

    im = imaging.sitk2d(im,sitk.BinaryErode,nErode)
    im = imaging.sitk2d(im,sitk.BinaryDilate,nErode)
    im = imaging.sitk2d(im,sitk.BinaryDilate,nDilate)
    im = imaging.sitk2d(im,sitk.BinaryErode,nDilate)

    # im = imaging.sitk2d(im,sitk.BinaryFillhole)

    im = sitk.gafi(im)
    l,N = ndimage.label(im)
    l = sitk.gifa(l.astype(n.uint16))

    return l

def divergence(F):
    """ compute the divergence of n-D scalar field `F` """
    return reduce(n.add,n.gradient(F))


def edgePotential(im,alpha=300,beta=500):
    im = sitk.SmoothingRecursiveGaussian(im,0.3)
    # im = sitk.SmoothingRecursiveGaussian(im,g)
    im = sitk.Laplacian(im)
    import stacking
    # for deconvolved images
    im = sitk.Abs(sitk.Cast(im,6)*sitk.Cast((im<0),6))
    im = stacking.scale(im)
    # pdb.set_trace()
    # im = sitk.Sigmoid(im,
    #                    alpha=alpha,
    #                    beta=beta,
    #                    outputMaximum=1.0,
    #                    outputMinimum=0.0)
    # im = -im
    return im

def initialEdges(im,pixelPositions,radius=1):
    fm = sitk.gifa(n.ones(im.GetSize()[::-1],dtype=n.float))
    fm.SetSpacing(im.GetSpacing())
    posList = []
    for ipos in range(len(pixelPositions)):
        posList.append(pixelPositions[ipos])

    # pdb.set_trace()
    seeds = sitk.VectorUIntList(posList)
    fm = sitk.FastMarching(fm,
                      trialPoints = seeds,
                      normalizationFactor=1.,
                      stoppingValue=radius)
    fm = fm<1000
    # fm = sitk.BinaryDilate(fm)-fm
    fm = sitk.SignedMaurerDistanceMap(fm)
    # fm = sitk.BinaryNot(fm)

    return fm

def activeContours(initial,edges,propagationScaling=1.,curvatureScaling=0.05,advectionScaling=2,iterations=2000):
    geo = sitk.GeodesicActiveContourLevelSet(
                              sitk.Cast(initial,6),
                              sitk.Cast(edges,6),
                              maximumRMSError=0.02,
                              # propagationScaling=propagationScaling,
                              propagationScaling=propagationScaling,
                              curvatureScaling=curvatureScaling,
                              advectionScaling=advectionScaling,
                              numberOfIterations=iterations,
                              reverseExpansionDirection=False)
    return geo

@descriptors.imageFormat(sitk.Image)
def laplace2d(im):
    res = []
    for iz in range(im.GetSize()[2]):
        tmp = sitk.SmoothingRecursiveGaussian(im[:,:,iz],0.3)
        tmp = sitk.gafi(sitk.Laplacian(tmp))
        res.append(tmp)
    res = sitk.gifa(n.array(res))
    return res


if __name__=="__main__":

    tmpRes = sitk.SmoothingRecursiveGaussian(so,2)
    tmpRes = sitk.Laplacian(tmpRes)
    tmpRes = sitk.Cast(tmpRes<-5,3)#*sitk.Cast(sitk.Abs(tmpRes),3)
    tmpRes = sitk.gafi(tmpRes)

