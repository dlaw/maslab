#include "qik.h"

unsigned int baud0 = 3; //250k baud rate
unsigned int baud2 = 25; //38.4k baud rate

void setup(){
  int serial;
  usart0_init(baud0);
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




