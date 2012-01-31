# for the arduino
ir_max = [89., 131., 167., 94.]

# Multi-purpose
drive_speed = .9 # standard drive forward speed

# DumpBalls
dump_search = 60 # seconds before end-of-match to start looking for yellow wall
dump_dance = 3 # seconds before end-of-match to start the HappyDance
dump_ir_final = .9
dump_ir_turn_tol = .1
dump_fwd_speed = .6
dump_turn_speed = .4
back_up_time = 1.
wall_center_tolerance = 10 # pixels from center that wall center can be

# HappyDance
dance_turn = 0.6 # the speed at which to turn while dancing
dance_period = 0.2 # how often to switch dance directions

# GoToBall
ball_follow_kp = .006
close_ball_row = 80 # snarf the ball if its center is below this row
go_to_ball_timeout = 7.
ball_stuck_ratio = 1.04

# GoToYellow
yellow_follow_kp = .007
dump_ir_threshhold = .5 # how close we need to be to a yellow wall before dumping

# Unstick
ir_sensor_angles = [-1.4, -0.7, 0.7, 1.4] # position of sensors on the robot (0 is straight ahead, positive direction is clockwise)
bump_sensor_angles = [2.36, 3.93] # 45 degrees from straight behind
ir_stuck_threshold = 0.9
ir_unstuck_threshold = 0.8 # ir_stuck_threshold should be larger than ir_unstuck_threshold
unstick_angle_offset_range = 1.6 # add between -this and +this (randomly) to the escape angle
probability_to_use_bump = 0.9 # when getting unstuck, use bump sensors this percent of the time (as a decimal)
unstick_wiggle_period = 0.5 # after this amount of time, generate a new Unstick (with new randomness)
unstick_clean_period = 0.3 # time to keep moving after getting unstuck

# SnarfBall
snarf_time = .4 # how long to snarf a ball after losing sight of it
snarf_speed = 1. # how fast to drive while snarfing

# LookAround
look_around_timeout = 3
look_around_speed = .8
init_prob_forcing_wall_follow = 0.02 # initial value of the below, also reset to this each time ForcedFollowWall happens
prob_forcing_wall_follow = init_prob_forcing_wall_follow # each time we create a new LookAround(), go to ForcedFollowWall with this probability
delta_prob_forcing_wall_follow = 0.01 # increase the above by this amount each time we create a new LookAround()

# HerpDerp
herp_derp_timeout = 0.5
herp_derp_min_drive = .3
herp_derp_max_drive = .7
herp_derp_min_turn = .3
herp_derp_max_turn = .6

# FollowWall
follow_wall_timeout = 20 # how long to follow a wall before looking away
wall_follow_dist = .6 # target distance for wall following
wall_follow_limit = .4 # maximum distance we can be from a wall
wall_follow_kp = .7
wall_follow_kd = 3.
wall_follow_kdd = 2.
lost_wall_timeout = 2 # how long to turn after losing a wall
wall_follow_drive = .6 # .5 # how to move after losing a wall
wall_follow_turn = .5 # .3 # how to move after losing a wall
wall_stuck_timeout = 3 # how long an IR can be >1 before we go to unstick
