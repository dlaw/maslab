import time, arduino, kinect, random, numpy as np

class State:
    def finish(self):
        pass
    def __repr__(self):
        return "{0}".format(self.__class__)

want_dump = False

# Bounce around the field.  For now, just turn around.  Eventually drive around walls.
class FieldBounce(State):
    timeout = random.choice(np.linspace(4, 6, 5))
    def __init__(self, min_time = 1):
        self.turn = random.choice([-.5, .5])
        self.min_stop_time = time.time() + min_time
    def next(self):
        if max(arduino.get_ir()) > .75:
            arduino.drive(-.8, 0)
            self.min_stop_time = max(self.min_stop_time, time.time() + 1)
            return self
        arduino.drive(0, self.turn)
        if want_dump and kinect.yellow_walls:
            return WallFollow()
        if kinect.balls and time.time() > self.min_stop_time:
            return BallCenter()
        return self
    def __repr__(self):
        return "{0} with turn {1} and stopping in no sooner than {2} seconds".format(self.__class__, self.turn, time.time()-self.min_stop_time)

class Reverse(State):
    timeout = None
    def __init__(self, duration=1.1):
        self.stop_time = time.time() + duration
    def next(self):
        if time.time() > self.stop_time:
            return FieldBounce()
        arduino.drive(-.8, 0)
        return self

# no ball found, so try to drive
class Explore(State):
    timeout = 13
    turn = time.time()
    def next(self):
        if max(arduino.get_ir()) > .8:
            self.turn = time.time() + .7
        if time.time() < self.turn:
            arduino.drive(0, -.5)
        else:
            arduino.drive(.8, 0)
        return self

# After sighting a ball, wait .3 seconds before driving to it (because of motor slew limits)
class BallCenter(State):
    def __init__(self):
        self.stop_time = time.time() + .3
        self.timeout = .5
    def next(self):
        arduino.drive(0, 0)
        if time.time() > self.stop_time:
            return BallFollow()
        else:
            return self

# Visual servo to a ball
class BallFollow(State):
    kp = .003
    def __init__(self, timeout=10):
        self.timeout = timeout
    def next(self):
        if not kinect.balls:
            return Reverse()
        if max(arduino.get_ir()) > .75:
            return WallHumper(successor=BallSnarf)
        ball = max(kinect.balls, key = lambda ball: ball['size'])
        offset = self.kp * (ball['col'][0] - 80)
        arduino.drive(max(0, .8 - abs(offset)), offset)
        # slow down if you need to turn more, but never go backwards
        if ball['row'][0] > 80:
            return BallSnarf()
        else:
            return self
    def __repr__(self):
        return "{0}".format(self.__class__)

# Visual servo to a wall
class WallFollow(State):
    kp = .003
    def __init__(self, timeout=10):
        self.timeout = timeout
    def next(self):
        if not kinect.yellow_walls:
            return Reverse()
        if max(arduino.get_ir()) > .75:
            return WallHumper(successor=DumpBalls)
        wall = max(kinect.yellow_walls, key = lambda w: w['size'])
        offset = self.kp * (wall['col'][0] - 80)
        arduino.drive(max(0, .8 - abs(offset)), offset)
        # slow down if you need to turn more, but never go backwards
        return self
    def __repr__(self):
        return "{0}".format(self.__class__)

# Drive forward after losing sight of a ball
class BallSnarf(State):
    def __init__(self):
        self.timeout = 2
    def next(self):
        arduino.set_sucker(True)
        arduino.drive(.7 if max(arduino.get_ir()) < .95 else 0, 0)
        return self

# Use the front IRs to nose in to a wall
class WallHumper(State):
    kp = 1
    def __init__(self, successor=Reverse, ir_stop=.95):
        self.successor = successor
        self.ir_stop = ir_stop
        self.timeout = 10
    def next(self):
        left_ir, right_ir = arduino.get_ir()
        if min(left_ir, right_ir) > self.ir_stop:
            arduino.drive(0, 0)
            return self.successor()
        elif abs(left_ir - right_ir) > .1:
            arduino.drive(.2, self.kp * (right_ir - left_ir))
            return self
        else:
            arduino.drive(.5, 0)
            return self

# dump balls, assuming we're already lined up to the wall
class DumpBalls:
    def __init__(self):
        self.stop_time = time.time() + 10
        arduino.drive(0, 0)
        arduino.set_door(True)
        self.timeout = 20
    def next(self):
        if time.time() > self.stop_time:
            arduino.set_door(False)
            return Reverse()
        return self
    def finish(self):
        arduino.set_door(False)

