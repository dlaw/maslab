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

@cython.boundscheck(False)
@cython.wraparound(False)
def identify(np.ndarray[np.uint8_t, ndim=3] image,
             np.ndarray[np.float64_t, ndim=2] constants):
    """
    targets = [[target_hue, target_sat, target_val, hue_c, sat_c, val_c], ...]
    (each row represents one color, highest priority colors first)
    
    A pixel matches a color if, in HSV space, the distance between
    (hue / hue_c, sat / sat_c, val / val_c) and
    (target_hue / hue_c, target_sat / sat_c, target_val / val_c)
    is less than one.

    For each pixel, this function populates result with the index
    of the highest priority color matched, or -1 if none were matched.
    result.shape = image.shape[:-1]
    """
    cdef int i, x, y, num_colors = len(constants)
    cdef np.ndarray[np.int32_t, ndim=2] colors = \
        np.empty_like(image[...,0], 'int32')
    cdef double hue, sat, val
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            colors[x, y] = -1
            for i in range(num_colors):
                hue = image[x, y, 0] - constants[i, 0]
                sat = image[x, y, 1] - constants[i, 1]
                val = image[x, y, 2] - constants[i, 2]
                if hue < -90: hue += 180
                elif hue > 90: hue -= 180
                hue *= constants[i, 3]
                sat *= constants[i, 4]
                val *= constants[i, 5]
                if (hue * hue + sat * sat + val * val) < 1.0:
                    print("set")
                    colors[x, y] = i
                    break
    return colors

@cython.boundscheck(False)
@cython.wraparound(False)
def colorize(np.ndarray[np.uint8_t, ndim=3] image,
             np.ndarray[np.float64_t, ndim=2] constants,
             np.ndarray[np.int32_t, ndim=2] colors):
    cdef int i, x, y
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            i = colors[x, y]
            if i == -1:
                image[x, y, 2] >>= 1
            else:
                image[x, y, 0] = <np.uint8_t> constants[i, 0]
                image[x, y, 1] = <np.uint8_t> constants[i, 1]
                image[x, y, 2] = <np.uint8_t> constants[i, 2]

                
