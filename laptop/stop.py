#!/usr/bin/python2.7

import arduino, time

time.sleep(1)
arduino.drive(0, 0)
arduino.set_sucker(False)
arduino.set_helix(False)
arduino.set_door(False)
