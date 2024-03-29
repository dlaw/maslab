#include <avr/interrupt.h>

// DO NOT MODIFY

void usart0_init(unsigned int baud){
  UBRR0H = (unsigned char)(baud >> 8); //set baud rate register to correct baud
  UBRR0L = (unsigned char)baud;
  UCSR0B = (1<<RXEN0)|(1<<TXEN0)|(1<<RXCIE0); //enable tx, rx, and rx complete interrupt
  UCSR0C = (1<<USBS0)|(3<<UCSZ00); //set data format (8 bit w/ 1 stop)
}

void usart0_tx(unsigned char data){
  while (!(UCSR0A & (1<<UDRE0))); //wait until all transmissions are done
  UDR0 = data;  //shove the data into the buffer
}

unsigned char usart0_rx(void){
  while (!(UCSR0A & (1<<RXC0))); //wait for data to come in
  return UDR0;  //return serial data
}

void usart1_init(unsigned int baud){
  UBRR1H = (unsigned char)(baud >> 8); //set baud rate register to correct baud
  UBRR1L = (unsigned char)baud;
  UCSR1B = (1<<RXEN1)|(1<<TXEN1); //enable tx and rx
  UCSR1C = (1<<USBS1)|(3<<UCSZ10); //set data format (8 bit w/ 2 stops)
}

void usart1_tx(unsigned char data){
  while (!(UCSR1A & (1<<UDRE1))); //wait until all transmissions are done
  UDR1 = data;  //shove the data into the buffer
}

unsigned char usart1_rx(void){
  while (!(UCSR1A & (1<<RXC1))); //wait for data to come in
  return UDR1;  //return serial data
}
