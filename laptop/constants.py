# Ball dumping: timing of the end
dump_search = 30 # seconds before end-of-match to start looking for yellow wall
dump_time = 5 # seconds before end-of-match to actually dump balls

drive_speed = .8 # standard drive forward speed
ball_follow_kp = .004
close_ball_row = 80 # snarf the ball if its center is below this row
wall_follow_kp = .004

# Ball snarfing: when we consume a ball
snarf_time = .7 # how long to snarf a ball after losing sight of it
snarf_speed = 1 # how fast to drive while snarfing
