"""
to compile, run:
	cython blobs.pyx
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing \
	      -o blobs.so -I/usr/include/python2.7 \
	     -I/usr/lib/python2.7/site-packages/numpy/core/include/ \
	     blobs.c
"""

import numpy as np
cimport numpy as np
cimport cython
DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

@cython.boundscheck(False)
def find_blobs(np.ndarray[DTYPE_t, ndim=2] arr not None, np.ndarray[float, ndim=2] depth not None, int min_size, int max_size):
    assert arr.dtype == DTYPE
    cdef DTYPE_t next_color = 1
    cdef int maxr = arr.shape[0]
    cdef int maxc = arr.shape[1]
    cdef int r, c
    cdef DTYPE_t size, sum_r, sum_c
    cdef float sum_d, avg_r, avg_c, avg_d, var_d, var_d2
    cdef list blobs = []
    for r in range(maxr):
        for c in range(maxc):
            if arr[r,c] == 1:
                next_color = next_color + 1
                size, sum_r, sum_c, sum_d, var_d = flood_fill(arr, depth, r, c, next_color)
                if size>=min_size and size<=max_size:
                    avg_r = 1.0*sum_r/size
                    avg_c = 1.0*sum_c/size
                    avg_d = 1.0*sum_d/size
                    blobs.append((next_color, size, avg_r, avg_c, avg_d, var_d))
    return blobs

@cython.boundscheck(False)
def flood_fill(np.ndarray[DTYPE_t, ndim=2] arr not None, np.ndarray[float, ndim=2] depth not None, int r, int c, DTYPE_t color):
    cdef int maxr = arr.shape[0]
    cdef int maxc = arr.shape[1]
    cdef int dr, dc, nr, nc
    cdef list to_visit
    cdef DTYPE_t size = 1
    cdef DTYPE_t sum_r = r
    cdef DTYPE_t sum_c = c
    cdef float sum_d = depth[r,c]
    cdef float var_d_m = depth[r,c]
    cdef float var_d_s = 0
    cdef float var_d_oldm
    arr[r,c] = color
    to_visit = [(r,c)]
    while to_visit:
        r,c = to_visit.pop()
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr==0 and dc==0:
                    continue
                nr = r+dr
                nc = c+dc
                if nr>=0 and nr<maxr and nc>=0 and nc<maxc and arr[nr,nc]==1:
                    arr[nr,nc] = color
                    to_visit.append((nr,nc))
                    size = size + 1
                    sum_r = sum_r + nr
                    sum_c = sum_c + nc
                    sum_d = sum_d + depth[nr,nc]
                    # from http://www.johndcook.com/standard_deviation.html
                    var_d_oldm = var_d_m
                    var_d_m = var_d_oldm + (depth[nr,nc] - var_d_oldm) / size
                    var_d_s = var_d_s + (depth[nr,nc] - var_d_oldm)*(depth[nr,nc] - var_d_m)
    return (size, sum_r, sum_c, sum_d, var_d_s/(size-1) if size>1 else 0.0)

