ir_max = [89., 131., 167., 94.] # for IR calibration
drive_speed = .9 # standard drive forward speed
helix_twiddle_period = [5, 0.5] # list of (time to stay on, time to stay off)

# Control state transitions
max_balls_to_possess = 13 # max number of balls that can fit in the third level at any given time
# TODO measure how many balls we can possess
min_balls_to_stalk_yellow = 6 # if we have this many balls, are within yellow_stalk_time, and see a yellow wall, turn off wall following
yellow_stalk_time = 100 # time to look for yellow walls and stay near them
max_look_around_timeouts = 3 # if we're stalking yellow but look around this many times without seeing yellow, re-enable wall following
max_ball_attempts = 7 # if we try this many times without the ball count increasing, go to ForcedFollowWall
ignore_balls_length = 17

# DumpBalls
dump_time = 40 # time to stop going for red balls
dump_ir_final = .75
dump_ir_turn_tol = .2
dump_fwd_speed = .6
dump_turn_speed = .4
back_up_time = 1.
wall_center_tolerance = 10 # pixels from center that wall center can be

# HappyDance
dance_turn = 0.6 # the speed at which to turn while dancing
dance_period = 0.2 # how often to switch dance directions
eject_time = 3. # how long to empty the top

# GoToBall
ball_follow_kp = .006
close_ball_row = 80 # snarf the ball if its center is below this row
go_to_ball_timeout = 12.
ball_stuck_ratio = 1.04

# DriveBlind
drive_blind_timeout = .3 # how long to keep driving after losing a (b/w)all and before looking around

# GoToYellow
yellow_follow_kp = .007
dump_ir_threshhold = .5 # how close we need to be to a yellow wall before dumping

# Unstick
ir_sensor_angles = [-1.4, -0.7, 0.7, 1.4] # position of sensors on the robot (0 is straight ahead, positive direction is clockwise)
bump_sensor_angles = [0.79, 5.50, 2.36, 3.93] # 45 degrees from straight behind
ir_stuck_threshold = 0.9
ir_unstuck_threshold = 0.8 # ir_stuck_threshold should be larger than ir_unstuck_threshold
unstick_angle_offset_range = 1.6 # add between -this and +this (randomly) to the escape angle
probability_to_use_bump = 0.9 # when getting unstuck, use bump sensors this percent of the time (as a decimal)
unstick_wiggle_period = 0.4 # after this amount of time, generate a new Unstick (with new randomness)
unstick_clean_period = 0.2 # time to keep moving after getting unstuck
unstick_max_turn = 0.6 # the magnitude of the maximum turn value while unsticking

# SnarfBall
snarf_time = .4 # how long to snarf a ball after losing sight of it
snarf_speed = 1. # how fast to drive while snarfing

# LookAround
look_around_timeout = 3
look_around_speed = .5 # also used in LookAway

# LookAway
look_away_timeout = 6

# HerpDerp
herp_derp_timeout = 0.5
herp_derp_min_drive = .4
herp_derp_max_drive = .6
herp_derp_min_turn = .2
herp_derp_max_turn = .3

# FollowWall
follow_wall_timeout = 17 # how long to follow a wall before looking away
wall_follow_dist = .6 # target distance for wall following
wall_follow_limit = .4 # maximum distance we can be from a wall
wall_follow_kp = .7
wall_follow_kd = 3.
wall_follow_kdd = 2.
lost_wall_timeout = 2 # how long to turn after losing a wall
wall_follow_drive = .6 # how fast to drive
wall_follow_turn = .5 # how to turn after losing a wall
wall_stuck_timeout = 3 # how long an IR can be >1 before we go to unstick
wall_absent_before_look_away = 2. # we need to be on a wall for this long in order to LookAway
