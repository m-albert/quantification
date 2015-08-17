__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

samples = [1,2,4,5,9,10,13,14,15,16]
# samples = [10,13,14,15,16]
for isample,sample in enumerate(samples):
    b = brain.Brain('/data/malbert/data/dbspim/20150810_p2y12/20150810_p2y12_65dpf/20150809_p2y12_6dpf_1min_3_%s.czi' %sample,
                    dimc=1,
                    times=range(10)
                    )
    descriptors.RawChannel(b,0,'p2y12')
    registration.RegistrationParameters(b,b.p2y12,'intrareg')
    # registration.Transformation(b,b.p2y12,b.reg,'aligned')
#b.classifiers['pu1'] = '/data/malbert/quantification/20150502_45dpf_p2y12_fast_Subset.czi/classifier.ilp'
#b.classifier = '/data/malbert/quantification/20150502_45dpf_p2y12_fast_Subset.czi/classifier.ilp'
# prediction.Prediction(b,b.pu1,'pred')

# segmentation.Segmentation(b,b.pred,'segpred',redo=True,threshold=0.95,sizeThresholds=[500,10000])
