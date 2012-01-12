#include "commands.h"
#include "external_interrupt.h"

#define baud0 1;  //500k baud rate
#define baud2 25; //38.4k baud rate

volatile unsigned char com=0;
volatile unsigned char data[12]; // max 12 bytes of data per command
volatile char frame=0;

volatile int tickl=0;            //left motor tick counter
volatile int tickr=0;            //right motor tick counter

volatile int dl;
volatile int dr;

ISR(ADC_vect){               //ADC complete interrupt handler
  analog[adchan]=ADCH;
}

ISR(USART0_RX_vect){         //USART receive interrupt handler
  if (!frame){               //if incoming command
    com = UDR0;              //write rx buffer to command variable
    frame = commands[com];   //number of expected data bytes to follow
  }else                      //if incoming data
    data[--frame] = UDR0;    //write rx buffer to data array
  if(!frame)                 //if command is complete
    (*responses[com])(data); //run responder
}

ISR(PCINT0_vect){            //Pin Change interrupt handler
  if(((PINB>>2)^(PINB>>3))&1){
    tickl++;
  }else{
    tickl--;
  }
}

void setup(){
  adc_init(2,6);      //channel 2, div 64 clock prescaler
  ext_pcint_init();   //left motor pcint init
  usart0_init(baud0);
  usart2_init(baud2);
  usart2_tx(0xaa);    //initialize the qik controller
  adchan=2;           //adc channel selection 
  pinMode(2, INPUT);  
  pinMode(30, INPUT); //qik controller error input pin
  timer0_init(0);
  sei();
  adc_start();        //start ADC conversions
}

void loop(){ 
}

// the timed control loop currently triggers every
// 508 uS
ISR(TIMER0_COMPA_vect) {
  int rot_speed;
  int vel;
  
  update_state(&ticks_l, &ticks_r, &dist_to_target, &theta_to_target);
  
  switch (navstate) {
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
