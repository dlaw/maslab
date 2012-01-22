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

int32_t target_ltime;
int32_t target_rtime;

volatile int dl;
volatile int dr;


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
  usart0_tx(analog[adcmap[data[0]]]);
}

// command 0x03
void rotate(serdata data) {
  theta_to_target = (uint32_t) data[0] + ((uint32_t) data[1] << 8) + ((uint32_t) data[2] << 16) + ((uint32_t) data[3] << 24);
 
  rotate_speed = data[4]; 

  navstate = 1; // start rotating
  usart0_tx(0x00);
}

// command 0x04
void gotopoint(serdata data) {
  //deprecated
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

void setmotorspeed(serdata data) {
  int32_t new_ltime = (uint32_t) data[4] + ((uint32_t) data[5] << 8) + ((uint32_t) data[6] << 16) + ((uint32_t) data[7] << 24);
  int32_t new_rtime = (uint32_t) data[0] + ((uint32_t) data[1] << 8) + ((uint32_t) data[2] << 16) + ((uint32_t) data[3] << 24);

  navstate = 2;
  
  if ((new_ltime < 0 & target_ltime > 0) | (new_ltime > 0 & target_ltime < 0)) {
    dl = (new_ltime > 0) ? 16 : -16;
  }
    
  if ((new_rtime < 0 & target_rtime > 0) | (new_rtime > 0 & target_rtime < 0)) {
    dr = (new_rtime > 0) ? 16 : -16;
  }
  
  target_ltime = new_ltime;
  target_rtime = new_rtime;
  
  drive(dl, dr);
  
  usart0_tx(0x00);
}

void buttonpressed(serdata data) {
  usart0_tx(digitalRead(53));
}

void setsucker(serdata data) {
  if (data[0] == 0x00) {
    digitalWrite(6, LOW);
  } else {
    digitalWrite(6, HIGH);
  }
}

void sethelix(serdata data) {
  if (data[0] == 0x00) {
    digitalWrite(7, LOW);
  } else {
    digitalWrite(7, HIGH);
  }
}

void setdoor(serdata data) {
  if (data[0] == 0x00) {
    OCR1A=97;
  } else {
    OCR1A=535;
  }
}

// How many bytes of data will follow each command?
unsigned char commands[15]={
  0,2,1,5,8,0,0,3,0,0,8,0,1,1,1
};

// What function shall be called to respond to each command?
responder responses[15]={
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
  &setmotorspeed,
  &buttonpressed,
  &setsucker,
  &sethelix,
  &setdoor
};
