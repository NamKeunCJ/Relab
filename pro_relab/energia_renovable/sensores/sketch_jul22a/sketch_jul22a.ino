#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Adafruit_INA219.h>
#include <LiquidCrystal_I2C.h>

// 🌐 WiFi Config
const char* ssid = "prueba";
const char* password = "del1almil";
const char* serverUrl = "http://10.130.131.232:5000/api/voltaje";

// 🔢 Código único
int codigoGenerado = 0;

// Pines
const int flujoPin = 14;     // Pin sensor de flujo

// Variables globales
volatile int pulseCount = 0;
volatile unsigned long lastPulseTime = 0;  // <-- Para evitar rebotes

float caudal = 0.0;
float voltaje_dc_hidrica = 0.0;
float amperios = 0.0;
float presionBar = 0.0;  // presión simulada

const float PULSOS_POR_LITRO = 4.8;
//const float PULSOS_POR_LITRO = 25.8;
unsigned long lastMillis = 0;

// Sensores
Adafruit_INA219 ina219;
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Dirección típica de LCD I2C

// --- Interrupción de flujo con filtro anti-rebote ---
void IRAM_ATTR contarPulsos() {
  unsigned long tiempoActual = micros();
  if (tiempoActual - lastPulseTime > 200) {  // Evita rebotes: mínimo 200 µs entre pulsos (5 kHz máx)
    pulseCount++;
    lastPulseTime = tiempoActual;
  }
}

// 🔢 Generar código aleatorio
int generarCodigo() {
  return random(100000, 999999);
}

void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
  codigoGenerado = generarCodigo();
  Serial.printf("Código único: %d\n", codigoGenerado);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  randomSeed(analogRead(39)); // Código aleatorio

  connectWiFi();

  // Inicializar I2C
  Wire.begin(21, 22); // SDA, SCL

  // Inicializar INA219
  if (!ina219.begin()) {
    Serial.println("⚠️ INA219 no detectado. Verifica conexiones.");
    while (1);
  }
  ina219.setCalibration_32V_2A();
  Serial.println("INA219 listo.");

  // Inicializar LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("  Sistema Hidrico  ");
  delay(2000);
  lcd.clear();

  // Sensor flujo
  pinMode(flujoPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(flujoPin), contarPulsos, RISING);
}

void loop() {
  if (millis() - lastMillis >= 1000) {
    lastMillis = millis();

    // Medir flujo
    detachInterrupt(digitalPinToInterrupt(flujoPin));
    float pulsos = pulseCount;
    pulseCount = 0;
    attachInterrupt(digitalPinToInterrupt(flujoPin), contarPulsos, RISING);

    caudal = pulsos / PULSOS_POR_LITRO; // L/min
    float caudalCm3Seg = (caudal * 1000.0) / 60.0; // cm³/s

    // Medir INA219
    voltaje_dc_hidrica = ina219.getBusVoltage_V();
    amperios = ina219.getCurrent_mA() / 1000.0; // A

    // Mostrar en serial
    Serial.printf("Voltaje: %.2f V\n", voltaje_dc_hidrica);
    Serial.printf("Corriente: %.2f A\n", amperios);
    Serial.printf("Pulsos: %.0f\n", pulsos);
    Serial.printf("Caudal: %.2f L/min | %.2f Cm3/s\n", caudal, caudalCm3Seg);
    Serial.printf("Presion: %.2f bar\n", presionBar);
    Serial.println("--------------------------");

    // Mostrar en LCD
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("V:");
    lcd.print(voltaje_dc_hidrica, 2);
    lcd.print(" I:");
    lcd.print(amperios, 2);

    lcd.setCursor(0, 1);
    lcd.print("F:");
    lcd.print(caudal, 1);
    lcd.print("L P:");
    lcd.print(presionBar, 2);

    // Enviar al servidor
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");

      String json = "{";
      json += "\"dispositivo\":\"hidrica\",";
      json += "\"voltaje\":" + String(voltaje_dc_hidrica, 2) + ",";
      json += "\"codigo\":" + String(codigoGenerado) + ",";
      json += "\"caudal\":" + String(caudal, 2) + ",";
      json += "\"presion\":" + String(presionBar, 2) + ",";
      json += "\"corriente\":" + String(amperios, 2);
      json += "}";

      int response = http.POST(json);
      Serial.printf("Respuesta: %d\n", response > 0 ? response : 0);
      if (response <= 0) Serial.println(http.errorToString(response));
      http.end();
    } else {
      Serial.println("WiFi no conectado");
    }
  }
}
