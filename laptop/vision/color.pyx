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
cimport cython, numpy as np

#cython: boundscheck=False
#cython: wraparound=False

def identify(np.ndarray[np.uint8_t, ndim=3] image,
             np.ndarray[np.int32_t, ndim=2] colors,
             np.ndarray[np.int32_t, ndim=2] result):
    """
    targets = [[target_hue, hue_c, target_sat, sat_c, target_val, val_c], ...]
    (each row represents one color, highest priority colors first)
    
    A pixel matches a color if, in HSV space, the distance between
    (hue / hue_c, sat / sat_c, val / val_c) and
    (target_hue / hue_c, target_sat / sat_c, target_val / val_c)
    is less than one.

    For each pixel, this function populates result with the index
    of the highest priority color matched, or -1 if none were matched.
    result.shape = image.shape[:-1]
    """
    cdef int i, x, y, num_colors = len(colors)
    cdef double hue, sat, val,
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            result[x, y] = -1
            for i in range(num_colors):
                hue = ((image[x, y, 0] - colors[i, 0] + 90) % 180) - 90
                sat = (image[x, y, 1] - colors[i, 2])
                val = (image[x, y, 2] - colors[i, 4])
                hue /= colors[i, 1]
                sat /= colors[i, 3]
                val /= colors[i, 5]
                if (hue * hue + sat * sat + val * val) < 1:
                    result[x, y] = i
                    break
