__author__ = 'malbert'

from imports import *

sys.path.append('/home/malbert/software/trackpy')

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
os.mkdir(tmpDir)

elastixPath = '/home/malbert/bin/elastix'

import misc
import brain
import objects
import microglia
import fli
import aponeuron
import descriptors

