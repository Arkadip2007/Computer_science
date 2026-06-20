import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ======================
# GLOBAL SETTINGS
# ======================

fs = 44100
buffer_size = 1024
sample_index = 0

params = {
    "A": {"freq": 542.0, "amp": 0.5, "phase": 0.0, "wave": "Sine", "duty": 0.5, "enabled": True},
    "B": {"freq": 271.0, "amp": 0.35, "phase": 0.0, "wave": "Square", "duty": 0.25, "enabled": True}
}

time_scale = 0.028
amp_scale = 1.4  # Default Zoom
dark_mode = False

# Colors
theme_colors = {
    "light": {"bg": "#f0f0f0", "fg": "black", "graph_bg": "white", "ax_bg": "white", "line_color": "black"},
    "dark":  {"bg": "#2e2e2e", "fg": "white", "graph_bg": "#1e1e1e", "ax_bg": "#1e1e1e", "line_color": "white"}
}

# ======================
# WAVE GENERATOR
# ======================

def generate_wave(t, p):
    if not p["enabled"]:
        return np.zeros_like(t)

    # Base angle
    angle = 2 * np.pi * p["freq"] * t + p["phase"]
    
    # Pre-calculate for duty cycle (Normalized time 0 to 1)
    # (t * freq) % 1 gives a sawtooth from 0 to 1
    duty_cycle_t = (t * p["freq"] + p["phase"]/(2*np.pi)) % 1

    if p["wave"] == "Sine":
        return p["amp"] * np.sin(angle)

    elif p["wave"] == "Square":
        # FIXED: Square now respects Duty Cycle
        return p["amp"] * np.where(duty_cycle_t < p["duty"], 1, -1)

    elif p["wave"] == "Triangle":
        return p["amp"] * (2 / np.pi) * np.arcsin(np.sin(angle))

    elif p["wave"] == "Sawtooth":
        return p["amp"] * (2 * (t * p["freq"] - np.floor(0.5 + t * p["freq"])))

    elif p["wave"] == "Noise":
        return p["amp"] * np.random.uniform(-1, 1, len(t))

    elif p["wave"] == "Pulse":
        # Pulse is essentially same as Variable Duty Square
        return p["amp"] * np.where(duty_cycle_t < p["duty"], 1, -1)

    return np.zeros_like(t)

# ======================
# AUDIO CALLBACK
# ======================

def audio_callback(outdata, frames, time, status):
    global sample_index
    t = (np.arange(frames) + sample_index) / fs
    left = generate_wave(t, params["A"])
    right = generate_wave(t, params["B"])
    outdata[:] = np.column_stack((left, right))
    sample_index += frames

# ======================
# GUI SETUP
# ======================

root = tk.Tk()
root.title("Dual Channel Signal Generator - Lab Edition")
root.geometry("1100x600")

# Apply initial theme safely
current_theme = theme_colors["light"]
style = ttk.Style()
style.theme_use('clam') 

# Main Layout Containers
# Left side for controls, Right side for Graph
main_container = tk.Frame(root)
main_container.pack(fill=tk.BOTH, expand=True)

left_panel = tk.Frame(main_container)
left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

right_panel = tk.Frame(main_container)
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# ======================
# MOUSE SCROLL BINDING
# ======================

def bind_scroll(widget, variable, step, min_val, max_val):
    def on_scroll(event):
        # Linux (4=UP, 5=DOWN) vs Windows (event.delta)
        delta = 0
        if event.num == 5 or event.delta < 0:
            delta = -step
        elif event.num == 4 or event.delta > 0:
            delta = step
            
        # Calculate new value
        current_val = widget.get() # Get directly from widget
        new_val = current_val + delta
        new_val = max(min_val, min(new_val, max_val))
        
        # widget.set() ব্যবহার করলে স্লাইডার এবং সাউন্ড দুটোই আপডেট হবে
        widget.set(new_val)

    # মাউস যখন স্লাইডারের উপরে আসবে (Hover), তখন স্ক্রলিং অন হবে
    def on_enter(event):
        widget.bind_all("<Button-4>", on_scroll) # Linux Scroll UP
        widget.bind_all("<Button-5>", on_scroll) # Linux Scroll DOWN
        widget.bind_all("<MouseWheel>", on_scroll) # Windows Scroll

    # মাউস সরে গেলে স্ক্রলিং অফ হবে (যাতে অন্য কোথাও এফেক্ট না পড়ে)
    def on_leave(event):
        widget.unbind_all("<Button-4>")
        widget.unbind_all("<Button-5>")
        widget.unbind_all("<MouseWheel>")

    # ইভেন্ট বাইন্ডিং
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# ======================
# THEME TOGGLE
# ======================

def apply_theme():
    c = theme_colors["dark"] if dark_mode else theme_colors["light"]
    
    root.configure(bg=c["bg"])
    main_container.configure(bg=c["bg"])
    left_panel.configure(bg=c["bg"])
    right_panel.configure(bg=c["bg"])
    
    # Update Matplotlib
    fig.patch.set_facecolor(c["bg"])
    ax.set_facecolor(c["graph_bg"])
    
    # Axes and Label colors
    ax.tick_params(colors=c["fg"], which='both')
    for spine in ax.spines.values():
        spine.set_color(c["fg"])
    
    # Update controls background recursively
    def update_widget_bg(widget):
        try:
            widget.configure(bg=c["bg"], fg=c["fg"])
        except:
            pass
        for child in widget.winfo_children():
            update_widget_bg(child)

    update_widget_bg(left_panel)
    update_widget_bg(right_panel)
    
    # Re-draw graph to apply changes
    canvas.draw()

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()

tk.Button(root, text="Toggle Dark/Light", command=toggle_theme).pack(side=tk.TOP, fill=tk.X)

# ======================
# CONTROL BUILDER
# ======================

def create_control(frame, channel, name, min_val, max_val, step):
    
    # Variable wrapper to make updates smoother
    var = tk.DoubleVar(value=params[channel][name])

    def on_slider_change(val):
        params[channel][name] = float(val)
        entry.delete(0, tk.END)
        entry.insert(0, str(round(float(val), 4)))

    def on_entry_change(event=None):
        try:
            val = float(entry.get())
            val = max(min(val, max_val), min_val)
            var.set(val)
            params[channel][name] = val
        except ValueError:
            pass

    def inc():
        v = var.get() + step
        if v <= max_val:
            var.set(v)
            on_slider_change(v)

    def dec():
        v = var.get() - step
        if v >= min_val:
            var.set(v)
            on_slider_change(v)

    # Sub-frame for this control
    ctrl_frame = tk.Frame(frame)
    ctrl_frame.pack(pady=2, fill=tk.X)

    lbl = tk.Label(ctrl_frame, text=name.upper(), font=("Arial", 8))
    lbl.pack()

    # Slider
    slider = tk.Scale(ctrl_frame, from_=min_val, to=max_val,
                      resolution=step, orient=tk.HORIZONTAL,
                      variable=var, command=on_slider_change,
                      showvalue=0, length=200)
    slider.pack(fill=tk.X)
    
    # Enable Scrolling on Slider
    bind_scroll(slider, var, step, min_val, max_val)

    # Manual Input Row
    f_btns = tk.Frame(ctrl_frame)
    f_btns.pack()

    tk.Button(f_btns, text="-", width=2, command=dec, font=("Arial", 8)).pack(side=tk.LEFT)
    
    entry = tk.Entry(f_btns, width=8, justify='center')
    entry.insert(0, str(params[channel][name]))
    entry.bind("<Return>", on_entry_change)
    entry.pack(side=tk.LEFT, padx=5)
    
    tk.Button(f_btns, text="+", width=2, command=inc, font=("Arial", 8)).pack(side=tk.LEFT)

# ======================
# CHANNEL CONTROLS
# ======================

def build_channel_ui(parent, ch_name):
    frame = tk.LabelFrame(parent, text=f"CHANNEL {ch_name}", padx=5, pady=5)
    frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)

    # Play/Pause
    btn_txt = tk.StringVar(value="Mute" if params[ch_name]["enabled"] else "Unmute")
    def toggle():
        toggle_channel(ch_name)
        btn_txt.set("Unmute" if not params[ch_name]["enabled"] else "Mute") # Logic inverted for label
        
    tk.Button(frame, textvariable=btn_txt, command=toggle, bg="#ddd").pack(fill=tk.X, pady=5)

    create_control(frame, ch_name, "freq", 1, 5000, 1)
    create_control(frame, ch_name, "amp", 0, 1.0, 0.01)
    create_control(frame, ch_name, "phase", 0, 6.28, 0.1)
    create_control(frame, ch_name, "duty", 0.01, 0.99, 0.01)

    # Wave Selector
    tk.Label(frame, text="Waveform").pack(pady=(10,0))
    wave_cb = ttk.Combobox(frame, values=["Sine", "Square", "Triangle", "Sawtooth", "Noise", "Pulse"], state="readonly")
    wave_cb.set(params[ch_name]["wave"])
    wave_cb.bind("<<ComboboxSelected>>", lambda e: params[ch_name].update({"wave": wave_cb.get()}))
    wave_cb.pack(fill=tk.X, pady=5)

def toggle_channel(ch):
    params[ch]["enabled"] = not params[ch]["enabled"]

build_channel_ui(left_panel, "A")
build_channel_ui(left_panel, "B")

# ======================
# OSCILLOSCOPE (RIGHT PANEL)
# ======================

fig, ax = plt.subplots(figsize=(6, 4))
# Remove extra margins
plt.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)

# Initial Line Setup
x = np.linspace(0, time_scale, 1000)
line_a, = ax.plot(x, np.zeros_like(x), label="A", linewidth=1.5)
line_b, = ax.plot(x, np.zeros_like(x), label="B", linewidth=1.5, alpha=0.8)

ax.set_ylim(-1, 1)
ax.legend(loc="upper right")
ax.grid(True, linestyle='--', alpha=0.3)

canvas = FigureCanvasTkAgg(fig, master=right_panel)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# ======================
# OSCILLOSCOPE CONTROLS (Under Graph)
# ======================

zoom_frame = tk.LabelFrame(right_panel, text="Oscilloscope Control", padx=10, pady=10)
zoom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

# Time Scale Control
def update_time(val):
    global time_scale
    time_scale = float(val)

time_var = tk.DoubleVar(value=time_scale)
tk.Label(zoom_frame, text="Time Scale (Zoom X)").pack()
time_slider = tk.Scale(zoom_frame, from_=0.001, to=0.05, resolution=0.001, 
                       orient=tk.HORIZONTAL, variable=time_var, command=update_time, length=300)
time_slider.pack(fill=tk.X)
bind_scroll(time_slider, time_var, 0.001, 0.001, 0.05)

# Amplitude Zoom Control
def update_amp_scale(val):
    global amp_scale
    amp_scale = float(val)

amp_var = tk.DoubleVar(value=amp_scale)
tk.Label(zoom_frame, text="Amplitude Zoom (Zoom Y)").pack()
amp_slider = tk.Scale(zoom_frame, from_=0.1, to=5.0, resolution=0.1, 
                      orient=tk.HORIZONTAL, variable=amp_var, command=update_amp_scale, length=300)
amp_slider.pack(fill=tk.X)
bind_scroll(amp_slider, amp_var, 0.1, 0.1, 5.0)


# ======================
# PLOT UPDATE LOOP
# ======================

def update_plot():
    # Generate visualization data
    # Note: We generate a fixed number of points for the visible window
    t = np.linspace(0, time_scale, 1000)

    # We do NOT divide by amp_scale here. The signal is constant.
    # We only change the ax limits to "zoom".
    y_a = generate_wave(t, params["A"])
    y_b = generate_wave(t, params["B"])

    line_a.set_xdata(t)
    line_b.set_xdata(t)
    line_a.set_ydata(y_a)
    line_b.set_ydata(y_b)

    # Dynamic Axes Limits
    ax.set_xlim(0, time_scale)
    # Zoom In = Smaller Limits. So we divide 1 by scale.
    # e.g., Scale 2.0 -> Limits -0.5 to 0.5 (Magnified)
    limit = 1.0 / amp_scale
    ax.set_ylim(-limit, limit)

    canvas.draw_idle()
    root.after(50, update_plot)

# ======================
# START APP
# ======================

# Apply initial theme properly
apply_theme()

# Audio Stream
stream = sd.OutputStream(callback=audio_callback, samplerate=fs, channels=2, blocksize=buffer_size)
stream.start()

update_plot()
root.mainloop()

stream.stop()
stream.close()
