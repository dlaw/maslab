"""
to compile, run:
	cython blobs.pyx
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing \
	      -o blobs.so -I/usr/include/python2.7 \
	     -I/usr/lib/python2.7/site-packages/numpy/core/include/ \
	     -I/usr/local/lib/python2.7/dist-packages/numpy/core/include/ \
         blobs.c
"""

import numpy as np
cimport cython, numpy as np
DTYPE = np.int32
ctypedef np.int32_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
def find_blobs(np.ndarray[DTYPE_t, ndim=2] arr not None, 
               np.ndarray[unsigned short, ndim=2] depth not None,
               int min_size, int color):
    assert arr.dtype == DTYPE
    cdef DTYPE_t size
    cdef int r, c, maxr = arr.shape[0], maxc = arr.shape[1]
    cdef list blobs = []
    cdef dict blob_data
    cdef np.ndarray[np.uint8_t, ndim=2] vis = np.zeros_like(arr, dtype=np.uint8)
    for r in range(maxr):
        for c in range(maxc):
            if not vis[r,c] and arr[r,c] == color:
                blob_data = flood_fill(arr, vis, depth, r, c, arr[r,c])
                if blob_data['size'] >= min_size:
                    blobs.append(blob_data)
    return blobs

@cython.boundscheck(False)
@cython.wraparound(False)
def flood_fill(np.ndarray[DTYPE_t, ndim=2] arr not None,
               np.ndarray[np.uint8_t, ndim=2] vis not None,
               np.ndarray[unsigned short, ndim=2] depth not None,
               int r, int c, DTYPE_t color):
    cdef int dr, dc, nr, nc, maxr = arr.shape[0], maxc = arr.shape[1]
    cdef list to_visit = [(r,c)]
    cdef DTYPE_t size = 1
    cdef tuple r_data = make_data_tuple(<float>r)
    cdef tuple c_data = make_data_tuple(<float>c)
    cdef tuple d_data = make_data_tuple(depth[r,c])
    vis[r,c] = 1
    while to_visit:
        r,c = to_visit.pop()
        for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,1),
                       (1,1), (1,0), (1,-1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if nr>=0 and nr<maxr and nc>=0 and nc<maxc and not vis[nr,nc] and arr[nr,nc] == color:
                to_visit.append((nr,nc))
                vis[nr,nc] = 1
                size = size + 1
                r_data = update_data_tuple(r_data, <float>nr, size)
                c_data = update_data_tuple(c_data, <float>nc, size)
                if depth[nr,nc] != 2047:
                    d_data = update_data_tuple(d_data, depth[nr,nc], size)
    return {'size': size,
            'color': color,
            'row': get_data(r_data, size),
            'col': get_data(c_data, size),
            'depth': get_data(d_data, size)}

# tuple of (sum, M_k, S_k)
cdef inline tuple make_data_tuple(float x): return (x, x, <float>0.)
# from http://www.johndcook.com/standard_deviation.html
cdef inline tuple update_data_tuple(tuple data, float x, DTYPE_t size):
    return (data[0]+x,
            data[1]+(x-data[1])/size,
            data[2]+(x-data[1])*(x-data[1]-(x-data[1])/size))
# tuple of (average/mean, variance)
cdef inline tuple get_data(tuple data, DTYPE_t size):
    return (data[0]/size,
            data[2]/(size-1) if size>1 else 0.0)

