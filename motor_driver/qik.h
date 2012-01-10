#include "usart.h"

void coast(char motor);
void drive(char motor, char vel);

void coast(char motor){
  usart2_tx(0x86+motor); 
}

void drive(char motor, char vel){
  usart2_tx((vel<0 ? 0x8a : 0x88) + motor<<2); //direction
  usart2_tx(vel<0 ? -vel : vel); //magnitude
}
