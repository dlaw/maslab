void coast(char motor);
void drive(char motor, char vel);
void usart2_init(unsigned int baud);
void usart2_tx(unsigned char data);

unsigned int baud = 3; //250k baud rate
unsigned int baud2 = 25; //38.4k baud rate

void setup(){
  int serial;
  //Serial.begin(384000);
  usart2_init(baud2);
  usart2_tx(0xaa);
}

void loop(){
  char go;
  for (go=-127;go<127;go++){
    drive(1,go);
    drive(0,-1*go);
    delay(100);
  }
}

void coast(char motor){
  usart2_tx(0x86+motor); 
}

void drive(char motor, char vel){
  char dir;
  if (vel >=0){
    dir = 0x88 + motor*4;
  }
  else{
    dir = 0x8a + motor*4;
    vel ^= 0xFF;
  }
  usart2_tx(dir);
  usart2_tx(vel&0x7F);
}

void usart2_init(unsigned int baud){
  UBRR2H = (unsigned char)(baud >> 8); //set baud rate register to correct baud
  UBRR2L = (unsigned char)baud;
  UCSR2B = (1<<RXEN2)|(1<<TXEN2); //enable tx and rx
  UCSR2C = (1<<USBS2)|(3<<UCSZ20); //set data format (8 bit w/ 2 stops)
}

void usart2_tx(unsigned char data){
  while (!(UCSR2A & (1<<UDRE2))); //wait until all transmissions are done
  UDR2 = data;  //shove the data into the buffer
}

