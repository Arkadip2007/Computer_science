import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, CheckButtons, Button

# --- কনফিগারেশন ---
BUFFER_FRAMES = 16384  
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

is_running = True
frame_counter = 0  

ch1_buffer = np.zeros(BUFFER_FRAMES, dtype=np.float32)
ch2_buffer = np.zeros(BUFFER_FRAMES, dtype=np.float32)

p = pyaudio.PyAudio()
try:
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                    input=True, frames_per_buffer=1024)
except Exception as e:
    print(f"Error: {e}")
    exit()

fig = plt.figure(figsize=(14, 7), facecolor=COLOR_BG)
fig.canvas.manager.set_window_title('Keysight Oscilloscope - Pro FFT Edition')

plt.subplots_adjust(left=0.05, right=0.75, top=0.95, bottom=0.1)
ax = fig.add_subplot(111, facecolor=COLOR_SCREEN)

line1, = ax.plot([], [], color=COLOR_CH1, lw=1.5, label='CH1')
line2, = ax.plot([], [], color=COLOR_CH2, lw=1.5, label='CH2')

ax.set_ylim(-1, 1)
ax.set_xlim(0, 1) 
ax.grid(True, which='major', color=COLOR_GRID, linestyle='-', alpha=0.8)
ax.grid(True, which='minor', color=COLOR_GRID, linestyle=':', alpha=0.4)
ax.minorticks_on()
ax.set_xticklabels([])
ax.set_yticklabels([])

# ==========================================
# ডান দিকের কন্ট্রোল প্যানেল
# ==========================================
fig.text(0.87, 0.92, "CONTROL PANEL", color='white', ha='center', fontsize=14, fontweight='bold')

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

ax_check = plt.axes([0.8, 0.65, 0.14, 0.1], facecolor=COLOR_PANEL)
check = CheckButtons(ax_check, ('CH1 (Yellow)', 'CH2 (Green)'), (True, True))
for t in check.labels:
    t.set_color('white')

# ভোল্টেজ স্লাইডার (Max 50 করা হয়েছে যাতে দুর্বল সাউন্ডও বড় করে দেখা যায়)
fig.text(0.87, 0.58, "VERTICAL (Volt/Div)", color='white', ha='center', fontsize=10)
ax_volt = plt.axes([0.8, 0.54, 0.14, 0.03], facecolor=COLOR_PANEL)
s_volt = Slider(ax_volt, '', 0.1, 50.0, valinit=5.0, color=COLOR_CH1)

fig.text(0.87, 0.46, "HORIZONTAL (Time/Div)", color='white', ha='center', fontsize=10)
ax_time = plt.axes([0.8, 0.42, 0.14, 0.03], facecolor=COLOR_PANEL)
s_time = Slider(ax_time, '', 100, BUFFER_FRAMES//2, valinit=2000, color='#3498DB')

fig.text(0.87, 0.35, "MEASUREMENTS", color='gray', ha='center', fontsize=10, style='italic')
ax_meas = plt.axes([0.8, 0.15, 0.15, 0.15], facecolor=COLOR_BG)
ax_meas.axis('off')
txt_vpp1 = ax_meas.text(0.0, 0.8, "CH1 Vpp: 0.00 V", color=COLOR_CH1, fontsize=11, fontweight='bold')
txt_vpp2 = ax_meas.text(0.0, 0.5, "CH2 Vpp: 0.00 V", color=COLOR_CH2, fontsize=11, fontweight='bold')
txt_freq = ax_meas.text(0.0, 0.2, "Freq: -- Hz", color='white', fontsize=11, fontweight='bold')

def on_scroll(event):
    if event.inaxes == ax_volt:
        step = 1.0 if event.step > 0 else -1.0
        s_volt.set_val(max(s_volt.valmin, min(s_volt.valmax, s_volt.val + step)))
    elif event.inaxes == ax_time:
        step = 200 if event.step > 0 else -200
        s_time.set_val(max(s_time.valmin, min(s_time.valmax, s_time.val + step)))
fig.canvas.mpl_connect('scroll_event', on_scroll)

def init():
    line1.set_data([], [])
    line2.set_data([], [])
    return line1, line2, txt_vpp1, txt_vpp2, txt_freq

# --- মেইন আপডেট লজিক ---
def update(frame):
    global is_running, ch1_buffer, ch2_buffer, frame_counter

    if not is_running:
        return line1, line2, txt_vpp1, txt_vpp2, txt_freq

    try:
        frames_avail = stream.get_read_available()
        if frames_avail > 0:
            frames_to_read = min(frames_avail, 4096) 
            raw_data = stream.read(frames_to_read, exception_on_overflow=False)
            data_int = np.frombuffer(raw_data, dtype=np.int16)
            
            if len(data_int) % 2 != 0:
                data_int = data_int[:-1]
                
            if len(data_int) > 0:
                new_ch1 = data_int[0::2] / 32768.0
                new_ch2 = data_int[1::2] / 32768.0
                
                ch1_buffer = np.roll(ch1_buffer, -len(new_ch1))
                ch1_buffer[-len(new_ch1):] = new_ch1
                
                ch2_buffer = np.roll(ch2_buffer, -len(new_ch2))
                ch2_buffer[-len(new_ch2):] = new_ch2
    except Exception as e:
        pass

    gain = s_volt.val
    display_points = int(s_time.val)
    
    # নয়েজ ইগনোর করার জন্য সিগন্যাল স্ট্রেন্থ চেক করা হচ্ছে
    signal_peak = np.max(np.abs(ch1_buffer[-display_points:]))
    
    # ট্রিগার লজিক (সিগন্যাল দুর্বল হলে ট্রিগার করবে না)
    trigger_threshold = 0.05 
    if signal_peak > trigger_threshold:
        search_end = len(ch1_buffer) - display_points
        search_start = max(0, search_end - display_points) 
        search_area = ch1_buffer[search_start:search_end] 
        triggers = np.where((search_area[:-1] < trigger_threshold) & (search_area[1:] >= trigger_threshold))[0]
        trig_idx = search_start + triggers[-1] if len(triggers) > 0 else len(ch1_buffer) - display_points
    else:
        trig_idx = len(ch1_buffer) - display_points 
        
    disp_ch1 = ch1_buffer[trig_idx : trig_idx + display_points] * gain
    disp_ch2 = ch2_buffer[trig_idx : trig_idx + display_points] * gain
    
    x_data = np.linspace(0, 1, display_points)
    status = check.get_status()
    
    if status[0]:
        line1.set_data(x_data, disp_ch1)
        line1.set_visible(True)
    else:
        line1.set_visible(False)
        
    if status[1]:
        line2.set_data(x_data, disp_ch2)
        line2.set_visible(True)
    else:
        line2.set_visible(False)
        
    frame_counter += 1
    if frame_counter % 5 == 0:
        if status[0]:
            vpp1 = np.ptp(disp_ch1) / gain
            txt_vpp1.set_text(f"CH1 Vpp: {vpp1:.3f} V")
            
            # --- নিখুঁত ফ্রিকোয়েন্সি ক্যালকুলেশন (FFT) ---
            # যদি সিগন্যালে পর্যাপ্ত ভলিউম থাকে তবেই ফ্রিকোয়েন্সি মাপবে, নাহলে নয়েজ ইগনোর করবে
            if vpp1 > 0.02: 
                # Hanning উইন্ডো ব্যবহার করে সিগন্যাল স্মুথ করা হচ্ছে
                window = np.hanning(len(disp_ch1))
                fft_result = np.abs(np.fft.rfft(disp_ch1 * window))
                freqs = np.fft.rfftfreq(len(disp_ch1), 1/RATE)
                
                # সবচেয়ে শক্তিশালী ফ্রিকোয়েন্সি বের করা
                peak_freq = freqs[np.argmax(fft_result)]
                
                if peak_freq > 20: # 20Hz এর নিচের ফ্রিকোয়েন্সি (DC noise) বাদ
                    txt_freq.set_text(f"Freq: {peak_freq:.1f} Hz")
                else:
                    txt_freq.set_text("Freq: -- Hz")
            else:
                txt_freq.set_text("Freq: Low Signal")
        else:
            txt_vpp1.set_text("CH1 Vpp: OFF")
            txt_freq.set_text("Freq: -- Hz")

        if status[1]:
            vpp2 = np.ptp(disp_ch2) / gain
            txt_vpp2.set_text(f"CH2 Vpp: {vpp2:.3f} V")
        else:
            txt_vpp2.set_text("CH2 Vpp: OFF")

    return line1, line2, txt_vpp1, txt_vpp2, txt_freq

ani = FuncAnimation(fig, update, init_func=init, interval=30, blit=True)
plt.show()

stream.stop_stream()
stream.close()
p.terminate()
