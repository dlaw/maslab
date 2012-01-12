#include "qik.h"
#include "nav.h"

#define TO_INT32(arr,i) (arr[i] + ((uint32_t) arr[i+1]) << 8 + \
    ((uint32_t) arr[i+2]) << 16 + ((uint32_t) arr[i+3]) << 24)
#define TO_INT16(arr,i) (arr[i] + ((uint16_t) arr[i+1] << 8))

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
  theta_to_target = TO_INT32(data,0);
  navstate = 1; // start rotating
  usart0_tx(0x00);
}

void gotopoint(serdata data) {
  dist_to_target = TO_INT32(data,0);
  theta_to_target = TO_INT32(data,4);
  navstate = 2;
  usart0_tx(0x00);
}

void getangle(serdata data) {
	usart0_tx((unsigned char) (theta_to_target >> 24) & 0xFF);
	usart0_tx((unsigned char) (theta_to_target >> 16) & 0xFF);
	usart0_tx((unsigned char) (theta_to_target >> 8) & 0xFF);
	usart0_tx((unsigned char) (theta_to_target) & 0xFF);
}

void getdistance(serdata data) {
	usart0_tx((unsigned char) (dist_to_target >> 24) & 0xFF);
	usart0_tx((unsigned char) (dist_to_target >> 16) & 0xFF);
	usart0_tx((unsigned char) (dist_to_target >> 8) & 0xFF);
	usart0_tx((unsigned char) (dist_to_target) & 0xFF);
}

void changeparam(serdata data) {
	unsigned char param = data[0];
	parameters[param] = TO_INT16(data,1);
	usart0_tx(param);
}

// How many bytes of data will follow each command?
unsigned char commands[3]={
  0,2,1,4,8,0,0,3
};

// What function shall be called to respond to each command?
responder responses[3]={
  &ack,
  &setmotors,
  &sendir,
  &rotate,
  &gotopoint,
  &getangle,
  &getdistance,
  &changeparam,
};
