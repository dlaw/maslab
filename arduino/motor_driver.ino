#include "commands.h"
#include "adc.h"

volatile unsigned char analog[15];
volatile char adchan=0;

unsigned char baud0 = 1; //500k baud rate
unsigned char baud2 = 25; //38.4k baud rate
volatile unsigned char com;
volatile unsigned char data[12];
volatile char ser_state=0;
volatile unsigned char raw_rx=0;
volatile char frame=0;
volatile char index=0;
int16_t go;

ISR(ADC_vect){
  analog[adchan]=ADCH;
}

ISR(USART0_RX_vect){
  if (frame){
    data[frame-1] = UDR0;
    frame--;
  }else{
    raw_rx = UDR0;
    frame = commands[raw_rx];
    com=raw_rx;
  }
  if(!frame)index++;
}

void setup(){
  adc_init(2,6);  //channel 2, div 64 clock prescaler
  adchan=2;
  pinMode(2, INPUT);
  pinMode(30, INPUT);
  digitalWrite(48, HIGH); 
  int serial;
  usart0_init(baud0);
  usart2_init(baud2);
  usart2_tx(0xaa);
  sei();
  adc_start();
  drive(50,50);
}

void loop(){ 
  if(index>0){
    (*responses[com])(data);
    index--;
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
