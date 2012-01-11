#include "qik.h"
#include "adc.h"

const int DIST_BETWEEN_WHEELS = 10;
const int ACCURACY_THRESHOLD = 10;
const int ROT_K = -50;
const int ROT_MOVE_K = -10;
const int VEL_K = 5;

volatile int state; // algorithm's internal state

volatile int dl;
volatile int dr;

volatile uint32_t dist_to_target;
volatile int32_t theta_to_target;

volatile int ticks_l;
volatile int ticks_r;

unsigned char baud0 = 103; //250k baud rate
unsigned char baud2 = 25; //38.4k baud rate
volatile unsigned char analog[15];
volatile char adchan=0;
volatile uint32_t com_buf[5];
volatile uint32_t data_buf[5];
volatile uint32_t raw_rx=0;
volatile char frame=0;
volatile char com_index=0;
volatile char data_index=0;
int16_t go;



ISR(ADC_vect){
  analog[adchan]=ADCH;
}

ISR(USART0_RX_vect){
  raw_rx |= (((uint32_t) UDR0)<<frame);
  frame+=8;
  if(frame==32){
    if((raw_rx>>31)==0x1){
      com_buf[com_index]=raw_rx;
      com_index++;
    }
    else{
      data_buf[data_index]=raw_rx;
      data_index++;
    }
    frame=0;
    raw_rx=0;
  }
}

void setup(){
  adc_init(2,6);  //channel 2, div 64 clock prescaler
  adchan=2;
  pinMode(2, INPUT);
  pinMode(30, INPUT);
  digitalWrite(30, HIGH); 
  int serial;
  usart0_init(baud0);
  usart2_init(baud2);
  usart2_tx(0xaa);
  sei();
  adc_start();
}

void loop(){ 
  if(com_index>0){
    usart0_tx(com_buf[com_index-1]&0xff);
    com_index--;
  }
  if(data_index>0){
    usart0_tx(data_buf[data_index-1]&0xff);
    data_index--;
  }
  /*if(analog[2]>30){
   drive(1,50);
   drive(0,50);
   delay(100);
   }else{
   drive(1,-50);
   drive(0,50);
   delay(100);
   }*/
}

void timer0_init(int period) {
  TCCR0A |= (1<<WGM01); // set timer 0 to CTC mode
  TCCR0B |= (1<<CS01)|(1<<CS00); // set /64 clock prescaler
  OCR0A = 127; // trigger the timer interrupt every 500 us
  TIMSK0 |= (1<<OCIE0A);
}

ISR(TIMER0_COMPA_vect) {
  int rot_speed;
  int vel;
  
  update_state();
  
  switch (state) {
    case 0: // waiting for command
      dl = 0;
      dr = 0;
      break;
      
    case 1: // rotating to face destination
      rot_speed = theta_to_target * ROT_K;
      dl = 0 + rot_speed;
      dr = 0 - rot_speed;
      
      break;
      
    case 2: // moving forward
      vel = VEL_K * dist_to_target;
      rot_speed = theta_to_target * ROT_MOVE_K;
      
      dl = vel + rot_speed;
      dr = vel - rot_speed;
   
      if (dl > 127) dl = 127;
      if (dr > 127) dr = 127;
      if (dl < -127) dl = -127;
      if (dr < -127) dr = -127;
      
      if (dist_to_target < ACCURACY_THRESHOLD) {
        state = 0;
        dl = 0;
        dr = 0;
        // tell the eeepc that we've reached the destination point
      }
        
      break;
  }
}

void go_to_point(int32_t target_x, int32_t target_y) {
  dist_to_target = sqrt(target_x*target_x + target_y*target_y);
  if (target_x != 0) {
    theta_to_target = ((int32_t) (atan(target_y/target_x) * 65536));
  } else {
    theta_to_target = 102943;
  }
}

void correction(uint32_t r, int32_t theta) {
  theta_to_target = theta;
  dist_to_target = r;
}

void update_state() {
  int dist_moved = (ticks_l + ticks_r) >> 1;
  dist_to_target = dist_to_target - cos( (((float) theta_to_target) / 65536)) * dist_moved;
  
  int32_t theta_rotd = ((ticks_l - ticks_r)<<16) / DIST_BETWEEN_WHEELS;
  theta_to_target = theta_to_target + theta_rotd;
  
  // reset tick counters
  ticks_l = 0;
  ticks_r = 0;
}
