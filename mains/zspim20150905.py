__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *


b = brain.Brain('/data/norlin/zSPIM/Apoptosis/050915/2015-09-05_16.55.58',
                    dimc=1,
                    times=range(400),
                    baseDataDir='/data/norlin/zSPIM/Apoptosis/050915',
                    fileNameFormat="Cam_Right_%05d.h5"
                    )

descriptors.RawChannel(b,2,'Data0',hierarchy='Data',relRawDataDir='Stack_2_Channel_0')
descriptors.RawChannel(b,2,'Data1',hierarchy='Data',relRawDataDir='Stack_2_Channel_1')
descriptors.RawChannel(b,2,'Data2',hierarchy='Data',relRawDataDir='Stack_2_Channel_2')
descriptors.RawChannel(b,2,'Data3',hierarchy='Data',relRawDataDir='Stack_2_Channel_3')