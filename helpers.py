__author__ = 'malbert'


# delete key from h5s
# keys = ['interaligned','interreg','intrareg','intraaligned','seg']
# keys = ['skeletons_test_%s' %i for i in range(25)]
keys = ['signal']
times = range(10)
tmpBs = bs
# for ii,i in enumerate(['/data/malbert/quantification/20150811_p2y12_4dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,3,5,9,10,11,12,13,15,16]]):
# for ii,i in enumerate(['/data/malbert/quantification/20150809_p2y12_6dpf_1min_3_%s.czi/raw_ch0' %j for j in [1,2,4,5,9,10,13,14,15,16]]):
# for ii,i in enumerate(['/data/malbert/quantification/20150812_p2y12_5dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,5,6,7,8,9,10,11]]):
# for ii,i in enumerate(['/data/malbert/quantification/20150812_p2y12_5dpf_1min_%s.czi/raw_ch0' %j for j in [1]]):
for ib in range(len(bs)):
    for it,t in enumerate(times):
        print ib,it
        tmpFile = tmpBs[ib].fileDict[t]
        for key in keys:
            try:
                del tmpFile[key]
            except: pass
        # tmpFile.close()



# rename key from h5s
oldkey = 'interaligned'
newkey = 'interaligned_old'
times = range(10)
for ii,i in enumerate(['/data/malbert/quantification/20150811_p2y12_4dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,3,5,9,10,11,12,13,15,16]]):
# for ii,i in enumerate(['/data/malbert/quantification/20150812_p2y12_5dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,5,6,7,8,9,10,11]]):
# for ii,i in enumerate(['/data/malbert/quantification/20150809_p2y12_6dpf_1min_3_%s.czi/raw_ch0' %j for j in [1,2,4,5,9,10,13,14,15,16]]):
    for it,t in enumerate(times):
        try:
            tmpFile = h5py.File(os.path.join(i,'f%06d.h5' %t))
            tmpFile[newkey] = tmpFile[oldkey]
            del tmpFile[oldkey]
        except: pass
        tmpFile.close()


for i in range(10):
    q = sitk.gifa(bs[i].interaligned[0][mask.slices])
    q = beads.scaleStack([4,4,4],q)
    sitk.WriteImage(q,'/home/malbert/delme/pointstacks45dpf/stack_%s.tif' %i)

for i in range(1):
    q = sitk.gifa(bs[i].interaligned[0][mask.slices])
    l = sitk.gifa(imaging.reassignLabels(n.array(bs[i].objects[0]['labels']),random=True).astype(n.uint16))
    q = beads.scaleStack([2,2,2],q)
    l = beads.scaleStack([2,2,2],l)
    sitk.WriteImage(q,'/home/malbert/delme/pointstacks45dpf/stack_%s.tif' %i)
    sitk.WriteImage(l,'/home/malbert/delme/pointstacks45dpf/stack_labels_%s.tif' %i)


q = n.sum([(n.array(bs[i].objects[0]['labels'])>0).astype(n.uint16) for i in range(len(bs))],0).astype(n.float)
projs = []
for dim in range(3):
    projs.append(n.max(q,dim))
qmax = n.max(q,0)

q2 = [(n.array(bs[i].objects[0]['labels'])>0).astype(n.uint16) for i in range(len(bs))]

# ims = [[n.array(bs[ib].interaligned[bs[ib].times[0]]),n.array(bs[ib].interaligned[bs[ib].times[-1]])] for ib in range(len(bs))]
# mshape = mask.shape
# upperm = n.zeros(mask.shape,dtype=n.bool)
# upperm[:] = mask.ga()
# upperm[mshape[2]/2:] = 0
# ready = False
# iz = -1
# while not ready:
#     readies = []
#     for ib in range(len(bs)):
#         readies.append(n.min(bool(n.min(im1[uppermp]))))
#     ready = n.min(readies)
#     print readies
#     upperm[iz] = 0
#     iz -= 1
#     uppermp = upperm>0]
# upperm = mask.ga()[mshape[2]/2:]
# lowerm = mask.ga()[:mshape[2]/2]
# uppermnz = upperm.nonzero()
# lowermnz = lowerm.nonzero()
# uppermp = upperm>0
# lowermp = lowerm>0
# ready = False
# iz = -1
# while not ready:
#     readies = []
#     for ib in range(len(bs)):
#         readies.append(n.min(bool(n.min(ims[ib][0][uppermp]))))
#     ready = n.min(readies)
#     print readies
#     uppermp[iz] = 0
#     iz -= 1
#     uppermp = upperm>0
#             # print n.min(im2[uppermp])


ims = [[n.array(bs[ib].interaligned[bs[ib].times[0]]),n.array(bs[ib].interaligned[bs[ib].times[-1]])] for ib in range(len(bs))]
m = mask.ga().astype(n.bool)

readies = []
for ib in range(len(bs)):
    print ib
    first = n.min(n.min(ims[ib][0]*m+n.invert(m),-1),-1)
    last = n.min(n.min(ims[ib][1]*m+n.invert(m),-1),-1)
    readies.append([first,last])


    # readies.append(n.min(bool(n.min(ims[ib][0][uppermp]))))
