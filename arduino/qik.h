#include "adc.h"

void coast(char motor){
  usart2_tx(0x86+motor); 
}

void drive(char lvel, char rvel){
  usart2_tx((lvel<0 ? 0x8a : 0x88)); //direction
  usart2_tx(lvel<0 ? -lvel : lvel); //magnitude
  usart2_tx((rvel<0 ? 0x8e : 0x8c)); //direction
  usart2_tx(rvel<0 ? -rvel : rvel); //magnitude
}
