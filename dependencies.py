__author__ = 'malbert'

# from imports import *

import sys,os,inspect,subprocess,shutil,copy,ast,time,itertools,re,pdb
import signal,logging

timestamp = time.localtime()
timestamp = '%02d%02d%02d_%02d%02d%02d' %tuple([timestamp[i] for i in range(6)])

if sys.platform == 'darwin':
    prefix = '/Volumes'
    sys.path.append('/Users/malbert/Documents/software/SimpleITK-0.9.1-py2.7-macosx-10.6-intel.egg_FILES')
    sys.path.append('/Users/malbert/Documents/projects/preprocessing')
    sys.path.append('/Users/malbert/Documents/projects/scripts')
    #sys.path.append('/Users/malbert/Documents/projects/dualview')
    sys.path.append('/Users/malbert/Documents/projects/zeissFusion/experimental')
    sys.path.append('/Users/malbert/Documents/software/trackpy')
    tmpDir = os.path.join('/tmp','quantificationTmpFolder_%s' %timestamp)
    elastixPath = '/Users/malbert/Documents/software/elastix_macosx64_v4.8/bin/elastix'
    transformixPath = '/Users/malbert/Documents/software/elastix_macosx64_v4.8/bin/transformix'
    fijiPath = 'fiji'

elif sys.platform == 'linux2':
    prefix = ''
    sys.path.append('/home/malbert/software/trackpy')
    sys.path.append('/home/malbert/software/scripts')
    sys.path.append('/home/malbert/software/fusion/zeiss/experimental')
    sys.path.append('/home/malbert/software/fusion/dependencies_linux/SimpleITKcurrent')
    tmpDir = os.path.join('/data/malbert/tmp','quantificationTmpFolder_%s' %timestamp)
    elastixPath = '/home/malbert/bin/elastix'
    transformixPath = '/home/malbert/bin/transformix'
    fijiPath = '/home/malbert/software/fiji/Fiji/ImageJ-linux64'

# import stacking.scale
# import imaging.sizeFilter

import ilastiking,filing,imaging,stacking
import transformations
import tifffile
import trackpy
import pandas
import zeissFusion as zf

from matplotlib import pyplot

import czifile

if not os.path.exists(tmpDir): os.mkdir(tmpDir)

projectDir = os.path.dirname(os.path.abspath(__file__))

config = dict()

import SimpleITK as sitk
sitk.gifa = sitk.GetImageFromArray
sitk.gafi = sitk.GetArrayFromImage

import h5py
import numpy as n
from scipy import ndimage,spatial,cluster,interpolate
import random

curDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(curDir)

import morphsnakes

import misc
import brain
import descriptors
import objects
import prediction
import registration
import segmentation
import tracking
import activity


ar = n.array

# import objects
# import microglia
# import fli
# import aponeuron
# import skeletonization

