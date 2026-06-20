import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import struct

# কনফিগারেশন
CHUNK = 1024 * 2             # একসাথে কতগুলো ডেটা পয়েন্ট পড়বে
FORMAT = pyaudio.paInt16     # 16-bit রেজোলিউশন
CHANNELS = 2                 # ২ চ্যানেল (লেফট এবং রাইট)
RATE = 44100                 # স্যাম্পলিং রেট (Hz)

# PyAudio ইনিশিয়ালাইজেশন
p = pyaudio.PyAudio()

# স্ট্রিম ওপেন করা (মাইক্রোফোন থেকে ইনপুট নেওয়ার জন্য)
try:
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
except Exception as e:
    print("মাইক্রোফোন ওপেন করতে সমস্যা হচ্ছে। দয়া করে ইনপুট ডিভাইস চেক করুন।")
    print(f"Error: {e}")
    exit()

# গ্রাফ সেটআপ
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
fig.suptitle('2-Channel Audio Oscilloscope', fontsize=16)

# X-অক্ষ (টাইম ডোমেইন)
x = np.arange(0, CHUNK)

# চ্যানেল ১ (লেফট) এর জন্য লাইন
line1, = ax1.plot(x, np.random.rand(CHUNK), '-', lw=1, color='g')
ax1.set_title('Channel 1 (Left)')
ax1.set_ylim(-30000, 30000)  # 16-bit অডিওর রেঞ্জ (-32768 থেকে 32767)
ax1.set_ylabel('Amplitude')
ax1.grid(True)

# চ্যানেল ২ (রাইট) এর জন্য লাইন
line2, = ax2.plot(x, np.random.rand(CHUNK), '-', lw=1, color='r')
ax2.set_title('Channel 2 (Right)')
ax2.set_ylim(-30000, 30000)
ax2.set_xlabel('Samples')
ax2.set_ylabel('Amplitude')
ax2.grid(True)

# আপডেট ফাংশন (এটি বারবার কল হবে)
def update(frame):
    try:
        # মাইক থেকে ডেটা পড়া
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        # বাইনারি ডেটাকে ইন্টিজারে কনভার্ট করা
        data_int = np.frombuffer(data, dtype=np.int16)
        
        # স্টেরিও ডেটা আলাদা করা
        # অ্যারের স্ট্রাকচার হয়: [L, R, L, R, L, R...]
        # তাই আমরা স্লাইসিং ব্যবহার করব
        left_channel = data_int[0::2]  # জোড় পজিশন (0, 2, 4...)
        right_channel = data_int[1::2] # বিজোড় পজিশন (1, 3, 5...)
        
        # গ্রাফ আপডেট করা
        line1.set_ydata(left_channel)
        line2.set_ydata(right_channel)
        
    except Exception as e:
        print(f"Error: {e}")
    
    return line1, line2

# অ্যানিমেশন শুরু করা
ani = FuncAnimation(fig, update, interval=1, blit=True)

print("অসিলোস্কোপ চালু হয়েছে... বন্ধ করতে গ্রাফ উইন্ডোটি ক্লোজ করুন।")
plt.show()

# প্রোগ্রাম বন্ধ হলে স্ট্রিম ক্লিন করা
stream.stop_stream()
stream.close()
p.terminate()
