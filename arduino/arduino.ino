#include "commands.h"

#define baud0 1  //500k baud rate
#define baud2 25 //38.4k baud rate

volatile unsigned char com = 0;
volatile unsigned char data[12]; // max 12 bytes of data per command
volatile char frame = 0;

volatile unsigned char ramp_counter = 0;

const int SERVO_PIN = 0;

// SERIOUSLY, DONT MODIFY
void setup(){
  // DO NOT MODIFY THE SETUP
  DDRF &= ~0xff;  //adc 2
  adchan=0;           //adc channel selection 
  adc_init(6);      //channel 2, div 64 clock prescaler
  adc_select(adcmap[adchan]);
  adc_start();

  ext_int_init();   //left motor pcint init
  usart0_init(baud0);
  usart1_init(baud2);

  // set Timer0 to CTC mode
  TCCR0A &= B00000000;
  TCCR0A |= B00000010;
  
  // set /1024 prescaler
  TCCR0B &= B11111000;
  TCCR0B |= B00000101;

  OCR0A = 20; // trigger the timer interrupt every 500 us
  TIMSK0 |= B00000010; // enable interrupt A
  
  sei();            // start interrupts
  usart1_tx(0xaa);    //initialize the qik controller
  
  pinMode(11, OUTPUT);
  
  //init servo timer
  // servo output pin is 11
  //TCCR1A = B10100010;
  //TCCR1B = B00011011;
  //ICR1=4999;  //fPWM=50Hz (Period = 20ms Standard). 
  //OCR1A=130;
  
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

void loop() {
  if (ramp_counter) { // ramp every 1.28 ms, so 0 to 127 in 162 ms
    if (target_lvel > current_lvel) current_lvel++;
    if (target_lvel < current_lvel) current_lvel--;
    if (target_rvel > current_rvel) current_rvel++;
    if (target_rvel < current_rvel) current_rvel--;
    drive(current_lvel, current_rvel);
    ramp_counter = 0;
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

// the timed control loop currently triggers every 1.28 ms
ISR(TIMER0_COMPA_vect) {
  ramp_counter++;
}
