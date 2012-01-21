import time, arduino, random

s = .8

# Bounce around the field.  For now, just turn around.            
class FieldBounce:
    def __init__(self):
        self.direction = random.choice([[.4, -.4], [-.4, .4]])
    def next(self, balls, yellow_walls, green_walls):
        arduino.set_speeds(*self.direction)
        if balls:
            return BallCenter()
        return self

class BallCenter:
    def __init__(self):
        self.stop_time = time.time() + 1
    def next(self, balls, yellow_walls, green_walls):
        arduino.set_speeds(0, 0)
        if time.time() > self.stop_time:
            return BallFollow()
        else:
            return self

class BallFollow:
    kp = .004
    def next(self, balls, yellow_walls, green_walls):
        if not balls:
            return FieldBounce()
        ball = max(balls, key = lambda ball: ball['size'])
        offset = self.kp * (ball['col'][0] - 80)
        arduino.set_speeds(s + offset - abs(offset),
                           s - offset - abs(offset))
        80 - abs(offset)
        if ball['row'][0] > 90:
            return BallSnarf()
        else:
            return self

class BallSnarf:
    def __init__(self):
        self.stop_time = time.time() + 1
    def next(self, balls, yellow_walls, green_walls):
        if time.time() > self.stop_time:
            arduino.set_speeds(0, 0)
            return FieldBounce()
        else:
            arduino.set_speeds(s, s)
            return self

class DumpBalls:
    # get real friendly with a yellow wall
    pass
