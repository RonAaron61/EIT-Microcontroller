//https://github.com/RonAaron61/EIT-Microcontroller/
//Library Source and examples:
//https://github.com/MajicDesigns/MD_AD9833/tree/main
//https://github.com/adafruit/Adafruit_ADS1X15/blob/master/examples/singleended/singleended.ino

#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <MD_AD9833.h>
#include <SPI.h>

Adafruit_ADS1115 ads;

//#define FNC_PIN 34
#define Frequency 30000  // Frequency = 30kHz

const uint8_t PIN_DATA = 35;  ///< SPI Data pin number
const uint8_t PIN_CLK = 36;    ///< SPI Clock pin number
const uint8_t PIN_FSYNC = 34; ///< SPI Load pin number (FSYNC in AD9833 usage)
MD_AD9833  AD(PIN_DATA, PIN_CLK, PIN_FSYNC); // Arbitrary SPI pins


int LED1 = 39;
int LED2 = 40;
int LED_BuIn = 15;  //Build In LED on Microcontroller

int mux[16][4] = {{0,0,0,0}, {0,0,0,1}, {0,0,1,0}, {0,0,1,1}, {0,1,0,0}, {0,1,0,1}, {0,1,1,0}, {0,1,1,1}, {1,0,0,0}, {1,0,0,1}, {1,0,1,0}, {1,0,1,1}, {1,1,0,0}, {1,1,0,1}, {1,1,1,0}, {1,1,1,1}};
float result[208];

byte* ddata = reinterpret_cast<byte*>(&result); // pointer for transferData()
size_t pcDataLen = sizeof(result);

char ser;

#define SDA 8
#define SCL 9
int16_t adc;
float voltage;

void setup(){
  Serial.begin(115200);
  
  //AD9833 object
  AD.begin();
  AD.setFrequency(MD_AD9833::CHAN_0, Frequency);
  AD.setMode(MD_AD9833::MODE_OFF);  //Set AD9833 OFF

  // AD1115
  Wire.begin(SDA, SCL);
  ads.setGain(GAIN_ONE);  // 1x gain  +/- 4.096V  1 bit = 0.125mV
  if (!ads.begin())
  {
    while (1){
      Serial.println("Failed to initialize ADS.");
    }
  }

  pinMode(1,OUTPUT);
  pinMode(2,OUTPUT);
  pinMode(3,OUTPUT);
  pinMode(4,OUTPUT);

  pinMode(5,OUTPUT);
  pinMode(6,OUTPUT);
  pinMode(7,OUTPUT);
  pinMode(10,OUTPUT);

  pinMode(11,OUTPUT);
  pinMode(12,OUTPUT);
  pinMode(13,OUTPUT);
  pinMode(14,OUTPUT);

  pinMode(16,OUTPUT);
  pinMode(17,OUTPUT);
  pinMode(18,OUTPUT);
  pinMode(21,OUTPUT);

  //LED
  pinMode(LED1,OUTPUT);
  pinMode(LED2,OUTPUT);
  pinMode(LED_BuIn,OUTPUT);

  digitalWrite(LED1, HIGH);
  digitalWrite(LED2,1);
  digitalWrite(LED_BuIn, 1);
  delay(1000);
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, 0);
  digitalWrite(LED_BuIn, 0);
}

void Get_Data(int n_elec = 16){
  int a = 0;
  int b = 0;
  int iter = 0;
  
  AD.setMode(MD_AD9833::MODE_SINE);
  
  digitalWrite(LED1, HIGH);
  for (int i=0; i<n_elec; i++){
    a = i+1;
    if (a > n_elec-1){
      a -= n_elec;
    }

    digitalWrite(1,mux[i][0]);
    digitalWrite(2,mux[i][1]);
    digitalWrite(3,mux[i][2]);
    digitalWrite(4,mux[i][3]);

    digitalWrite(5,mux[a][0]);
    digitalWrite(6,mux[a][1]);
    digitalWrite(7,mux[a][2]);
    digitalWrite(10,mux[a][3]);

    for (int j = 0; j<n_elec; j++){
      b = j+1;
      if (b > n_elec-1){
        b -= n_elec;
      }

      if ((j == i) || (j == a) || (b ==i)){
        continue;
      }

      digitalWrite(11,mux[j][0]);
      digitalWrite(12,mux[j][1]);
      digitalWrite(13,mux[j][2]);
      digitalWrite(14,mux[j][3]);

      digitalWrite(16,mux[b][0]);
      digitalWrite(17,mux[b][1]);
      digitalWrite(18,mux[b][2]);
      digitalWrite(21,mux[b][3]);

      digitalWrite(LED_BuIn, mux[j][3]);

      delay(800);

      adc = ads.readADC_SingleEnded(0);
      //voltage = ads.computeVolts(adc);
      result[iter] = ads.computeVolts(adc);
      iter++;
    }
  }
  
  AD.setMode(MD_AD9833::MODE_OFF);
  
  digitalWrite(LED1, LOW);
  digitalWrite(LED_BuIn, LOW);
  digitalWrite(LED2, HIGH);
  delay(2000);
  digitalWrite(LED2, LOW);
}


void Tester(int a, int b, int c, int d){
  float adc;
  
  AD.setMode(MD_AD9833::MODE_SINE);
  
  digitalWrite(LED1, HIGH);

  digitalWrite(1,mux[a][0]);
  digitalWrite(2,mux[a][1]);
  digitalWrite(3,mux[a][2]);
  digitalWrite(4,mux[a][3]);

  digitalWrite(5,mux[b][0]);
  digitalWrite(6,mux[b][1]);
  digitalWrite(7,mux[b][2]);
  digitalWrite(10,mux[b][3]);

  digitalWrite(11,mux[c][0]);
  digitalWrite(12,mux[c][1]);
  digitalWrite(13,mux[c][2]);
  digitalWrite(14,mux[c][3]);

  digitalWrite(16,mux[d][0]);
  digitalWrite(17,mux[d][1]);
  digitalWrite(18,mux[d][2]);
  digitalWrite(21,mux[d][3]);

  adc = ads.readADC_SingleEnded(0);
  Serial.println(ads.computeVolts(adc));
}


void loop(){
  // Get the Data 
  if(Serial.available() > 0){
    ser = Serial.read();
    if(ser == 'D'){
      Get_Data();
      for (int i=0; i<208;i++){
        Serial.println(result[i],5);
      }
      Serial.println("Done");
    }

    //Set signal to ON and assign electrode 1-2-3-4 only to look and adjust for the closest signal gain
    else if(ser == 'C'){
      Tester(1,2,3,4);
    }
  }
}
