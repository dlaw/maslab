# Ball dumping: timing of the end
dump_start = 30 # seconds before end-of-match to start looking for yellow wall
dump_dance = 5 # seconds before end-of-match to start the HappyDance
dance_turn = 0.6 # the speed at which to turn while dancing
dance_period = 0.2 # how often to switch dance directions

drive_speed = 1 # standard drive forward speed
ball_follow_kp = .004
close_ball_row = 80 # snarf the ball if its center is below this row
yellow_follow_kp = .004

# position of sensors on the robot (0 is straight ahead, positive direction is clockwise)
bump_sensor_angles = [4.6, 4.0, 3.4, 2.8, 2.2, 1.6]
ir_sensor_angles = [-1.4, -0.7, 0.7, 1.4]
# ir_stuck_threshold should be larger than ir_unstuck_threshold
ir_stuck_threshold = 0.9
ir_unstuck_threshold = 0.8
probability_to_use_bump = 0.9 # when getting unstuck, use bump sensors this percent of the time (as a decimal)
unstick_wiggle_period = [1.0, 0.4] # list, where first number is how long to try going forward and second is how long to try going backwards
unstick_clean_period = 1.0 # time to keep moving after getting unstuck
escape_drive_kp = 1.0
escape_turn_kp = 1.0

# Ball snarfing: when we consume a ball
snarf_time = .7 # how long to snarf a ball after losing sight of it
snarf_speed = 1 # how fast to drive while snarfing

look_around_timeout = 10

# wall following navigation
follow_wall_timeout = 10
wall_follow_dist = .9 # target distance for wall following
wall_follow_limit = .8 # maximum distance we can be from a wall
wall_follow_kp = 5 # this could be off by an order of magnitude
lost_wall_timeout = 1 # how long to turn after losing a wall
wall_follow_turn = .7 # how fast to turn after losing a wall
wall_follow_time = 10 # how long to follow a wall before looking away
