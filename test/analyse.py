__author__ = 'malbert'

from dependencies import *

trackTimes = range(100)
tracks=tracking.trackObjects(b.segregpredmic(trackTimes),minTrackLength=len(trackTimes),memory=2)

# miccalc,outercalc,motility = [],[],[]
# containers,containercs,containerbs = [],[],[]
# for itrack,track in enumerate(tracks):
#     print itrack
#     tmp1,tmp2,tmp3 = [],[],[]
#     bboxes = misc.getAttributeFromAll(track,'bbox')
#
#     extrema = n.array([[[bboxes[ibox][idim].start,bboxes[ibox][idim].stop] for idim in range(3)] for ibox in range(len(bboxes))]).astype(n.float)
#     minima = n.min(extrema[:,:,0],0).astype(n.float)
#     maxima = n.max(extrema[:,:,1],0).astype(n.float)
#
#     container = n.zeros((len(track),)+tuple([maxima[idim]-minima[idim] for idim in range(3)]),dtype=n.float)
#     containerc = n.zeros((len(track),)+tuple([maxima[idim]-minima[idim] for idim in range(3)]),dtype=n.float)
#     containerb = n.zeros((len(track),)+tuple([maxima[idim]-minima[idim] for idim in range(3)]),dtype=n.float)
#     for itime,obj in enumerate(track):
#         bboxc = b.signal(trackTimes[itime])[obj.bbox]
#         mc = bboxc[tuple(obj.coordinates)]
#         tmp1.append(n.max(mc))
#         tmpMinima = n.zeros((3,1),dtype=n.int64)
#         tmpMinima[:,0] = minima-extrema[itime,:,0]
#         container[itime][tuple(n.array(obj.coordinates)-tmpMinima)] = 1
#         containerc[itime][tuple(n.array(obj.coordinates)-tmpMinima)] = mc
#         containerb[itime][tuple([slice(extrema[itime][idim][0]-minima[idim],extrema[itime][idim][1]-minima[idim]) for idim in range(3)])] = bboxc
#         bboxc[tuple(obj.coordinates)] = 0
#         tmp2.append(n.max(bboxc))
#     containers.append(container)
#     containercs.append(containerc)
#     containerbs.append(containerb)
#     tmpMotility = n.zeros(len(track))
#     tmpMotility[1:] = n.sum(n.sum(n.sum(n.abs(container[1:]-container[:-1]),-1),-1),-1)
#     tmpMotility[0] = tmpMotility[1]
#     tmpMotility = tmpMotility
#     motility.append(tmpMotility/tmpMotility[0])
#     miccalc.append(tmp1)#/tmp1[0])
#     outercalc.append(tmp2)#/tmp2[0])
#
# ims = misc.getImages(b,tracks,tmin=0,tmax=len(trackTimes))

# tifffile.imshow(ims,vmax=1)


# ranges = [100,400]
# shape0 = b.signal[itime].shape
# X,Y,Z = n.mgrid[0:shape0[0],0:shape0[1],0:shape0[2]]
# vals = []
# for itime,time in enumerate(trackTimes[:1]):
#     print itime
#     signal = b.signal[itime]
#     nonzero = n.array(signal)>0
#     centers = [mic[itime].center for mic in tracks]
#     distances = []
#     for center in centers:
#         print '     ',center
#         distances.append(n.sqrt((X-center[0])**2+(Y-center[1])**2+((Z-center[2])*2.6)**2))
#
#     tmpVals = []
#     for ir,ra in enumerate(ranges):
#         print ir
#         tmpInds = (n.sum([distance<ra for distance in distances],0)>0)*nonzero
#         tmpVals.append(n.mean(signal[tmpInds]))
#     vals.append(tmpVals)




# nDilations = 15
# vals = []
# for itime,time in enumerate(trackTimes):
#     print itime
#     signal = b.signal[itime]
#     nonzero = n.array(signal)>0
#     tmp = sitk.gifa(ims[itime])>0
#     mic = sitk.gifa(ims[itime])>0
#     tmp = sitk.BinaryDilate(tmp,(2,5,5))
#     mic = sitk.BinaryDilate(tmp,(2,5,5))
#     tmpVals = []
#     for idilate in range(nDilations):
#         print '    %s' %idilate
#         tmp=sitk.BinaryDilate(tmp,(3,8,8))
#         tmpInds = (sitk.gafi(tmp-mic)*nonzero).astype(n.bool)
#         tmpVals.append(n.mean(signal[tmpInds]))
#     vals.append(tmpVals)

# nDilations = 15
# vals = []
# for itime,time in enumerate(trackTimes):
#     print itime
#     signal = b.signal(time)
#     nonzero = n.array(signal)>0
#     tmp = sitk.gifa((n.array(b.regpredmic(time))>0.5).astype(n.uint16))
#     tmp = sitk.BinaryErode(tmp,1)
#     tmp = sitk.BinaryDilate(tmp,1)
#     mic = sitk.gifa((n.array(b.regpredmic(time))>0.5).astype(n.uint16))
#     mic = sitk.BinaryErode(mic,1)
#     mic = sitk.BinaryDilate(mic,1)
#     # mic = sitk.gifa(b.predmic(time)>0.2)>0
#     # tmp = sitk.BinaryDilate(tmp,(2,5,5))
#     # mic = sitk.BinaryDilate(tmp,(2,5,5))
#     tmpVals = []
#     for idilate in range(nDilations):
#         print '    %s' %idilate
#         tmp=sitk.BinaryDilate(tmp,(8,8,3))
#         tmpInds = (sitk.gafi(tmp-mic)*nonzero).astype(n.bool)
#         tmpVals.append(n.mean(signal[tmpInds]))
#     vals.append(tmpVals)



def processTP(time):

    nDilations = 15
    signal = b.signal(time)[2:]
    nonzero = n.array(signal)>0
    tmp = sitk.gifa((n.array(b.regpredmic(time)[2:])>0.5).astype(n.uint16))
    tmp = sitk.BinaryErode(tmp,1)
    tmp = sitk.BinaryDilate(tmp,1)
    mic = sitk.gifa((n.array(b.regpredmic(time)[2:])>0.5).astype(n.uint16))
    mic = sitk.BinaryErode(mic,1)
    mic = sitk.BinaryDilate(mic,1)
    # mic = sitk.gifa(b.predmic(time)>0.2)>0
    # tmp = sitk.BinaryDilate(tmp,(2,5,5))
    # mic = sitk.BinaryDilate(tmp,(2,5,5))
    tmpVals = []
    tmpMics = []
    inds = []
    inds2 = []
    for idilate in range(nDilations):
        print '    %s' %idilate
        tmp=sitk.BinaryDilate(tmp,(8,8,3))
        tmpInds = (sitk.gafi(tmp-mic)*nonzero).astype(n.bool)
        tmptmpMics = []
        inds.append(tmpInds)
        layerints = n.zeros_like(signal)
        layerints[tmpInds] = signal[tmpInds]
        # pdb.set_trace()
        inds2.append(layerints)
        for imic in range(len(tracks)):
            bbox = list(tracks[imic][time].bbox)
            # pdb.set_trace()
            increase = [5,15,15]
            bbox[0] = slice(n.max([0,bbox[0].start-2-increase[0]]),bbox[0].stop-2+increase[0])
            bbox[1] = slice(n.max([0,bbox[1].start-increase[1]]),bbox[1].stop+increase[1])
            bbox[2] = slice(n.max([0,bbox[2].start-increase[2]]),bbox[2].stop+increase[2])
            bbox = tuple(bbox)
            micinds = n.zeros_like(tmpInds)
            micinds[bbox] = tmpInds[bbox]
            tmptmpMics.append(n.mean(signal[micinds]))
        tmpVals.append(n.mean(signal[tmpInds]))
        tmpMics.append(tmptmpMics)
    return [n.array(tmpVals),n.array(tmpMics),n.array(inds2)]


if __name__=="__main__":
    from multiprocessing import Pool

    p = Pool(15)
    # res = p.map(processTP,range(11,12))

    # pickle.dump(res,open('/home/malbert/delme/results200_400.pc','w'))

    # vals,mics,inds = processTP(10)

    res3 = processTP(10)