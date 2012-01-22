import time, arduino, kinect, random

# Bounce around the field.  For now, just turn around.  Eventually follow walls.
class FieldBounce:
    def __init__(self, min_time = 0):
        self.direction = random.choice([[.4, -.4], [-.4, .4]])
        self.min_stop_time = time.time() + min_time
    def next(self):
        arduino.set_speeds(*self.direction)
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
    def next(self):
        if not kinect.balls:
            return FieldBounce()
        ball = max(kinect.balls, key = lambda ball: ball['size'])
        offset = self.kp * (ball['col'][0] - 80)
        arduino.set_speeds(.8 + offset - abs(offset),
                           .8 - offset - abs(offset))
        if ball['row'][0] > 90:
            return BallSnarf()
        else:
            return self

# Drive forward after losing sight of a ball
class BallSnarf:
    def __init__(self):
        self.stop_time = time.time() + .8
    def next(self):
        if time.time() > self.stop_time:
            arduino.set_speeds(0, 0)
            return FieldBounce()
        else:
            arduino.set_speeds(.7, .7)
            return self

class WallHumper:
    def __init__(self, successor=FieldBounce):
        self.successor = successor
    def next(self):
        # do IR feedback
        pass

class DumpBalls:
    # get real friendly with a yellow wall
    pass
