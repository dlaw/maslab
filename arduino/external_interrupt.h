#include <avr/interrupt.h>

volatile int tickl=0;            //left motor encoder tick counter
volatile int tickr=0;            //right motor encoder tick counter

void ext_int_init(void){		//hardcode the pins that you want!
  EICRB |= (1<<ISC40)|(1<<ISC50);   //configure any logical change interrupt for int4 and int5
  EIMSK |= (1<<INT4)|(1<<INT5);     //enable int4 and int5
}
