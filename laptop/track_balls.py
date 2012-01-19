#!/usr/bin/python2.7

import arduino, freenect, cv, numpy as np, time, color, blobs, kinect

color_defs = [('red', 175, 1./15, 1./150, 1./250),
              ('yellow', 23, 1./10, 1./100, 1./140),
              ('green', 50, 1./15, 1./250, 1./350),
              ('blue', 114, 1./15, 1./400, 1./400)]

constants = np.vstack([[hue, 255., 255., hue_c, sat_c, val_c]
                       for name, hue, hue_c, sat_c, val_c in color_defs])

const = {'kinect_fov': np.pi/2,
         'depth_scaler': 0.001,
         'small_angle': 0.3,
         'after_losing_sight': 20,
         'drive_dist': 100}

cycles_since_lost_sight = 0
start_time = time.time()

time.sleep(.1)
assert arduino.is_alive()

def move():
    global cycles_since_lost_sight
    t, image, depth = kinect.get_images()
    colors = color.identify(image, constants)
    top, bottom, wallcolor = walls.identify(colors, 3, 3, 2)
    blob_data = blobs.find_blobs(colors, depth, 0)
    if not len(blob_data): #no blobs found
        cycles_since_lost_sight += 1
        if cycles_since_lost_sight >= const['after_losing_sight']:
            #arduino.rotate(2*np.pi)
            arduino.set_motors(.6, .6)
        else: #drive straight
            arduino.set_motors(.6, -.6)
    else: #track blob closest to center
        cycles_since_lost_sight = 0
        blob_to_track = min(blob_data, key = lambda blob: abs(80-blob['col'][0]))
        angle = const['kinect_fov'] / 160. * (80 - blob_to_track['col'][0])
        if abs(angle) < const['small_angle']: #move towards it
            dist = const['depth_scaler'] * blob_to_track['depth'][0]
            #arduino.drive(max(dist, 100), angle)
            arduino.set_motors(.6, -.6)
        else: #rotate only (don't drive)
            if angle > 0:
                arduino.set_motors(-.6, -.6)
            else:
                arduino.set_motors(.6, .6)

if __name__ == '__main__':
    while time.time() < start_time + 179:
        move()
    arduino.set_motors(0, 0)

