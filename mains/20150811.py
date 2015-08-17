__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *


reference = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/stack1.tif')
reference.SetSpacing([4,4,1.])
# samples = [1,2,4,5,9,10,13,14,15,16]
samples = [1,2,3,5,9,10,11,12,13,15,16]
for isample,sample in enumerate(samples):
    b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150811_p2y12_40dpf/20150811_p2y12_4dpf_1min_%s.czi' %sample,
                    dimc=1,
                    times=range(10)
                    )
    descriptors.RawChannel(b,0,'p2y12')
    registration.RegistrationParameters(b,b.p2y12,'intrareg')
    registration.RegistrationParameters(b,b.p2y12,'interreg',
                                        reference=reference,
                                        initialRegistration=b.intrareg,
                                        singleRegistrationTime=0)
    registration.Transformation(b,b.p2y12,b.interreg,'aligned')



#b.classifiers['pu1'] = '/data/malbert/quantification/20150502_45dpf_p2y12_fast_Subset.czi/classifier.ilp'
#b.classifier = '/data/malbert/quantification/20150502_45dpf_p2y12_fast_Subset.czi/classifier.ilp'
# prediction.Prediction(b,b.pu1,'pred')

# segmentation.Segmentation(b,b.pred,'segpred',redo=True,threshold=0.95,sizeThresholds=[500,10000])
