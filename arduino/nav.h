#include <Arduino.h>
#include "consts.h"

volatile int32_t dist_to_target;
volatile int32_t theta_to_target;
volatile int navstate; // algorithm's internal state
volatile int16_t parameters[8];
volatile char rotate_speed;


inline void SEND_INT22(uint32_t val){
  usart0_tx((unsigned char) (val >> 24) & 0xFF);
  usart0_tx((unsigned char) (val >> 16) & 0xFF);
  usart0_tx((unsigned char) (val >> 8) & 0xFF);
  usart0_tx((unsigned char) val & 0xFF);
}

// Initialize Timer0 for use in timing the control loop
void timer0_init(char period) {
  // set Timer0 to CTC mode
  TCCR0A &= B00000000;
  TCCR0A |= B00000010;
  
  // sett /1024 prescaler
  TCCR0B &= B11111000;
  TCCR0B |= B00000101;

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
  
  //dist_to_target -= (pgm_read_word(&(COS_FIX_PT[(int) (constrained_theta << 5) / 3217])) * dist_moved) >> 16;
  dist_to_target += ((cosine_fix_pt((unsigned char) (constrained_theta) / 1610) * dist_moved) >> 15);
  //dist_to_target += dist_moved;
  //SEND_INT22(pgm_read_word(&(COS_FIX_PT[(int) (constrained_theta << 5) / 3217])));
  
  int32_t theta_rotd = ((((int32_t) *ticks_l) - ((int32_t) *ticks_r))<<16) / parameters[DIST_BETWEEN_WHEELS];
  // dist_between_weels must be equal to:| (distance between wheels) * (ticks per revolution)
  //                                     | --------------------------------------------------
  //                                     |                circumference of wheels
  theta_to_target = theta_to_target + theta_rotd;
  
  // reset tick counters
  *ticks_l = 0;
  *ticks_r = 0;
}

