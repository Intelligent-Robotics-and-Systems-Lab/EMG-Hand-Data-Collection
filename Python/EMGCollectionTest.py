import serial
import time

# --------------- CONFIG ----------------
PORT = 'COM6'        # Change to your Arduino COM port
BAUDRATE = 9600    # Match your Arduino sketch
TIMEOUT = 2          # seconds

# --------------- CONNECT ----------------
try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
    time.sleep(2)  # Allow time for Arduino reset
    print(f"[INFO] Connected to {PORT} at {BAUDRATE} baud.")
except Exception as e:
    print(f"[ERROR] Could not connect: {e}")
    ser = None

# --------------- READ DATA --------------
if ser:
    try:
        print("[INFO] Starting to read data. Press Ctrl+C to stop.")
        while True:
            if ser.in_waiting:
                line = ser.readline().decode(errors='ignore').strip()
                print(f"[DATA] {line}")
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        ser.close()
        print("[INFO] Serial connection closed.")
else:
    print("[ERROR] Serial not connected.")
