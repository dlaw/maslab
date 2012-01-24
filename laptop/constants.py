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
ir_stuck_threshold = 0.9
unstalled_time_before_unstuck = 1.0
stalled_time_before_reverse = 0.3

# Ball snarfing: when we consume a ball
snarf_time = .7 # how long to snarf a ball after losing sight of it
snarf_speed = 1 # how fast to drive while snarfing

wall_follow_dist = .9 # target distance for wall following
wall_follow_limit = .8 # maximum distance we can be from a wall
wall_follow_kp = NotImplementedError
