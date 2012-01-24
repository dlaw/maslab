import arduino, kinect, random, time, constants, numpy as np

class State:
    # override next() whenever an action should not be interrupted
    def next(self, time_left):
        """
        Superclass method to execute appropriate event handlers and actions.
        Returns a new state if the state shall change, and self otherwise.
        """
        if (any(arduino.get_stall()) or any(arduino.get_bump())
            or max(arduino.get_ir() > 1)):
            return self.on_stuck()
        elif time_left < constants.dump_search and kinect.yellow_walls:
            return self.on_yellow()
        elif time_left >= constants.dump_search and kinect.balls:
            return self.on_ball()
        else:
            return state.default_action()
    def on_ball(self):
        """
        Action to take when a ball is seen and dump_mode is False.
        Returns a new state if the state shall change, and self otherwise.
        """
        return GoToBall()
    def on_yellow(self):
        """
        Action to take when a yellow wall is seen and dump_mode is True.
        Returns a new state if the state shall change, and self otherwise.
        """
        return GoToYellow()
    def on_stuck(self):
        """
        Action to take when we are probably stuck.
        Returns a new state if the state shall change, and self otherwise.
        """
        return Unstick()
    def default_action(self):
        """
        Action to take if none of the other event handlers apply.
        Returns a new state if the state shall change, and self otherwise.
        """
        raise NotImplementedError # subclass has to do this one

class LookAround(State):
    def __init__(self):
        arduino.rotate(random.choice([6.29, -6.29])) # 2 pi in either direction
    def default_action(self):
        if arduino.get_angle() == 0: # saw nothing after turning
            return GoToWall() # drive to wall and then enter wall following mode
        else:
            return self

class GoToBall(State):
    def on_ball(self): # TODO do the right thing if we're getting close to a wall
        # drive towards the ball
        ball = max(kinect.balls, key = lambda ball: ball['size'])
        offset = constants.ball_follow_kp * (ball['col'][0] - 80)
        # slow down if you need to turn more, but never go backwards
        arduino.drive(max(0, .8-abs(offset)), offset)
        if ball['row'][0] > constants.close_ball_row:
            return SnarfBall()
        return self
    def default_action(self):
        # lost the ball
        return LookAround()

class SnarfBall(State):
    def __init__(self):
        self.stop_time = time.time() + constants.snarf_time
    def next(self, time_left): # override next because we snarf no matter what
        # TODO do the right thing for balls against a wall
        if time.time() < self.stop_time:
            arduino.drive(constants.snarf_speed, 0)
            return self
        else:
            return LookAround()

class GoToYellow(State):
    def on_yellow(self):
        # drive towards the yellow
        wall = max(kinect.yellow_walls, key = lambda wall: wall['size'])
        offset = constants.wall_follow_kp * (wall['col'][0] - 80)
        # slow down if you need to turn more, but never go backwards
        arduino.drive(max(0, .8-abs(offset)), offset)
        return self
    def default_action(self):
        # lost the wall
        return LookAround()

class DumpBalls(State):
    def next(self, time_left): # override next so nothing can interrupt a dump
        # TODO drive towards the wall
        if time_left < constants.dump_dance:
            return self
        else:
            arduino.set_door(True)
            return HappyDance()

class HappyDance(State):
    def __init__(self):
        self.next_shake = time.time() + constants.dance_period
        self.shake_dir = 1
    def next(self, time_left): # override next so nothing can interrupt a HappyDance
        if time.time() > self.next_shake:
            self.next_shake = time.time() + constants.dance_period
            self.shake_dir *= -1
        arudino.drive(0, self.shake_dir * constants.dance_turn)
        return self

class Unstick(State):
    """
    The initialization randomly picks an obstacle and decides to drive away
    from it. Once we have a direction in mind, we try driving away for t0
    seconds. If the motors are still stalled, try reversing for t1 before
    driving forward for t0 again. Now, if the motors are still stalled,
    generate a new instance of this class (to start over again with new
    randomness). Once the motors unstall, continue driving for t2 seconds
    to fully escape.

    constants.unstick_times = [t0, t1, t2] as defined above
    """
    def __init__(self):
        triggered_bump = np.where(arduino.get_bump())[0]
        triggered_ir = np.where(np.array(arduino.get_ir()) > constants.ir_stuck_threshold)[0]
        if len(triggered_bump) and (not len(triggered_ir) or np.random.rand()<constants.probability_to_use_bump):
            # only bump sensors are triggered, or both types are triggered and we randomly chose to look at bump
            self.escape_angle = constants.bump_sensor_angles[random.choice(triggered_bump)] # randomly pick a triggered bump sensor
        elif len(triggered_ir):
            # only IR senors are triggered, or both types are triggered and we randomly chose to look at IR
            self.escape_angle = constants.ir_sensor_angles[random.choice(triggered_ir)] # randomly pick a triggered IR sensor
        else:
            self.escape_angle = None # oops, not good style
        self.last_time_stalled = time.time()
        self.unstick_state = 0 # 0 is fwd, 1 is rev, 2 is fwd, 3 is give up (but don't actually set it to 3)
        self.next_state_change = time.time() + constants.unstick_times[0]
    def next(self, time_left):
        if self.escape_angle is None: # init said nothing was triggered
            return LookAround()
        if not any(arduino.get_stall()): # no motors are stalled!
            self.escape(False)
            if time.time() - self.last_time_stalled > constants.unstick_times[2]:
                return LookAround()
            return self
        else:
            self.last_time_stalled = time.time()
            if time.time() > self.next_state_change:
                self.unstick_state += 1
                if self.unstick_state == 3:
                    return Unstick()
                # otherwise, unstick_state is either 1 or 2
                self.next_state_change = time.time() + constants.unstick_times[2-self.unstick_state] # yes, it works
            self.escape(self.unstick_state == 1) # reverse only if we're in unstick_state 1
            return self
    def escape(self, reverse):
        """
        We're hitting an obstacle at angle (front of the robot is 0, positive
        is clockwise) and need to escape. Periodically reverse the direction if
        the motors are stalling (as passed in to the reverse argument).

        For angles 0 or pi, you want full forward and no turn. For angles pi/2
        and 3pi/2, you want no forward and only turn. This suggests using trig
        functions, though maybe there's a better implementation.
        """
        offset = np.pi if reverse else 0
        drive = constants.escape_drive_kp * np.cos(self.escape_angle + offset)
        turn = constants.escape_turn_kp * np.sin(self.escape_angle + offset)
        arduino.drive(drive, turn)

class GoToWall(State):
    # Drive straight to a wall, then enter state FollowWall
    def default_action(self):
        if max(arduino.get_ir()) > constants.wall_follow_dist:
            arduino.drive(0, 0)
            return FollowWall()
        else:
            arduino.drive(constants.drive_speed, 0)
            return self

class FollowWall(State):
    def __init__(self, side, distance):
        pass
    def on_ball():
        # if a wall is in the way, ignore the ball
    def on_yellow():
        # if a wall is in the way, ignore the yellow
    def default_action(self):
        pass
