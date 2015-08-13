__author__ = 'malbert'

from dependencies import *

trackTimes = range(100)
tracks=tracking.trackObjects(b.segregpredmic(trackTimes),minTrackLength=len(trackTimes),memory=2)

miccalc,outercalc,motility = [],[],[]
containers,containercs,containerbs = [],[],[]
for itrack,track in enumerate(tracks):
    print itrack
    tmp1,tmp2,tmp3 = [],[],[]
    bboxes = misc.getAttributeFromAll(track,'bbox')

    extrema = n.array([[[bboxes[ibox][idim].start,bboxes[ibox][idim].stop] for idim in range(3)] for ibox in range(len(bboxes))]).astype(n.float)
    minima = n.min(extrema[:,:,0],0).astype(n.float)
    maxima = n.max(extrema[:,:,1],0).astype(n.float)

    container = n.zeros((len(track),)+tuple([maxima[idim]-minima[idim] for idim in range(3)]),dtype=n.float)
    containerc = n.zeros((len(track),)+tuple([maxima[idim]-minima[idim] for idim in range(3)]),dtype=n.float)
    containerb = n.zeros((len(track),)+tuple([maxima[idim]-minima[idim] for idim in range(3)]),dtype=n.float)
    for itime,obj in enumerate(track):
        bboxc = b.signal(trackTimes[itime])[obj.bbox]
        mc = bboxc[tuple(obj.coordinates)]
        tmp1.append(n.max(mc))
        tmpMinima = n.zeros((3,1),dtype=n.int64)
        tmpMinima[:,0] = minima-extrema[itime,:,0]
        container[itime][tuple(n.array(obj.coordinates)-tmpMinima)] = 1
        containerc[itime][tuple(n.array(obj.coordinates)-tmpMinima)] = mc
        containerb[itime][tuple([slice(extrema[itime][idim][0]-minima[idim],extrema[itime][idim][1]-minima[idim]) for idim in range(3)])] = bboxc
        bboxc[tuple(obj.coordinates)] = 0
        tmp2.append(n.max(bboxc))
    containers.append(container)
    containercs.append(containerc)
    containerbs.append(containerb)
    tmpMotility = n.zeros(len(track))
    tmpMotility[1:] = n.sum(n.sum(n.sum(n.abs(container[1:]-container[:-1]),-1),-1),-1)
    tmpMotility[0] = tmpMotility[1]
    tmpMotility = tmpMotility
    motility.append(tmpMotility/tmpMotility[0])
    miccalc.append(tmp1)#/tmp1[0])
    outercalc.append(tmp2)#/tmp2[0])

ims = misc.getImages(b,tracks,tmin=0,tmax=len(trackTimes))
