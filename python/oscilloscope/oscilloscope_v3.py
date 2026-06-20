import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

# --- কনফিগারেশন ---
CHUNK = 4096
DISPLAY_FRAMES = 1000
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
MAX_VOLTAGE = 1.0

# --- Keysight কালার প্যালেট ---
C_BODY = '#2e2e2e'       # হার্ডওয়্যার বডি (Dark Grey)
C_SCREEN = '#000000'     # ডিসপ্লে (Black)
C_GRID = '#555555'       # গ্রিড লাইন
C_CH1 = '#FFD700'        # চ্যানেল ১ (Yellow)
C_CH2 = '#00FF00'        # চ্যানেল ২ (Green)
C_BTN_RUN = '#00FF00'    # রান বাটন (Green LED)
C_BTN_CH1 = '#FFD700'    # চ্যানেল ১ বাটন
C_BTN_CH2 = '#00FF00'    # চ্যানেল ২ বাটন
C_TEXT = '#FFFFFF'

# --- অডিও সেটআপ ---
p = pyaudio.PyAudio()
try:
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
except Exception as e:
    print("মাইক্রোফোন পাওয়া যাচ্ছে না! ডিফল্ট ইনপুট চেক করুন।")
    exit()

# --- GUI লেআউট সেটআপ ---
fig = plt.figure(figsize=(14, 7), facecolor=C_BODY)
fig.canvas.manager.set_window_title('Keysight InfiniiVision Simulator')

# গ্রিড লেআউট (বাম দিকে স্ক্রিন, ডান দিকে কন্ট্রোল প্যানেল)
gs = gridspec.GridSpec(10, 14, figure=fig)

# ১. মেইন ডিসপ্লে স্ক্রিন (বামে)
ax_screen = fig.add_subplot(gs[1:9, 0:10], facecolor=C_SCREEN)
ax_screen.set_ylim(-MAX_VOLTAGE, MAX_VOLTAGE)
ax_screen.set_xlim(0, DISPLAY_FRAMES)
ax_screen.grid(True, which='major', color=C_GRID, linestyle='--', linewidth=0.7)
ax_screen.set_xticklabels([])
ax_screen.set_yticklabels([])

# স্পাইন (বর্ডার) স্টাইলিং
for spine in ax_screen.spines.values():
    spine.set_edgecolor('#888888')
    spine.set_linewidth(2)

# লাইন প্লট (ওয়েভফর্ম)
x = np.arange(0, DISPLAY_FRAMES)
line1, = ax_screen.plot(x, np.zeros(DISPLAY_FRAMES), color=C_CH1, lw=2.5, label='1')
line2, = ax_screen.plot(x, np.zeros(DISPLAY_FRAMES), color=C_CH2, lw=2.5, label='2', alpha=0.8)

# --- হার্ডওয়্যার লুক (UI Elements) ---

# লোগো এবং টেক্সট
fig.text(0.02, 0.92, "KEYSIGHT", color='white', fontsize=14, fontweight='bold', fontfamily='sans-serif')
fig.text(0.09, 0.92, "InfiniiVision", color='gray', fontsize=14, fontstyle='italic')
fig.text(0.85, 0.95, "Run/Stop", color='white', fontsize=10, ha='center')

# ডানদিকের প্যানেল (Control Panel Simulation)
# আমরা 'Patches' ব্যবহার করে বাটন এবং নব আঁকব

# ফাংশন: বাটন আঁকার জন্য
def draw_button(x, y, label, color='gray', text_color='white', bg=True):
    if bg:
        # বাটন শেপ
        rect = FancyBboxPatch((x, y), 0.08, 0.06, boxstyle="round,pad=0.01", 
                              fc=color, ec='black', transform=fig.transFigure)
        fig.patches.append(rect)
    # টেক্সট
    fig.text(x+0.04, y+0.03, label, color=text_color, ha='center', va='center', 
             fontsize=9, fontweight='bold', transform=fig.transFigure)

# ফাংশন: নব (Knob) আঁকার জন্য
def draw_knob(x, y, label):
    circle = Circle((x, y), 0.025, fc='#1a1a1a', ec='#555555', lw=2, transform=fig.transFigure)
    fig.patches.append(circle)
    # নবের মাঝখানের দাগ
    fig.lines.append(plt.Line2D([x, x], [y, y+0.02], color='white', lw=2, transform=fig.transFigure))
    fig.text(x, y-0.04, label, color='gray', fontsize=8, ha='center', transform=fig.transFigure)

# --- বাটন প্লেসমেন্ট ---
# Run/Stop বাটন (Green)
draw_button(0.81, 0.88, "Run", color='#00cc00', text_color='black')

# Vertical Controls
fig.text(0.85, 0.75, "Vertical", color='white', fontsize=12, ha='center', fontweight='bold')
draw_button(0.76, 0.65, "1", color=C_BTN_CH1, text_color='black') # CH1 Button
draw_button(0.86, 0.65, "2", color=C_BTN_CH2, text_color='black') # CH2 Button

# Knobs
draw_knob(0.80, 0.55, "Position")
draw_knob(0.90, 0.55, "Scale")

# Horizontal Controls
fig.text(0.85, 0.40, "Horizontal", color='white', fontsize=12, ha='center', fontweight='bold')
draw_knob(0.85, 0.30, "Time/Div")

# Trigger Controls
fig.text(0.85, 0.18, "Trigger", color='white', fontsize=12, ha='center', fontweight='bold')
draw_button(0.81, 0.10, "Level", color='#444444')

# --- অন-স্ক্রিন ইনফো (OSD) ---
# টপ বার
ax_screen.text(0.02, 0.95, "2.00V/", transform=ax_screen.transAxes, color=C_CH1, fontweight='bold')
ax_screen.text(0.12, 0.95, "2.00V/", transform=ax_screen.transAxes, color=C_CH2, fontweight='bold')
ax_screen.text(0.45, 0.95, "500us/  0.0s", transform=ax_screen.transAxes, color='white')
ax_screen.text(0.90, 0.95, "Auto", transform=ax_screen.transAxes, color='white')

# বটম বার (Measurements)
rect_bottom = Rectangle((0, -0.15), 1, 0.15, transform=ax_screen.transAxes, facecolor='black', alpha=0.8)
ax_screen.add_patch(rect_bottom)

info_vpp1 = ax_screen.text(0.02, 0.05, "Vpp(1): -- V", transform=ax_screen.transAxes, color=C_CH1, fontsize=11, fontweight='bold')
info_vpp2 = ax_screen.text(0.25, 0.05, "Vpp(2): -- V", transform=ax_screen.transAxes, color=C_CH2, fontsize=11, fontweight='bold')
info_freq = ax_screen.text(0.50, 0.05, "Freq(1): -- Hz", transform=ax_screen.transAxes, color='white', fontsize=11)


# --- লজিক পার্ট (ডেটা প্রসেসিং) ---
volts_per_sample = MAX_VOLTAGE / 32768.0

def find_trigger(data, threshold=0.1):
    # সিম্পল রাইজিং এজ ট্রিগার
    triggers = np.where((data[:-1] < threshold) & (data[1:] >= threshold))[0]
    return triggers[0] if len(triggers) > 0 else 0

def update(frame):
    try:
        raw_data = stream.read(CHUNK, exception_on_overflow=False)
        data_int = np.frombuffer(raw_data, dtype=np.int16)
        data_volts = data_int * volts_per_sample
        
        left_ch = data_volts[0::2]
        right_ch = data_volts[1::2]
        
        # ট্রিগার (চ্যানেল ১ এর উপর)
        trig_idx = find_trigger(left_ch)
        
        # বাফার থেকে ফিক্সড লেন্থ ডেটা নেওয়া
        if trig_idx + DISPLAY_FRAMES < len(left_ch):
            y1 = left_ch[trig_idx : trig_idx + DISPLAY_FRAMES]
            y2 = right_ch[trig_idx : trig_idx + DISPLAY_FRAMES]
        else:
            y1 = left_ch[:DISPLAY_FRAMES]
            y2 = right_ch[:DISPLAY_FRAMES]
            
        # লাইন আপডেট
        line1.set_ydata(y1)
        line2.set_ydata(y2)
        
        # ভোল্টেজ মেজারমেন্ট আপডেট
        vpp1 = np.ptp(y1)
        vpp2 = np.ptp(y2)
        info_vpp1.set_text(f"Vpp(1): {vpp1:.2f}V")
        info_vpp2.set_text(f"Vpp(2): {vpp2:.2f}V")
        
        # ফ্রিকোয়েন্সি ক্যালকুলেশন (বেসিক)
        zeros = np.where(np.diff(np.sign(y1)))[0]
        if len(zeros) > 2:
            freq = RATE / (zeros[-1] - zeros[0]) * ((len(zeros)-1)/2)
            info_freq.set_text(f"Freq(1): {freq:.1f}Hz")
        
    except Exception:
        pass
    
    return line1, line2, info_vpp1, info_vpp2, info_freq

# অ্যানিমেশন
ani = FuncAnimation(fig, update, interval=20, blit=False) # Blit False রাখলাম যাতে UI ঠিক থাকে

plt.show()

stream.stop_stream()
stream.close()
p.terminate()
