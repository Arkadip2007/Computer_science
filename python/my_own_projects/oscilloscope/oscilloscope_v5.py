import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, CheckButtons, Button

# --- কনফিগারেশন ---
BUFFER_FRAMES = 8192  # ডিসপ্লে করার জন্য মোট ডেটা
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

# --- Keysight কালার স্কিম ---
COLOR_BG = '#1e1e1e'
COLOR_PANEL = '#2d2d2d'
COLOR_SCREEN = '#000000'
COLOR_CH1 = '#F4D03F'
COLOR_CH2 = '#2ECC71'
COLOR_GRID = '#444444'

# গ্লোবাল ভেরিয়েবল
is_running = True
prev_display_points = 1000  # x-axis বার বার আপডেট এড়ানোর জন্য

# রোলিং বাফার (স্মুথ এনিমেশনের জন্য)
audio_buffer = np.zeros(BUFFER_FRAMES * CHANNELS, dtype=np.int16)

# --- অডিও সেটআপ ---
p = pyaudio.PyAudio()
try:
    # chunk সাইজ ছোট রাখা হয়েছে যাতে রিড করতে সময় কম লাগে
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                    input=True, frames_per_buffer=1024)
except Exception as e:
    print(f"Error: অডিও ডিভাইস পাওয়া যায়নি। বিস্তারিত: {e}")
    exit()

# --- গ্রাফিক্যাল ইন্টারফেস তৈরি ---
fig = plt.figure(figsize=(14, 7), facecolor=COLOR_BG)
fig.canvas.manager.set_window_title('Keysight Oscilloscope - Lab Edition')

plt.subplots_adjust(left=0.05, right=0.75, top=0.95, bottom=0.1)
ax = fig.add_subplot(111, facecolor=COLOR_SCREEN)

line1, = ax.plot([], [], color=COLOR_CH1, lw=1.5, label='CH1')
line2, = ax.plot([], [], color=COLOR_CH2, lw=1.5, label='CH2')

ax.set_ylim(-1, 1)
ax.grid(True, which='major', color=COLOR_GRID, linestyle='-', alpha=0.8)
ax.grid(True, which='minor', color=COLOR_GRID, linestyle=':', alpha=0.4)
ax.minorticks_on()
ax.set_xticklabels([])
ax.set_yticklabels([])

# ==========================================
# ডান দিকের কন্ট্রোল প্যানেল (Control Panel)
# ==========================================

fig.text(0.87, 0.92, "CONTROL PANEL", color='white', ha='center', fontsize=14, fontweight='bold')

# ১. Run / Stop বাটন
ax_run = plt.axes([0.8, 0.8, 0.14, 0.06])
btn_run = Button(ax_run, 'STOP', color='#E74C3C', hovercolor='#C0392B')
btn_run.label.set_fontsize(12)
btn_run.label.set_fontweight('bold')
btn_run.label.set_color('white')

def toggle_run(event):
    global is_running
    is_running = not is_running
    btn_run.label.set_text('STOP' if is_running else 'RUN')
    btn_run.color = '#E74C3C' if is_running else '#2ECC71'
    fig.canvas.draw_idle()
    
btn_run.on_clicked(toggle_run)

# ২. চ্যানেল অন/অফ কন্ট্রোল
ax_check = plt.axes([0.8, 0.65, 0.14, 0.1], facecolor=COLOR_PANEL)
check = CheckButtons(ax_check, ('CH1 (Yellow)', 'CH2 (Green)'), (True, True))
for t in check.labels:
    t.set_color('white')
    t.set_fontsize(11)

# ৩. ভোল্টেজ স্কেল (Amplitude Slider)
fig.text(0.87, 0.58, "VERTICAL (Volt/Div)", color='white', ha='center', fontsize=10)
ax_volt = plt.axes([0.8, 0.54, 0.14, 0.03], facecolor=COLOR_PANEL)
s_volt = Slider(ax_volt, '', 0.1, 5.0, valinit=1.0, color=COLOR_CH1)

# ৪. টাইম স্কেল (Timebase Slider)
fig.text(0.87, 0.46, "HORIZONTAL (Time/Div)", color='white', ha='center', fontsize=10)
ax_time = plt.axes([0.8, 0.42, 0.14, 0.03], facecolor=COLOR_PANEL)
s_time = Slider(ax_time, '', 100, BUFFER_FRAMES, valinit=1000, color='#3498DB')

# ==========================================
# মাউস স্ক্রোলিং ইভেন্ট (New Feature)
# ==========================================
def on_scroll(event):
    # যদি মাউস ভোল্টেজ স্লাইডারের উপর থাকে
    if event.inaxes == ax_volt:
        step = 0.2 if event.step > 0 else -0.2
        new_val = max(s_volt.valmin, min(s_volt.valmax, s_volt.val + step))
        s_volt.set_val(new_val)
    
    # যদি মাউস টাইম স্লাইডারের উপর থাকে
    elif event.inaxes == ax_time:
        step = 100 if event.step > 0 else -100
        new_val = max(s_time.valmin, min(s_time.valmax, s_time.val + step))
        s_time.set_val(new_val)

fig.canvas.mpl_connect('scroll_event', on_scroll)

# --- মেইন আপডেট লজিক ---
def update(frame):
    global is_running, audio_buffer, prev_display_points

    if not is_running:
        return line1, line2  

    try:
        # শুধু যতটুকু ডেটা রেডি আছে ততটুকুই পড়ব (Non-blocking)
        frames_avail = stream.get_read_available()
        if frames_avail > 0:
            raw_data = stream.read(frames_avail, exception_on_overflow=False)
            data_int = np.frombuffer(raw_data, dtype=np.int16)
            
            # নতুন ডেটা বাফারে যুক্ত করা (পুরোনো ডেটা বাদ দিয়ে)
            audio_buffer = np.roll(audio_buffer, -len(data_int))
            audio_buffer[-len(data_int):] = data_int
            
    except Exception as e:
        pass

    # স্লাইডার থেকে ভ্যালু পড়া
    gain = s_volt.val
    display_points = int(s_time.val)
    
    # x-axis শুধুমাত্র তখনই আপডেট করব যখন জুম পরিবর্তন হবে (পারফরম্যান্স বুস্ট)
    if display_points != prev_display_points:
        ax.set_xlim(0, display_points)
        prev_display_points = display_points

    # ভোল্টেজ অ্যাডজাস্টমেন্ট
    data_volts = (audio_buffer / 32768.0) * gain
    
    ch1 = data_volts[0::2]
    ch2 = data_volts[1::2]
    
    # চ্যানেল ১ 
    if check.get_status()[0]:
        line1.set_data(np.arange(display_points), ch1[-display_points:])
        line1.set_visible(True)
    else:
        line1.set_visible(False)
        
    # চ্যানেল ২
    if check.get_status()[1]:
        line2.set_data(np.arange(display_points), ch2[-display_points:])
        line2.set_visible(True)
    else:
        line2.set_visible(False)
        
    return line1, line2

# interval কমানো হয়েছে যাতে 60fps এর কাছাকাছি চলে
ani = FuncAnimation(fig, update, interval=15, blit=True)
plt.show()

# ক্লিনআপ
stream.stop_stream()
stream.close()
p.terminate()
