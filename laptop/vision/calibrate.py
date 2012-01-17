#!/usr/bin/python2.7

import cv, numpy as np, color, blobs, kinect, walls

color_defs = {'red': (175, 15, 150, 250),
              'yellow': (30, 15, 150, 250),
              'green': (60, 15, 150, 250),
              'blue': (114, 15, 150, 250)}
maxv = {}
const = {}
for c in color_defs:
    maxv[c + '_hue'] = 180
    const[c + '_hue'] = color_defs[c][0]
    maxv[c + '_hue_c'] = 100
    const[c + '_hue_c'] = color_defs[c][1]
    maxv[c + '_sat_c'] = 400
    const[c + '_sat_c'] = color_defs[c][2]
    maxv[c + '_val_c'] = 400
    const[c + '_val_c'] = color_defs[c][3]

def updater(name):
    def update(value):
        const[name] = value
    return update

def show_video():
    t, image, depth = kinect.get_images()
    colors = np.array([[const['red_hue'], 1./const['red_hue_c'],
                        255, 1./const['red_sat_c'],
                        255, 1./const['red_val_c']],
                       [const['yellow_hue'], 1./const['yellow_hue_c'],
                        255, 1./const['yellow_sat_c'],
                        255, 1./const['yellow_val_c']],
                       [const['green_hue'], 1./const['green_hue_c'],
                        255, 1./const['green_sat_c'],
                        255, 1./const['green_val_c']],
                       [const['blue_hue'], 1./const['blue_hue_c'],
                        255, 1./const['blue_sat_c'],
                        255, 1./const['blue_val_c']]], 'float64')
    result = color.identify(image, colors)
    top, bottom, wallcolor = walls.identify(result, 3)
    blob_data = blobs.find_blobs(result, depth, 10, 0)
    image[...,0] = np.select([result==-1,result==0,result==1,result==2,result==3],
                             [image[...,0], const['red_hue'], const['yellow_hue'],
                              const['green_hue'], const['blue_hue']])
    image[...,1] = np.where(result==-1, image[...,1], 255)
    image[...,2] = np.where(result==-1, image[...,2] / 2, 255)
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_HSV2BGR)
    for blob in blob_data:
        cv.Circle(cv.fromarray(image), (int(blob['col'][0]), int(blob['row'][0])),
                  int((blob['size'] / 3.14)**0.5), [255, 255, 255])
    cv.ShowImage('Video', cv.fromarray(image))
    cv.ShowImage('Depth', cv.fromarray(depth << 5))
        
cv.NamedWindow('Video', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Depth', cv.CV_WINDOW_NORMAL)
cv.NamedWindow('Constants')
for c in const:
    cv.CreateTrackbar(c, 'Constants', const[c], maxv[c], updater(c))

if __name__ == '__main__':
    while True:
        show_video()
        if cv.WaitKey(10) == 27:
            break

