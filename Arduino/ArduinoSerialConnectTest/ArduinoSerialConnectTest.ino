void setup() {
  Serial.begin(115200);  // Initialize the serial communication at 115200 baud rate
  while (!Serial);       // Wait for serial to be ready (not always necessary, but good practice)
  delay(1000);
  Serial.println("ESP32 ready. Waiting for data...");
}

void loop() {
  if (Serial.available() > 0) {
    char receivedChar = Serial.read();  // Read the received character from serial
    Serial.print("Received: ");
    Serial.println(receivedChar);  // Print the received character

    Serial.write(receivedChar);  // Echo the received character back to the sender
  }
}