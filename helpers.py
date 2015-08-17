__author__ = 'malbert'


# delete key from h5s
key = 'interreg'
times = range(10)
for ii,i in enumerate(['/data/malbert/quantification/20150811_p2y12_4dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,3,5,9,10,11,12,13,15,16]]):
    for it,t in enumerate(times):
        tmpFile = h5py.File(os.path.join(i,'f%06d.h5' %t))
        try:
            del tmpFile[key]
        except: pass
        tmpFile.close()

# rename key from h5s
oldkey = 'interreg1'
newkey = 'intrareg1'
times = range(10)
for ii,i in enumerate(['/data/malbert/quantification/20150811_p2y12_4dpf_1min_%s.czi/raw_ch0' %j for j in [1,2,3,5,9,10,11,12,13,15,16]]):
    for it,t in enumerate(times):
        tmpFile = h5py.File(os.path.join(i,'f%06d.h5' %t))
        try:
            tmpFile[newkey] = tmpFile[oldkey]
            del tmpFile[oldkey]
        except: pass
        tmpFile.close()
