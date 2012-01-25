#include "commands.h"

// DO NOT MODIFY
#define baud0 1  //500k baud rate
#define baud2 25 //38.4k baud rate

volatile unsigned char com=0;
volatile unsigned char data[12]; // max 12 bytes of data per command
volatile char frame=0;

volatile unsigned char control_semaphore;

int32_t last_theta = 0;
int32_t accumulated_error = 0;
int32_t delta;
int32_t delta_error;

char lvel;
char rvel;

volatile uint32_t ldif;
volatile uint32_t rdif;

int32_t a_lerror;
int32_t a_rerror;
int32_t d_lerror;
int32_t d_rerror;
int32_t last_lerror;
int32_t last_rerror;

int stall_countl = 0;
int stall_countr = 0;
volatile unsigned char ramp_counter;

const int SERVO_PIN = 0;

// SERIOUSLY, DONT MODIFY
void setup(){
  // DO NOT MODIFY THE SETUP
  DDRE &= ~0x38;  //digital pins 2,3,5 - (3,5) left (2) right
  DDRG &= ~0x20;  //digital pin 4, right 
  DDRF &= ~0xff;  //adc 2
  
  // load all of the parameters from their default values
  for (int i = 0; i < 8; i ++) {
    parameters[i] = PARAMETERS[i];
  }
  adchan=0;           //adc channel selection 
  adc_init(6);      //channel 2, div 64 clock prescaler
  adc_select(adcmap[adchan]);
  adc_start();

  ext_int_init();   //left motor pcint init
  usart0_init(baud0);
  usart1_init(baud2);
  //adchan=2;           //adc channel selection 
  timer0_init(20); // period in milliseconds = val * .064 
  sei();            // start interrupts
  usart1_tx(0xaa);    //initialize the qik controller
  
  pinMode(48, INPUT);
  pinMode(49, INPUT);
  pinMode(5, INPUT);
  pinMode(4, INPUT);
  
  // enable timers 4 + 5
  TCCR4B |= B00000001;
  TIMSK4 |= B00100000;
  TCCR4A = 0x00;
  
  TCCR5B |= B00000001;
  TIMSK5 |= B00100000;
  TCCR5A = 0x00;
  
    pinMode(11, OUTPUT);
  
  //init servo timer
  // servo output pin is 11
  TCCR1A = B10100010;
  TCCR1B = B00011011;
  ICR1=4999;  //fPWM=50Hz (Period = 20ms Standard). 
  OCR1A=130;
  

  pinMode(6, OUTPUT); // sucker
  digitalWrite(6, LOW);
  
  pinMode(7, OUTPUT); // helix
  digitalWrite(7, LOW);
  
  pinMode(8, OUTPUT); // shooter
  digitalWrite(8, LOW);
  
  pinMode(53, INPUT); // start switch
  digitalWrite(53, HIGH); // turn on internal pullup


  //setup bump sensor inputs
  pinMode(52, INPUT);
  digitalWrite(52, HIGH);

  pinMode(51, INPUT);
  digitalWrite(51, HIGH);

  pinMode(50, INPUT);
  digitalWrite(50, HIGH);

  pinMode(49, INPUT);
  digitalWrite(49, HIGH);

  pinMode(48, INPUT);
  digitalWrite(48, HIGH);

  pinMode(47, INPUT);
  digitalWrite(47, HIGH);
}

void loop(){
  // DO NOT MODIFY
  
  if (ramp_counter > 1) {
    ramp_counter = 0;
    // provide some protection against sudden acceleration
  
    if (lvel > target_lvel + MAX_DIFF) lvel -= MAX_DIFF;
    else if (lvel < target_lvel - MAX_DIFF) lvel += MAX_DIFF;
    else lvel = target_lvel;
    
    if (rvel > target_rvel + MAX_DIFF) rvel -= MAX_DIFF;
    else if (rvel < target_rvel - MAX_DIFF) rvel += MAX_DIFF;
    else rvel = target_rvel;
        
    usart1_tx(lvel<0 ? 0x8a : 0x88); //direction
    usart1_tx(lvel<0 ? -lvel : lvel); //magnitude
    usart1_tx(rvel<0 ? 0x8e : 0x8c); //direction
    usart1_tx(rvel<0 ? -rvel : rvel); //magnitude
  }

  // DO NOT MODIFY

  // the control loop only triggers if it is allowed to by the timing semaphore
  if (control_semaphore > 10) {
    int rot_speed;
    int vel;
    
    control_semaphore = 0;  // disable the semaphore
    
    switch (navstate) {
      case 0: // waiting for command
        if (timeout > 500) {
          drive(0,0);
          timeout = 0;
        }
        
        timeout++;
        break;
        
      case 1: // rotate in place
        update_state(&tickl, &tickr);
        // update the distance/angle to target from how much we've moved in the last 500 uS
        // this is commented out until some bugs are fixed
      
        accumulated_error += theta_to_target;
        delta = (theta_to_target - last_theta);
        
        if (accumulated_error > 40000000) { accumulated_error = 40000000; }
        
        rot_speed = (theta_to_target * parameters[ROT_K]) >> 16;
        //rot_speed += ((((theta_to_target - last_theta)) * parameters[ROT_K_D]) >> 14);
        rot_speed += ((accumulated_error * parameters[ROT_K_I]) >> 18);
        
        dl = 0 + rot_speed;
        dr = 0 - rot_speed;
      
        
        if (dl > rotate_speed) dl = rotate_speed;
        if (dr > rotate_speed) dr = rotate_speed;
        if (dl < -rotate_speed) dl = -rotate_speed;
        if (dr < -rotate_speed) dr = -rotate_speed;
        
        
        if ((delta < 2000) & (theta_to_target < parameters[THETA_ACCURACY_THRESHOLD])) { // close enough
          navstate = 0;   // go back to waiting for commands
          dl = 0;
          dr = 0;
        }
        
        
        drive(dl, dr);
        last_theta = theta_to_target;
        break;
        
      case 2: // velocity feedback on motors
        // DO NOT MODIFY
        int rerror = abs(abs(target_rtime) - rdif);
        int lerror = abs(abs(target_ltime) - ldif);
      
        if (rdif == 0) {
          if (dr == 0) {
            dr = (target_rtime > 0) ? 48 : -48;
          }
        } else {
          if (rdif > (abs(target_rtime) + ((unsigned char) abs(target_rtime) >> 7))) {
            dr +=  (target_rtime > 0) ? 1 : -1;
          } else if (rdif < (abs(target_rtime) - ((unsigned char) abs(target_rtime) >> 7))) {
            dr +=  (target_rtime > 0) ? -1 : 1;
          }
        }
        
        if (ldif == 0) {
          if (dl == 0) {
            dl = (target_ltime > 0) ? 48 : -48;
          }
        } else {
          if ((ldif > (abs(target_ltime) + ((unsigned char) abs(target_ltime) >> 7)))) {
            dl += (target_ltime > 0) ? 1 : -1;
          } else if (ldif < (abs(target_ltime) - ((unsigned char) abs(target_ltime) >> 7))) {
            dl += (target_ltime > 0) ? -1 : 1;
          }
        }
        
        if (tickl == 0) {
          stall_countl++;
        } else {
          stall_countl = 0;
        }
        
        if (tickr == 0) {
          stall_countr++;
        } else {
          stall_countr = 0;
        }
        
        // DO NOT MODIFY
        if (stall_countl > 20) {
          dl += (target_ltime > 0) ? 1 : -1;
        }
        
        if (stall_countr > 20) {
          dr += (target_rtime > 0) ? 1 : -1;
        }
        
        if (stall_countr > 200) {
          target_rtime = 0;
          dr = 0;
          stall_countr = 0;
        }
        
        if (stall_countl > 200) {
          target_ltime = 0;
          dl = 0;
          stall_countl = 0;
        }
        
        if (dr > 127) dr = 127;
        if (dr < -127) dr = -127;
        if (dl > 127) dl = 127;
        if (dl < -127) dl = -127;
        
        if ((target_rtime < 0) && (dr > 0)) dr = 0;
        if ((target_rtime > 0) && (dr < 0)) dr = 0;
        if ((target_ltime < 0) && (dl > 0)) dl = 0;
        if ((target_ltime > 0) && (dl < 0)) dl = 0;
        if ((target_ltime == 0)) dl = 0;
        if ((target_rtime == 0)) dr = 0;

        // DO NOT MODIFY
        drive(dl, dr);

        ldif = 0;
        rdif = 0;
        tickl = 0;
        tickr = 0;
        break;
        
    }
  }
}

// ******************************
// * INTERRUPT SERVICE ROUTINES *
// ******************************

ISR(ADC_vect){               //ADC complete interrupt handler
  analog[adcmap[adchan]]= ADCH;
  adchan++;
  if(adchan>5)adchan=0;
  adc_select(adcmap[adchan]);
}

ISR(USART0_RX_vect){         //USART receive interrupt handler
  if (!frame){               //if incoming command
    com = UDR0;              //write rx buffer to command variable
    frame = commands[com];   //number of expected data bytes to follow
  } else                     //if incoming data
    data[--frame] = UDR0;    //write rx buffer to data array
  if(!frame)                 //if command is complete
    (*responses[com])(data); //run responder
}

ISR(INT4_vect){               //Pin Change interrupt handler
  if(((PINE>>4)^(PING>>5))&1) // Used for detecting encoder ticks
    tickr++;                  // if they are different, we are rotating one direction
  else
    tickr--;                  // otherwise, the other direction
}

ISR(INT5_vect){            //Pin Change interrupt handler
  if(((PINE>>5)^(PINE>>3))&1) // Used for detecting encoder ticks
    tickl++;                  // if they are different, we are rotating one direction
  else
    tickl--;                  // otherwise, the other direction
}

// the timed control loop currently triggers every 9.984 ms
ISR(TIMER0_COMPA_vect) {
  control_semaphore++;
  ramp_counter++;
}

ISR(TIMER4_CAPT_vect) {
  rdif = ICR4;
  __asm__("nop");
  TCNT4H = 0x00;
  TCNT4L = 0x00;

}

ISR(TIMER5_CAPT_vect) {
  ldif = ICR5;
  __asm__("nop");
  TCNT5H = 0x00;
  TCNT5L = 0x00;

}
