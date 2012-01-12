#include "commands.h"
#include "adc.h"

volatile unsigned char analog[15];
volatile char adchan=0;

unsigned char baud0 = 1; //500k baud rate
unsigned char baud2 = 25; //38.4k baud rate
volatile unsigned char com=0;
volatile unsigned char data[12];
volatile char ser_state=0;
volatile char frame=0;
volatile char index=0;
int16_t go;

ISR(ADC_vect){
  analog[adchan]=ADCH;
}

ISR(USART0_RX_vect){
  if (frame){                //incoming data
    data[frame-1] = UDR0;    //write rx buffer to data array
    frame--;                 //decrement remaining bytes to follow
  }else{                     //incoming command
    com = UDR0;              //write rx buffer to command variable
    frame = commands[com];   //number of expected data bytes to follow
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
