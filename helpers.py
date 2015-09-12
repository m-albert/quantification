__author__ = 'malbert'


# delete key from h5s
# keys = ['interaligned','interreg','intrareg','intraaligned','seg']
keys = ['objects']
times = range(10)
for ii,i in enumerate(['/data/malbert/quantification/20150811_p2y12_4dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,3,5,9,10,11,12,13,15,16]]):
# for ii,i in enumerate(['/data/malbert/quantification/20150809_p2y12_6dpf_1min_3_%s.czi/raw_ch0' %j for j in [1,2,4,5,9,10,13,14,15,16]]):
# for ii,i in enumerate(['/data/malbert/quantification/20150812_p2y12_5dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,5,6,7,8,9,10,11]]):
    for it,t in enumerate(times):
        print i,t
        tmpFile = h5py.File(os.path.join(i,'f%06d.h5' %t))
        for key in keys:
            try:
                del tmpFile[key]
            except: pass
        tmpFile.close()



# rename key from h5s
oldkey = 'interaligned'
newkey = 'interaligned_old'
times = range(10)
# for ii,i in enumerate(['/data/malbert/quantification/20150811_p2y12_4dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,3,5,9,10,11,12,13,15,16]]):
# for ii,i in enumerate(['/data/malbert/quantification/20150812_p2y12_5dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,5,6,7,8,9,10,11]]):
for ii,i in enumerate(['/data/malbert/quantification/20150809_p2y12_6dpf_1min_3_%s.czi/raw_ch0' %j for j in [1,2,4,5,9,10,13,14,15,16]]):
    for it,t in enumerate(times):
        try:
            tmpFile = h5py.File(os.path.join(i,'f%06d.h5' %t))
            tmpFile[newkey] = tmpFile[oldkey]
            del tmpFile[oldkey]
        except: pass
        tmpFile.close()

