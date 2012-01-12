#include <Arduino.h>

void timer0_init(int period) {
  TCCR0A &= B00000000;
  TCCR0A |= B00000010;
  
  TCCR0B &= B11111000;
  TCCR0B |= B00000011;
  //TCCR0B &= (0xFF)&(0<<CS01)&(0<<CS00);
  OCR0A = 127; // trigger the timer interrupt every 500 us
  TIMSK0 |= B00000010;
}


void go_to_point(int32_t target_x, int32_t target_y, volatile uint32_t dist_to_target, volatile int32_t theta_to_target) {
  dist_to_target = (uint32_t) sqrt(target_x*target_x + target_y*target_y);
  if (target_x != 0) {
    theta_to_target = ((int32_t) (atan(target_y/target_x) * 65536));
  } else {
    theta_to_target = 102943;
  }
}


void correction(uint32_t r, int32_t theta, volatile uint32_t dist_to_target, volatile int32_t theta_to_target) {
  theta_to_target = theta;
  dist_to_target = r;
}

void update_state(volatile int *ticks_l, volatile int *ticks_r, volatile uint32_t *dist_to_target, volatile int32_t *theta_to_target) {
  int dist_moved = (*ticks_l + *ticks_r) >> 1;
  
  *dist_to_target = *dist_to_target - (pgm_read_word(&(COS_FIX_PT[*theta_to_target >> 6])) * dist_moved) >> 16;
  
  
  int32_t theta_rotd = ((*ticks_l - *ticks_r)<<16) / DIST_BETWEEN_WHEELS;
  *theta_to_target = *theta_to_target + theta_rotd;
  
  // reset tick counters
  *ticks_l = 0;
  *ticks_r = 0;
}

