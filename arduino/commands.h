#include "qik.h"
#include "nav.h"
#include "external_interrupt.h"

#define TO_INT32(arr,i) (arr[i] + ((uint32_t) arr[i+1]) << 8 + \
    ((uint32_t) arr[i+2]) << 16 + ((uint32_t) arr[i+3]) << 24)
#define TO_INT16(arr,i) (arr[i] + ((uint16_t) arr[i+1] << 8))

// serdata is an array of volatile unsigned chars
typedef volatile unsigned char serdata[];

// responder is the type of a function that takes serdata and returns void
typedef void (*responder) (serdata);

// command 0x00
// Send an ack
void ack(serdata data){
  usart0_tx(0x00);
}

// commnad 0x01
// Set motor speeds and send an ack
void setmotors(serdata data){
  drive(data[1],data[0]);
  usart0_tx(0x00);
  navstate = 0; // override whatever other control loop is happening
}

// command 0x02
//Send an IR sensor reading
void sendir(serdata data){
  usart0_tx(analog[data[0]]);
}

// command 0x03
void rotate(serdata data) {
  theta_to_target = TO_INT32(data,0);
  navstate = 1; // start rotating
  usart0_tx(0x00);
}

// command 0x04
void gotopoint(serdata data) {
  dist_to_target = TO_INT32(data,0);
  theta_to_target = TO_INT32(data,4);
  navstate = 2;
  usart0_tx(0x00);
}

// command 0x05
void getangle(serdata data) {
	usart0_tx((unsigned char) (theta_to_target >> 24) & 0xFF);
	usart0_tx((unsigned char) (theta_to_target >> 16) & 0xFF);
	usart0_tx((unsigned char) (theta_to_target >> 8) & 0xFF);
	usart0_tx((unsigned char) (theta_to_target) & 0xFF);
}

// command 0x06
void getdistance(serdata data) {
	usart0_tx((unsigned char) (dist_to_target >> 24) & 0xFF);
	usart0_tx((unsigned char) (dist_to_target >> 16) & 0xFF);
	usart0_tx((unsigned char) (dist_to_target >> 8) & 0xFF);
	usart0_tx((unsigned char) (dist_to_target) & 0xFF);
}

// command 0x07
void changeparam(serdata data) {
	unsigned char param = data[0];
	parameters[param] = TO_INT16(data,1);
	usart0_tx(param);
}

// command 0x08
void sendticks(serdata data) {
  usart0_tx((unsigned char) (tickl>>8) &0xFF);
  usart0_tx((unsigned char) (tickl) &0xFF);
  usart0_tx((unsigned char) (tickr>>8) &0xFF);
  usart0_tx((unsigned char) (tickr) &0xFF);
}  

void sendbattvoltage(serdata data) {
  adc_select(9);
}

// How many bytes of data will follow each command?
unsigned char commands[10]={
  0,2,1,4,8,0,0,3,0,0
};

// What function shall be called to respond to each command?
responder responses[10]={
  &ack,
  &setmotors,
  &sendir,
  &rotate,
  &gotopoint,
  &getangle,
  &getdistance,
  &changeparam,
  &sendticks,
  &sendbattvoltage
};
