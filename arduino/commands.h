#include "qik.h"
#include "nav.h"
#include "external_interrupt.h"

inline void SEND_INT32(uint32_t val){
  usart0_tx((unsigned char) (val >> 24) & 0xFF);
  usart0_tx((unsigned char) (val >> 16) & 0xFF);
  usart0_tx((unsigned char) (val >> 8) & 0xFF);
  usart0_tx((unsigned char) val & 0xFF);
}
inline void SEND_INT16(uint16_t val){
  usart0_tx((unsigned char) (val >> 8) & 0xFF);
  usart0_tx((unsigned char) val & 0xFF);
}
#define TO_INT32(arr,i) (arr[i] + ((uint32_t) arr[i+1]) << 8 + \
    ((uint32_t) arr[i+2]) << 16 + ((uint32_t) arr[i+3]) << 24)
#define TO_INT16(arr,i) (arr[i] + ((uint16_t) arr[i+1] << 8))

// serdata is an array of volatile unsigned chars
typedef volatile unsigned char serdata[];

// responder is the type of a function that takes serdata and returns void
typedef void (*responder) (serdata);

long timeout;

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
  timeout = 0;
}

// command 0x02
//Send an IR sensor reading
void sendir(serdata data){
  usart0_tx(analogRead(data[0]));
}

// command 0x03
void rotate(serdata data) {
  theta_to_target = (uint32_t) data[0] + ((uint32_t) data[1] << 8) + ((uint32_t) data[2] << 16) + ((uint32_t) data[3] << 24);
  
  //theta_to_target = 0x0006487E;
  rotate_speed = data[4]; 
  //rotate_speed = 127;
  navstate = 1; // start rotating
  usart0_tx(0x00);
}

// command 0x04
void gotopoint(serdata data) {
  dist_to_target = data[4] + (data[5] << 8) + ((int32_t) data[6] << 16) + ((int32_t) data[7] << 24);
  theta_to_target = (uint32_t) data[0] + ((uint32_t) data[1] << 8) + ((uint32_t) data[2] << 16) + ((uint32_t) data[3] << 24);

  navstate = 2;
  usart0_tx(0x00);
}

// command 0x05
void getangle(serdata data) {
  SEND_INT32(theta_to_target);
}

// command 0x06
void getdistance(serdata data) {
  SEND_INT32(dist_to_target);
}

// command 0x07
void changeparam(serdata data) {
	unsigned char param = data[0];
	parameters[param] = TO_INT16(data,1);
	usart0_tx(param);
}

// command 0x08
void sendticks(serdata data) {
  SEND_INT16(tickl);
  SEND_INT16(tickr);
}  

// command 0x09
void sendbattvoltage(serdata data) {
  int battvoltage = analogRead(9);
  SEND_INT16(battvoltage);
}

// How many bytes of data will follow each command?
unsigned char commands[10]={
  0,2,1,5,8,0,0,3,0,0
};

// What function shall be called to respond to each command?
responder responses[11]={
  &ack,
  &setmotors,
  &sendir,
  &rotate,
  &gotopoint,
  &getangle,
  &getdistance,
  &changeparam,
  &sendticks,
  &sendbattvoltage,
  &setmotorspeed
};
