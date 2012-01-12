#include <Arduino.h>

volatile uint32_t dist_to_target;
volatile int32_t theta_to_target;
volatile int navstate; // algorithm's internal state


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


void update_state(volatile int *ticks_l, volatile int *ticks_r) {
  int dist_moved = (*ticks_l + *ticks_r) >> 1;
  
  dist_to_target = dist_to_target - (pgm_read_word(&(COS_FIX_PT[theta_to_target >> 6])) * dist_moved) >> 16;
  
  
  int32_t theta_rotd = ((*ticks_l - *ticks_r)<<16) / DIST_BETWEEN_WHEELS;
  theta_to_target = theta_to_target + theta_rotd;
  
  // reset tick counters
  *ticks_l = 0;
  *ticks_r = 0;
}

