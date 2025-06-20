#Running in CMD
# 1. cd C:\Users\LBB10\Desktop\Reserach
# 2. .venv\Scripts\activate
# 3. cd C:\Users\LBB10\Desktop\Reserach\.venv
# 4. python IntegrationTest.py
# 5. python IntegrationTest.py > output_log.txt 2>&1  If you want to save the output
# Hit Ctrl + C to stop file

import numpy as np
import pandas as pd
import joblib
import time
import serial
from extract_features import features
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# ESP32 Communication Functions
def initialize_serial_connection(port='COM4', baudrate=115200):
    """Initializes the serial connection to the ESP32."""
    ser = serial.Serial(port, baudrate)
    time.sleep(2)  # Allow the ESP32 to initialize
    return ser

def send_integer_to_esp32(ser, value):
    """Sends an integer (0-9) to the ESP32."""
    if 0 <= value <= 9:
        ser.write(str(value).encode())  # Convert integer to string and send
        print(f"Sent to ESP32: {value}")

        # Wait for a response
        while ser.in_waiting == 0:
            time.sleep(0.1)

        # Read and print response
        response = ser.read(ser.in_waiting).decode()
        print(f"Received from ESP32: {response}")
    else:
        print("Invalid value. Please provide an integer between 0 and 9.")

# Initialize Serial Connection
ser = initialize_serial_connection()

# Load trained classifier
clf = joblib.load("svmKernel_classifier01_prob.pkl")
scaler = joblib.load("scaler.pkl")

# Load recorded EMG dataset
data = pd.read_csv('Data/DB1_E3_S23-25rebalanced.csv')

# Extract relevant EMG channels and labels
emg = data.iloc[:, [6, 8, 9]].to_numpy()
restimulus = data.iloc[:, 10].to_numpy()

# Define window parameters
windowTime = 0.1  # 100ms window
samplingFreq = 100  # Hz
windowLen = int(windowTime * samplingFreq)  # Number of samples per window
overlap = 0.5  # 50% overlap
step = int(windowLen * (1 - overlap))  # Step size for overlapping windows

# Simulated real-time classification
predictions = []
feat2compare = []

print("Starting live data simulation...\n")

for start in range(0, len(emg) - windowLen, step):
    finish = start + windowLen

    # Extract current data window
    current_window = emg[start:finish, :]

    # Extract corresponding label (ground truth)
    true_label = np.bincount(restimulus[start:finish]).argmax()  # Mode of labels in window
    feat2compare.append(true_label)

    # Extract features from the current window
    X_live, _ = features(current_window, restimulus[start:finish], windowLen, overlap)

    # Scale the features
    X_live = scaler.transform(X_live)

    # Predict class for the current window
    cur_pred = clf.predict(X_live)[0]  # Extract single prediction
    probabilities = clf.predict_proba(X_live)

    predictions.append(cur_pred)

    # Print results in a live format
    #print(f"Time step {start//step + 1}: True Label: {true_label}, Predicted: {cur_pred}, Probability: {probabilities}")

    # Send prediction to ESP32
    send_integer_to_esp32(ser, cur_pred)

# Close Serial Connection
ser.close()

# Evaluate Results
conf_matrix = confusion_matrix(feat2compare, predictions)

# Define a color map
cmap = sns.color_palette("coolwarm", as_cmap=True)

# Create a mask to highlight correct predictions (diagonal elements)
mask = np.zeros_like(conf_matrix, dtype=bool)
np.fill_diagonal(mask, True)

plt.figure(figsize=(8, 6))
sns.set(font_scale=1.2)

# Plot the full confusion matrix
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap=cmap, annot_kws={"size": 14},
            cbar_kws={'label': 'Prediction Frequency'},
            linewidths=0.5, linecolor='gray')

# Overlay accurate predictions with a different color
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap="Blues", annot_kws={"size": 14},
            cbar=False, mask=~mask, linewidths=0.5, linecolor='gray', alpha=0.5)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix with Highlighted Accurate Predictions")
plt.show()

accuracy = accuracy_score(feat2compare, predictions)
print(f"Simulated Live Classification Accuracy: {accuracy * 100:.2f}%")
