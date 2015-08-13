__author__ = 'malbert'

from dependencies import *

class Track(descriptors.UnstructuredData):


    def __init__(self,parent,baseSegmentation,nickname,redo=False,
                 minTrackLength=5,
                 maxObjectDisplacementPerDimension=10.,
                 memory=0,
                 *args,**kargs):

        self.fileName = 'tracks.pc'
        self.baseSegmentation = baseSegmentation

        self.minTrackLength = minTrackLength
        self.maxObjectDisplacementPerDimension = maxObjectDisplacementPerDimension
        self.memory = memory

        super(Track,self).__init__(parent,nickname,redo,*args,**kargs)

        return

    def prepare(self,redo):

        if os.path.exists(self.fileName) and not redo:
            print 'tracking already prepared'
            tmpFile = open(self.fileName,'r')
            returnObj = pickle.load(tmpFile)
            tmpFile.close()
            return returnObj

        returnObj = trackObjects(self.baseSegmentation,
                                 minTrackLength=self.minTrackLength,
                                 maxObjectDisplacementPerDimension=self.maxObjectDisplacementPerDimension,
                                 memory=self.memory)

        # pdb.set_trace()

        tmpFile = open(self.fileName,'w')
        pickle.dump(returnObj,tmpFile)
        tmpFile.close()

        return returnObj



def trackObjects(objectSnaps,minTrackLength=50,maxObjectDisplacementPerDimension=10,memory=0):

    print 'tracking objects...'

    indexing = misc.customIndex(2)

    objs = objectSnaps
    indices = []
    times = []

    # normalize features
    sizes = n.array(misc.getAttributeFromAll(objs,'size'))
    sizeNormFactor = maxObjectDisplacementPerDimension/float(sizes.max())

    nfeatures = 4
    features = [[] for i in range(nfeatures)]
    for itime in range(len(objs)):
        for iobjs in range(len(objs[itime])):
            # times.append(objs[itime][iobjs].time)
            times.append(itime)
            for ifeat in range(3):
                features[ifeat].append(objs[itime][iobjs].center[ifeat])
            features[-1].append(objs[itime][iobjs].size*sizeNormFactor)
            indices.append(indexing.encode([itime,iobjs]))

    print features[-1]

    maxObjectDisplacement = n.sqrt(maxObjectDisplacementPerDimension**2*nfeatures)
    print 'maxObjectDisplacement %s' %maxObjectDisplacement
    dataDict = dict()
    dataDict['frame'] = times
    pos_columns = []
    for ifeat in range(nfeatures):
        dataDict[str(ifeat)] = features[ifeat]
        pos_columns.append(str(ifeat))
    dataFrame = pandas.DataFrame(data=dataDict,index=indices)
    #pdb.set_trace()
    trackResults = trackpy.link_df(dataFrame,
                                   maxObjectDisplacement,
                                   pos_columns=pos_columns,
                                   retain_index=True,
                                   memory=memory)

    # pdb.set_trace()


    nParticles = int(n.array(trackResults.particle).max())
    tracks = []
    for itrack in range(nParticles):
        tmpInds = n.where(n.array(trackResults.particle) == itrack)[0]
        if not len(tmpInds) >= minTrackLength: continue
        tmpTrack = []
        tmpTotInds = n.array(trackResults.index)
        for tmpInd in tmpInds:
            tmpTime,tmpObj = indexing.decode(tmpTotInds[tmpInd])
            # tmpTrack.append(objs[tmpTime][tmpObj])
            tmpTrack.append(objs[tmpTime][tmpObj])
        tracks.append(tmpTrack)

    return tracks