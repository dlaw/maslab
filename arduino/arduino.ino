#include "commands.h"
#include "external_interrupt.h"

#define baud0 1  //500k baud rate
#define baud2 25 //38.4k baud rate

volatile unsigned char com = 0;
volatile unsigned char data[12]; // max 12 bytes of data per command
volatile char frame = 0;

volatile unsigned char ramp_counter = 0;

const int SERVO_PIN = 0;
volatile unsigned char allow;
volatile unsigned int blink=0;

void setup(){
  DDRF &= ~0xff;  //adc 2
  adchan=0;           //adc channel selection 
  adc_init(6);      //channel 2, div 64 clock prescaler
  adc_select(adcmap[adchan]);
  adc_start();

  //ext_int_init();   //left motor pcint init
  usart0_init(baud0);
  usart1_init(baud2);

  qik_init();		//qik initialization (pwm frequency)

  // set Timer0 to CTC mode
  TCCR0A &= B00000000;
  TCCR0A |= B00000010;
  
  // set /1024 prescaler
  TCCR0B &= B11111000;
  TCCR0B |= B00000101;

  OCR0A = 20; // trigger the timer interrupt every 500 us
  TIMSK0 |= B00000010; // enable interrupt A
  
  // int4 for ball detect
  EICRB = B00000011;
  EIMSK = B00010000;
  
  sei();            // start interrupts
  
  pinMode(11, OUTPUT);
  
  //init servo timer
  // servo output pin is 11
  //TCCR1A = B10100010;
  //TCCR1B = B00011011;
  //ICR1=4999;  //fPWM=50Hz (Period = 20ms Standard). 
  //OCR1A=130;
  
  DDRH  |= B00111000;
  PORTH &= B11000111;
  
  pinMode(53, INPUT); // start switch
  digitalWrite(53, HIGH); // turn on internal pullup

  //setup bump sensor inputs
  pinMode(52, INPUT);
  digitalWrite(52, HIGH);

  pinMode(51, INPUT);
  digitalWrite(51, HIGH);

  pinMode(50, OUTPUT);
  digitalWrite(50, LOW);
  
  pinMode(36, INPUT);      //qik reset
  digitalWrite(36, LOW);
  
  pinMode(35, OUTPUT);
  pinMode(37, OUTPUT);
  pinMode(39, OUTPUT);
  
  //pinMode(2, INPUT);
  pinMode(3, OUTPUT);
  digitalWrite(3, LOW);
  //digitalWrite(2, HIGH);
  
  //main.py LED
  pinMode(30,OUTPUT);
  pinMode(31,OUTPUT);
  digitalWrite(31,HIGH);
  is_alive=0;

  PORTE |= B00010000;
}

void loop() {
  if(is_alive==1){
    if((blink>=400)){
      blink=0;
      digitalWrite(30,HIGH);
    }
    if(blink>=200){
      digitalWrite(30,LOW);
    }
  }
  if (ramp_counter) {
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
  //analog[adcmap[adchan]]= ADCH;
  fil[adchan] *= 15;
  fil[adchan] += ((uint32_t) ADCH)<<20;  
  fil[adchan] >>= 4;
  adchan++;
  if(adchan>4)adchan=0;
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
//ball sense debouncing
  if (allow <= 100) allow++;
//helix pwm @ 50%
  if (helix) PORTG ^= 0x04;
  else PORTG &= ~0x04;
//blinky counter
  blink++;
}

ISR(INT4_vect) {
  if (allow > 100) {
    // needs some sort of a debounce functionality
    ball_cnt++;
    allow = 0;
    TCNT0 = 0;
  }
}
