import numpy as np
cimport cython, numpy as np

def identify(np.ndarray[np.int32_t, ndim=2] img,
             top_color, wall_colors, min_height = 4, max_skip = 2):
    cdef np.ndarray[np.int32_t] top = np.empty(img.shape[1], np.int32)
    cdef np.ndarray[np.int32_t] bottom = np.empty(img.shape[1], np.int32)
    cdef np.ndarray[np.int32_t] color = np.empty(img.shape[1], np.int32)
    cdef int good_count, skip_count, start_mark, end_mark, col, row
    for col in range(img.shape[1]):
        good_count = skip_count = 0
        for row in range(img.shape[0] - 1, -1, -1): # scan up to top of blue
            if img[row, col] == top_color:
                skip_count = 0
                if good_count == 0:
                    start_mark = row
                good_count += 1
            else:
                skip_count += 1
                if skip_count == max_skip:
                    if good_count < min_height:
                        good_count = 0
                    else:
                        top[col] = row + 1
                        break
        else: # can't ID wall in this column
            top[col] = bottom[col] = color[col] = -1
            continue
        bottom[col] = img.shape[0] - 1
        color[col] = -1
        skip_count = 0
        for row in range(start_mark, img.shape[0]): # scan down to bottom of wall
            if img[row, col] in wall_colors:
                skip_count = 0
                color[col] = img[row, col]
            else:
                skip_count += 1
                if skip_count == max_skip:
                    bottom[col] = row - 1
                    break
    return top, bottom, color

@cython.boundscheck(False)
@cython.wraparound(False)
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
