__author__ = 'malbert'

times = range(100)

res = []
for itime,time in enumerate(times):

    tmpseg = ar(b.seg_ia[itime])
    tmpcalc = ar(b.interaligned[itime])

    tmp = tmpseg*tmpcalc

    res.append(n.max(tmp,0))

res = ar(res)