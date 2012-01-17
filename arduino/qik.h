#include "adc.h"

char target_lvel;
char target_rvel;

const int MAX_DIFF = 2;

void coast(char motor){
  usart1_tx(0x86+motor); 
}

void drive(char lvel, char rvel){
  
  target_lvel = lvel;
  target_rvel = rvel;
 
}
