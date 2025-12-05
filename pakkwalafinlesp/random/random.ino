void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0)); // Seed randomness
}

void loop() {


  // Random values
  int v1 = random(70, 106);   // GSR
  int v2 = random(90, 101);   // HEART
  int v3 = 300;               // TEMP (always 300)
  int v4 = random(90, 100);   // AIR QUANTITY
  int v5 = random(100, 501);  // SPO2
  int v6 = random(37, 41);    // extra

  // Build JSON
  String jsonOutput = "{";

  jsonOutput += "\"GSR_DATA\": " + String(v1) + ", ";
  jsonOutput += "\"HEART_DATA\": " + String(v2) + ", ";
  jsonOutput += "\"TEMP_DATA\": " + String(v3) + ", ";
  jsonOutput += "\"AIR_QUA_DATA\": " + String(v4) + ", ";
  jsonOutput += "\"SPO2\": " + String(v5);

  jsonOutput += "}";

  // Print JSON
  Serial.println(jsonOutput);

  delay(2000);
}
