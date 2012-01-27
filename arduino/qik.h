#include "adc.h"

char target_lvel = 0, target_rvel = 0, current_lvel = 0, current_rvel = 0;
int cnt = 0;

void qik_init(void){
  usart1_tx(0x84);
  usart1_tx(0x01);
  usart1_tx(0x02);
  usart1_tx(0x55);
  usart1_tx(0x2a);
}

void qik_reset(void){
  pinMode(36, OUTPUT);
  digitalWrite(36, LOW);
  delay(10);
  pinMode(36, INPUT);
  pinMode(36, HIGH);
}

void coast(char motor){
  usart1_tx(0x86+motor); 
}

void drive(char lvel, char rvel) {  
  usart1_tx(lvel < 0 ? 0x8a : 0x88); //direction
  usart1_tx(lvel < 0 ? -lvel : lvel); // magnitude
  usart1_tx(rvel > 0 ? 0x8e : 0x8c); //direction
  usart1_tx(rvel < 0 ? -rvel : rvel); // magnitude
}
