__author__ = 'malbert'

# from imports import *

import sys,os,inspect,subprocess,shutil,copy,ast,time,itertools,re,pdb


sys.path.append('/home/malbert/software/trackpy')
sys.path.append('/home/malbert/software/scripts')
sys.path.append('/home/malbert/software/fusion/zeiss/experimental')
sys.path.append('/home/malbert/software/fusion/dependencies_linux/SimpleITKcurrent')

import ilastiking,filing,imaging
import tifffile
import trackpy
import pandas
import zeissFusion as zf

from matplotlib import pyplot

import czifile

timestamp = time.localtime()
timestamp = '%02d%02d%02d_%02d%02d%02d' %tuple([timestamp[i] for i in range(6)])
tmpDir = os.path.join('/data/malbert/tmp','quantificationTmpFolder_%s' %timestamp)
# pdb.set_trace()
if not os.path.exists(tmpDir): os.mkdir(tmpDir)

elastixPath = '/home/malbert/bin/elastix'

config = dict()

import SimpleITK as sitk

import h5py
import numpy as n
from scipy import ndimage

import misc
import brain
import descriptors
import registration
import prediction
import segmentation
import tracking
import activity

# import objects
# import microglia
# import fli
# import aponeuron
# import skeletonization

