#include "usart.h"

void coast(char motor){
  usart2_tx(0x86+motor); 
}

void drive(char lvel, char rvel){
  usart2_tx((vel<0 ? 0x8a : 0x88)); //direction
  usart2_tx(vel<0 ? -vel : vel); //magnitude
  usart2_tx((vel<0 ? 0x8e : 0x8c)); //direction
  usart2_tx(vel<0 ? -vel : vel); //magnitude
}
