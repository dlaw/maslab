#include <avr/interrupt.h>
#include "usart.h"

volatile unsigned char analog[15];
volatile char adchan=0;

void adc_init(char channel, char prescaler){
  ADMUX |= (1<<REFS0)|(1<<ADLAR)|(channel&0x0f); //select ADC channel, rvcc as ref, and left-shift the data
  //ADCSRB |= ((channel&0x10)>>1); //bit 5 of ADC channel select
  ADCSRA |= (prescaler&0x07); //set prescaler 3-bits -> (1,2,4,8,16,32,64,128)
  ADCSRA |=(1<<ADATE); //AUTO TRIGGER ENABLE
  ADCSRA |=(1<<ADEN); //ENABLE ADC
  ADCSRA |=(1<<ADIE); //INTERUPT ENABLE
}

void adc_start(void){
  ADCSRA |=(1<<ADSC); //start conversions
}

