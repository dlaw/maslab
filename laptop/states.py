import time, arduino, random

s = .8

# Bounce around the field.  For now, just turn around.            
class FieldBounce:
    def __init__(self):
        self.direction = random.choice([[.6, -.6], [-.6, .6]])
    def next(self, balls, yellow_walls, green_walls):
        arduino.set_speeds(*self.direction)
        if balls:
            return SuckBalls()
        return self

class SuckBalls:
    kp = .002
    snarfing = False # have we just lost sight of a ball?
    def next(self, balls, yellow_walls, green_walls):
        if self.snarfing:
            if time.time() > self.snarf_stop:
                arduino.set_speeds(0, 0)
                return FieldBounce()
            else:
                arduino.set_speeds(s, s)
                return self
        else:
            if not balls:
                return FieldBounce()
            ball = max(balls, key = lambda ball: ball['size'])
            offset = self.kp * (ball['col'][0] - 80)
            arduino.set_speeds(s + offset - abs(offset),
                               s - offset - abs(offset))
            80 - abs(offset)
            if ball['row'][0] > 90:
                self.snarfing = True
                self.snarf_stop = time.time() + 2
            return self

class DumpBalls:
    # get real friendly with a yellow wall
    pass
