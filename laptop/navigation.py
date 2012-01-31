import arduino, random, main, maneuvering, constants, kinect, time, numpy as np

class LookAround(main.State):
    timeout = constants.look_around_timeout
    def __init__(self):
        self.turn = random.choice([-1, 1]) * constants.look_around_speed
        self.force_wall_follow = False
        if np.random.rand() < constants.prob_forcing_wall_follow:
            self.force_wall_follow = True
        else:
            constants.prob_forcing_wall_follow *= constants.look_around_multiplier_prob_forcing_wall_follow
    def next(self, time_left):
        if self.force_wall_follow:
            constants.prob_forcing_wall_follow = constants.init_prob_forcing_wall_follow # reset
            return ForcedFollowWall()
        return main.State.next(self, time_left)
    def default_action(self):
        arduino.drive(0, self.turn)
    def on_timeout(self):
        return GoToWall() # enter wall-following mode

class LookAway(main.State):
    timeout = constants.look_away_timeout
    def __init__(self, turning_away = True):
        self.turning_away = turning_away
    def on_stuck(self):
        return self.default_action()
    def default_action(self):
        turn, ir = (-1, 0) if self.turning_away else (1, 3)
        arduino.drive(0, turn * constants.look_around_speed)
        if arduino.get_ir()[ir] > constants.wall_follow_dist:
            if self.turning_away:
                return LookAway(turning_away = False)
            else:
                return FollowWall()
    def on_timeout(self):
        return GoToWall()

class GoToBall(main.State):
    timeout = constants.go_to_ball_timeout
    size = 1.
    def __init__(self):
        self.non_herp_time = time.time()
    def on_ball(self):
        ball = max(kinect.balls, key = lambda ball: ball['size'])
        if ball['size'] > self.size * constants.ball_stuck_ratio:
            self.non_herp_time = time.time()
        if time.time() - self.non_herp_time > constants.herp_derp_timeout:
            return maneuvering.HerpDerp()
        self.size = .9 * self.size + .1 * ball['size']
        offset = constants.ball_follow_kp * (ball['col'][0] - 80)
        arduino.drive(max(0, constants.drive_speed - abs(offset)), offset)
        if ball['row'][0] > constants.close_ball_row:
            return maneuvering.SnarfBall()
    def default_action(self): # we don't see a ball, and we're not stuck
        return LostBall()
    def on_timeout(self):
        return maneuvering.HerpDerp()

class LostBall(main.State):
    timeout = constants.lost_ball_timeout
    def default_action(self):
        arduino.drive(constants.drive_speed, 0)

class GoToYellow(main.State):
    def on_yellow(self):
        wall = max(kinect.yellow_walls, key = lambda wall: wall['size'])
        offset = constants.yellow_follow_kp * (wall['col'][0] - 80)
        arduino.drive(max(0, constants.drive_speed - abs(offset)), offset)
        if (max(arduino.get_ir()[1:-1]) > constants.dump_ir_threshhold
            and wall['size'] > 3500):
            return maneuvering.DumpBalls(final = abs(wall['col'][0] - 80) <
                                         constants.wall_center_tolerance)
    def default_action(self):
        return LookAround()
    def on_timeout(self):
        return maneuvering.HerpDerp()

class GoToWall(main.State):
    def default_action(self):
        if max(arduino.get_ir()) > constants.wall_follow_dist:
            arduino.drive(0, 0)
            return FollowWall()
        arduino.drive(constants.drive_speed, 0)
    def on_timeout(self):
        return maneuvering.HerpDerp()

class FollowWall(main.State): # PDD controller
    last_p, last_d = None, None
    turning_away = False
    timeout = random.uniform(.5, 1) * constants.follow_wall_timeout
    def __init__(self):
        self.time_last_unstuck = time.time()
        self.time_wall_seen = time.time()
        self.time_wall_absent = 0
    def on_stuck(self):
        if ((time.time() - self.time_last_unstuck > constants.wall_stuck_timeout)
            or any(arduino.get_bump())):
            return maneuvering.Unstick()
        return self.follow()
    def default_action(self):
        self.time_last_unstuck = time.time()
        return self.follow()
    def follow(self):
        side_ir = arduino.get_ir()[3] # hard-coded to follow on right
        p = constants.wall_follow_dist - side_ir
        d = (p - self.last_p) if self.last_p else 0
        dd = (d - self.last_d) if self.last_d else 0
        self.last_p, self.last_d = p, d
        if time.time() - self.time_wall_seen > constants.lost_wall_timeout:
            return GoToWall()
        elif ((max(arduino.get_ir()[1:-1]) > constants.wall_follow_limit
               and (time.time() - self.time_wall_absent) > constants.lost_wall_timeout)
               or self.turning_away): # too close in front
            self.turning_away = True
            self.time_wall_seen = time.time()
            drive = 0
            turn = constants.wall_follow_turn * -1
            arduino.drive(drive, turn)
            if (max(arduino.get_ir()[1:-1]) < constants.wall_follow_limit and
                side_ir > constants.wall_follow_limit):
                self.turning_away = False
        elif side_ir > constants.wall_follow_limit: # if we see a wall
            self.time_wall_seen = time.time()
            drive = constants.wall_follow_drive
            turn = (constants.wall_follow_kp * p +
                    constants.wall_follow_kd * d +
                    constants.wall_follow_kdd * dd)
            arduino.drive(drive, turn)
        else: # lost wall but not timed out, so turn into the wall
            self.time_wall_absent = time.time()
            drive = 0
            turn = constants.wall_follow_turn
            arduino.drive(drive, turn)
    def on_timeout(self):
        return LookAway()

class ForcedFollowWall(FollowWall):
    def on_ball(self):
        return self.default_action() # ignore balls
    def on_timeout(self):
        return FollowWall()
