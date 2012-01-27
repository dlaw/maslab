import arduino, random, main, maneuvering, constants, kinect, time

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
        if (max(arduino.get_ir()[1:-1]) > constants.dump_ir_threshhold
            and wall['size'] > 3500):
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
    timeout = random.uniform(.5, 1) * constants.follow_wall_timeout
    def __init__(self):
        if np.random.rand() < constants.prob_change_wall_follow_dir:
            constants.wall_follow_on_left = not constants.wall_follow_on_left
        if constants.wall_follow_on_left:
            self.ir = 0
            self.dir = -1 # sign of direction to turn into wall
        else:
            self.ir = 3
            self.dir = 1
        self.time_wall_seen = time.time()
        self.turning_away = False
        self.err = None
    def on_stuck(self):
        # TODO decide if we still need this hack
        if any(arduino.get_bump()):
            return maneuvering.Unstick()
        return self.default_action()
    def default_action(self):
        dist = arduino.get_ir()[self.ir]
        self.last_err, self.err = self.err, constants.wall_follow_dist - dist
        if self.last_err is None: self.last_err = self.err # initialize D to 0
        if self.turning_away or max(arduino.get_ir()[1:-1]) > constants.wall_follow_dist: # too close in front
            self.turning_away = True
            self.time_wall_seen = time.time()
            arduino.drive(0, constants.wall_follow_turn * -1 * self.dir)
            if max(arduino.get_ir()[1:-1]) < constants.wall_follow_dist and dist > constants.wall_follow_limit:
                self.turning_away = False
        elif dist > constants.wall_follow_limit: # if we see a wall
            self.time_wall_seen = time.time()
            arduino.drive(constants.drive_speed, self.dir * 
                          (constants.wall_follow_kp * self.err + 
                           constants.wall_follow_kd * (self.err - self.last_err)))
        elif time.time() - self.time_wall_seen < constants.lost_wall_timeout:
            arduino.drive(constants.wall_follow_drive, constants.wall_follow_turn * self.dir)
        else: # lost wall
            return LookAround()

class ForcedFollowWall(FollowWall):
    def on_ball(self):
        return self.default_action() # ignore balls
    def on_timeout(self):
        return FollowWall()
