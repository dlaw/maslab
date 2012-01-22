#!/usr/bin/python2.7

import cv, numpy as np, kinect, time

def spin():
    for i in range(10):
        t = time.time()
        for i in range(20):
            kinect.process_frame()
        print(20 / (time.time() - t))

import cProfile
cProfile.run('spin()')
