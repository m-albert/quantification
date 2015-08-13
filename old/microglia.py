__author__ = 'malbert'

from dependencies import *
#import objects

class MicrogliaSnap(objects.Object):
    def __init__(self):
        self.skeletonCoords = 0

class Microglia(object):
    def __init__(self):
        self.debug = False
        self.snaps = []
        self.times = []

def getSkeleton(ms):

    nDilations=3

    binary = n.zeros(tuple([ms.bbox[idim].stop-ms.bbox[idim].start for idim in range(3)]),dtype=n.uint16)
    binary[ms.coordinates] = 1
    binary = sitk.gifa(binary)
    binary = sitk.BinaryFillhole(binary)
    for i in range(nDilations):
        binary = sitk.BinaryDilate(binary)
    binary = sitk.BinaryThinning(binary)
    binary = sitk.gafi(binary)
    ms.skeletonCoords = n.where(binary)
    return

def getSkeletons(objectIterable,nDilations=5):

    fileNameString = 'tmp%09d.tif'

    fileDir = '/data/malbert/tmp/skeletonize/%s' %importsDict['timestamp']
    if not os.path.exists(fileDir): os.mkdir(fileDir)
    #else: raise(Exception('directory already exists'))

    objs = []
    def recursiveAppendFunc(element):
        if n.iterable(element):
            for iel in range(len(element)):
                recursiveAppendFunc(element[iel])
        else:
            objs.append(element)
        return

    recursiveAppendFunc(objectIterable)
    #pdb.set_trace()

    for iobj in range(len(objs)):
        tmp = objects.getObjectImage(objs[iobj])
        tmp = sitk.gifa(tmp.astype(n.uint8))

        tmp = sitk.BinaryFillhole(tmp)
        for i in range(nDilations):
            tmp = sitk.BinaryDilate(tmp)

        sitk.WriteImage(tmp,os.path.join(fileDir,fileNameString %iobj))

    os.system("/home/malbert/software/fiji/Fiji/ImageJ-linux64 skeletonize.py %s" %fileDir)

    for iobj in range(len(objs)):
        tmp = sitk.gafi(sitk.ReadImage(os.path.join(fileDir,fileNameString %iobj)))
        os.remove(os.path.join(fileDir,fileNameString %iobj))
        objs[iobj].skeletonCoords = tmp.nonzero()

    os.rmdir(fileDir)

    return

def skeletonizeImage(im):
    fileNameString = 'tmp%09d.tif'
    fileDir = '/data/malbert/tmp/skeletonize/%s' %(importsDict['timestamp']+'_skelIm')
    if not os.path.exists(fileDir): os.mkdir(fileDir)

    sitk.WriteImage(sitk.Cast(im,sitk.sitkUInt8),os.path.join(fileDir,fileNameString %0))

    os.system("/home/malbert/software/fiji/Fiji/ImageJ-linux64 skeletonize.py %s" %fileDir)

    tmp = sitk.ReadImage(os.path.join(fileDir,fileNameString %0))
    return tmp

def getSkeletonNodesOld(ms):

    def isNode(pixelBox):
        pixelBox = pixelBox.reshape((3,3,3)).astype(n.bool)
        return pixelBox[1,1,1]*(n.sum(pixelBox)-1)

    #coords = ms.skeletonCoords
    tmp = n.zeros(tuple([ms.bbox[i].stop-ms.bbox[i].start for i in range(3)]),dtype=n.uint8)
    if ms.skeletonCoords is None: raise(Exception('no skeleton computed yet'))
    tmp[ms.skeletonCoords] = 1

    #tmp = ndimage.convolve(tmp,n.ones((3,3,3)))
    tmp = ndimage.generic_filter(tmp,isNode,footprint=n.ones((3,3,3)),mode='constant')
    nodes = (tmp>2)+(tmp==1)
    coordValues = (tmp>2)*1.1+(tmp==1)*2+(tmp==2)*1.1
    ms.nodeValues = coordValues[ms.skeletonCoords]
    ms.skeletonNodes = nodes.nonzero()
    return

def getSkeletonNodes(ms):

    coords = n.array(ms.skeletonCoords)

    tmp = n.zeros(tuple([ms.bbox[i].stop-ms.bbox[i].start+2 for i in range(3)]),dtype=n.uint8)
    if ms.skeletonCoords is None: raise(Exception('no skeleton computed yet'))

    tmp[tuple(coords+n.ones((3,1),dtype=n.uint16))] = 1

    convBox = n.ones((3,3,3))
    convIndices = n.array(convBox.nonzero())
    nodeValues = n.zeros(len(coords[0]))
    for icoord in range(len(coords[0])):
        tmpCoord = coords[:,icoord]
        tmpIndices = convIndices + tmpCoord.reshape((3,1))
        nodeValues[icoord] = (n.sum(tmp[tuple(tmpIndices)])-1)


    #tmp = ndimage.convolve(tmp,n.ones((3,3,3)))
    #tmp = ndimage.generic_filter(tmp,isNode,footprint=n.ones((3,3,3)),mode='constant')
    #nodes = (tmp>2)+(tmp==1)
    #coordValues = (tmp>2)*1.1+(tmp==1)*2+(tmp==2)*1.1
    ms.nodeValues = nodeValues
    validNodeValues = [1,3,4,5,6,7]
    ms.skeletonNodes = tuple(coords[:,n.min([n.abs(nodeValues-validNodeValues[i]) for i in range(len(validNodeValues))],0)==0])
    return