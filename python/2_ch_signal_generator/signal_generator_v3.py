import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

fs=44100
buffer_size=1024
sample_index=0

params={
"A":{"freq":1000.0,"amp":0.5,"phase":0.0,"wave":"Sine","duty":0.5,"enabled":True},
"B":{"freq":500.0,"amp":0.5,"phase":0.0,"wave":"Sine","duty":0.5,"enabled":True}
}

time_scale=0.01
amp_scale=1.0
apply_theme(LIGHT_THEME)


def generate_wave(t,p):

    if not p["enabled"]:
        return np.zeros_like(t)

    phase_t=(t*p["freq"]+p["phase"]/(2*np.pi))%1

    if p["wave"]=="Sine":
        return p["amp"]*np.sin(2*np.pi*phase_t)

    elif p["wave"]=="Square":
        return p["amp"]*np.where(phase_t<p["duty"],1,-1)

    elif p["wave"]=="Triangle":
        return p["amp"]*(2*np.abs(2*phase_t-1)-1)

    elif p["wave"]=="Sawtooth":
        return p["amp"]*(2*phase_t-1)

    elif p["wave"]=="Pulse":
        return p["amp"]*np.where(phase_t<p["duty"],1,-1)

    elif p["wave"]=="Noise":
        return p["amp"]*np.random.uniform(-1,1,len(t))

    return np.zeros_like(t)

def audio_callback(outdata,frames,time,status):
    global sample_index
    t=(np.arange(frames)+sample_index)/fs
    left=generate_wave(t,params["A"])
    right=generate_wave(t,params["B"])
    outdata[:]=np.column_stack((left,right))
    sample_index+=frames

root=tk.Tk()
root.title("Dual Channel Signal Generator")
style=ttk.Style()

def toggle_theme():
   LIGHT_THEME = {
    "bg":"#f0f0f0",
    "fg":"black",
    "plot":"white"
}

DARK_THEME = {
    "bg":"#222222",
    "fg":"white",
    "plot":"#111111"
}

def apply_theme(theme):

    root.configure(bg=theme["bg"])

    style.configure(".",
    background=theme["bg"],
    foreground=theme["fg"])

    style.configure("TFrame",
    background=theme["bg"])

    style.configure("TLabelframe",
    background=theme["bg"],
    foreground=theme["fg"])

    style.configure("TLabelframe.Label",
    background=theme["bg"],
    foreground=theme["fg"])

    style.configure("TLabel",
    background=theme["bg"],
    foreground=theme["fg"])

    style.configure("TButton",
    background=theme["bg"],
    foreground=theme["fg"])

    ax.set_facecolor(theme["plot"])
    fig.patch.set_facecolor(theme["bg"])

    canvas.draw_idle()

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode

    if dark_mode:
        apply_theme(DARK_THEME)
    else:
        apply_theme(LIGHT_THEME)


ttk.Button(root,text="Toggle Dark/Light",command=toggle_theme).pack()


def toggle_channel(ch):
    params[ch]["enabled"]=not params[ch]["enabled"]

def create_control(frame,channel,name,min_val,max_val,step):

    def update(val):
        params[channel][name]=float(val)
        entry.delete(0,tk.END)
        entry.insert(0,str(round(float(val),4)))

    def entry_update(event=None):
        try:
            val=float(entry.get())
            val=max(min(val,max_val),min_val)
            params[channel][name]=val
            slider.set(val)
        except:pass

    def inc():slider.set(params[channel][name]+step)
    def dec():slider.set(params[channel][name]-step)

    tk.Label(frame,text=name.upper()).pack()

    slider=tk.Scale(frame,from_=min_val,to=max_val,
    resolution=step,orient=tk.HORIZONTAL,
    command=update,length=180)
    slider.set(params[channel][name])
    slider.pack()

    def on_scroll(event):
        if event.delta>0:slider.set(slider.get()+step)
        else:slider.set(slider.get()-step)

    slider.bind("<MouseWheel>",on_scroll)

    f=tk.Frame(frame);f.pack()

    tk.Button(f,text="-",width=3,command=dec).pack(side=tk.LEFT)

    entry=tk.Entry(f,width=8)
    entry.insert(0,str(params[channel][name]))
    entry.bind("<Return>",entry_update)
    entry.pack(side=tk.LEFT)

    tk.Button(f,text="+",width=3,command=inc).pack(side=tk.LEFT)

frame_a=tk.LabelFrame(root,text="CHANNEL A")
frame_a.pack(side=tk.LEFT,padx=10)

tk.Button(frame_a,text="Play/Pause",
command=lambda:toggle_channel("A")).pack()

create_control(frame_a,"A","freq",1,20000,1)
create_control(frame_a,"A","amp",0,1,0.01)
create_control(frame_a,"A","phase",0,6.28,0.01)
create_control(frame_a,"A","duty",0.01,0.99,0.01)

wave_a=ttk.Combobox(frame_a,
values=["Sine","Square","Triangle",
"Sawtooth","Noise","Pulse"])
wave_a.set("Sine")
wave_a.bind("<<ComboboxSelected>>",
lambda e:params["A"].update({"wave":wave_a.get()}))
wave_a.pack()

frame_b=tk.LabelFrame(root,text="CHANNEL B")
frame_b.pack(side=tk.LEFT,padx=10)

tk.Button(frame_b,text="Play/Pause",
command=lambda:toggle_channel("B")).pack()

create_control(frame_b,"B","freq",1,20000,1)
create_control(frame_b,"B","amp",0,1,0.01)
create_control(frame_b,"B","phase",0,6.28,0.01)
create_control(frame_b,"B","duty",0.01,0.99,0.01)

wave_b=ttk.Combobox(frame_b,
values=["Sine","Square","Triangle",
"Sawtooth","Noise","Pulse"])
wave_b.set("Sine")
wave_b.bind("<<ComboboxSelected>>",
lambda e:params["B"].update({"wave":wave_b.get()}))
wave_b.pack()

fig,ax=plt.subplots(figsize=(6,4))
x=np.linspace(0,time_scale,1000)
line_a,=ax.plot(x,np.zeros_like(x),label="A")
line_b,=ax.plot(x,np.zeros_like(x),label="B")

ax.set_ylim(-1,1)
ax.legend()

canvas=FigureCanvasTkAgg(fig,master=root)
canvas.get_tk_widget().pack(side=tk.RIGHT,fill=tk.BOTH,expand=True)

def update_time(val):
    global time_scale
    time_scale=float(val)

def update_amp_scale(val):
    global amp_scale
    amp_scale=float(val)

zoom_frame=tk.LabelFrame(root,text="Oscilloscope Control")
zoom_frame.pack(side=tk.BOTTOM,fill=tk.X,anchor="center")

tk.Scale(zoom_frame,from_=0.001,to=0.05,
resolution=0.001,orient=tk.HORIZONTAL,
label="Time Scale",command=update_time).pack(fill=tk.X)

tk.Scale(zoom_frame,from_=0.5,to=5,
resolution=0.1,orient=tk.HORIZONTAL,
label="Amplitude Zoom",
command=update_amp_scale).pack(fill=tk.X)

def update_plot():

    t=np.linspace(0,time_scale,1000)

    y_a=generate_wave(t,params["A"])
    y_b=generate_wave(t,params["B"])

    line_a.set_xdata(t)
    line_b.set_xdata(t)
    line_a.set_ydata(y_a)
    line_b.set_ydata(y_b)

    ax.set_xlim(0,time_scale)
    ax.set_ylim(-amp_scale,amp_scale)

    canvas.draw_idle()
    root.after(50,update_plot)

stream=sd.OutputStream(callback=audio_callback,
samplerate=fs,
channels=2,
blocksize=buffer_size)

stream.start()
update_plot()
root.mainloop()

stream.stop()
stream.close()

