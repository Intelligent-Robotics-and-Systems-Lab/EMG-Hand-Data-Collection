import numpy as np
import pandas as pd
from scipy.stats import mode

def features(data, classifier, windowLen, overlap):
    #data: data to be analysed and to create features with
    #classifier: the labels for the data to train a ML model
    #window length: number of data points per feature
    #overlap: the overlap percentage as a decimal of each window

    #For future expansion can add a 20 point histogram and a marginal discrete wavelet transfrom
    #For future could also add the first and maybe second derivatives of each feature taken

    # Overhead Variables
    len_data = len(data)

    # Split the data into sections based on the time interval with overlap
    rows = int(np.floor(len_data / (windowLen * overlap)) - 1)  # Number of sections
    cols = data.shape[1]  # Number of columns

    # Initialize Variables
    AVG = np.zeros((rows, cols))  # mean of the window
    RMS = np.zeros((rows, cols))  # Root Mean Squared
    MAV = np.zeros((rows, cols))  # Mean Absolute Value
    WFL = np.zeros((rows, cols))  # Waveform Length
    SSC = np.zeros((rows, cols))  # Slope Sign Change
    classifierMode = np.zeros(rows)  # To store the mode of classifier

    for i in range(rows):
        # Calculate the start and end indices of the current section
        start = int(i * (windowLen * overlap))
        finish = int(start + windowLen)

        # Adjust the end index if it exceeds the length of data
        if finish > len_data:
            finish = len_data

        cur_sec = data[start:finish, :]  # Current data segment

        # Calculate the relevant features for each segment
        AVG[i, :] = np.mean(cur_sec, axis=0)  # mean
        RMS[i, :] = np.sqrt(np.mean(cur_sec**2, axis=0))  # Root Mean Square
        MAV[i, :] = np.mean(np.abs(cur_sec), axis=0)  # Mean Absolute Value
        WFL[i, :] = np.sum(np.abs(np.diff(cur_sec, axis=0)), axis=0)  # Waveform Length
        SSC[i, :] = np.sum(np.abs(np.diff(np.sign(np.diff(cur_sec, axis=0)), axis=0)), axis=0)  # Slope Sign Change

        # Find the mode of the classifier within the current segment
        classifierCur_Sec = classifier[start:finish, :]
        classifierMode[i] = mode(classifierCur_Sec.flatten())[0][0]

    # Convert matrices into separate columns in the DataFrame
    columns = []
    columns += [f'AVG_{j+1}' for j in range(cols)]
    columns += [f'RMS_{j+1}' for j in range(cols)]
    columns += [f'MAV_{j+1}' for j in range(cols)]
    columns += [f'WFL_{j+1}' for j in range(cols)]
    columns += [f'SSC_{j+1}' for j in range(cols)]

    feat = pd.DataFrame(np.hstack([AVG, RMS, MAV, WFL, SSC]), columns=columns)

    identifier = classifierMode  # Labels for each segment

    return feat, identifier
