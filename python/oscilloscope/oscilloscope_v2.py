import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec

# --- কনফিগারেশন (Settings) ---
CHUNK = 4096              # বাফার সাইজ (বড় রাখা হয়েছে সেফটির জন্য)
DISPLAY_FRAMES = 1000     # স্ক্রিনে একসাথে কতগুলো পয়েন্ট দেখাবে (Zoom Level)
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
MAX_VOLTAGE = 1.0         # ইনপুট ভোল্টেজ লিমিট (গেইন বা ভোল্ট/ডিভ অ্যাডজাস্ট করতে পারেন)

# --- Keysight কালার স্কিম ---
COLOR_BG = '#282c34'      # অসিলোস্কোপ বডি কালার (Dark Grey)
COLOR_SCREEN = '#000000'  # স্ক্রিন কালার (Black)
COLOR_CH1 = '#F4D03F'     # Keysight Yellow
COLOR_CH2 = '#2ECC71'     # Keysight Green
COLOR_GRID = '#444444'    # গ্রিড কালার
COLOR_TEXT = '#FFFFFF'    # টেক্সট কালার

# --- অডিও স্ট্রিম সেটআপ ---
p = pyaudio.PyAudio()

# ইনপুট ডিভাইস চেক (এরর এড়ানোর জন্য)
try:
    # ডিফল্ট ইনপুট ডিভাইস ওপেন করার চেষ্টা
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
except OSError as e:
    print("Error: ইনপুট ডিভাইস পাওয়া যাচ্ছে না বা অন্য অ্যাপ ব্যবহার করছে।")
    print("টিপস: PulseAudio বা Jack অডিও সার্ভার চেক করুন।")
    exit()

# --- গ্রাফিক্যাল ইন্টারফেস (UI) সেটআপ ---
fig = plt.figure(figsize=(12, 7), facecolor=COLOR_BG)
fig.canvas.manager.set_window_title('Keysight Style DSO - Python Edition')

# লেআউট তৈরি (মেইন স্ক্রিন + সাইড ইনফো প্যানেল)
gs = gridspec.GridSpec(1, 4, figure=fig)
ax = fig.add_subplot(gs[0, 0:3], facecolor=COLOR_SCREEN) # ৩ ভাগ জায়গা নেবে স্ক্রিন
ax_info = fig.add_subplot(gs[0, 3], facecolor=COLOR_BG)  # ১ ভাগ জায়গা নেবে ইনফো প্যানেল

# এক্স-অক্ষ (ফিক্সড)
x = np.arange(0, DISPLAY_FRAMES)
volts_per_sample = MAX_VOLTAGE / 32768.0

# লাইন অবজেক্ট তৈরি
line1, = ax.plot(x, np.zeros(DISPLAY_FRAMES), color=COLOR_CH1, lw=2, label='1')
line2, = ax.plot(x, np.zeros(DISPLAY_FRAMES), color=COLOR_CH2, lw=2, label='2', alpha=0.8)

# স্ক্রিন সাজানো (Keysight লুক)
ax.set_ylim(-MAX_VOLTAGE, MAX_VOLTAGE)
ax.set_xlim(0, DISPLAY_FRAMES)
ax.grid(True, which='major', color=COLOR_GRID, linestyle='--', linewidth=0.8)
ax.grid(True, which='minor', color=COLOR_GRID, linestyle=':', linewidth=0.5)
ax.minorticks_on()

# টেক্সট লেবেল সরানো (ক্লিন লুকের জন্য)
ax.set_xticklabels([])
ax.set_yticklabels([])

# টপ বার ইনফো
header_text = ax.text(0.02, 1.02, "RUN", transform=ax.transAxes, color='#00FF00', fontsize=12, fontweight='bold')
ax.text(0.1, 1.02, "AUTO", transform=ax.transAxes, color='white', fontsize=10)
ax.text(0.8, 1.02, "200us/div", transform=ax.transAxes, color='white', fontsize=10)

# চ্যানেল ইন্ডিকেটর (বামে ছোট ত্রিভুজ থাকে আসল মেশিনে)
ax.text(-0.02, 0.5, "1", transform=ax.transAxes, color=COLOR_CH1, fontweight='bold', va='center')
ax.text(-0.02, 0.45, "2", transform=ax.transAxes, color=COLOR_CH2, fontweight='bold', va='center')

# --- সাইড ইনফো প্যানেল (Fake Measurement Display) ---
ax_info.axis('off') # বর্ডার বা গ্রাফ দরকার নেই
text_vpp1 = ax_info.text(0.1, 0.8, "CH1 Vpp:\n0.00 V", color=COLOR_CH1, fontsize=14, fontweight='bold')
text_vpp2 = ax_info.text(0.1, 0.6, "CH2 Vpp:\n0.00 V", color=COLOR_CH2, fontsize=14, fontweight='bold')
text_freq = ax_info.text(0.1, 0.4, "Freq:\n-- Hz", color='white', fontsize=12)
ax_info.text(0.1, 0.9, "MEASUREMENTS", color='gray', fontsize=10, style='italic')

# --- ট্রিগার লজিক (গ্রাফ স্থির রাখার জন্য) ---
def find_trigger(data, threshold=0.05):
    # সিগন্যাল যখন নেগেটিভ থেকে পজিটিভের দিকে যায় (Rising Edge)
    # বাফার সেফটি: শেষদিকের DISPLAY_FRAMES বাদ দিয়ে খুঁজবো যাতে array out of bound না হয়
    search_zone = data[:-DISPLAY_FRAMES] 
    triggers = np.where((search_zone[:-1] < threshold) & (search_zone[1:] >= threshold))[0]
    
    if len(triggers) > 0:
        return triggers[0]
    return 0 # ট্রিগার না পেলে শুরু থেকেই দেখাও

# --- মেইন আপডেট লুপ ---
def update(frame):
    try:
        # ডেটা পড়া
        raw_data = stream.read(CHUNK, exception_on_overflow=False)
        data_int = np.frombuffer(raw_data, dtype=np.int16)
        
        # ভোল্টেজে কনভার্ট
        data_volts = data_int * volts_per_sample
        
        # চ্যানেল আলাদা করা
        left_ch = data_volts[0::2]
        right_ch = data_volts[1::2]
        
        # ট্রিগার খোঁজা (চ্যানেল ১ এর ওপর ভিত্তি করে)
        trig_idx = find_trigger(left_ch, threshold=0.08)
        
        # ডিসপ্লে ডেটা স্লাইস করা (Fixed Size)
        # আমরা নিশ্চিত করছি যে স্লাইসটি যেন সবসময় DISPLAY_FRAMES সাইজের হয়
        y1_data = left_ch[trig_idx : trig_idx + DISPLAY_FRAMES]
        y2_data = right_ch[trig_idx : trig_idx + DISPLAY_FRAMES]
        
        # গ্রাফ আপডেট
        line1.set_ydata(y1_data)
        line2.set_ydata(y2_data)
        
        # সাইডবারের ইনফো আপডেট (Vpp = Max - Min)
        vpp1 = np.ptp(y1_data) # Peak-to-Peak
        vpp2 = np.ptp(y2_data)
        
        text_vpp1.set_text(f"CH1 Vpp:\n{vpp1:.2f} V")
        text_vpp2.set_text(f"CH2 Vpp:\n{vpp2:.2f} V")
        
        # Frequency calculation (Simple zero-crossing approximation)
        # This is basic; real FFT would be heavier
        zero_crossings = np.where(np.diff(np.sign(y1_data)))[0]
        if len(zero_crossings) > 2:
            cycle_samples = zero_crossings[-1] - zero_crossings[0]
            num_cycles = (len(zero_crossings) - 1) / 2
            signal_freq = (RATE * num_cycles) / cycle_samples
            text_freq.set_text(f"Freq (CH1):\n{signal_freq:.1f} Hz")
        
    except Exception as e:
        print(f"Update Error: {e}")
        pass
    
    return line1, line2, text_vpp1, text_vpp2, text_freq

# অ্যানিমেশন চালু
# blit=True গ্রাফিক্স ফাস্ট করে, কিন্তু টেক্সট আপডেটে মাঝে মাঝে সমস্যা করে।
# এখানে blit=False রাখলাম যাতে সাইডবার ঠিকমতো কাজ করে।
ani = FuncAnimation(fig, update, interval=20, blit=False)

plt.show()

# ক্লিনআপ
stream.stop_stream()
stream.close()
p.terminate()
