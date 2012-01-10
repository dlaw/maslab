void coast(char motor);
void drive(char motor, char vel);

void setup(){
  int serial;
  Serial.begin(384000);
  Serial2.begin(384000);
  Serial2.write(0xAA);
}

void loop(){
  if (Serial.available() > 0) {
    serial = Serial.read();
  
  }
  char go;
  for (go=-127;go<127;go++){
    drive(1,go);
    drive(0,-1*go);
    delay(100);
  }
}

void coast(char motor){
  Serial2.write(0x86+motor); 
}

void drive(char motor, char vel){
  char dir;
  if (vel >=0){
    dir = 0x88 + motor*4;
  }else{
    dir = 0x8a + motor*4;
  }
  Serial2.write(dir);
  Serial2.write(vel&0x7F);
}
