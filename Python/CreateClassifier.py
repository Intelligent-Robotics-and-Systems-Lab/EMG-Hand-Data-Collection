# Luke Boyd
#1/15/2025
#File is to create the classifier for the robotic EMG hand ML project
import numpy as np
import pandas as pd
from extract_features import features
from sklearn.svm import LinearSVC
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib  # For saving and loading the model
from sklearn.feature_selection import VarianceThreshold
import matplotlib.pyplot as plt

#Load test data
data = pd.read_csv('Data/DB1_E3_S23-25rebalanced.csv') #Plug in name of csv

emg = data.iloc[:, [6, 8, 9]]
restimulus = data.iloc[:, 10] # Convert to 1D array if needed

#Create the window length
windowTime = 0.05 #Time of window in seconds
sampleFreq = 100 #Hz
windowLength = int(windowTime * sampleFreq) #Number of data points per window
overlap = 0.5; #Overlap percentage

# Extract features and labels
feat, labels = features(emg.to_numpy(), restimulus.to_numpy(), windowLength, overlap)

#Use a specific model function instead of tensorflow: https://scikit-learn.org/stable/
# Split data into training and validation sets (70% training, 30% validation)
X_train, X_val, y_train, y_val = train_test_split(feat, labels, test_size=0.3, random_state=42)

# Initialize and fit the scaler only on the training data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)

# Transform the validation data using the same scaler
X_val = scaler.transform(X_val)

# Save the trained scaler
joblib.dump(scaler, "scaler.pkl")

print(np.var(X_train, axis=0))

#Find Feature Importance

# Train a linear SVM to estimate feature importance
linear_clf = LinearSVC(C=1.0, max_iter=10000)
linear_clf.fit(X_train, y_train)

# Get absolute values of coefficients (importance)
feature_importance = np.abs(linear_clf.coef_).mean(axis=0)

# Sort and print ranked features
sorted_indices = np.argsort(feature_importance)[::-1]
print("\nFeature Importances (LinearSVC approximation):")
for idx in sorted_indices:
    print(f"Feature {idx + 1}: Importance = {feature_importance[idx]:.4f}")

# Optional: Plot feature importances
plt.figure(figsize=(10, 5))
plt.bar(range(len(feature_importance)), feature_importance[sorted_indices])
plt.xticks(ticks=range(len(feature_importance)), labels=sorted_indices + 1, rotation=90)
plt.xlabel("Feature Index")
plt.ylabel("Importance (|coef|)")
plt.title("Feature Importance using LinearSVC")
plt.tight_layout()
plt.show()


# Create and train the SVM classifier
# Train classifier with probability support

#Train with probabilities
clf = svm.SVC(probability=True, kernel='rbf', C=1, gamma='scale', decision_function_shape='ovr', class_weight="balanced")
clf.fit(X_train, y_train)
print("Training the SVM classifier...")

# Validate the classifier
print("Validating the model...")
predictions = clf.predict(X_val)
accuracy = accuracy_score(y_val, predictions)
decision_scores = clf.decision_function(X_val)
print(f"Validation Accuracy: {accuracy * 100:.2f}%")
for i in range(len(decision_scores)):
    print(f"Sample {i + 1}: Decision Scores: {decision_scores[i]}")


#First training gave 67.07% accuracy with AVG, RMS, MAV, WFL, and SSC
#Change to linearSVC, and parrallel processing for 64.98% accuracy with AVG, RMS, MAV, WFL, and SSC, 36 min
#Back to normal SVM -> Trained to 69.68% Accuracy using StandardScalar ans scalar.fit_transform
# Kernel SVM -> Trained to 68.96% and took about an hour and still gave a prediction of all 0
#Kernel with probabilities and no rest trained and no stability  to an accuacy of 52.06%

#Save the trained model
#model_filename = "svmKernel_classifier01_prob.pkl"
#joblib.dump(clf, model_filename)
#print(f"Model saved as {model_filename}")

