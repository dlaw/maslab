#include "qik.h"
#include "nav.h"

// serdata is an array of volatile unsigned chars
typedef volatile unsigned char serdata[];

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

//Send an IR sensor reading
void sendir(serdata data){
  usart0_tx(analog[data[0]]);
}

void rotate(serdata data) {
	theta_to_target = data[0] + ((uint32_t) data[1]) << 8 + ((uint32_t) data[2]) << 16 + ((uint32_t) data[3]) << 24;
	navstate = 1; // start rotating
}

void gotopoint(serdata data) {
	dist_to_target = data[0] + ((uint32_t) data[1]) << 8 + ((uint32_t) data[2]) << 16 + ((uint32_t) data[3]) << 24;
	theta_to_target = data[4] + ((int32_t) data[5]) << 8 + ((int32_t) data[6]) << 16 + ((int32_t) data[7]) << 24;
	navstate = 2;
}

void getangle(serdata data) {
	usart0_tx((unsigned char) (theta_to_target >> 24) & 0xFF);
	usart0_tx((unsigned char) (theta_to_target >> 16) & 0xFF);
	usart0_tx((unsigned char) (theta_to_target >> 8) & 0xFF);
	usart0_tx((unsigned char) (theta_to_target) & 0xFF);
}

void getdistance(serdata data) {
	usart0_tx((unsigned char) (distance_to_target >> 24) & 0xFF);
	usart0_tx((unsigned char) (distance_to_target >> 16) & 0xFF);
	usart0_tx((unsigned char) (distance_to_target >> 8) & 0xFF);
	usart0_tx((unsigned char) (distance_to_target) & 0xFF);
}

// How many bytes of data will follow each command?
unsigned char commands[3]={
  0,2,1,4,8,0,0
};

// What function shall be called to respond to each command?
responder responses[3]={
  &ack,
  &setmotors,
  &sendir,
  &rotate,
  &gotopoint,
  &getangle,
  &getdistance
};
