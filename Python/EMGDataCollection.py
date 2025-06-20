import time
import serial
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import random
from itertools import combinations
import os

# ------------------ Serial Setup ------------------
def initialize_serial_connection(port='COM6', baudrate=9600):
    try:
        ser = serial.Serial(port, baudrate)
        time.sleep(2)
        return ser
    except Exception as e:
        print(f"[Serial] Error: {e}")
        return None

# ------------------ GUI Setup ------------------
root = tk.Tk()
root.title("EMG Data Collector - Sample Based")
root.geometry("800x750")

grasp_type = tk.StringVar(value="Select Grasp")
rest_samples = tk.IntVar(value=100)
active_samples = tk.IntVar(value=100)
total_cycles = tk.IntVar(value=10)
filename = tk.StringVar(value="")
testing_mode = tk.BooleanVar(value=False)

is_running = False
ser = None

# ------------------ UI Layout ------------------
tk.Label(root, text="Grasp Type:").pack()
grasp_menu = ttk.Combobox(root, textvariable=grasp_type,
                          values=["Cylinder", "Pinch", "Ball", "Inverse Pinch", "All Transitions"], font=("Helvetica", 16))
grasp_menu.pack()

tk.Label(root, text="Rest Samples per Cycle:").pack()
tk.Entry(root, textvariable=rest_samples).pack()

tk.Label(root, text="Active Samples per Cycle:").pack()
tk.Entry(root, textvariable=active_samples).pack()

tk.Label(root, text="Total Cycles per Pair/Grasp:").pack()
tk.Entry(root, textvariable=total_cycles).pack()

def choose_file_path():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        filename.set(file_path)
        file_path_label.config(text=f"File Path: {file_path}")

choose_file_btn = tk.Button(root, text="Choose File Path", font=("Helvetica", 16), command=choose_file_path)
choose_file_btn.pack(pady=10)

file_path_label = tk.Label(root, text="File Path: Not Set", font=("Helvetica", 14), width=50, anchor="w")
file_path_label.pack(pady=10)

tk.Checkbutton(root, text="Testing Mode (No Serial)", variable=testing_mode).pack(pady=10)

status_box = tk.Label(root, text="Idle", font=("Helvetica", 20), width=20, height=2, bg="gray")
status_box.pack(pady=20)

serial_status = tk.Label(root, text="Serial: Not Connected", bg="lightgray", font=("Helvetica", 14), width=30)
serial_status.pack(pady=10)

progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress.pack(pady=20)
progress_label = tk.Label(root, text="0 / 0 Samples Collected")
progress_label.pack()

def reset_ui():
    global is_running
    is_running = False

    # Reset variables
    grasp_type.set("Select Grasp")
    rest_samples.set(100)
    active_samples.set(100)
    total_cycles.set(10)
    filename.set("")

    # Reset UI elements
    update_status("gray", "Idle")
    update_serial_status(False)
    progress["value"] = 0
    progress_label.config(text="0 / 0 Samples Collected")
    file_path_label.config(text="File Path: Not Set")

    # Close serial if open
    if ser:
        try:
            ser.close()
        except:
            pass

reset_btn = tk.Button(root, text="Reset", font=("Helvetica", 16), command=reset_ui)
reset_btn.pack(pady=5)

# ------------------ UI Update Functions ------------------
def update_status(color, text):
    status_box.config(bg=color, text=text)

def update_serial_status(connected):
    if connected:
        serial_status.config(bg="lightgreen", text="Serial: Connected")
    else:
        serial_status.config(bg="lightcoral", text="Serial: Not Connected")

def update_progress(current, total):
    progress["maximum"] = total
    progress["value"] = current
    progress_label.config(text=f"{current} / {total} Samples Collected")

# ------------------ Core Logic ------------------
def data_collection_loop():
    global is_running, ser
    mode = grasp_type.get()
    rest_n = rest_samples.get()
    active_n = active_samples.get()
    cycles = total_cycles.get()
    file_path = filename.get()

    if mode in ["1", "2", "3", "4"]:
        grasp_sequence = [(int(mode),)] * cycles
    elif mode == "All Transitions":
        grasp_sequence = []
        grasp_types = [1, 2, 3, 4]
        for (g1, g2) in combinations(grasp_types, 2):
            grasp_sequence.extend([(g1, g2)] * cycles)
    else:
        update_status("gray", "Invalid Mode")
        return

    total_samples = len(grasp_sequence) * (rest_n + active_n)
    collected_samples = 0

    try:
        with open(file_path, 'w') as f:
            f.write("timestamp,grasp_type,raw_data\n")

            for pair in grasp_sequence:
                if not is_running:
                    break

                # Single grasp (rest -> active)
                if len(pair) == 1:
                    g = pair[0]
                    update_status("red", f"Rest")
                    collected_samples = collect_samples(f, 0, rest_n, collected_samples, total_samples)

                    if not is_running:
                        break

                    update_status("green", f"Active Grasp {g}")
                    collected_samples = collect_samples(f, g, active_n, collected_samples, total_samples)

                # Transition (rest -> grasp2)
                else:
                    g1, g2 = pair
                    update_status("red", f"Rest (Before {g2})")
                    collected_samples = collect_samples(f, 0, rest_n, collected_samples, total_samples)

                    if not is_running:
                        break

                    update_status("green", f"Active Grasp {g2}")
                    collected_samples = collect_samples(f, g2, active_n, collected_samples, total_samples)

    except Exception as e:
        print(f"[Error] {e}")

    abs_file_path = os.path.abspath(file_path)
    file_path_label.config(text=f"File Path: {abs_file_path}")
    update_status("gray", "Done")
    messagebox.showinfo("Collection Complete", f"Data saved to:\n{abs_file_path}")
    print(f"[File Saved] {abs_file_path}")

def collect_samples(f, grasp, num_samples, collected, total):
    sample_count = 0
    while sample_count < num_samples and is_running:
        timestamp = time.time()

        if testing_mode.get():
            raw_data = ','.join([f"{random.uniform(0, 1):.3f}" for _ in range(3)])
        else:
            if ser and ser.in_waiting:
                try:
                    raw_data = ser.readline().decode().strip()
                except:
                    continue
            else:
                continue

        f.write(f"{timestamp},{grasp},{raw_data}\n")
        sample_count += 1
        collected += 1
        update_progress(collected, total)

    return collected

def start_collection():
    global is_running, ser

    if is_running:
        return

    if filename.get().strip() == "":
        messagebox.showerror("Missing File Name", "Please select a valid file name before starting.")
        return

    if not testing_mode.get():
        ser = initialize_serial_connection()
        update_serial_status(ser is not None)
        if ser is None:
            update_status("gray", "Serial Failed")
            return
    else:
        update_serial_status(False)

    is_running = True
    progress["value"] = 0

    # Estimate total samples
    if grasp_type.get() == "All Transitions":
        num_pairs = 6  # Combinations of 4 grasps (1,2,3,4)
        total = num_pairs * (rest_samples.get() + active_samples.get()) * total_cycles.get()
    elif grasp_type.get() in ["1", "2", "3", "4"]:
        total = (rest_samples.get() + active_samples.get()) * total_cycles.get()
    else:
        total = 0

    update_progress(0, total)
    threading.Thread(target=data_collection_loop, daemon=True).start()

def stop_collection():
    global is_running
    is_running = False

# ------------------ Buttons ------------------
start_btn = tk.Button(root, text="Start", font=("Helvetica", 16), command=start_collection)
start_btn.pack(pady=5)

stop_btn = tk.Button(root, text="Stop", font=("Helvetica", 16), command=stop_collection)
stop_btn.pack(pady=5)

# ------------------ Run ------------------
root.mainloop()

if ser:
    ser.close()
