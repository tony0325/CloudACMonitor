#include <PZEM004Tv30.h>  //https://github.com/mandulaj/PZEM-004T-v30
#include <LiquidCrystal_I2C.h> //https://robojax.com/learn/arduino/?vid=robojax_ESP32_LCD
#include <HTTPClient.h>
const char* ssid = "OnHub";
const char* password = "1122334455";
//const char* ssid = "kukui_test";
//const char* password = "youshallnotpa55";
HTTPClient http;
#define RXD1 4
#define TXD1 2
#define RXD2 16
#define TXD2 17
int uploadPeriod = 120000; //ms
 
LiquidCrystal_I2C lcd(0x27, 16, 4); // GPIO21(SDA)/GPIO22(SCL)
PZEM004Tv30 pzem1(&Serial1);
PZEM004Tv30 pzem2(&Serial2);
 
void uploadData(float* volt1, float* volt2, float* cur1, float* cur2, \
                float* powe1, float* powe2, float* ener1, float* ener2, \
                float* pf_1, float* pf_2) {
 
  String url = "https://script.google.com/macros/s/AKfycbxJMNgxQpf-nNXu--A--hL7XQsXWY8_tfWGtVQy2oifhiYBr0M/exec?rssi=" \
  + String(WiFi.RSSI()) \
  + "&voltage1=" + String(*volt1) + "&voltage2=" + String(*volt2) \
  + "&current1=" + String(*cur1) + "&current2=" + String(*cur2) \
  + "&power1=" + String(*powe1) + "&power2=" + String(*powe2) \
  + "&energy1=" + String(*ener1,3) + "&energy2=" + String(*ener2,3) \
  + "&pf1=" + String(*pf_1) + "&pf2=" + String(*pf_2);
 
  
  if ((WiFi.status() == WL_CONNECTED)) {
    http.begin(url);
    int httpCode = http.GET();  
 
    if (httpCode > 0) { 
      String payload = http.getString();
      //Serial.printf("Reply from server：%s\n", payload.c_str());
      Serial.println("HTTP request is done");
    } else {
      Serial.println("[Error] HTTP request is failed!!!");
    }
 
    http.end();
  }
}
 
void setup() {
  Serial.begin(115200);
  Serial1.begin(9600, SERIAL_8N1, RXD1, TXD1);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  WiFi.begin(ssid, password);
 
  for(int counter = 0; counter < 10; counter++) {
    if (WiFi.status() == WL_CONNECTED){
      break;
    }
    else
      Serial.print(".");
      delay(1000);
      if(counter == 6) {
      ESP.restart();
    }
  }
  
  Serial.print("\nIP address：");
  Serial.println(WiFi.localIP() );
  Serial.printf("WIFI RSSI: %d dBm\n", WiFi.RSSI());
  
  //Serial.print("Reset Energy");
  //pzem1.resetEnergy();
  //pzem2.resetEnergy();
 
  Serial.printf("Set address to 0x42\n");
  pzem1.setAddress(0x42);
  pzem2.setAddress(0x42);
 
  lcd.begin();  
  lcd.backlight();
}
 
void loop() {
  
  float volt1 = pzem1.voltage();
  float volt2 = pzem2.voltage();
  Serial.printf("Voltage1: %.2f V / Voltage2: %.2f V\n", volt1, volt2);
  
  float cur1 = pzem1.current();
  float cur2 = pzem2.current();
  Serial.printf("Current1: %.2f A / Current2: %.2f A\n", cur1, cur2);
 
  float powe1 = pzem1.power();
  float powe2 = pzem2.power();
  Serial.printf("Power1: %.2f W / Power2: %.2f W\n", powe1, powe2);
 
  float ener1 = pzem1.energy();
  float ener2 = pzem2.energy();
  Serial.printf("Energy1: %.2f kWh / Energy2: %.2f kWh\n", ener1, ener2);
 
  float freq1 = pzem1.frequency();
  float freq2 = pzem2.frequency();
  Serial.printf("Freq1: %.2f Hz / Freq2: %.2f Hz\n", freq1, freq2);
 
  float pf_1 = pzem1.pf();
  float pf_2 = pzem2.pf();
  Serial.printf("PF1: %.2f / PF2: %.2f\n", pf_1, pf_2);
 
  lcd.clear();// clear previous values from screen
  lcd.printf("Vol1/2:%.0f/%.0fV", volt1, volt2);
  lcd.setCursor(0,1);
  lcd.printf("Pow1/2:%.0f/%.0fW", powe1, powe2);
  lcd.setCursor(0,2);
  lcd.printf("Eng1/2:%.0f/%.0fkWh", ener1, ener2);
  lcd.setCursor(0,3);
  lcd.printf("RSSI:%ddBm", WiFi.RSSI());
  
  uploadData(&volt1, &volt2, &cur1, &cur2, &powe1, &powe2, &ener1, &ener2, &pf_1, &pf_2);
  delay(uploadPeriod);
}
