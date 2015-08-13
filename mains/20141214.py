__author__ = 'malbert'

import sys
sys.path.append('..')
from dependencies import *

b = brain.Brain('/data/malbert/data/dbspim/20141214_gcamp_pu1_ot_30sec_Subset.czi',
                dimt=120,
                dimc=1,
                times=range(50)
                )


descriptors.RawChannel(b,0,'pu1')
#b.classifiers['pu1'] = '/data/malbert/quantification/20150502_45dpf_p2y12_fast_Subset.czi/classifier.ilp'
#b.classifier = '/data/malbert/quantification/20150502_45dpf_p2y12_fast_Subset.czi/classifier.ilp'
prediction.Prediction(b,b.pu1,'pred')

segmentation.Segmentation(b,b.pred,'segpred',redo=True,threshold=0.95,sizeThresholds=[500,10000])