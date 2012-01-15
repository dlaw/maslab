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
def select(np.ndarray[DTYPE_t, ndim=3] hsv not None, np.ndarray[np.uint8_t, ndim=2] targets not None, np.ndarray[np.uint16_t, ndim=2] scalers not None):
    """
    targets = [[target_hue, target_sat, target_val], ...]
    scalers = [[hue_c, sat_c, val_c], ...]
    (each row represents one color, highest priority colors first)
    
    A pixel matches a color if, in HSV space, the distance between
    (hue / hue_c, sat / sat_c, val / val_c) and
    (target_hue / hue_c, target_sat / sat_c, target_val / val_c)
    is less than one.

    This function returns an array where each pixel is the (1-based) index
    of the highest priority color matched, or 0 if none were matched.
    """
    assert hsv.dtype == DTYPE
    cdef np.ndarray[DTYPE_t, ndim=2] arr = np.empty_like(hsv[...,0])
    cdef float hue, sat, val
    assert targets.shape[0] == scalers.shape[0]
    cdef int num_colors = targets.shape[0]
    cdef int i, j, c

    for i in range(hsv.shape[0]):
        for j in range(hsv.shape[1]):
            arr[i,j] = 0
            for c in range(num_colors):
                hue = (((<float>hsv[i,j,0] - targets[c,0] + 90) % 180) - 90) / scalers[c,0]
                sat = (<float>hsv[i,j,1] - targets[c,1]) / scalers[c,1]
                val = (<float>hsv[i,j,2] - targets[c,2]) / scalers[c,2]
                if (hue*hue + sat*sat + val*val) < 1:
                    arr[i,j] = c+1
                    break
    return arr

@cython.boundscheck(False)
def filter_by_column(np.ndarray[DTYPE_t, ndim=2] img not None, int color_to_keep, int marker_color, int marker_width, int direction):
    """
    Scan through img one column at a time, where img is the result of running
    color.select. Keep all pixels of color color_to_keep and discard all of
    color marker_color, until you see marker_width pixels of marker_color in
    a row. After that, discard all pixels (meaning set them to 0). If
    direction=1, scan starting at row 0; if direction=-1, scan the other way.
    """

    cdef int i, j, count
    cdef np.ndarray[np.uint16_t, ndim=1] markers = np.empty((img.shape[1],), dtype=np.uint16)
    for j in range(img.shape[1]):
        count = 0
        for i in range(img.shape[0])[::direction]:
            if img[i,j] == marker_color:
                count = count+1
                img[i,j] = 0
                if count == marker_width:
                    break
            else:
                count = 0
        markers[j] = i
        for i in range(img.shape[0])[i::direction]:
            img[i,j] = 0
    return markers

