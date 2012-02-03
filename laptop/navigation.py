import arduino, random, main, maneuvering, constants, kinect, time, numpy as np, variables

class LookAround(main.State):
    timeout = constants.look_around_timeout
    def __init__(self):
        self.turn = random.choice([-1, 1]) * constants.look_around_speed
        self.saw_yellow = False
    def default_action(self):
        if (variables.can_follow_walls and variables.ignore_balls and
            not variables.yellow_stalk_period):
            return GoToWall()
        if kinect.yellow_walls: # safe to go here because default_action() will be called at least once before on_timeout()
            self.saw_yellow = True
        arduino.drive(0, self.turn)
    def on_timeout(self):
        if not variables.can_follow_walls:
            variables.saw_yellow.pop()
            variables.saw_yellow.insert(0, self.saw_yellow)
            if not any(variables.saw_yellow): # we lost the yellow (repeatedly), so follow walls again
                variables.can_follow_walls = True
                variables.ignore_balls_until_yellow = True
        if variables.can_follow_walls:
            return GoToWall() # enter wall-following mode
        return maneuvering.HerpDerp() # if wall-following is disabled, instead HerpDerp

class LookAway(main.State):
    timeout = constants.look_away_timeout
    def __init__(self, turning_away = True):
        self.turning_away = turning_away
        self.turn = -1 if turning_away else 1
        self.ir = 0 if turning_away else 3
    def on_stuck(self):
        return self.default_action()
    def default_action(self):
        arduino.drive(0, self.turn * constants.look_around_speed)
        if arduino.get_ir()[self.ir] > constants.wall_follow_limit: # ok because of state C
            if self.turning_away:
                return LookAway(turning_away = False)
            else:
                return FollowWall()
    def on_timeout(self):
        return maneuvering.HerpDerp()

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
        return DriveBlind(constants.ball_blind_timeout)
    def on_timeout(self):
        return maneuvering.HerpDerp()

class DriveBlind(main.State):
    def __init__(self, timeout):
        self.timeout = timeout
    def default_action(self):
        arduino.drive(constants.drive_speed, 0)
    def on_timeout(self):
        return maneuvering.HerpDerp()

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
        return DriveBlind(constants.yellow_blind_timeout)
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
    def on_block(self): # ignore front top right bump sensor
        if arduino.get_bump()[1]:
            return maneuvering.HerpDerp()
        return self.follow()
    def on_stuck(self):
        if ((time.time() - self.time_last_unstuck > constants.wall_stuck_timeout)
            or any(arduino.get_bump()[2:4])):
            # if this was called by an IR, require stricter conditions
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
            drive = .2 # TODO kludge
            turn = constants.wall_follow_turn
            arduino.drive(drive, turn)
    def on_timeout(self):
        if time.time() - self.time_wall_absent > constants.wall_absent_before_look_away:
            return LookAway()
        return self.follow()

