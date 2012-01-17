#include "adc.h"

char lastlvel;
char lastrvel;

const int MAX_DIFF = 8;

void coast(char motor){
  usart1_tx(0x86+motor); 
}

void drive(char lvel, char rvel){
  if ((lvel - lastlvel) > MAX_DIFF) {
    lvel = lastlvel + MAX_DIFF;
  }
  
  if ((lvel - lastlvel) < -MAX_DIFF) {
    lvel = lastlvel - MAX_DIFF;
  }
  
  if ((rvel - lastrvel) > MAX_DIFF) {
    rvel = lastrvel + MAX_DIFF;
  }
  
  if ((rvel - lastrvel) < -MAX_DIFF) {
    rvel = lastrvel - MAX_DIFF;
  }
  
  lastrvel = rvel;
  lastlvel = lvel;
  
  usart1_tx((lvel<0 ? 0x8a : 0x88)); //direction
  usart1_tx(lvel<0 ? -lvel : lvel); //magnitude
  usart1_tx((rvel<0 ? 0x8e : 0x8c)); //direction
  usart1_tx(rvel<0 ? -rvel : rvel); //magnitude
}
