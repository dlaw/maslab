import time, arduino, random

# Bounce around the field.  For now, just turn around.            
class FieldBounce:
    def __init__(self):
        self.direction = random.choice([[1, -1], [-1, 1]])
    def next(self, balls, yellow_walls, green_walls):
        arduino.set_speeds(*self.direction)
        if balls:
            print("sucking balls")
            return SuckBalls()
        return self

class SuckBalls:
    kp = .006
    snarfing = False # have we just lost sight of a ball?
    def next(self, balls, yellow_walls, green_walls):
        if snarfing:
            if time.time() > self.snarf_stop:
                arduino.set_speeds(0, 0)
                print("bouncing")
                return FieldBounce()
            else:
                arduino.set_speeds(1, 1)
                return self
        else:
            ball = max(balls[0], key = lambda ball: ball['size'])
            offset = self.kp * (ball['col'][0] - 80)
            arduino.set_speeds(1 - offset, 1 + offset)
            if ball['row'][0] > 90:
                print("snarfing")
                self.snarfing = True
                self.snarf_time = time.time() + 2
            return self

class DumpBalls:
    # get real friendly with a yellow wall
    pass
