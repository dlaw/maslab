#include "commands.h"
#include "external_interrupt.h"

#define baud0 1  //500k baud rate
#define baud2 25 //38.4k baud rate

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
  // load default parameters
  pinMode(2, INPUT);  
  pinMode(29, OUTPUT); //qik controller error input pin
  digitalWrite(29,0);
  for (int i = 0; i < 6; i ++) {
    parameters[i] = PARAMETERS[i];
  }
  adc_init(2,6);      //channel 2, div 64 clock prescaler
  ext_pcint_init();   //left motor pcint init
  usart0_init(baud0);
  usart1_init(baud2);
  usart1_tx(0xaa);    //initialize the qik controller
  adchan=2;           //adc channel selection 
  timer0_init(125); // period in microseconds = argument * 4 (maximum 255)
  sei();
  adc_start();        //start ADC conversions
  drive(100,100);
  }

void loop(){ // nothing happens in the loop
}

// the timed control loop currently triggers every 500 uS
ISR(TIMER0_COMPA_vect) {
  int rot_speed;
  int vel;
  
  update_state(&tickl, &tickr);

  // This block would normalize the theta_to_target variable to
  // be within the range [-pi, pi], but i don't believe that this
  // is something we actually want at this time

  /*if (theta_to_target > 205887) { // if theta > pi
    theta_to_target -= 411775; // subtract 2 pi
  } else if (theta_to_target < -205887) { // if theta < pi
    theta_to_target += 411775;
  }*/
  
  switch (navstate) {
    case 0: // waiting for command
      dl = 0;
      dr = 0;
      break;
      
    case 1: // rotate in place
      rot_speed = (theta_to_target * parameters[ROT_K]) >> 16;
      dl = 0 + rot_speed;
      dr = 0 - rot_speed;

      if (theta_to_target < parameters[THETA_ACCURACY_THRESHOLD]) { // close enough
        navstate = 0;   // go back to waiting for commands
        dl = 0;
        dr = 0;
      }
      
      break;
      
    case 2: // move towards target
      vel = parameters[VEL_K] * dist_to_target;
      rot_speed = theta_to_target * parameters[ROT_MOVE_K];
      
      dl = vel + rot_speed;
      dr = vel - rot_speed;
   
      if (dl > 127) dl = 127;
      if (dr > 127) dr = 127;
      if (dl < -127) dl = -127;
      if (dr < -127) dr = -127;
      
      if (dist_to_target < parameters[DIST_ACCURACY_THRESHOLD]) {
        navstate = 0; // go back to waiting for commands
        dl = 0;
        dr = 0;
      }
        
      break;
  }
}
