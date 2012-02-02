#include "qik.h"


// serdata is an array of volatile unsigned chars
typedef volatile unsigned char serdata[];

// responder is the type of a function that takes serdata and returns void
typedef void (*responder) (serdata);

volatile unsigned char ball_cnt = 0;
volatile unsigned char is_alive = 0;
// command 0x00
// Send an ack
void ack(serdata data){
  is_alive=1;
  usart0_tx(0x00);
}

// command 0x01
// Set motor speeds and send an ack
void set_drive(serdata data){
  target_lvel = data[1];
  target_rvel = data[0];
  usart0_tx(0x00);
}

// command 0x02
// Send analog data
void send_analog(serdata data){
  //usart0_tx(analog[adcmap[data[0]]]);
  usart0_tx(((uint8_t)(fil[data[0]]>>20)));
}

// command 0x03
// get state of start switch
void button_pressed(serdata data) {
  usart0_tx(digitalRead(53));
}

// command 0x04
// get state of bump sensors
void get_bump(serdata data) {
  char out = digitalRead(51) << 3;
  out += digitalRead(52) << 2;
  out += digitalRead(22) << 1;
  out += digitalRead(24);
  usart0_tx(out);
}

// command 0x05
// set aux motor
void set_motor(serdata data) {
  // data[1] is index of motor: 0 helix, 1 sucker, 2 door
  // data[0] is new value
  if (data[1] == 2) {
    if (data[0] != 0) digitalWrite(35, HIGH);
    else digitalWrite(35, LOW);
    
  } else if (data[1] == 1) {
    if (data[0] != 0) digitalWrite(37, HIGH);
    else digitalWrite(37, LOW);
    
  } else if (data[1] == 0) {
    if (data[0] != 0) digitalWrite(39, HIGH);
    else digitalWrite(39, LOW);
  }   
    
  usart0_tx(0x00);
  
  drive(current_lvel, current_rvel);
}

void get_ball_cnt(serdata data) {
  usart0_tx(ball_cnt);
  ball_cnt = 0;
}

// How many bytes of data will follow each command?
unsigned char commands[] = {
  0, 2, 1, 0, 0, 2, 0
};

// What function shall be called to respond to each command?
responder responses[] = {
  &ack,
  &set_drive,
  &send_analog,
  &button_pressed,
  &get_bump,
  &set_motor,
  &get_ball_cnt
};
