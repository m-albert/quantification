__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *

ref = sitk.ReadImage('/home/malbert/delme/ref4dpf.tif')
mov = sitk.ReadImage('/data/malbert/atlas/references/45dpf_af_gfp/20150811/output/stack1.tif')

mov.SetSpacing([0.25,0.25,3.2/8.])

q = registration.getParamsFromElastixCompose([ref,mov])
