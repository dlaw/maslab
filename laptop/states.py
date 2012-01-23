import time, arduino, kinect, random

# Bounce around the field.  For now, just turn around.  Eventually drive around walls.
class FieldBounce:
    def __init__(self, min_time = .5, want_dump = False):
        left, right = arduino.get_ir()
        self.direction = [.4, -.4] if left > right else [-.4, .4]
        self.min_stop_time = time.time() + min_time
    def next(self):
        # TODO: check IRs to determine if we're on a wall and must back up
        arduino.set_speeds(*self.direction)
        if want_dump and kinect.yellow_walls:
            wall = max(kinect.yellow_walls, key = lambda wall: wall['size'])
            if wall['size'] > 100 #min size for something to be a wall
                return WallHumper(successor=DumpBalls)
            #known flaw: WallHumper won't work if the wall isn't straight-ish ahead
        if kinect.balls and time.time() > self.min_stop_time:
            return BallCenter()
        return self

# After sighting a ball, wait .3 seconds before driving to it (because of motor slew limits)
class BallCenter:
    def __init__(self):
        self.stop_time = time.time() + .3
    def next(self):
        arduino.set_speeds(0, 0)
        if time.time() > self.stop_time:
            return BallFollow()
        else:
            return self

# Visual servo to a ball
class BallFollow:
    kp = .004
    def __init__(self, timeout=10):
        self.stop_time = time.time() + timeout
    def next(self):
        if time.time() > self.stop_time or not kinect.balls:
            return FieldBounce()
        # TODO: if IRs trigger, drive up to the wall and then FieldBounce
        ball = max(kinect.balls, key = lambda ball: ball['size'])
        offset = self.kp * (ball['col'][0] - 80)
        arduino.drive(max(0, .8 - abs(offset)), offset)
        # slow down if you need to turn more, but never go backwards
        if ball['row'][0] > 80:
            return BallSnarf()
        else:
            return self

# Drive forward after losing sight of a ball
class BallSnarf:
    def __init__(self):
        self.stop_time = time.time() + 1
    def next(self):
        if time.time() < self.stop_time:
            arduino.set_sucker(True)
            arduino.set_speeds(.7, .7)
            return self
        else:
            arduino.set_sucker(False)
            arduino.set_speeds(0, 0)
            return FieldBounce()

# Use the front IRs to nose in to a wall
class WallHumper:
    def __init__(self, successor=FieldBounce, ir_stop=130):
        self.successor = successor
        self.ir_stop = ir_stop
    def next(self):
        left_ir, right_ir = arduino.get_ir()
        left = .4 if left_ir < self.ir_stop else 0
        right = .4 if right_ir < self.ir_stop else 0
        arduino.set_speeds(left, right)
        if left < self.ir_stop or right < self.ir_stop:
            return self
        else:
            return self.successor()

# dump balls, assuming we're already lined up to the wall
class DumpBalls:
    def __init__(self):
        self.stop_time = time.time() + 2
        arduino.set_door(True)
    def next(self):
        if time.time() > self.stop_time:
            arduino.set_door(False)
            return FieldBounce()
