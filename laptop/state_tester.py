#!/usr/bin/python2.7

import signal, time, arduino, kinect, navigation, maneuvering, constants
from main import State

time.sleep(1) # wait for arduino and kinect to power up

want_change = False

def run():
    global want_change
    print("starting state_tester.py")
    state = navigation.LookAround()
    arduino.set_helix(True)
    arduino.set_sucker(True)
    fake_time_left = 180
    while True:
        if want_change:
            want_change = False
            arduino.drive(0, 0)
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
            if new_state is not None: # if the state has changed
                state = new_state
                print("{0} with {1} seconds to go".format(state, fake_time_left))
        except Exception, ex:
            print("{0} while attempting to change states".format(ex))

def change_state(*args):
    global want_change
    want_change = True

signal.signal(signal.SIGINT, change_state)

if __name__ == '__main__': # called from the command line
    run()

