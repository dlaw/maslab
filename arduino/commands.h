#include "qik.h"

unsigned char commands[2]={
  0,2
};

void ack(volatile unsigned char data[]){
  usart0_tx(0x00);
}

void dreary(volatile unsigned char data[]){
  drive(data[0],data[1]);
  usart0_tx(0x00);
}

typedef void (*functor)(volatile unsigned char[]);

functor responses[2]={
  &ack,
  &dreary,
};
