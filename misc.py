__author__ = 'malbert'

from dependencies import *

def sortAxes(ar,order):
    oraxes = n.array(range(len(ar.shape)))
    for iax,ax in enumerate(order):
        tmpAx = n.where(oraxes==ax)[0][0]
        ar = ar.swapaxes(iax,tmpAx)
        curAxis = oraxes[iax]
        oraxes[iax] = oraxes[tmpAx]
        oraxes[tmpAx] = curAxis
    return ar

def getAttributeFromAll(objList,attribute):
    res = []
    def recursiveReturnAttribute(element,attribute):
        if n.iterable(element):
            for iel in range(len(element)):
                recursiveReturnAttribute(element[iel],attribute)
        else:
            res.append(element.__getattribute__(attribute))
        return
    recursiveReturnAttribute(objList,attribute)
    return res

def applyFunctionToAll(objList,func):
    res = []
    objnumber = []
    def recursiveReturnFunc(element,func):
        if n.iterable(element):
            for iel in range(len(element)):
                recursiveReturnFunc(element[iel],func)
        else:
            res.append(func(element))
            print len(objnumber)
            objnumber.append(1)
        return
    recursiveReturnFunc(objList,func)
    return res

class customIndex:
    def __init__(self,N):
        self.N = N
    def encode(self,numbers):
        retString = '1'
        for inum in range(len(numbers)): retString += '%03d' %numbers[inum]
        return int(retString)
    def decode(self,num):
        num = str(num)[1:]
        res = []
        for inum in range(self.N):
            res += [int(num[3*inum:3*(inum+1)])]
        return res


def showCoordinates(obj,attribute='coordinates'):

    tmp = obj.__getattribute__(attribute)
    if tmp is None: raise(Exception('no skeleton computed yet'))

    import mayavi.mlab
    fig = mayavi.mlab.figure(attribute)
    if attribute=='skeletonCoords' and not (obj.nodeValues is None):
        mayavi.mlab.points3d(tmp[0],tmp[1],tmp[2],obj.nodeValues,scale_factor=1.,figure=fig)
    else:
        mayavi.mlab.points3d(tmp[0],tmp[1],tmp[2],scale_factor=1.,figure=fig)#,n.random.randint(0,100,len(tmp[0])))#,n.ones(len(tmp[0]))*1)#,scale_mode='scalar')
    #nodes.glyph.scale_mode = 'scalar'
    return


def animate(objectList,attribute):

    tmp = objectList[0].__getattribute__(attribute)
    if tmp is None: raise(Exception('no skeleton computed yet'))

    import mayavi.mlab
    fig = mayavi.mlab.figure(attribute)

    mayavi.mlab.points3d(0,0,0)
    plt = mayavi.mlab.points3d(tmp[0],tmp[1],tmp[2],objectList[0].nodeValues,scale_factor=1.,figure=fig)

    @mlab.animate(delay=100)
    def anim():
        f = mayavi.mlab.gcf()
        while True:
            for (x, y, z) in zip(xs, ys, zs):
                print('Updating scene...')
                plt.mlab_source.x[0] = x
                plt.mlab_source.y[0] = y
                plt.mlab_source.z[0] = z
                f.scene.render()
                yield


    anim()
    return

def getImages(brain,objList,tmin,tmax,colorDimension=1,attribute='coordinates'):

    # assumes times are the same! res[iobjtime-tmin]

    res = n.zeros((tmax-tmin,)+brain.shape,dtype=n.uint16)
    for iobj in range(len(objList)):
        if not colorDimension: color = 1
        for iobjtime in range(len(objList[iobj])):
            if colorDimension == 1: color = iobj+1000
            elif colorDimension == 2: color = iobjtime+1000
            obj = objList[iobj][iobjtime]
            res[iobjtime-tmin][obj.bbox][tuple(obj.__getattribute__(attribute))] = color
    return res