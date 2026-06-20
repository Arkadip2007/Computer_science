import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# =========================
# GLOBAL SETTINGS
# =========================

fs = 44100
buffer_size = 1024
sample_index = 0

# Channel parameters
params = {
    "A": {"freq":1000.0, "amp":0.5, "phase":0.0, "wave":"Sine", "duty":0.5},
    "B": {"freq":500.0,  "amp":0.5, "phase":0.0, "wave":"Sine", "duty":0.5}
}

# =========================
# WAVE GENERATION
# =========================

def generate_wave(t, p):
    angle = 2*np.pi*p["freq"]*t + p["phase"]

    if p["wave"] == "Sine":
        return p["amp"] * np.sin(angle)

    elif p["wave"] == "Square":
        return p["amp"] * np.where(np.sin(angle)>=np.cos(np.pi*p["duty"]),1,-1)

    elif p["wave"] == "Triangle":
        return p["amp"] * (2/np.pi)*np.arcsin(np.sin(angle))

    elif p["wave"] == "Sawtooth":
        return p["amp"] * (2*(t*p["freq"] - np.floor(0.5+t*p["freq"])))

    return np.zeros_like(t)

# =========================
# AUDIO CALLBACK
# =========================

def audio_callback(outdata, frames, time, status):
    global sample_index
    t = (np.arange(frames) + sample_index) / fs

    left = generate_wave(t, params["A"])
    right = generate_wave(t, params["B"])

    outdata[:] = np.column_stack((left, right))
    sample_index += frames

# =========================
# GUI
# =========================

root = tk.Tk()
root.title("Professional Dual Channel Signal Generator")

# =========================
# CONTROL CREATOR FUNCTION
# =========================

def create_control(frame, channel, name, min_val, max_val, step):

    def slider_update(val):
        params[channel][name] = float(val)
        entry.delete(0, tk.END)
        entry.insert(0, f"{float(val):.4f}")

    def entry_update(event=None):
        try:
            val = float(entry.get())
            val = max(min(val, max_val), min_val)
            params[channel][name] = val
            slider.set(val)
        except:
            pass

    def increase():
        val = params[channel][name] + step
        val = min(val, max_val)
        slider.set(val)

    def decrease():
        val = params[channel][name] - step
        val = max(val, min_val)
        slider.set(val)

    tk.Label(frame, text=f"{name.upper()}").pack()

    slider = tk.Scale(frame, from_=min_val, to=max_val,
                      resolution=step, orient=tk.HORIZONTAL,
                      command=slider_update, length=200)
    slider.set(params[channel][name])
    slider.pack()

    btn_frame = tk.Frame(frame)
    btn_frame.pack()

    tk.Button(btn_frame, text="-", width=3, command=decrease).pack(side=tk.LEFT)

    entry = tk.Entry(btn_frame, width=10)
    entry.insert(0, str(params[channel][name]))
    entry.bind("<Return>", entry_update)
    entry.pack(side=tk.LEFT)

    tk.Button(btn_frame, text="+", width=3, command=increase).pack(side=tk.LEFT)

# =========================
# CHANNEL A
# =========================

frame_a = tk.LabelFrame(root, text="CHANNEL A")
frame_a.pack(side=tk.LEFT, padx=10, pady=10)

create_control(frame_a, "A", "freq", 1, 20000, 1)
create_control(frame_a, "A", "amp", 0, 1, 0.01)
create_control(frame_a, "A", "phase", 0, 6.28, 0.01)
create_control(frame_a, "A", "duty", 0.01, 0.99, 0.01)

wave_a = ttk.Combobox(frame_a, values=["Sine","Square","Triangle","Sawtooth"])
wave_a.set("Sine")
wave_a.bind("<<ComboboxSelected>>", lambda e: params["A"].update({"wave":wave_a.get()}))
wave_a.pack()

# =========================
# CHANNEL B
# =========================

frame_b = tk.LabelFrame(root, text="CHANNEL B")
frame_b.pack(side=tk.LEFT, padx=10, pady=10)

create_control(frame_b, "B", "freq", 1, 20000, 1)
create_control(frame_b, "B", "amp", 0, 1, 0.01)
create_control(frame_b, "B", "phase", 0, 6.28, 0.01)
create_control(frame_b, "B", "duty", 0.01, 0.99, 0.01)

wave_b = ttk.Combobox(frame_b, values=["Sine","Square","Triangle","Sawtooth"])
wave_b.set("Sine")
wave_b.bind("<<ComboboxSelected>>", lambda e: params["B"].update({"wave":wave_b.get()}))
wave_b.pack()

# =========================
# OSCILLOSCOPE
# =========================

fig, ax = plt.subplots(figsize=(6,4))
x = np.linspace(0, 0.01, 1000)
line_a, = ax.plot(x, np.zeros_like(x), label="A")
line_b, = ax.plot(x, np.zeros_like(x), label="B")
ax.set_ylim(-1,1)
ax.set_xlim(0,0.01)
ax.legend()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

def update_plot():
    t = np.linspace(0, 0.01, 1000)
    y_a = generate_wave(t, params["A"])
    y_b = generate_wave(t, params["B"])

    line_a.set_ydata(y_a)
    line_b.set_ydata(y_b)
    canvas.draw()
    root.after(50, update_plot)

# =========================
# START AUDIO
# =========================

stream = sd.OutputStream(callback=audio_callback,
                         samplerate=fs,
                         channels=2,
                         blocksize=buffer_size)

stream.start()
update_plot()
root.mainloop()

stream.stop()
stream.close()

