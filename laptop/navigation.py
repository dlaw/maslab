import arduino, random, main, maneuvering

class LookAround(main.State):
    timeout = constants.look_around_timeout
    def __init__(self):
        self.turn = random.choice([-1, 1]) * constants.look_around_speed
    def default_action(self):
        arduino.drive(0, self.turn)
    def on_timeout(self):
        return GoToWall() # enter wall-following mode

class GoToBall(main.State):
    def on_ball(self):
        ball = max(kinect.balls, key = lambda ball: ball['size'])
        offset = constants.ball_follow_kp * (ball['col'][0] - 80)
        arduino.drive(max(0, constants.drive_speed - abs(offset)), offset)
        if ball['row'][0] > constants.close_ball_row:
            return maneuvering.SnarfBall()
    def default_action(self):
        return LookAround()

class GoToYellow(main.State):
    def on_yellow(self):
        wall = max(kinect.yellow_walls, key = lambda wall: wall['size'])
        offset = constants.yellow_follow_kp * (wall['col'][0] - 80)
        arduino.drive(max(0, constants.drive_speed - abs(offset)), offset)
        if max(arduino.get_ir()) > constants.dump_ir_threshhold:
            return maneuvering.DumpBalls()
    def default_action(self):
        return LookAround() # lost the wall

class GoToWall(main.State):
    def default_action(self):
        if max(arduino.get_ir()) > constants.wall_follow_dist:
            arduino.drive(0, 0)
            return FollowWall()
        arduino.drive(constants.drive_speed, 0)

class FollowWall(main.State):
    timeout = constants.follow_wall_timeout # times out to LookAround
    def __init__(self, on_left = None):
        """
        TODO actually use on_left (currently, we never pass it in as an argument)
        """
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
        elif time.time() - self.time_wall_seen < constants.lost_wall_timeout:
            arduino.drive(0, constants.wall_follow_turn * self.dir)
        else: # lost wall
            return LookAround()
