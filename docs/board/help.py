#!/usr/bin/env python3 
# coding: utf_8
# checkpath.py

import sys
import math 
import numpy as np
import vector as vec 
import common as com 
import pilfont 
import pilimage 
import board 

##======
## メイン文
##======
name = None 
if __name__ == '__main__':
    if len(sys.argv) == 1:
        pass 
    elif len(sys.argv) == 2:
        name = sys.argv[1]
    else:
        com.panic('too few or many argments!'
              +f'usage: python3 { sys.argv[0] } [ imgfile.png ] ')

    # print(f'{pim.PilImage.__init__.__doc__}')
    help(name)
    
    sys.exit(0)



##EOF

