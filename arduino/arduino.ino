#include "commands.h"
#include "test_motors.h"
#define baud0 1  //500k baud rate
#define baud2 25 //38.4k baud rate

volatile unsigned char com=0;
volatile unsigned char data[12]; // max 12 bytes of data per command
volatile char frame=0;

volatile boolean control_semaphore;

volatile int dl;
volatile int dr;

void setup(){
  DDRE &= ~0x38;  //digital pins 2,3,5 - (3,5) left (2) right
  DDRG &= ~0x20;  //digital pin 4, right 
  DDRF &= ~0x04;  //adc 2
  
    // load all of the parameters from their default values
  for (int i = 0; i < 6; i ++) {
    parameters[i] = PARAMETERS[i];
  }

  adc_init(2,6);      //channel 2, div 64 clock prescaler
  ext_int_init();   //left motor pcint init
  usart0_init(baud0);
  usart1_init(baud2);
  adchan=2;           //adc channel selection 
  timer0_init(156); // period in milliseconds = val * .064 
  sei();            // start interrupts
  adc_start();        //start ADC conversions
  usart1_tx(0xaa);    //initialize the qik controller

  adc_init(9, 6);
  adc_start();
  
  pinMode(53, INPUT);
  digitalWrite(53, HIGH);
}

void loop(){
  if (digitalRead(53) == LOW) {
    test_motors();
  }

  // the control loop only triggers if it is allowed to by the timing semaphore
  if (control_semaphore) {
    int rot_speed;
    int vel;
    
    // disable the semaphore
    control_semaphore = false;
    
    // update the distance/angle to target from how much we've moved in the last 500 uS
    // this is commented out until some bugs are fixed
    //update_state(&tickl, &tickr);
    
    switch (navstate) {
      case 0: // waiting for command
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
        
        drive(dl, -dr);
        break;
        
      case 2: // move towards target
        // in this mode, theta_to_target should be in the range [-pi, pi]
  
        while (theta_to_target > 205887) { // while theta > pi
          theta_to_target -= 411775; // subtract 2 pi
        }
  
        while (theta_to_target < -205887) { // while theta < pi
          theta_to_target += 411775;
        }
  
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

        drive(dl, -dr);
        break;   
    }
  }
}

// ******************************
// * INTERRUPT SERVICE ROUTINES *
// ******************************

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

ISR(INT4_vect){            //Pin Change interrupt handler
  if(((PINE>>4)^(PING>>5))&1){ // Used for detecting encoder ticks
    tickr++;                  // if they are different, we are rotating one direction
  }else{
    tickr--;                  // otherwise, the other direction
  }
}

ISR(INT5_vect){            //Pin Change interrupt handler
  if(((PINE>>5)^(PINE>>3))&1){ // Used for detecting encoder ticks
    tickl++;                  // if they are different, we are rotating one direction
  }else{
    tickl--;                  // otherwise, the other direction
  }
}

// the timed control loop currently triggers every 9.984 ms
ISR(TIMER0_COMPA_vect) {
<<<<<<< Updated upstream
  control_semaphore = true;
=======
  int rot_speed;
  int vel;
  
  // update the distance/angle to target from how much we've moved in the last 500 uS
  update_state(&tickl, &tickr);
  
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
      // in this mode, theta_to_target should be in the range [-pi, pi]

      while (theta_to_target > 205887) { // while theta > pi
        theta_to_target -= 411775; // subtract 2 pi
      }

      while (theta_to_target < -205887) { // while theta < pi
        theta_to_target += 411775;
      }

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

  drive(dl, -dr);
>>>>>>> Stashed changes
}

