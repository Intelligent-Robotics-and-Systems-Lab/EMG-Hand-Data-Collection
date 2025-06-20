import numpy as np
import pandas as pd
import joblib
import time
from extract_features import features
from sklearn.metrics import accuracy_score, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler


# Load trained classifier
clf = joblib.load("svmKernel_classifier01_prob.pkl")
scaler = joblib.load("scaler.pkl")


# Load recorded EMG dataset
#data = pd.read_csv('Data/DB1_E3_S1rebalanced.csv')
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

    print(current_window[1,:])

    # Extract corresponding label (ground truth)
    true_label = np.bincount(restimulus[start:finish]).argmax()  # Mode of labels in window
    feat2compare.append(true_label)

    # Extract features from the current window
    X_live, _ = features(current_window, restimulus[start:finish], windowLen, overlap)

    # X_live = scaler.transform(X_live.to_numpy().reshape(1, -1))
    X_live = scaler.transform(X_live)

    # Predict class for the current window
    cur_pred = clf.predict(X_live)
    probabilities = clf.predict_proba(X_live)

    predictions.append(cur_pred)

    # Print results in a live format
    print(f"Time step {start//step + 1}: True Label: {true_label}, Predicted: {cur_pred}, Probability: {probabilities}")

# Evaluate Results
conf_matrix = confusion_matrix(feat2compare, predictions)

# Normalize confusion matrix row-wise to show percentages
conf_matrix_percent = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis] * 100

# Define a color map
cmap = sns.color_palette("coolwarm", as_cmap=True)  # Properly defining cmap before use

# Create a mask to highlight correct predictions (diagonal elements)
mask = np.zeros_like(conf_matrix_percent, dtype=bool)
np.fill_diagonal(mask, True)

plt.figure(figsize=(8, 6))
sns.set(font_scale=1.2)

# Plot the full confusion matrix with percentages
sns.heatmap(conf_matrix_percent, annot=True, fmt='.1f', cmap=cmap, annot_kws={"size": 14},
            cbar_kws={'label': 'Prediction Percentage (%)'},
            linewidths=0.5, linecolor='gray')

# Overlay accurate predictions with a different color (optional highlight)
sns.heatmap(conf_matrix_percent, annot=True, fmt='.1f', cmap="Blues", annot_kws={"size": 14},
            cbar=False, mask=~mask, linewidths=0.5, linecolor='gray', alpha=0.5)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix (Percentage) with Highlighted Accurate Predictions")
plt.show()

# Print overall accuracy
accuracy = accuracy_score(feat2compare, predictions)
print(f"Simulated Live Classification Accuracy: {accuracy * 100:.2f}%")