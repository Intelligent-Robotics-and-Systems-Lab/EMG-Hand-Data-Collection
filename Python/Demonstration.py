import numpy as np
import pandas as pd
import joblib
import time
import serial
import serial.tools.list_ports
from extract_features import features
from sklearn.preprocessing import StandardScaler
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ------------------- Serial Communication -------------------
def initialize_serial_connection(port='COM4', baudrate=115200):
    ser = serial.Serial(port, baudrate)
    time.sleep(2)
    return ser

def send_integer_to_esp32(ser, value):
    if ser is None:
        return
    if 0 <= value <= 9:
        ser.write(str(value).encode())
        while ser.in_waiting == 0:
            time.sleep(0.1)
        response = ser.read(ser.in_waiting).decode()
        print(f"Sent: {value}, Received: {response}")
        return response

# ------------------- Load Data & Classifier -------------------
data = pd.read_csv('Data/DB1_E3_S23-25rebalanced.csv')
clf = joblib.load("svmKernel_classifier01_prob.pkl")
scaler = joblib.load("scaler.pkl")

# Split by label
data0 = data[data.iloc[:, 10] == 0]
data1 = data[data.iloc[:, 10] == 1]
data2 = data[data.iloc[:, 10] == 2]
data3 = data[data.iloc[:, 10] == 3]
data4 = data[data.iloc[:, 10] == 4]

datasets = {'Class 0': data0, 'Class 1': data1, 'Class 2': data2, 'Class 3': data3, 'Class 4': data4}

# ------------------- UI Setup -------------------
root = tk.Tk()
root.title("EMG Classifier UI")
root.geometry("1920x1080")
root.columnconfigure(0, weight=1)
root.rowconfigure(3, weight=1)

# Dropdown Menu
top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
top_frame.columnconfigure((0, 1), weight=1)

style = ttk.Style()
style.configure("TCombobox", font=("Helvetica", 20))

selected_class = tk.StringVar(value='Class 0')
dropdown = ttk.Combobox(top_frame, textvariable=selected_class, values=list(datasets.keys()), font=("Helvetica", 20))
dropdown.grid(row=0, column=0, padx=10, sticky="ew")

root.option_add("*TCombobox*Listbox*Font", "Helvetica 20")

#Start Button
start_button = tk.Button(top_frame, text="Start Classification", font=("Helvetica", 20))
start_button.grid(row=0, column=1, padx=10, sticky="ew")

# Middle frame with image and status
mid_frame = tk.Frame(root)
mid_frame.grid(row=1, column=0, sticky="ew", padx=10)
mid_frame.columnconfigure((0, 1), weight=1)

# Image Display
image_label = tk.Label(mid_frame)
image_label.grid(row=0, column=0, sticky="nsew")

# Status Box
status_box = tk.Label(mid_frame, text="Status", height=3, bg="gray", font=("Helvetica", 16))
status_box.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

# Graph Plot
bottom_frame = tk.Frame(root)
bottom_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
bottom_frame.rowconfigure(0, weight=1)
bottom_frame.columnconfigure(0, weight=1)

fig, ax = plt.subplots(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=bottom_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=0, sticky="nsew")

# ------------------- Functional UI Elements -------------------
def update_label_image(label_val):
    img_path = f'label_{label_val}.png'
    try:
        img = Image.open(img_path).resize((500, 500))
        img = ImageTk.PhotoImage(img)
        image_label.config(image=img)
        image_label.image = img
    except Exception as e:
        print(f"[Image] Error loading image: {e}")

def update_status_color(is_correct, true_label, pred_label):
    color = "green" if is_correct else "red"
    text = f"True Class: {true_label} | Predicted Class: {pred_label}"
    status_box.config(bg=color, text=text)

def update_plot(history):
    ax.clear()
    for i in range(history.shape[1]):
        ax.plot(history[:, i], label=f'Channel {i+1}')
    ax.set_title("EMG Data (Scrolling View)")
    ax.set_xlim(0, history.shape[0])
    ax.legend(loc = 'upper right')
    canvas.draw()

def classify_data(df):
    emg = df.iloc[:, [6, 8, 9]].to_numpy()
    restimulus = df.iloc[:, 10].to_numpy()

    windowTime = 0.1
    samplingFreq = 100
    windowLen = int(windowTime * samplingFreq)
    overlap = 0.5
    step = int(windowLen * (1 - overlap))
    history_len = 200
    plot_history = np.zeros((history_len, 3))

    for start in range(0, len(emg) - windowLen, step):
        finish = start + windowLen
        current_window = emg[start:finish, :]
        true_label = np.bincount(restimulus[start:finish]).argmax()

        X_live, _ = features(current_window, restimulus[start:finish], windowLen, overlap)
        X_live = scaler.transform(X_live)
        cur_pred = clf.predict(X_live)[0]

        # Update scrolling buffer
        plot_history = np.roll(plot_history, -windowLen, axis=0)
        plot_history[-windowLen:, :] = current_window
        update_plot(plot_history)

        update_label_image(true_label)
        update_status_color(cur_pred == true_label, true_label, cur_pred)
        send_integer_to_esp32(ser, cur_pred)

        root.update()
        time.sleep(0.05)

def start_classification():
    global ser
    try:
        ser = initialize_serial_connection()
        print("[Serial] Connected.")
    except Exception as e:
        print(f"[Serial] Could not connect: {e}")
        ser = None

    df = datasets[selected_class.get()]
    classify_data(df)

start_button.config(command=start_classification)

# ------------------- Run -------------------
ser = None
root.mainloop()

if ser:
    ser.close()
