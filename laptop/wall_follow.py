#!/usr/bin/python2.7

import numpy as np, arduino, time

FOLLOWING_ON_RIGHT = 1
JUST_LOST_ON_RIGHT = 2
FOLLOWING_ON_LEFT  = 3
JUST_LOST_ON_LEFT  = 4
SEARCHING_FOR_WALL = 5

LEFT_IR_CHANNEL  = 2
RIGHT_IR_CHANNEL = 6

MAX_DIST_BEFORE_LOCKING_ON  = 1.0
MIN_DIST_BEFORE_LOSING_WALL = 1.2
# max_dist should be less than min_dist (to avoid rapid switching of states)
TARGET_DIST_FROM_WALL = 0.6

accum_err = 0
last_err  = 0
drive_speed = 0.4
turn_speed  = 0.2
pid_freq  = 30 #units: calls/sec
last_time = 0

last_left  = drive_speed
last_right = drive_speed
cur_state  = SEARCHING_FOR_WALL
cycles_in_state = 0
CYCLES_STRAIGHT_AFTER_LOSING  = 30
CYCLES_TURNING_AFTER_STRAIGHT = 30

def pid(err, kp=-.003, ki=0, kd=0):
    global accum_err, last_err
    accum_err += err
    p, i, d, last_err = err, accum_err, err-last_err, err
    turn = kp*p + ki*i + kd*d
    left = np.clip(drive_speed + turn, -1, 1)
    right = np.clip(drive_speed - turn, -1, 1)
    arduino.set_motors(left, -right)

while True:
    last_time = time.time()
    next_state = cur_state

    if cur_state == SEARCHING_FOR_WALL:
        last_left = np.clip(last_left + (np.random.rand()-.5)/10, -1, 1)
        last_right = np.clip(last_right + (np.random.rand()-.5)/10, -1, 1)
        arduino.set_motors(last_left, last_right) #randomized, so we don't care about right being negated

        if arduino.get_ir(LEFT_IR_CHANNEL) < MAX_DIST_BEFORE_LOCKING_ON:
            next_state = FOLLOWING_ON_LEFT
        elif arduino.get_ir(RIGHT_IR_CHANNEL) < MAX_DIST_BEFORE_LOCKING_ON:
            next_state = FOLLOWING_ON_RIGHT
    
    elif cur_state == FOLLOWING_ON_RIGHT:
        dist = arduino.get_ir(RIGHT_IR_CHANNEL)
        pid(dist - TARGET_DIST_FROM_WALL)
        if dist > MIN_DIST_BEFORE_LOSING_WALL:
            next_state = JUST_LOST_ON_RIGHT

    elif cur_state == FOLLOWING_ON_LEFT:
        dist = arduino.get_ir(LEFT_IR_CHANNEL)
        pid(TARGET_DIST_FROM_WALL - dist) #reverse the order of subtraction from the right following case
        if dist > MIN_DIST_BEFORE_LOSING_WALL:
            next_state = JUST_LOST_ON_LEFT

    elif cur_state == JUST_LOST_ON_RIGHT: #drive straight, then turn and attempt to find wall, then give up
        if cycles_in_state < CYCLES_STRAIGHT_AFTER_LOSING:
            arduino.set_motors(drive_speed, -drive_speed)
        elif cycles_in_state < CYCLES_STRAIGHT_AFTER_LOSING + CYCLES_TURNING_AFTER_STRAIGHT:
            arduino.set_motors(drive_speed + turn_speed, -(drive_speed - turn_speed))
            if arduino.get_ir(RIGHT_IR_CHANNEL) < MAX_DIST_BEFORE_LOCKING_ON:
                next_state = FOLLOWING_ON_RIGHT
        else:
            next_state = SEARCHING_FOR_WALL

    elif cur_state == JUST_LOST_ON_LEFT: #I'm too lazy to combine this with the above case, but that should happen soon
        if cycles_in_state < CYCLES_STRAIGHT_AFTER_LOSING:
            arduino.set_motors(drive_speed, -drive_speed)
        elif cycles_in_state < CYCLES_STRAIGHT_AFTER_LOSING + CYCLES_TURNING_AFTER_STRAIGHT:
            arduino.set_motors(drive_speed - turn_speed, -(drive_speed + turn_speed)) #signs flipped from above
            if arduino.get_ir(LEFT_IR_CHANNEL) < MAX_DIST_BEFORE_LOCKING_ON:
                next_state = FOLLOWING_ON_LEFT
        else:
            next_state = SEARCHING_FOR_WALL

    cycles_in_state += 1
    if next_state != cur_state:
        cycles_in_state = 0
        accum_err = 0
        last_err = 0
        last_left = drive_speed
        last_right = drive_speed
        cur_state = next_state

    time_to_sleep = (1./pid_freq) - (time.time() - last_time) #total time desired - time used so far
    if time_to_sleep > 0:
        time.sleep(time_to_sleep)
    else:
        print "pid_freq is too high"

