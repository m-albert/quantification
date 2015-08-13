__author__ = 'malbert'

def processTP(time):

    nDilations = 15
    signal = n.array(b.signal(time)[2:])
    signal = signal[signal>0.1]
    nonzero = n.array(b.reggcamp(time)[2:])>0
    tmp = sitk.gifa((n.array(b.regpredmic(time)[2:])>0.5).astype(n.uint16))
    tmp = sitk.BinaryErode(tmp,1)
    tmp = sitk.BinaryDilate(tmp,1)
    tmpVals = []
    inds = []
    for idilate in range(nDilations):
        print '    %s' %idilate
        tmpn=sitk.Cast(sitk.Convolution(tmp,fp)>0,3)
        tmpInds = (sitk.gafi(tmpn-tmp)*nonzero).astype(n.bool)
        inds.append(tmpInds)
        tmpVals.append(n.mean(signal[tmpInds]))
        tmp = tmpn
    return n.array(tmpVals)

def processTP2(time):

    fp = n.zeros((3,9,9))
    # fp[:2,4:,:5] = 1
    fp[0,4:7,2:5]=1
    fp[1,4:,0:5]=1
    fp = sitk.Cast(sitk.gifa(fp),3)

    nDilations = 15
    signal = n.array(b.signal(time)[2:])
    #signal = signal[signal>0.1]
    nonzero = n.array(b.reggcamp(time)[2:])>0
    tmp = sitk.gifa((n.array(b.regpredmic(time)[2:])>0.5).astype(n.uint16))
    tmp = sitk.BinaryErode(tmp,1)
    tmp = sitk.BinaryDilate(tmp,1)
    tmpVals = []
    inds = []
    for idilate in range(nDilations):
        print '    %s' %idilate
        # tmpn=sitk.BinaryDilate(tmp,(8,8,3))
        tmpn=sitk.Cast(sitk.Convolution(tmp,fp)>0,3)
        tmpInds = (sitk.gafi(tmpn-tmp)*nonzero).astype(n.bool)
        inds.append(tmpInds)
        tmpVals.append(n.mean(signal[tmpInds]))
        tmp = tmpn
    return [n.array(tmpVals),n.array(inds)]
    # return n.array(tmpVals)


def processTP3(time):

    fp = n.ones((3,9,9))
    fp[0,2:7,2:7]=1
    fp[1]=1
    fp[2,2:7,2:7]=1
    # fp[1,4:,0:5]=1
    fp = sitk.Cast(sitk.gifa(fp),3)

    nDilations = 15
    signal = n.array(b.signal(time)[2:])
    #signal = signal[signal>0.1]
    nonzero = n.array(b.reggcamp(time)[2:])>0
    tmp = sitk.gifa((n.array(b.regpredmic(time)[2:])>0.5).astype(n.uint16))
    tmp = sitk.BinaryErode(tmp,1)
    tmp = sitk.BinaryDilate(tmp,1)
    tmpVals = []
    inds = []
    for idilate in range(nDilations):
        print '    %s' %idilate
        # tmpn=sitk.BinaryDilate(tmp,(8,8,3))
        tmpn=sitk.Cast(sitk.Convolution(tmp,fp)>0,3)
        tmpInds = (sitk.gafi(tmpn-tmp)*nonzero).astype(n.bool)
        inds.append(tmpInds)
        tmpVals.append(n.mean(signal[tmpInds]))
        tmp = tmpn
    return [n.array(tmpVals),n.array(inds)]
    # return n.array(tmpVals)

if __name__=="__main__":
    from multiprocessing import Pool

    p = Pool(23)
    # res2 = p.map(processTP2,range(0,100))
    # res3 = p.map(processTP3,range(0,100))
    #res3 = p.map(la,range(90))
    # res4 = processTP(10)

    tres2 = processTP2(50)
    tres3 = processTP3(50)