import numpy as np
import cv

def img_to_arr(im):
    arr = np.fromstring(
             im.tostring(),
             dtype = 'uint8',
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
            cv.IPL_DEPTH_8U,
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
            cv.IPL_DEPTH_8U,
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

