import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider, CheckButtons

# --- কনফিগারেশন ---
CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# --- Keysight কালার স্কিম ---
COLOR_BG = '#21252b'
COLOR_SCREEN = '#000000'
COLOR_CH1 = '#F4D03F' # Yellow
COLOR_CH2 = '#2ECC71' # Green
COLOR_GRID = '#333333'

p = pyaudio.PyAudio()

try:
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                    input=True, frames_per_buffer=CHUNK)
except Exception as e:
    print(f"Error: {e}")
    exit()

# --- গ্রাফিক্যাল ইন্টারফেস ---
fig = plt.figure(figsize=(12, 8), facecolor=COLOR_BG)
gs = gridspec.GridSpec(2, 4, height_ratios=[8, 1], width_ratios=[1, 1, 1, 1])

# মেইন ডিসপ্লে (Oscilloscope Screen)
ax = fig.add_subplot(gs[0, :3], facecolor=COLOR_SCREEN)
plt.subplots_adjust(bottom=0.25)

x_base = np.arange(0, CHUNK)
line1, = ax.plot([], [], color=COLOR_CH1, lw=1.5, label='CH1')
line2, = ax.plot([], [], color=COLOR_CH2, lw=1.5, label='CH2')

ax.set_ylim(-1, 1)
ax.grid(True, which='major', color=COLOR_GRID, linestyle='-', alpha=0.5)
ax.set_xticklabels([])
ax.set_yticklabels([])

# --- স্লাইডার এবং কন্ট্রোল (The "Knobs") ---
# ১. গেইন/অ্যামপ্লিটিউড স্লাইডার
ax_gain = plt.axes([0.15, 0.1, 0.25, 0.03], facecolor='#333333')
s_gain = Slider(ax_gain, 'Volt/Div ', 0.1, 10.0, valinit=1.0, color=COLOR_CH1)

# ২. টাইমবেস/জুম স্লাইডার
ax_time = plt.axes([0.15, 0.05, 0.25, 0.03], facecolor='#333333')
s_time = Slider(ax_time, 'Time/Div ', 100, CHUNK//2, valinit=1000, color='#3498DB')

# ৩. চ্যানেল টগল বাটন (Fixing the Error here)
ax_check = plt.axes([0.55, 0.05, 0.15, 0.08], facecolor=COLOR_BG)
check = CheckButtons(ax_check, ('CH1 ON', 'CH2 ON'), (True, True))

# বাটন টেক্সট কালার ঠিক করা
for text in check.labels:
    text.set_color('white')

# --- আপডেট লজিক ---
def update(frame):
    try:
        raw_data = stream.read(CHUNK, exception_on_overflow=False)
        data_int = np.frombuffer(raw_data, dtype=np.int16)
        
        # স্লাইডার থেকে ভ্যালু নেওয়া
        gain = s_gain.val
        display_points = int(s_time.val)
        
        # ডাটা প্রসেসিং ও নরমালাইজেশন
        data_volts = (data_int / 32768.0) * gain
        
        ch1 = data_volts[0::2]
        ch2 = data_volts[1::2]
        
        # লিমিট সেট করা
        ax.set_xlim(0, display_points)
        
        # চ্যানেল ১ কন্ট্রোল
        if check.get_status()[0]:
            line1.set_data(np.arange(len(ch1[:display_points])), ch1[:display_points])
            line1.set_visible(True)
        else:
            line1.set_visible(False)
            
        # চ্যানেল ২ কন্ট্রোল
        if check.get_status()[1]:
            line2.set_data(np.arange(len(ch2[:display_points])), ch2[:display_points])
            line2.set_visible(True)
        else:
            line2.set_visible(False)
            
    except Exception as e:
        pass
    
    return line1, line2

ani = FuncAnimation(fig, update, interval=20, blit=False)
plt.show()

# ক্লিনআপ
stream.stop_stream()
stream.close()
p.terminate()
