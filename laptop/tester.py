#!/usr/bin/python2.7

import time, cv, numpy as np, arduino, kinect, states, signal

# wait for arduino and kinect to power up
time.sleep(1)

def handler(signum, frame):
    want_change = True
signal.signal(signal.SIGINT, handler)

state = states.LookAround()

arduino.set_helix(True)
arduino.set_sucker(True)

fake_time_left = 180

while True:
    if want_change:
        arduino.set_speeds(0, 0)
        print "Enter a state name and, optionally, a time left (separated by a space), or enter nothing to quit"
        s = raw_input("> ")
        if s == "":
            arduino.set_sucker(False)
            arduino.set_helix(False)
            exit()
        s = s.split(" ")
        if len(s) > 1:
            fake_time_left = int(s[1])
        else:
            fake_time_left = 180
        state = eval("states." + s[0] + "()")
        print("State manually changed to {0}".format(state))
    kinect.process_frame()
    try:
        new_state = state.next(fake_time_left)
        assert new_state is not None
    except Exception, e:
        print("{0} while attempting to change states".format(e))
        new_state = state
    if state != new_state:
        print("{0} with {1} seconds to go".format(new_state, fake_time_left))
        state = new_state

