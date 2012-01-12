#include "qik.h"

typedef volatile unsigned char[] response;
typedef void (*responder) (response);

// Send an ack
void ack(response data){
  usart0_tx(0x00);
}

// Set motor speeds and send an ack
void setmotors(response data){
  drive(data[0],data[1]);
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
