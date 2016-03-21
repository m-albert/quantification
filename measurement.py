__author__ = 'malbert'

from dependencies import *

import matplotlib.pyplot as plt

def plotCell(tracks,objectNickname='seg',track=0):
    c = n.array(tracks["%s/centers/%s" %(objectNickname,track)])
    v = n.array(tracks["%s/sizes/%s" %(objectNickname,track)])
    s = n.array(tracks["%s/surfaces/%s" %(objectNickname,track)])
    r = s/v

    times = n.array(tracks[str(track)][:,0])*15/60.

    displacement = c-c[0]
    d = n.linalg.norm(displacement,axis=1)
    # d = n.linalg.norm(c[1:]-c[:-1],axis=1)
    # d = n.array([n.sum(d[:i]) for i in range(len(d))])
    # d = n.array(list(d)+[d[-1]])

    data = n.array([s/s[0],v/v[0],r/r[0]])

    f, axarr = plt.subplots(4,1)
    axarr[0].plot(times,d)
    axarr[1].plot(times,s/s[0])
    axarr[2].plot(times,v/v[0])
    axarr[3].plot(times,r/r[0])

    axarr[0].set_title('displacement')
    axarr[1].set_title('surface')
    axarr[2].set_title('volume')
    axarr[3].set_title('ratio')

    for i in range(1,len(axarr)):
        axarr[i].set_ylim([data.min(),data.max()])
        axarr[i].set_xlabel('min')
        # axarr[i].set_ylim[0,1]

    f.canvas.draw()

    return n.array([d,s/s[0],v/v[0],r/r[0]])

# def plotAll(tracks,objectNickname='seg',track=0):
def plotAll(tracks,track=0):
    objectNickname = tracks.baseData.nickname
    c = n.array(tracks["%s/centers/%s" %(objectNickname,track)])
    v = n.array(tracks["%s/sizes/%s" %(objectNickname,track)])
    s = n.array(tracks["%s/surfaces/%s" %(objectNickname,track)])
    r = s/v
    # pdb.set_trace()

    times = n.array(tracks[str(track)][:,0])
    # xtimes = n.array(tracks[str(track)][:,0])*15/60.
    xtimes = n.array(tracks[str(track)][:,0])
    objs = n.array(tracks[str(track)][:,1])
    ems,membraneDensity,cytoDensity,totalSignal,volumeDensity = [],[],[],[],[]
    for itime,time in enumerate(times):
        signal = n.array(tracks.parent.p2y12[int(time)])
        # tlabels = n.array(n.array(tracks[int(time)])==(track+1)).astype(n.uint16)
        tlabels = n.array(n.array(tracks.parent.__dict__[objectNickname][int(time)]['labels'])==(objs[itime]+1)).astype(n.uint16)
        tlabelsEroded = ndimage.binary_erosion(tlabels,iterations=2)
        volumeSignal = tlabels*signal
        cytoSignal = tlabelsEroded*signal
        membraneRegion = (tlabels-tlabelsEroded).astype(n.uint16)
        effectiveMembrane = membraneRegion*signal
        NSurface = n.sum(membraneRegion>0)
        NVolume = n.sum(tlabels>0)
        NCyto = n.sum(tlabelsEroded>0)
        ems.append(effectiveMembrane)
        membraneDensity.append(n.sum(effectiveMembrane)/float(NSurface))
        cytoDensity.append(n.sum(cytoSignal)/float(NCyto))
        cytoDensity.append(n.sum(cytoSignal)/float(NCyto))
        volumeDensity.append(n.sum(volumeSignal)/float(NVolume))
        totalSignal.append(n.sum(volumeSignal))
        # pdb.set_trace()

    totalSignal = n.array(totalSignal)
    cytoDensity = n.array(cytoDensity)
    volumeDensity = n.array(volumeDensity)
    membraneDensity = n.array(membraneDensity)
    densityRatio = membraneDensity/volumeDensity
    ems = n.array(ems)


    displacement = c-c[0]
    d = n.linalg.norm(displacement,axis=1)
    d2 = n.linalg.norm(c[1:]-c[:-1],axis=1)
    # d2 = n.array([n.sum(d[:i]) for i in range(len(d))])
    d2 = n.array(list(d2)+[d2[-1]])

    data0 = n.array([s/s[0],v/v[0],r/r[0]])

    f, axarr = plt.subplots(4,2)
    axarr[0][0].plot(xtimes,d)
    axarr[1][0].plot(xtimes,s/s[0])
    axarr[2][0].plot(xtimes,v/v[0])
    axarr[3][0].plot(xtimes,r/r[0])

    axarr[0][0].set_title('displacement')
    axarr[1][0].set_title('surface')
    axarr[2][0].set_title('volume')
    axarr[3][0].set_title('ratio')

    # axarr[0][1].set_title('momentaneous displacement')
    axarr[0][1].set_title('total signal')
    axarr[1][1].set_title('surface density')
    axarr[2][1].set_title('cytoplasmic density')
    axarr[3][1].set_title('density ratio')

    # axarr[0][1].plot(xtimes,d2)
    ys = [totalSignal,membraneDensity,volumeDensity,densityRatio]
    ys = n.array([i/i[0].astype(n.float) for i in ys])
    for i in range(4):
        axarr[i][1].plot(xtimes,ys[i])

    for i in range(1,len(axarr)):
        axarr[i][0].set_ylim([data0.min(),data0.max()])
        # axarr[i][0].set_xlabel('min')
        axarr[i][0].set_xlabel('15s')

    for i in range(4):
        # axarr[i][1].set_xlabel('min')
        axarr[i][1].set_xlabel('15s')
        axarr[i][1].set_ylim([ys.min(),ys.max()])
        # axarr[i].set_ylim[0,1]

    f.canvas.draw()

    # return n.array([d,s/s[0],v/v[0],r/r[0]]),ems
    return ems


def separateCell(miclabel):
    miclabel = (miclabel>0).astype(n.uint16)
    labels = []
    for time in range(len(miclabel)):
        tmpLabels,N = ndimage.label(miclabel[time])
        print N
        tmpSizes = imaging.getSizes(tmpLabels)
        if N != 2:
            # pdb.set_trace()
            # tmpLabels = imaging.sizeFilter(tmpLabels,n.sort(tmpSizes)[-3]+1)
            tmpLabels = imaging.mySizeFilter(tmpLabels,n.sort(tmpSizes)[-3]+1)
            # tmpSizes = imaging.getSizes(tmpLabels)
        labels.append(tmpLabels)
    labels = n.array(labels)
    labels = imaging.trackLabels(labels)[1]
    return labels

def plotSeparateCell(sepcell,micim=None):

    times = range(sepcell.shape[0])

    vs,ss,cs = [],[],[]

    for time in times:
        print 'time %s' %time
        tmpVolume = [objects.vtk_volume(sepcell[time]==1),objects.vtk_volume(sepcell[time]==2)]
        tmpSurface = [objects.vtk_surface(sepcell[time]==1),objects.vtk_surface(sepcell[time]==2)]
        vs.append(tmpVolume)
        ss.append(tmpSurface)
        cs.append(n.array(ndimage.center_of_mass(sepcell[time],sepcell[time],range(1,3))))

    vs,ss,cs = n.array(vs),n.array(ss),n.array(cs)

    # for time in range(sepcell.shape[0]):
    return vs,ss,cs

# f.clf()
# axarr[0][0] = fig.add_subplot(1,3,1)
#     plots = [[0 for i in range(3)] for j in range(3)]
#     plots[0][0] = axarr[0][0].imshow(Img[slices], cmap=plt.cm.gray)
#
# axarr[0][0].contour(phi[slices], [0], colors='r')

# la = []
# for i in range(len(ems)):
#     tmp = n.sum(n.sum(n.sum(ems[i],-1),-1),-1)
#     tmpN = n.sum(ems[i]>0)
#     tmpR = tmp/float(tmpN)
#     la.append(tmpR)
#
# vs = b.tracks_140["p2y12//0"]
# v = []
# for i in range(len(vs)):
#     tmp = n.sum(n.sum(n.sum(vs[i],-1),-1),-1)
#     tmpN = n.sum(vs[i]>0)
#     tmpR = tmp/float(tmpN)
#     v.append(tmpR)