__author__ = 'malbert'


# av = n.zeros_like(n.array(b.signal(0)))
#
# for itime in range(100):
#     av += n.array(b.signal(itime))


def processTP(time):


    signal = b.signal(time)[2:]
    gcamp = b.reggcamp(time)[2:]
    nonzero = n.array(gcamp)>0
    tmp = sitk.gifa((n.array(b.regpredmic(time)[2:])>0.5).astype(n.uint16))
    # tmp = sitk.BinaryErode(tmp,1)
    # tmp = sitk.BinaryDilate(tmp,1)

    tmp = sitk.gafi(tmp).astype(n.bool)

    micinds = tmp*nonzero
    mic = n.mean(signal[micinds])
    nonmicinds = nonzero-tmp*nonzero
    nonmic = n.mean(signal[nonmicinds])

    return [mic,nonmic,micinds,nonmicinds]


if __name__=="__main__":

    time = 10
    micres = processTP(time)