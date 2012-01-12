#include "qik.h"

// serdata is an array of volatile unsigned chars
typedef volatile unsigned char[] serdata;

// responder is the type of a function that takes serdata and returns void
typedef void (*responder) (serdata);

// Send an ack
void ack(serdata data){
  usart0_tx(0x00);
}

// Set motor speeds and send an ack
void setmotors(serdata data){
  drive(data[1],data[0]);
  usart0_tx(0x00);
}

// How many bytes of data will follow each command?
unsigned char commands[2]={
  0,2
};

// What function shall be called to respond to each command?
responder responses[2]={
  &ack,
  &setmotors
};
