import arduino, random, main, maneuvering, constants, kinect, time, numpy as np

class LookAround(main.State):
    timeout = constants.look_around_timeout
    def __init__(self):
        self.turn = random.choice([-1, 1]) * constants.look_around_speed
        self.force_wall_follow = False
        if np.random.rand() < constants.prob_forcing_wall_follow:
            self.force_wall_follow = True
        else:
            constants.prob_forcing_wall_follow += constants.delta_prob_forcing_wall_follow
    def default_action(self):
        if self.force_wall_follow:
            constants.prob_forcing_wall_follow = constants.init_prob_forcing_wall_follow # reset
            return ForcedFollowWall()
        arduino.drive(0, self.turn)
    def on_timeout(self):
        return GoToWall() # enter wall-following mode

class GoToBall(main.State):
    def on_ball(self):
        self.timeout = constants.go_to_ball_timeout
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

class FollowWall(main.State): # PDD controller
    timeout = random.uniform(.5, 1) * constants.follow_wall_timeout
    def __init__(self):
        if np.random.rand() < constants.prob_change_wall_follow_dir:
            constants.wall_follow_on_left = not constants.wall_follow_on_left
        self.ir, self.dir = (0, -1) if constants.wall_follow_on_left else (3, 1)
        self.time_wall_seen = time.time()
        self.turning_away = False
        self.last_p, self.last_d = None, None
    def on_stuck(self):
        if any(arduino.get_bump()):
            return maneuvering.Unstick()
        # TODO: check if IRs are totally unreasonable.
        return self.default_action()
    def default_action(self):
        side_ir = arduino.get_ir()[self.ir]
        p = constants.wall_follow_dist - side_ir
        d = (p - self.last_p) if self.last_p else 0
        dd = (d - self.last_d) if self.last_d else 0
        self.last_p, self.last_d = p, d
        if time.time() - self.time_wall_seen > constants.lost_wall_timeout:
            return LookAround()
        elif (max(arduino.get_ir()[1:-1]) > constants.wall_follow_dist
              or self.turning_away): # too close in front
            self.turning_away = True
            self.time_wall_seen = time.time()
            drive = 0
            turn = constants.wall_follow_turn * -1 * self.dir
            arduino.drive(drive, turn)
            if (max(arduino.get_ir()[1:-1]) < constants.wall_follow_dist and
                side_ir > constants.wall_follow_limit):
                self.turning_away = False
        elif side_ir > constants.wall_follow_limit: # if we see a wall
            self.time_wall_seen = time.time()
            drive = constants.wall_follow_drive
            turn = self.dir * np.clip((constants.wall_follow_kp * p +
                                       constants.wall_follow_kd * d +
                                       constants.wall_follow_kdd * dd),
                                       -constants.wall_follow_max_turn,
                                       constants.wall_follow_max_turn)
            arduino.drive(drive, turn)
        else: # lost wall but not timed out, so turn into the wall
            drive = constants.wall_follow_drive / 2
            turn = constants.wall_follow_turn
            arduino.drive(drive, turn)

class ForcedFollowWall(FollowWall):
    def on_ball(self):
        return self.default_action() # ignore balls
    def on_timeout(self):
        return FollowWall()
