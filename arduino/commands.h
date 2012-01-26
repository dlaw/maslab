#include "qik.h"
#include <Arduino.h>

// serdata is an array of volatile unsigned chars
typedef volatile unsigned char serdata[];

// responder is the type of a function that takes serdata and returns void
typedef void (*responder) (serdata);

// command 0x00
// Send an ack
void ack(serdata data){
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
  usart0_tx(analog[adcmap[data[0]]]);
}

// command 0x03
// get state of start switch
void button_pressed(serdata data) {
  usart0_tx(digitalRead(53));
}

// command 0x04
// get state of bump sensors
void get_bump(serdata data) {
  char out = digitalRead(52) << 5;
  out += digitalRead(51) << 4;
  out += digitalRead(50) << 3;
  out += digitalRead(49) << 2;
  out += digitalRead(48) << 1;
  out += digitalRead(47);
  usart0_tx(out);
}

// command 0x05
// set aux motor
void set_motor(serdata data) {
  // data[1] is index of motor: 0 helix, 1 sucker, 2 door
  // data[0] is new value
  if (data[1] == 2)
    digitalWrite(8, data[0] ? HIGH : LOW);
  else
    digitalWrite(data[1] ? 6 : 7, data[0] ? HIGH : LOW);
    
  usart0_tx(0x00);
}

// How many bytes of data will follow each command?
unsigned char commands[] = {
  0, 2, 1, 0, 0, 2
};

// What function shall be called to respond to each command?
responder responses[] = {
  &ack,
  &set_drive,
  &send_analog,
  &button_pressed,
  &get_bump,
  &set_motor
};
