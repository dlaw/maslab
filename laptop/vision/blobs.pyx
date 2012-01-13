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
    cdef DTYPE_t size
    cdef list blobs = []
    cdef tuple blob_data
    for r in range(maxr):
        for c in range(maxc):
            if arr[r,c] == 1:
                next_color = next_color + 1
                blob_data = flood_fill(arr, depth, r, c, next_color)
                size = blob_data[0]
                if size>=min_size and size<=max_size:
                    blobs.append(blob_data)
    return blobs

@cython.boundscheck(False)
def flood_fill(np.ndarray[DTYPE_t, ndim=2] arr not None, np.ndarray[float, ndim=2] depth not None, int r, int c, DTYPE_t color):
    cdef int maxr = arr.shape[0]
    cdef int maxc = arr.shape[1]
    cdef int dr, dc, nr, nc
    cdef list to_visit
    cdef DTYPE_t size = 1
    cdef tuple r_data = make_data_tuple(<float>r)
    cdef tuple c_data = make_data_tuple(<float>c)
    cdef tuple d_data = make_data_tuple(depth[r,c])
    
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
                    r_data = update_data_tuple(r_data, <float>nr, size)
                    c_data = update_data_tuple(c_data, <float>nc, size)
                    d_data = update_data_tuple(d_data, depth[nr,nc], size)
    return (size, color, get_data(r_data, size), get_data(c_data, size), get_data(d_data, size))

# tuple of (sum, M_k, S_k)
cdef inline tuple make_data_tuple(float x): return (x, x, <float>0.)
# from http://www.johndcook.com/standard_deviation.html
cdef inline tuple update_data_tuple(tuple data, float x, DTYPE_t size):
    return (
            data[0]+x,
            data[1]+(x-data[1])/size,
            data[2]+(x-data[1])*(x-data[1]-(x-data[1])/size)
           )
# tuple of (average/mean, variance)
cdef inline tuple get_data(tuple data, DTYPE_t size):
    return (
            data[0]/size,
            data[2]/(size-1) if size>1 else 0.0
           )

