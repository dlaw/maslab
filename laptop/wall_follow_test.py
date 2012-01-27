#!/usr/bin/python2.7

import signal, time, arduino, kinect, navigation, maneuvering, sys, traceback, constants, main

time.sleep(1) # wait for arduino and kinect to power up

want_change = True

class FollowWallTest(main.State):
    timeout = constants.follow_wall_timeout # times out to LookAround
    def __init__(self):
        self.on_left = True
        self.ir = 0 if self.on_left else 3
        self.dir = -1 if self.on_left else 1 # sign of direction to turn into wall
        self.time_wall_seen = time.time()
        self.err = None
    def next(self, time_left):
        return self.default_action()
    def default_action(self):
        dist = arduino.get_ir()[self.ir]
        print("IR: {0:1.4}".format(dist))
        self.last_err, self.err = self.err, constants.wall_follow_dist - dist
        if self.last_err is None: self.last_err = self.err # initialize D to 0
        if max(arduino.get_ir()[1:-1]) > constants.wall_follow_dist: # too close in front
            print "A"
            self.time_wall_seen = time.time()
            drive = 0
            turn = constants.wall_follow_turn * -1 * self.dir
            print("drive: {0:1.4} {0:1.4}".format(float(drive), float(turn)))
            arduino.drive(drive, turn)
        elif dist > constants.wall_follow_limit: # if we see a wall
            print "B"
            self.time_wall_seen = time.time()
            drive = constants.drive_speed
            turn = self.dir * (constants.wall_follow_kp * self.err + constants.wall_follow_kd * (self.err - self.last_err))
            print("drive: {0:1.4} {0:1.4}".format(float(drive), float(turn)))
            arduino.drive(drive, turn)
        elif time.time() - self.time_wall_seen < constants.lost_wall_timeout:
            print "C"
            drive = constants.drive_speed / 3
            turn = constants.wall_follow_turn * self.dir
            print("drive: {0:1.4} {0:1.4}".format(float(drive), float(turn)))
            arduino.drive(drive, turn)
        else: # lost wall
            print "D"
            return navigation.LookAround()

def run():
    global want_change
    print("starting wall_follow_test.py")
    state = FollowWallTest()
    fake_time_left = 180
    while True:
        if want_change:
            want_change = False
            arduino.drive(0, 0)
            print "Enter kp and kd, separated by a space"
            s = raw_input("> ")
            if s == "":
                exit()
            s = s.split(" ")
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
        if not isinstance(state, FollowWallTest):
            print("Back to FollowWallTest")
            state = FollowWallTest()

def change_state(*args):
    global want_change
    want_change = True

signal.signal(signal.SIGINT, change_state)

if __name__ == '__main__': # called from the command line
    run()
