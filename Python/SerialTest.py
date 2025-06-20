import serial
import time
import msvcrt  # For keypress detection on Windows

#Run this in the CMD window, it does not work in Pycharm

# Set the correct port and baud rate for your ESP32
ser = serial.Serial('COM4', 115200)  # Use 'COM4' as the port

# Add a small delay to ensure the ESP32 is ready
time.sleep(2)

# Wait for the serial connection to establish
time.sleep(2)

print("Press a key (0-9 or A-Z) to send it to the ESP32. Press 'q' to quit.")

while True:
    # Wait for a key press
    print("Waiting for key press...")
    key = msvcrt.getch()  # Read a single byte key press
    print(f"Key pressed (raw): {key}")  # Debug: Show the raw key pressed
    print(f"Key pressed (decoded): {key.decode()}")  # Debug: Show the decoded key pressed

    # Check if the key is 'q' (quit)
    if key == b'q':  # 'q' is the exit key
        print("Exiting...")
        break

    # Send the pressed key to ESP32
    ser.write(key)  # Send the key pressed as a byte
    print(f"Sent: {key.decode()}")  # Debug: Show what was sent

    # Ensure that the script waits until a response is available
    while ser.in_waiting == 0:  # Check if there is data to read
        time.sleep(0.1)  # Wait for a response from the ESP32

    # Read the response from ESP32
    response = ser.read(ser.in_waiting)  # Read all available data
    print(f"Received: {response.decode()}")  # Print the response from ESP32

ser.close()  # Close the serial connection
