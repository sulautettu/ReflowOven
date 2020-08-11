
// include the library code:

#include <max6675.h>   // Thermocouple ADC
#include "SoftPWM.h"  // drives heating relay


//max6675 data pins
int thermoDO = 4;   
int thermoCS = 5;
int thermoCLK = 6;

int relayPin = 13;

float temp;
float *ptemp;


MAX6675 thermocouple(thermoCLK, thermoCS, thermoDO);



void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  pinMode(relayPin, OUTPUT);
  SoftPWMBegin();

  // Create and set pin 13 to 0 (off)
  SoftPWMSet(relayPin, 0);
  SoftPWMSetFadeTime(relayPin, 100, 100);

}


void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}   

int checkSerial(){
  int x = 255;
  if (Serial.available() > 0) {
    x = Serial.read();
    //Serial.println(x);
    serialFlush();
    
  }
  return x;
}

void readTemp (){
  temp = thermocouple.readCelsius();
  ptemp = &temp;
  Serial.print("Temp: ");
  Serial.println(*ptemp,4);
  
}


// check constantly new command from serial (USB connection) 
// commands 0 to 100 are Power setting for heating in %
// command 101 is to send temperature to PC
 
void loop() {
int  serialIn = checkSerial();


  if  (0<= serialIn && serialIn <= 100){
      SoftPWMSetPercent(relayPin,serialIn ); //adjusting PWM pulse in range 0-100%
      
      
  }

  if (serialIn == 101){
    readTemp();
  }
  
delay(10);
}
