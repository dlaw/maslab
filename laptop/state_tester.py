#!/usr/bin/python2.7

import signal, time, arduino, kinect, navigation, maneuvering, sys, traceback, constants

time.sleep(1) # wait for arduino and kinect to power up

want_change = True

def run():
    global want_change
    print("starting state_tester.py")
    state = navigation.LookAround()
    arduino.set_helix(True)
    fake_time_left = 180
    while True:
        if want_change:
            want_change = False
            arduino.drive(0, 0)
            print "Enter a state constructor (with no spaces) and, optionally, a time left (separated by a space), or enter nothing to quit"
            s = raw_input("> ")
            if s == "":
                arduino.set_sucker(False)
                arduino.set_helix(False)
                exit()
            s = s.split(" ")
            """
            if len(s) > 1:
                fake_time_left = int(s[1])
            else:
                fake_time_left = 180
            new_state = None
            for class_name in ["navigation", "maneuvering"]:
                try:
                    new_state = eval(class_name + "." + s[0])
                    break
                except AttributeError:
                    continue
            if new_state is None:
                print("{0} was not found in any of the classes".format(s[0]))
            else:
                state = new_state
                print("State manually changed to {0}".format(state))
            """
            constants.wall_follow_kp = float(s[0])
            constants.wall_follow_kd = float(s[1])
        kinect.process_frame()
        try:
            new_state = state.next(fake_time_left)
            if new_state is not None: # if the state has changed
                state = new_state
                print("{0} with {1} seconds to go".format(state, fake_time_left))
        except Exception, ex:
            print("{0} while attempting to change states".format(ex))
            traceback.print_exc(file=sys.stdout)
        """
        if not isinstance(state, navigation.FollowWall):
            print("Back to FollowWall(on_left=False)")
            state = navigation.FollowWall(on_left=False)
        """

def change_state(*args):
    global want_change
    want_change = True

signal.signal(signal.SIGINT, change_state)

if __name__ == '__main__': # called from the command line
    run()

