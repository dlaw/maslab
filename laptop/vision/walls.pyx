import numpy as np
cimport cython, numpy as np

#cython: boundscheck=False
#cython: wraparound=False

def filter_by_column(np.ndarray[np.int32_t, ndim=2] img, int marker_color,
                     int marker_width, int direction):
    """
    Scan through img one column at a time, where img is the result of
    running color.select.  Discard all of color marker_color, until
    you see marker_width pixels of marker_color in a row. After that,
    discard all pixels (meaning set them to -1). If direction=1,
    scan starting at row 0; if direction=-1, scan the other way.
    """

    cdef int i, j, count
    cdef np.ndarray[np.uint16_t, ndim=1] markers = np.empty(img.shape[1],
                                                            dtype=np.uint16)
    for j in range(img.shape[1]):
        count = 0
        for i in range(img.shape[0])[::direction]:
            if img[i,j] == marker_color:
                count = count+1
                img[i,j] = -1
                if count == marker_width:
                    break
            else:
                count = 0
        markers[j] = i
        for i in range(img.shape[0])[i::direction]:
            img[i,j] = -1
    return markers
