/*
  MoniQuarium - Smart Aquarium ESP32 Arduino Client
  Mengirim data ADC / sensor ke Web Backend Server menggunakan HTTP POST.
  
  Sebelum mengunggah kode ini:
  1. Sesuaikan SSID & Password Wi-Fi Anda.
  2. Masukkan alamat IP Server Web (komputer yang menjalankan app.py) Anda.
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> // Library "ArduinoJson" oleh Benoit Blanchon (Instal via Library Manager)

// Konfigurasi Wi-Fi
const char* ssid = "SSID_WIFI_ANDA";
const char* password = "PASSWORD_WIFI_ANDA";

// Konfigurasi Server (Ubah [IP_ADDRESS_SERVER] dengan IP laptop/server Anda)
// Contoh: "http://192.168.1.10:5000/api/data"
const char* serverUrl = "http://[IP_ADDRESS_SERVER]:5000/api/data";

// Definisikan Pin ADC
#define PIN_TEMP_SENSE 36  // GPIO36 (VP) - Analog input
#define PIN_PH_SENSE   39  // GPIO39 (VN) - Analog input
#define PIN_TURB_SENSE 34  // GPIO34      - Analog input
#define PIN_LEVEL_SENSE 35 // GPIO35      - Analog input

void setup() {
  Serial.begin(115200);
  
  // Hubungkan ke Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi Network. IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Hanya jalankan jika terhubung ke Wi-Fi
  if (WiFi.status() == WL_CONNECTED) {
    
    // 1. Membaca Nilai Analog ADC dari Sensor (0 - 4095 pada ESP32)
    int adcTemp = analogRead(PIN_TEMP_SENSE);
    int adcPh = analogRead(PIN_PH_SENSE);
    int adcTurb = analogRead(PIN_TURB_SENSE);
    int adcLevel = analogRead(PIN_LEVEL_SENSE);
    
    // 2. Mengonversi Nilai ADC ke Nilai Parameter Fisik (Simulasi Konversi)
    // Kalibrasi ini disesuaikan dengan karakteristik sensor Anda
    
    // Simulasi sensor Suhu (misal: DS18B20 atau thermistor LM35)
    // Rumus konversi disesuaikan, di bawah ini adalah simulasi pembacaan suhu
    float temperature = (adcTemp / 4095.0) * 40.0 + 10.0; // Rentang 10 - 50 °C
    
    // Simulasi sensor pH air (misal: Analog pH Meter Kit v1.1)
    float ph = (adcPh / 4095.0) * 14.0; // Rentang 0 - 14 pH
    
    // Simulasi sensor kekeruhan air/Turbidity (mengukur kejernihan air)
    // 100% = sangat jernih (ADC rendah/tinggi tergantung jenis sensor), 0% = sangat keruh
    float turbidity = (adcTurb / 4095.0) * 100.0; // Rentang 0 - 100 %
    
    // Simulasi sensor ketinggian air (Water Level Sensor)
    float water_level = (adcLevel / 4095.0) * 100.0; // Rentang 0 - 100 %
    
    // Tampilkan di Serial Monitor
    Serial.println("---------- DATA ADC ----------");
    Serial.printf("Suhu Air: %.2f °C (ADC: %d)\n", temperature, adcTemp);
    Serial.printf("pH Air  : %.2f pH (ADC: %d)\n", ph, adcPh);
    Serial.printf("Kejernihan: %.2f %% (ADC: %d)\n", turbidity, adcTurb);
    Serial.printf("Level Air : %.2f %% (ADC: %d)\n", water_level, adcLevel);

    // 3. Serialisasi ke format JSON
    StaticJsonDocument<200> doc;
    doc["temperature"] = temperature;
    doc["ph"] = ph;
    doc["turbidity"] = turbidity;
    doc["water_level"] = water_level;
    
    String jsonPayload;
    serializeJson(doc, jsonPayload);
    
    // 4. Kirim HTTP POST Request ke Server
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server Response Code: " + String(httpResponseCode));
      Serial.println("Response Payload: " + response);
    } else {
      Serial.print("Error sending POST request: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  } else {
    Serial.println("WiFi Disconnected! Reconnecting...");
    WiFi.begin(ssid, password);
  }
  
  // Kirim data setiap 10 detik
  delay(10000);
}
