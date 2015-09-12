__author__ = 'malbert'

import sys
sys.path = [sys.path[0]]+['..']+sys.path[1:]
from dependencies import *


b = brain.Brain('/data/norlin/zSPIM/Apoptosis/050915/2015-09-05_16.55.58',
                    dimc=1,
                    times=range(400),
                    baseDataDir='/data/norlin/zSPIM/Apoptosis/050915'
                    )
descriptors.RawChannel(b,2,'Data')