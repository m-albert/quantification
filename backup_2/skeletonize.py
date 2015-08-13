__author__ = 'malbert'

from ij import IJ
import os
import sys

fileDir = sys.argv[1]

fileList = os.listdir(fileDir)
fileList.sort()

for ifile in range(len(fileList)):
    print 'processing file number %s' %ifile
    IJ.open(os.path.join(fileDir,fileList[ifile]))
    #IJ.run(tmp,"Make Binary","")
    IJ.getImage()
    IJ.run("Skeletonize (2D/3D)")
    IJ.save(os.path.join(fileDir,fileList[ifile]))