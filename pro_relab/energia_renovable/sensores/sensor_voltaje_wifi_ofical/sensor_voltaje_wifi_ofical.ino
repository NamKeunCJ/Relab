#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ZMPT101B.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ⚡ ZMPT101B Config
#define SENSOR_PIN 34
#define CALIBRATION 1.49
ZMPT101B voltageSensor(SENSOR_PIN, 50.0);

// 🖥️ LCD I2C Config
LiquidCrystal_I2C lcd(0x27, 16, 2);

// 🌐 WiFi Config
const char* ssid = "FAMILIA-RUEDA";
const char* password = "Uchiha20162025";
const char* serverUrl = "http://192.168.101.13:5000/api/voltaje";
//const char* ssid = "ADMON";
//const char* password = "803iu91z";
//const char* serverUrl = "http://172.18.14.183:5000/api/voltaje";
int codigoGenerado = 0;  // Código persistente durante toda la ejecución

float readVoltage(int samples = 100) {
  float sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += voltageSensor.getRmsVoltage() * CALIBRATION;
    delay(5);
  }
  return sum / samples;
}

// 🔢 Generar código aleatorio de 6 dígitos
int generarCodigo() {
  return random(100000, 999999); // Código de 6 dígitos
}

void connectWiFi() {
  WiFi.begin(ssid, password);
  lcd.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  lcd.clear();
  lcd.print("WiFi conectado");
  delay(1000);
}

void setup() {
  Wire.begin(21, 22);
  Serial.begin(115200);
  voltageSensor.setSensitivity(500.0f);
  lcd.init();
  lcd.backlight();
  lcd.print("Iniciando...");
  delay(1000);
  lcd.clear();
  randomSeed(analogRead(39));
  codigoGenerado = generarCodigo();
  Serial.printf("Código único: %d\n", codigoGenerado);

  connectWiFi();
}

void loop() {
  float voltage = readVoltage();
  if (voltage <= 110) {
    voltage = 0.0;
  }
  
  Serial.printf("Voltaje: %.1f V\n", voltage);
  Serial.printf("Codigo: %d\n", codigoGenerado);

  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("VAC: ");
  lcd.print(voltage, 1);
  lcd.print("V");

  lcd.setCursor(0, 1);
  lcd.print("Cod:");
  lcd.print(codigoGenerado);


  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"dispositivo\":\"fotovoltaica\",";
    json += "\"voltaje\":" + String(voltage, 2) + ",";
    json += "\"codigo\":" + String(codigoGenerado) + ",";
    json += "\"caudal\":null,";
    json += "\"presion\":null,";
    json += "\"corriente\":null";
    json += "}";


    int response = http.POST(json);

    Serial.printf("Respuesta: %d\n", response > 0 ? response : 0);
    if (response <= 0) Serial.println(http.errorToString(response));
    
    http.end();
  }
  else {
    Serial.println("WiFi no conectado");
  }
}