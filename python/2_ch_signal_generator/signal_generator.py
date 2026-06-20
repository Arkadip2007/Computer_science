import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading

# =========================
# GLOBAL SETTINGS
# =========================

fs = 44100
buffer_size = 1024

# Channel A parameters
freq_a = 1000.0
amp_a = 0.5
phase_a = 0.0
wave_a = "Sine"
duty_a = 0.5

# Channel B parameters
freq_b = 500.0
amp_b = 0.5
phase_b = 0.0
wave_b = "Sine"
duty_b = 0.5

running = True
sample_index = 0

# =========================
# WAVE GENERATION
# =========================

def generate_wave(t, freq, amp, phase, wave_type, duty):
    angle = 2 * np.pi * freq * t + phase

    if wave_type == "Sine":
        return amp * np.sin(angle)

    elif wave_type == "Square":
        return amp * np.where(np.sin(angle) >= np.cos(np.pi*duty), 1, -1)

    elif wave_type == "Triangle":
        return amp * (2/np.pi)*np.arcsin(np.sin(angle))

    elif wave_type == "Sawtooth":
        return amp * (2*(t*freq - np.floor(0.5 + t*freq)))

    return np.zeros_like(t)

# =========================
# AUDIO CALLBACK
# =========================

def audio_callback(outdata, frames, time, status):
    global sample_index

    t = (np.arange(frames) + sample_index) / fs

    left = generate_wave(t, freq_a, amp_a, phase_a, wave_a, duty_a)
    right = generate_wave(t, freq_b, amp_b, phase_b, wave_b, duty_b)

    outdata[:] = np.column_stack((left, right))
    sample_index += frames

# =========================
# GUI
# =========================

root = tk.Tk()
root.title("Professional Signal Generator")

main_frame = ttk.Frame(root)
main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

control_frame = ttk.Frame(main_frame)
control_frame.pack(side=tk.TOP, fill=tk.X)

# =========================
# CONTROL FUNCTIONS
# =========================

def update_freq_a(val): 
    global freq_a
    freq_a = float(val)

def update_amp_a(val): 
    global amp_a
    amp_a = float(val)

def update_phase_a(val): 
    global phase_a
    phase_a = float(val)

def update_duty_a(val):
    global duty_a
    duty_a = float(val)

def update_wave_a(val):
    global wave_a
    wave_a = val

def update_freq_b(val): 
    global freq_b
    freq_b = float(val)

def update_amp_b(val): 
    global amp_b
    amp_b = float(val)

def update_phase_b(val): 
    global phase_b
    phase_b = float(val)

def update_duty_b(val):
    global duty_b
    duty_b = float(val)

def update_wave_b(val):
    global wave_b
    wave_b = val

# =========================
# CHANNEL A CONTROLS
# =========================

ttk.Label(control_frame, text="CHANNEL A").grid(row=0, column=0)

tk.Scale(control_frame, from_=1, to=20000, resolution=1,
         orient=tk.HORIZONTAL, label="Freq A (Hz)",
         command=update_freq_a).grid(row=1, column=0)

tk.Scale(control_frame, from_=0, to=1, resolution=0.01,
         orient=tk.HORIZONTAL, label="Amp A",
         command=update_amp_a).set(0.5)

tk.Scale(control_frame, from_=0, to=6.28, resolution=0.01,
         orient=tk.HORIZONTAL, label="Phase A",
         command=update_phase_a).grid(row=3, column=0)

tk.Scale(control_frame, from_=0.01, to=0.99, resolution=0.01,
         orient=tk.HORIZONTAL, label="Duty A",
         command=update_duty_a).grid(row=4, column=0)

wave_select_a = ttk.Combobox(control_frame, values=["Sine","Square","Triangle","Sawtooth"])
wave_select_a.set("Sine")
wave_select_a.bind("<<ComboboxSelected>>", lambda e: update_wave_a(wave_select_a.get()))
wave_select_a.grid(row=5, column=0)

# =========================
# CHANNEL B CONTROLS
# =========================

ttk.Label(control_frame, text="CHANNEL B").grid(row=0, column=1)

tk.Scale(control_frame, from_=1, to=20000, resolution=1,
         orient=tk.HORIZONTAL, label="Freq B (Hz)",
         command=update_freq_b).grid(row=1, column=1)

tk.Scale(control_frame, from_=0, to=1, resolution=0.01,
         orient=tk.HORIZONTAL, label="Amp B",
         command=update_amp_b).set(0.5)

tk.Scale(control_frame, from_=0, to=6.28, resolution=0.01,
         orient=tk.HORIZONTAL, label="Phase B",
         command=update_phase_b).grid(row=3, column=1)

tk.Scale(control_frame, from_=0.01, to=0.99, resolution=0.01,
         orient=tk.HORIZONTAL, label="Duty B",
         command=update_duty_b).grid(row=4, column=1)

wave_select_b = ttk.Combobox(control_frame, values=["Sine","Square","Triangle","Sawtooth"])
wave_select_b.set("Sine")
wave_select_b.bind("<<ComboboxSelected>>", lambda e: update_wave_b(wave_select_b.get()))
wave_select_b.grid(row=5, column=1)

# =========================
# OSCILLOSCOPE
# =========================

fig, ax = plt.subplots(figsize=(6,4))
x = np.linspace(0, 0.01, 1000)
line_a, = ax.plot(x, np.zeros_like(x), label="Channel A")
line_b, = ax.plot(x, np.zeros_like(x), label="Channel B")
ax.set_ylim(-1,1)
ax.set_xlim(0,0.01)
ax.legend()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

def update_plot():
    t = np.linspace(0, 0.01, 1000)
    y_a = generate_wave(t, freq_a, amp_a, phase_a, wave_a, duty_a)
    y_b = generate_wave(t, freq_b, amp_b, phase_b, wave_b, duty_b)

    line_a.set_ydata(y_a)
    line_b.set_ydata(y_b)
    canvas.draw()
    root.after(50, update_plot)

# =========================
# START AUDIO THREAD
# =========================

stream = sd.OutputStream(callback=audio_callback,
                         samplerate=fs,
                         channels=2,
                         blocksize=buffer_size)

stream.start()

update_plot()
root.mainloop()

running = False
stream.stop()
stream.close()

