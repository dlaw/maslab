# Ball dumping: timing of the end
dump_search = 30 # seconds before end-of-match to start looking for yellow wall
dump_dance = 5 # seconds before end-of-match to start the HappyDance
dance_turn = 0.6 # the speed at which to turn while dancing
dance_period = 0.2 # how often to switch dance directions

drive_speed = .5 # standard drive forward speed
ball_follow_kp = .004
close_ball_row = 80 # snarf the ball if its center is below this row
yellow_follow_kp = .004

# position of sensors on the robot (0 is straight ahead, positive direction is clockwise)
bump_sensor_angles = [2.36, 3.93] # 45 degrees from straight behind
ir_sensor_angles = [-1.4, -0.7, 0.7, 1.4]
# ir_stuck_threshold should be larger than ir_unstuck_threshold
ir_stuck_threshold = 0.9
ir_unstuck_threshold = 0.8
probability_to_use_bump = 0.9 # when getting unstuck, use bump sensors this percent of the time (as a decimal)
unstick_wiggle_period = 0.5 # after this amount of time, generate a new Unstick (with new randomness)
unstick_clean_period = 0.3 # time to keep moving after getting unstuck
escape_drive_kp = 1.0
escape_turn_kp = 1.0

# Ball snarfing: when we consume a ball
snarf_time = .4 # how long to snarf a ball after losing sight of it
snarf_speed = 1. # how fast to drive while snarfing

# look around for balls
look_around_timeout = 3
look_around_speed = .8

# how close we need to be to a yellow wall before dumping
dump_ir_threshhold = .9

# wall following navigation
follow_wall_timeout = 20 # how long to follow a wall before looking away
wall_follow_dist = .6 # target distance for wall following
wall_follow_limit = .4 # maximum distance we can be from a wall
wall_follow_kp = .6
wall_follow_kd = 8. 
lost_wall_timeout = 1 # how long to turn after losing a wall
wall_follow_drive = .5 # how to move after losing a wall
wall_follow_turn = .3 # how to move after losing a wall

ir_max = [101., 102., 165., 107.]
