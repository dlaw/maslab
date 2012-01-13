#include <Arduino.h>
#include "consts.h"

volatile uint32_t dist_to_target;
volatile int32_t theta_to_target;
volatile int navstate; // algorithm's internal state
volatile int16_t parameters[6];


// Initialize Timer0 for use in timing the control loop
void timer0_init(char period) {
  // set Timer0 to CTC mode
  TCCR0A &= B00000000;
  TCCR0A |= B00000010;
  
  // sett /64 prescaler
  TCCR0B &= B11111000;
  TCCR0B |= B00000011;

  OCR0A = period; // trigger the timer interrupt every 500 us
  TIMSK0 |= B00000010; // enable interrupt A
}

// This function looks at the number of ticks on each wheel since the last time it was called,
// and updates the nav system's internal target state
void update_state(volatile int *ticks_l, volatile int *ticks_r) {
  int32_t constrained_theta = theta_to_target;


  // this is buggy. figure out what the theta variable holds. COS_FIX_PT does not
  // work right now
  while (constrained_theta > 411775) { // while theta > pi
    constrained_theta -= 411775; // subtract 2 pi
  }

  while (constrained_theta < 0) { // while theta > pi
    constrained_theta += 411775; // subtract 2 pi
  }

  int dist_moved = (*ticks_l + *ticks_r) >> 1;
  dist_to_target = dist_to_target - (pgm_read_word(&(COS_FIX_PT[constrained_theta >> 4])) * dist_moved) >> 16;
  
  int32_t theta_rotd = ((*ticks_l - *ticks_r)<<16) / parameters[DIST_BETWEEN_WHEELS];
  // dist_between_weels must be equal to:| (distance between wheels) * (ticks per revolution)
  //                                     | --------------------------------------------------
  //                                     |                circumference of wheels
  theta_to_target = theta_to_target + theta_rotd;
  
  // reset tick counters
  *ticks_l = 0;
  *ticks_r = 0;
}

