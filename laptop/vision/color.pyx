"""
to compile, run:
    cython color.pyx
    gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing \
          -o color.so -I/usr/include/python2.7 \
         -I/usr/lib/python2.7/site-packages/numpy/core/include/ \
         -I/usr/local/lib/python2.7/dist-packages/numpy/core/include/ \
         color.c
"""

import numpy as np
cimport numpy as np
cimport cython
DTYPE = np.uint8
ctypedef np.uint8_t DTYPE_t

@cython.boundscheck(False)
def select(np.ndarray[DTYPE_t, ndim=3] hsv not None, list targets not None, list scalers not None):
    """
    targets = [target_hue, target_sat, target_val]
    scalers = [hue_c, sat_c, val_c]
    
    Returns points in hsv for which the distance between
    (hue / hue_c, sat / sat_c, val / val_c) and
    (target_hue / hue_c, target_sat / sat_c, target_val / val_c)
    is less than one.
    """
    assert hsv.dtype == DTYPE
    cdef np.ndarray[DTYPE_t, ndim=2] arr = np.empty_like(hsv[...,0])
    cdef float hue, sat, val
    cdef float target0=targets[0]
    cdef float target1=targets[1]
    cdef float target2=targets[2]
    cdef float scaler0=scalers[0]
    cdef float scaler1=scalers[1]
    cdef float scaler2=scalers[2]
    
    for i in range(hsv.shape[0]):
        for j in range(hsv.shape[1]):
            hue = (((<float>hsv[i,j,0] - target0 + 90) % 180) - 90) / scaler0
            sat = (<float>hsv[i,j,1] - target1) / scaler1
            val = (<float>hsv[i,j,2] - target2) / scaler2
            arr[i,j] = (hue*hue + sat*sat + val*val) < 1
    return arr

