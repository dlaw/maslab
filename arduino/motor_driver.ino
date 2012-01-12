#include "qik.h"
#include "adc.h"

volatile unsigned char analog[15];
volatile char adchan=0;

unsigned char baud0 = 1; //500k baud rate
unsigned char baud2 = 25; //38.4k baud rate
volatile unsigned char com_buf[5];
volatile uint32_t data_buf[5];
volatile char ser_state=0;
volatile unsigned char raw_rx=0;
volatile char frame=0;
volatile char com_index=0;
volatile char data_index=0;
int16_t go;

ISR(ADC_vect){
  analog[adchan]=ADCH;
}

ISR(USART0_RX_vect){
  if (ser_state){
    data_buf[data_index] |= (((uint32_t) UDR0) << (frame<<3));
    if(!frame--){
      ser_state=0;
      data_index++;
    }
  }
  else{
    raw_rx = UDR0;
    frame = commands[raw_rx]-1;
    com_buf[com_index]=raw_rx;
    ser_state=1;
    com_index++;
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
    usart0_tx(com_buf[com_index-1]);
    delay(100);
    usart0_tx(0xaa);
    usart0_tx(frame);
    com_index--;
  }
  if(data_index>0){
    usart0_tx((data_buf[data_index-1]>>24)&0xff);
    usart0_tx((data_buf[data_index-1]>>16)&0xff);
    usart0_tx((data_buf[data_index-1]>>8)&0xff);
    usart0_tx(data_buf[data_index-1]&0xff);
    usart0_tx(0xbb);
    data_buf[data_index-1]=0;
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