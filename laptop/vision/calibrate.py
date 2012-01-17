#!/usr/bin/python2.7

import cv, numpy as np, color, blobs, kinect, walls

maxv = {'target_hue': 180,
        'hue_c': 50,
        'sat_c': 400,
        'val_c': 400,
        'min_area': 300,
        'wall_target_hue': 180,
        'wall_hue_c': 50,
        'wall_sat_c': 400,
        'wall_val_c': 400,
        'wall_pixel_height': 15}
const = {'target_hue': 175,
         'hue_c': 15,
         'sat_c': 150,
         'val_c': 200,
         'min_area': 100,
         'wall_target_hue': 114,
         'wall_hue_c': 15,
         'wall_sat_c': 150,
         'wall_val_c': 200,
         'wall_pixel_height': 4}

def updater(name):
    def update(value):
        const[name] = value
    return update

def show_video():
    t, image, depth = kinect.get_images()
    colors = np.array([[const['target_hue'], 1./const['hue_c'],
                        255, 1./const['sat_c'],
                        255, 1./const['val_c']],
                       [const['wall_target_hue'], 1./const['wall_hue_c'],
                        255,  1./const['wall_sat_c'],
                        255, 1./const['wall_val_c']],
                       [0, 0,
                        0, .01,
                        0, .01], 'float64')
    result = color.identify(image, colors)
    # wall = walls.filter_by_column(result, 1, const['wall_pixel_height'], -1)
    top, bottom, c = walls.identify(result, 1, [2])
    cv.CvtColor(cv.fromarray(image), cv.fromarray(image), cv.CV_HSV2BGR)
    image /= 2
    blob_data = blobs.find_blobs(result, depth, const['min_area'])
    for blob in blob_data:
        cv.Circle(cv.fromarray(image), (int(blob['col'][0]), int(blob['row'][0])),
                  int((blob['size'] / 3.14)**0.5), [255, 255, 255])
    for i in range(image.shape[1]):
        if top[i] != -1:
            cv.Line(cv.fromarray(image), (i, top[i]), (i, bottom[i]), [255,255,255])
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

