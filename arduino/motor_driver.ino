#include "qik.h"
#include "adc.h"

unsigned int baud0 = 8; //250k baud rate
unsigned int baud2 = 25; //38.4k baud rate
volatile unsigned char analog[15];
volatile char adchan;
int go;

ISR(ADC_vect){
  analog[adchan]=ADCH;
}

void setup(){
  adc_init(2,6);  //channel 2, div 64 clock prescaler
  adchan=2;
  pinMode(2, INPUT);
  pinMode(30, INPUT);
  digitalWrite(30,HIGH);
  int serial;
  usart0_init(baud0);
  usart2_init(baud2);
  usart2_tx(0xaa);
  sei();
  adc_start();
}

void loop(){
  if(analog[2]>30){
    drive(1,50);
    drive(0,50);
    delay(100);
  }else{
    drive(1,-50);
    drive(0,50);
    delay(100);
  }
}





