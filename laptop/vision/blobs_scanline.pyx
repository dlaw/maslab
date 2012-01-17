"""
to compile, run:
	cython blobs.pyx
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing \
	      -o blobs.so -I/usr/include/python2.7 \
	     -I/usr/lib/python2.7/site-packages/numpy/core/include/ \
	     -I/usr/local/lib/python2.7/dist-packages/numpy/core/include/ \
         blobs.c
"""

#cython: boundscheck=False
#cython: wraparound=False

import numpy as np
cimport cython, numpy as np
DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

cdef DTYPE_t size
cdef tuple r_data, c_data, d_data
cdef list ranges

def find_blobs(np.ndarray[DTYPE_t, ndim=2] arr not None, 
               np.ndarray[unsigned short, ndim=2] depth not None,
               int min_size):
    assert arr.dtype == DTYPE
    cdef DTYPE_t size
    cdef int r, c, maxr = arr.shape[0], maxc = arr.shape[1]
    cdef list blobs = []
    cdef dict blob_data
    cdef np.ndarray[np.uint8_t, ndim=2] vis = np.zeros_like(arr, dtype=np.uint8)
    for r in range(maxr):
        for c in range(maxc):
            if not vis[r,c] and arr[r,c] != 0xFF:
                blob_data = flood_fill(arr, vis, depth, r, c, arr[r,c])
                if blob_data['size'] >= min_size:
                    blobs.append(blob_data)
    return blobs

def flood_fill(np.ndarray[DTYPE_t, ndim=2] arr not None,
               np.ndarray[np.uint8_t, ndim=2] vis not None,
               np.ndarray[unsigned short, ndim=2] depth not None,
               int r, int c, DTYPE_t color):
    
    global size, r_data, c_data, d_data, ranges
    
    cdef int cur_r, min_c, max_c, orig_min_c, orig_max_c
    cdef char down, up, extend_left, extend_right
    cdef int last_r = arr.shape[0]-1, last_c = arr.shape[1]-1
    
    vis[r,c] = 1
    size = 1
    r_data = make_data_tuple(<float>r)
    c_data = make_data_tuple(<float>c)
    d_data = make_data_tuple(depth[r,c])
    ranges = [(r, c, c, False, False, True, True)]

    while ranges:
        cur_r, min_c, max_c, down, up, extend_left, extend_right = ranges.pop()
        orig_min_c, orig_max_c = min_c, max_c
        if extend_left:
            while min_c > 0 and not vis[cur_r, min_c-1] and arr[cur_r, min_c-1] == color:
                min_c = min_c - 1
                visit(vis, depth, cur_r, min_c)
        if extend_right:
            while max_c < last_c and not vis[cur_r, max_c+1] and arr[cur_r, max_c+1] == color:
                max_c = max_c + 1
                visit(vis, depth, cur_r, max_c)
        if min_c > 0:
            min_c = min_c - 1
        if max_c < last_c:
            max_c = max_c + 1

        if cur_r < last_r:
            add_next_line(vis, arr, depth, cur_r+1, not up, True, False,
                          min_c, max_c, orig_min_c, orig_max_c, color)
        if cur_r > 0:
            add_next_line(vis, arr, depth, cur_r-1, not down, False, True,
                          min_c, max_c, orig_min_c, orig_max_c, color)
    
    return {'size': size,
            'color': color,
            'row': get_data(r_data, size),
            'col': get_data(c_data, size),
            'depth': get_data(d_data, size)}

def visit(np.ndarray[np.uint8_t, ndim=2] vis not None,
          np.ndarray[unsigned short, ndim=2] depth not None,
          int r, int c):

    global size, r_data, c_data, d_data

    vis[r,c] = 1
    size = size+1
    r_data = update_data_tuple(r_data, <float>r, size)
    c_data = update_data_tuple(c_data, <float>c, size)
    if depth[r,c] != 0:
        d_data = update_data_tuple(d_data, <float>depth[r,c], size)

def add_next_line(np.ndarray[np.uint8_t, ndim=2] vis not None,
                  np.ndarray[DTYPE_t, ndim=2] arr not None,
                  np.ndarray[unsigned short, ndim=2] depth not None,
                  int new_r, char is_next, char down, char up,
                  int min_c, int max_c, int orig_min_c, int orig_max_c, DTYPE_t color):

   global ranges

   cdef char in_range, empty
   cdef int cur_c, cur_min_c

   cur_min_c = min_c
   in_range = False
   cur_c = min_c
   while cur_c <= max_c:
       empty = (is_next or (cur_c < orig_min_c or cur_c > orig_max_c)) and not vis[new_r, cur_c] and arr[new_r, cur_c] == color
       if not in_range and empty:
           cur_min_c = cur_c
           in_range = True
       elif in_range and not empty:
           ranges.append((new_r, cur_min_c, cur_c-1, down, up, cur_min_c==min_c, False))
           in_range = False
       if in_range:
           visit(vis, depth, new_r, cur_c)
       if not is_next and cur_c == orig_min_c:
           cur_c = orig_max_c
       cur_c = cur_c + 1
   if in_range:
       ranges.append((new_r, cur_min_c, cur_c-1, down, up, cur_min_c==min_c, True))

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

