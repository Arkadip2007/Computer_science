import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

fig = plt.figure(figsize=(6,6))
ax = plt.subplot(111, polar=True)

t = np.linspace(0, 20*np.pi, 5000)

line, = ax.plot([], [], lw=2)

ax.set_ylim(-1.2, 1.2)

def update(frame):
    # Use the slider value as a speed multiplier for how far to advance
    speed = speed_slider.val
    end = int(frame * speed)
    if end < 1:
        end = 1
    if end > len(t):
        end = len(t)
    theta = t[:end]
    r = np.sin(theta)
    line.set_data(theta, r)
    return line,

# Slider for speed control: 0.1x .. 8x (default 4x)
ax_speed = fig.add_axes([0.25, 0.02, 0.5, 0.03])
speed_slider = Slider(ax_speed, 'Speed', 0.1, 8.0, valinit=4.0)

ani = FuncAnimation(fig, update, frames=len(t),
                    interval=20, blit=True)

plt.show()
