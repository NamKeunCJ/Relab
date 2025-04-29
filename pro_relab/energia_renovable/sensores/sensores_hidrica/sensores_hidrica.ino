#include <WiFi.h>
#include <HTTPClient.h>

// 🌐 WiFi Config
//const char* ssid = "ADMON";
//const char* password = "803iu91z";
const char* ssid = "FAMILIA-RUEDA";
const char* password = "Uchiha20162025";
const char* serverUrl = "http://192.168.101.13:5000/api/voltaje";

// 🔢 Código único
int codigoGenerado = 0;

// 🔌 Valores simulados
float voltaje_dc_hidrica = 0.0;
float caudalLitrosMin = 0.0;
float presionBar = 0.0;
float amperios = 0.0;

// 🔢 Generar código aleatorio de 6 dígitos
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
  randomSeed(analogRead(39)); // Para código aleatorio
  connectWiFi();
}

void loop() {
  // Simular valores
  float presionPa = presionBar * 100000;
  float basePresion = presionPa / 100000;
  int exponentePresion = 5;

  float caudalCm3Seg = (caudalLitrosMin * 1000.0) / 60.0;
  float baseCaudal = caudalCm3Seg / 1000;
  int exponenteCaudal = 3;

  // Imprimir datos por serie
  Serial.printf("Voltaje_dc_hidrica: %.2f\n", voltaje_dc_hidrica);
  Serial.printf("Caudal: %.2f e%d cc/s\n", baseCaudal, exponenteCaudal);
  Serial.printf("Corriente: %.2f A\n", amperios);
  Serial.printf("Presion: %.2f e%d Pa\n", basePresion, exponentePresion);
  Serial.println("--------------------------");

  // Enviar al servidor solo el voltaje y el código
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"dispositivo\":\"hidrica\",";
    json += "\"voltaje\":" + String(voltaje_dc_hidrica, 2) + ",";
    json += "\"codigo\":" + String(codigoGenerado) + ",";
    json += "\"caudal\":" + String(caudalLitrosMin, 2) + ",";
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

  // Aumentar valores simulados
  voltaje_dc_hidrica = random(4800, 5400) / 100.0; // 48.00V - 54.00V

  // Calcular amperaje estimado con una resistencia de ~24.2 ohm
  amperios = voltaje_dc_hidrica / 24.2;


  // Caudal y presión simulados con rango razonable
  caudalLitrosMin = random(1000, 4000) / 100.0;        // 10.00 – 40.00 L/min
  presionBar = random(80, 150) / 10.0;                 // 8.0 – 15.0 bar



  delay(1000);
}
