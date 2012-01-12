"""
to compile, run:
	cython flood_fill.pyx
	gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.7 -o flood_fill.so flood_fill.c
"""

import numpy as np
cimport numpy as np
cimport cython
DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

@cython.boundscheck(False)
def flood_fill(np.ndarray[DTYPE_t, ndim=2] arr not None):
    assert arr.dtype == DTYPE
    cdef DTYPE_t next_color = 1
    cdef int maxr = arr.shape[0]
    cdef int maxc = arr.shape[1]
    cdef int r, c
    for r in range(maxr):
        for c in range(maxc):
            if arr[r,c] == 1:
                next_color = next_color + 1
                flood_fill_one_blob(arr, r, c, next_color)
    return arr

@cython.boundscheck(False)
def flood_fill_one_blob(np.ndarray[DTYPE_t, ndim=2] arr not None, int r, int c, DTYPE_t color):
    cdef int maxr = arr.shape[0]
    cdef int maxc = arr.shape[1]
    cdef int dr, dc, nr, nc
    cdef list to_visit
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
