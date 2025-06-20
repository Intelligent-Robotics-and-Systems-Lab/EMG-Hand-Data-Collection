/* EMG Sensor Test - Kara Schuler
   Last updated 1/11/2025

EMG sensors should be connected to pins A0, A1, A2

Open the Serial Plotter (Tools > Serial Plotter)
  value 1 = A0
  value 2 = A1
  value 3 = A2

Based on Arduino Example 1: Analog Read - Single Sensor: https://learn.sparkfun.com/tutorials/getting-started-with-the-myoware-20-muscle-sensor-ecosystem/arduino-example-1-analog-read---single-sensor
*/

void setup() 
{
  Serial.begin(9600);
}

void loop() 
{  
  // read voltage from the three sensors
  int a0v0 = analogRead(A0);
  int a1v0 = analogRead(A1);
  int a2v0 = analogRead(A2);

  Serial.print(a0v0); Serial.print(",");
  Serial.print(a1v0); Serial.print(",");
  Serial.println(a2v0);

  delay(50); // to avoid overloading the serial terminal
}