import numpy as np
import cv

def depth_to_dtype(depth):
    lookup = {
        cv.IPL_DEPTH_8U: 'uint8',
        cv.IPL_DEPTH_8S: 'int8',
        cv.IPL_DEPTH_16U: 'uint16',
        cv.IPL_DEPTH_16S: 'int16',
        cv.IPL_DEPTH_32S: 'int32',
        cv.IPL_DEPTH_32F: 'float32',
        cv.IPL_DEPTH_64F: 'float64',
    }
    return lookup[depth]

def dtype_to_depth(dtype):
    lookup = {
        'uint8':   cv.IPL_DEPTH_8U,
        'int8':    cv.IPL_DEPTH_8S,
        'uint16':  cv.IPL_DEPTH_16U,
        'int16':   cv.IPL_DEPTH_16S,
        'int32':   cv.IPL_DEPTH_32S,
        'float32': cv.IPL_DEPTH_32F,
        'float64': cv.IPL_DEPTH_64F,
    }
    return lookup[str(dtype)]

def img_to_arr(im):
    arr = np.fromstring(
             im.tostring(),
             dtype = depth_to_dtype(im.depth),
             count = im.width * im.height * im.nChannels
          )
    arr.shape = (im.height, im.width, im.nChannels)
    return arr

def arr_to_img(arr):
    try:
        nChannels = arr.shape[2]
    except:
        nChannels = 1
    im = cv.CreateImageHeader(
            (arr.shape[1], arr.shape[0]),
            dtype_to_depth(arr.dtype),
            nChannels
         )
    cv.SetData(
       im,
       arr.tostring(),
       arr.dtype.itemsize * nChannels * arr.shape[1]
    )
    return im

def arr_to_blank_img(arr):
    try:
        nChannels = arr.shape[2]
    except:
        nChannels = 1
    im = cv.CreateImage(
            (arr.shape[1], arr.shape[0]),
            dtype_to_depth(arr.dtype),
            nChannels
         )
    return im

def arr_rgb_to_hsv(rgb_arr):
    rgb_im = arr_to_img(rgb_arr)
    hsv_im = arr_to_blank_img(rgb_arr)
    cv.CvtColor(rgb_im, hsv_im, cv.CV_RGB2HSV)
    hsv_arr = img_to_arr(hsv_im)
    return hsv_arr

def arr_hsv_to_rgb(hsv_arr):
    hsv_im = arr_to_img(hsv_arr)
    rgb_im = arr_to_blank_img(hsv_arr)
    cv.CvtColor(hsv_im, rgb_im, cv.CV_HSV2RGB)
    rgb_arr = img_to_arr(rgb_im)
    return rgb_arr

"""
def arr_bgr_to_hsv(arr):
    arr = arr / 255.0
    arr = np.apply_along_axis(lambda (b,g,r): colorsys.rgb_to_hsv(r, g, b), 2, arr)
    arr = arr * np.array([180, 255, 255])
    return arr.astype(np.uint8)

def arr_hsv_to_bgr(arr):
    arr = arr / np.array([180.0, 255.0, 255.0])
    arr = np.apply_along_axis(lambda (h,s,v): colorsys.hsv_to_rgb(h, s, v), 2, arr)
    arr = arr[:,:,::-1] * 255
    return arr.astype(np.uint8)
"""

