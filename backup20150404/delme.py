import SimpleElastix2 as sitk

import numpy as n


f = sitk.GetImageFromArray(n.random.randint(0,100,(20,20,20)).astype(n.uint16))
m = sitk.GetImageFromArray(n.random.randint(0,100,(20,20,20)).astype(n.uint16))



selx = sitk.SimpleElastix()
selx.SetFixedImage(f)
selx.SetMovingImage(m)

p = sitk.ParameterMap()
p['Registration'] = ['MultiMetricMultiResolutionRegistration']
p['Metric'] = ['NormalizedMutualInformation']
p['Transform'] = ['AffineTransform']
p['FixedImagePyramidSchedule'] = ['8', '4', '2', '1']
p['FixedInternalImagePixelType'] = 'short'
p['MovingInternalImagePixelType'] = 'short'


plist = sitk.ParameterMapList()
plist.push_back(p)

selx.SetParameterMapList(plist)

selx.LogToConsoleOn()

selx.Execute()



for it in range(1000):
    print it
    outFile = '/data/malbert/quantification/20150317_45dpf_pu1_gcamp6s_right_15s_Subset.czi/seg_ch1/f%06d_Probabilities.h5'
    if os.path.exists(outFile): continue
    tmp = filing.readH5('pred_time%05d_3.h5' %it)
    filing.toH5(misc.sortAxes(tmp,[2,1,0]),
                outFile %it)