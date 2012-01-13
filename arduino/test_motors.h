void fixed_delay(int delval) {
  for(int i = 0; i < 16000; i++) {
    for(int j = 0; j < delval; j++) {
      __asm__("nop\n\t"); 
    }
  }
}

void test_motors(void) {
  drive(127, -127);
  
  // delay for 500 ms
  fixed_delay(500);
  
  drive(-127, 127);
  
  fixed_delay(500);
  
  usart0_tx(0x00);
}