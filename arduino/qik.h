#include "adc.h"

char target_lvel;
char target_rvel;

const int MAX_DIFF = 1;

void coast(char motor){
  usart1_tx(0x86+motor); 
}

void drive(char lvel, char rvel){

	if (target_lvel > 127) target_lvel = 127;
	if (target_lvel < -127) target_lvel = -127;
	if (target_rvel > 127) target_rvel = 127;
	if (target_rvel < -127) target_rvel = -127;
  
  target_lvel = lvel;
  target_rvel = -rvel;
 
}
