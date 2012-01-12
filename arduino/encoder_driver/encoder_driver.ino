int tickl=0,tickr=0,dir=0;;

void x_int_init(void);

ISR(PCINT0_vect){
  if(((PINB>>2)^(PINB>>3))&1){
    tickl++;
  }else{
    tickl--;
  }
}

void setup(){
  Serial.begin(9600);
  pinMode(48, OUTPUT);
  pinMode(49, OUTPUT);
  pinMode(52, OUTPUT);
  pinMode(53, OUTPUT);
  digitalWrite(49,HIGH);
  digitalWrite(52,LOW);
  digitalWrite(48,~dir);
  digitalWrite(53,dir);
  x_int_init();
  sei();
}

void loop(){
Serial.print(tickl);
Serial.print("   ");
delay(10);
Serial.println(tickr);
delay(10);
  
if(millis()%2000>1000){
  digitalWrite(48,1);
  digitalWrite(53,0);
}else{
  digitalWrite(48,0);
  digitalWrite(53,1);
}
}

void x_int_init(void){
  PCICR |= 0x01; //enable pin change interrupts for pcint7:0
  PCMSK0 = (1<<PCINT2); //mask pcint7:0 to just pcint2
}
