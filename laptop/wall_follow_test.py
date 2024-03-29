#!/usr/bin/python2.7

import signal, time, arduino, kinect, navigation, maneuvering, sys, traceback, constants, main, random, numpy as np

time.sleep(1) # wait for arduino and kinect to power up

want_change = True

class FollowWallTest(main.State): # PDD controller
    last_p, last_d = None, None
    turning_away = False
    timeout = random.uniform(.5, 1) * constants.follow_wall_timeout
    def __init__(self):
        self.time_last_unstuck = time.time()
        self.time_wall_seen = time.time()
        self.time_wall_absent = 0
    """
    def on_stuck(self):
        if ((time.time() - self.time_last_unstuck > constants.wall_stuck_timeout)
            or any(arduino.get_bump()) or arduino.get_ir()[0] > 1):
            return maneuvering.Unstick()
        return self.follow()
    """
    def next(self, time_left):
        return self.default_action()
    def default_action(self):
        self.time_last_unstuck = time.time()
        return self.follow()
    def follow(self):
        side_ir = arduino.get_ir()[3] # hard-coded to follow on right
        p = constants.wall_follow_dist - side_ir
        d = (p - self.last_p) if self.last_p else 0
        dd = (d - self.last_d) if self.last_d else 0
        self.last_p, self.last_d = p, d
        if time.time() - self.time_wall_seen > constants.lost_wall_timeout:
            return navigation.LookAround()
        elif ((max(arduino.get_ir()[1:-1]) > constants.wall_follow_limit
               and (time.time() - self.time_wall_absent) > constants.lost_wall_timeout)
               or self.turning_away): # too close in front
            self.turning_away = True
            self.time_wall_seen = time.time()
            drive = 0
            turn = constants.wall_follow_turn * -1
            arduino.drive(drive, turn)
            #print("A {d: 4.2f} {t: 4.2f} {ir: 4.2f}".format(d=drive, t=turn, ir=side_ir))
            if (max(arduino.get_ir()[1:-1]) < constants.wall_follow_limit and
                side_ir > constants.wall_follow_limit):
                self.turning_away = False
        elif side_ir > constants.wall_follow_limit: # if we see a wall
            self.time_wall_seen = time.time()
            drive = constants.wall_follow_drive
            turn = (constants.wall_follow_kp * p +
                    constants.wall_follow_kd * d +
                    constants.wall_follow_kdd * dd)
            arduino.drive(drive, turn)
            #print("B {d: 4.2f} {t: 4.2f} {ir: 4.2f}".format(d=drive, t=turn, ir=side_ir))
        else: # lost wall but not timed out, so turn into the wall
            self.time_wall_absent = time.time()
            drive = 0
            turn = constants.wall_follow_turn
            arduino.drive(drive, turn)
            #print("C {d: 4.2f} {t: 4.2f} {ir: 4.2f}".format(d=drive, t=turn, ir=side_ir))

def run():
    global want_change
    print("starting wall_follow_test.py")
    state = FollowWallTest()
    fake_time_left = 180
    while True:
        if want_change:
            want_change = False
            arduino.drive(0, 0)
            print "Enter kp, kd, and kdd, separated by spaces"
            s = raw_input("> ")
            if s == "":
                exit()
            s = s.split(" ")
            constants.wall_follow_kp = float(s[0])
            constants.wall_follow_kd = float(s[1])
            constants.wall_follow_kdd = float(s[2])
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

