#include <avr/interrupt.h>

void ext_pcint_init(void){		//hardcode the pins that you want!
  PCICR |= 0x01; //enable pin change interrupts for PCINT7:0
  PCMSK0 = (1<<PCINT2); //PCINT mask | PCINT2 for left encoder
}
