#include "usart.h"

void coast(char motor);
void drive(char motor, char vel);
void usart2_init(unsigned int baud);
void usart2_tx(unsigned char data);

unsigned int baud0 = 3; //250k baud rate
unsigned int baud2 = 25; //38.4k baud rate

void setup(){
  int serial;
  usart0_init(baud0)
  usart2_init(baud2);
  usart2_tx(0xaa);
}

void loop(){
  char go;
  for (go=-127;go<127;go++){
    drive(1,go);
    drive(0,-1*go);
    delay(100);
  }
}

void coast(char motor){
  usart2_tx(0x86+motor); 
}

void drive(char motor, char vel){
  usart2_tx((vel<0 ? 0x8a : 0x88) + motor<<2); //direction
  usart2_tx(vel<0 ? -vel : vel); //magnitude
}


