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