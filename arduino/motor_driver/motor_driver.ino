#include "qik.h"
#include "adc.h"
#include "consts.h"
#include "nav.h"

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
  pinMode(13, OUTPUT);
  
  adc_init(2,6);  //channel 2, div 64 clock prescaler
  adchan=2;
  pinMode(2, INPUT);
  pinMode(30, INPUT);
  digitalWrite(30, HIGH); 
  int serial;
  usart0_init(baud0);
  usart2_init(baud2);
  usart2_tx(0xaa);
  timer0_init(0);
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



ISR(TIMER0_COMPA_vect) {
  int rot_speed;
  int vel;
  
  update_state(&ticks_l, &ticks_r, &dist_to_target, &theta_to_target);
  
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
