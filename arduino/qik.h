#include "adc.h"

char target_lvel = 0, target_rvel = 0, current_lvel = 0, current_rvel = 0;

void coast(char motor){
  usart1_tx(0x86+motor); 
}

void drive(char lvel, char rvel) {
  usart1_tx(lvel < 0 ? 0x8a : 0x88); //direction
  //usart1_tx(lvel > 0 ? 0x8a : 0x88); //direction
  usart1_tx(lvel < 0 ? -lvel : lvel); // magnitude
  usart1_tx(rvel < 0 ? 0x8e : 0x8c); //direction
  //usart1_tx(rvel > 0 ? 0x8e : 0x8c); //direction
  usart1_tx(rvel < 0 ? -rvel : rvel); // magnitude
}
