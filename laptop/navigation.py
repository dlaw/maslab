import arduino, states, random

class GoToWall(states.State):
    # Drive straight to a wall, then enter state FollowWall
    def default_action(self):
        if max(arduino.get_ir()) > constants.wall_follow_dist:
            arduino.drive(0, 0)
            return FollowWall()
        arduino.drive(constants.drive_speed, 0)

class FollowWall(states.State):
    # TODO look around periodically
    def __init__(self, on_left = None):
        self.on_left = random.choice([True, False]) if on_left is None else on_left
        self.ir = 0 if self.on_left else 3
        self.dir = -1 if self.on_left else 1 # sign of direction to turn into wall
        self.time_wall_seen = time.time()
    def default_action(self):
        dist = arduino.get_ir()[self.ir]
        if dist > constants.wall_follow_limit: # if we see a wall
            self.time_wall_seen = time.time()
            arduino.drive(constants.drive_speed, constants.wall_follow_kp *
                          self.dir * (constants.wall_follow_dist - dist))
        elif time.time() - self.time_wall_seen < constants.wall_follow_timeout:
            arduino.drive(0, constants.wall_follow_turn * self.dir)
        else: # lost wall
            return states.LookAround()
