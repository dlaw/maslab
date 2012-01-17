import numpy as np
cimport cython, numpy as np

@cython.boundscheck(False)
@cython.wraparound(False)
def identify(np.ndarray[np.int32_t, ndim=2] img,
             top_color, min_height = 4, max_skip = 2, start_offset = 60):
    cdef np.ndarray[np.int32_t] top = np.empty(img.shape[1], np.int32)
    cdef np.ndarray[np.int32_t] bottom = np.empty(img.shape[1], np.int32)
    cdef np.ndarray[np.int32_t] color = np.empty(img.shape[1], np.int32)
    cdef int good_count, skip_count, start_mark, end_mark, col, row
    for col in range(img.shape[1]):
        good_count = skip_count = 0
        for row in range(img.shape[0] - 1 - start_offset, -1, -1): # scan up to top of blue
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
                        bottom[col] = start_mark
                        top[col] = row + skip_count
                        break
        else: # can't ID wall in this column
            if good_count != 0:
                bottom[col] = start_mark
                top[col] = skip_count
            else:
                top[col] = bottom[col] = color[col] = -1
                continue
        color[col] = -1
        good_count = 0
        for row in range(start_mark, img.shape[0]): # scan down to bottom of wall
            if color[col] == img[row, col]:
                good_count += 1
                if good_count == min_height:
                    break
            else:
                good_count = 0
                color[col] = img[row, col]
        else:
            color[col] = -1
    return top, bottom, color

