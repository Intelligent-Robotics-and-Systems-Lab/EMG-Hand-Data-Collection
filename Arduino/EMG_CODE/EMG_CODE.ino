#include <ESP32Servo.h>

Servo servo1;
Servo servo2;
int servoPin1 = 26;
int servoPin2 = 4;
float currentPos1 = 180.0; // Initialize to 180 degrees with float
float currentPos2 = 180.0; // Initialize to 180 degrees with float
float targetPos1 = 180.0; // Initialize to 180 degrees with float
float targetPos2 = 180.0; // Initialize to 180 degrees with float

unsigned long previousMillis = 0; // Store the last time the positions were printed
const int moveInterval = 10; // Interval at which to move the servos (10 milliseconds)
const int moveTime = 3000; // Time to move to the target position (3000 milliseconds or 3 seconds)
bool movingToPositions = false; // Flag to indicate if moving to positions

// Array to hold predefined positions
float predefinedPositions[5][2] = {
  {170.0, 155.0},    // Open Hand 
  {95.0, 77.0},      // Cylinder 
  {106.0, 155.0},    // Pinch
  {74.0, 62.4},      // Ball
  {43.4, 41.6},      // Cone 
};

void setup() {
  Serial.begin(115200); // Initialize serial communication
  delay(1000); // Give the Serial Monitor time to start
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  servo1.write(currentPos1); // Set servo 1 to 180 degrees
  servo2.write(currentPos2); // Set servo 2 to 180 degrees
}

void loop() {
  // Check for mode switch commands from Serial Monitor
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim(); // Remove any whitespace or newline characters
    Serial.println(input);

    // Convert input to an integer for position selection
    int positionIndex = input.toInt();

    // Ensure the input is within the valid range (0 to 4)
    if (positionIndex >= 0 && positionIndex <= 4) {
      // Retrieve target positions from predefined positions array
      targetPos1 = predefinedPositions[positionIndex][0];
      targetPos2 = predefinedPositions[positionIndex][1];

      // Move the servos to the target positions over moveTime (3 seconds)
      moveServos(targetPos1, targetPos2);
    } else {
      //Serial.println("Invalid input. Please enter a number between 0 and 4.");
    }
  }
}

void moveServos(float target1, float target2) {
  // Set flag to indicate moving to positions
  movingToPositions = true;

  // Move the servos to the target positions over moveTime (3 seconds)
  unsigned long startTime = millis();
  while (millis() - startTime < moveTime) {
    // Calculate the intermediate positions
    unsigned long elapsedTime = millis() - startTime;
    float fraction = (float)elapsedTime / moveTime;
    float newPos1 = currentPos1 + (target1 - currentPos1) * fraction;
    float newPos2 = currentPos2 + (target2 - currentPos2) * fraction;

    // Move the servos to the intermediate positions (cast to int for servo write)
    servo1.write(newPos1);
    servo2.write(newPos2);

    // Print the current positions with 2 decimal places
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= moveInterval) {
      previousMillis = currentMillis;
      //Serial.print(newPos1, 2);
      //Serial.print("-");
      //Serial.println(newPos2, 2);
    }

    // Delay for moveInterval before updating again
    delay(moveInterval);
  }

  // Ensure the servos reach the exact target positions at the end
  currentPos1 = target1;
  currentPos2 = target2;
  servo1.write(currentPos1);
  servo2.write(currentPos2);
  //Serial.print(currentPos1, 2);
  //Serial.print("-");
  //Serial.println(currentPos2, 2);

  // Reset flags after completing movement
  movingToPositions = false;
}
