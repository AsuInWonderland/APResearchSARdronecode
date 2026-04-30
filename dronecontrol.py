import tkinter as tk
from pynput import keyboard
import socket
import threading
import time

PI_IP = "enter_pi's_IP_here_I_am_not_leaking_mines"
UDP_PORT = 5005
UPDATE_HZ = 50 

class DroneGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Control")
        self.root.configure(bg="#1a1a1a")
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.armed = False
        self.pressed = set()
        self.roll, self.pitch, self.yaw = 1500, 1500, 1500
        self.throttle = 1000 
        self.aux1 = 1000 

        self.keys = {}
        self.setup_ui()
        
        self.running = True
        threading.Thread(target=self.udp_sender_loop, daemon=True).start()
        
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def setup_ui(self):
        # Keystrokes
        layout = [
            ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
            ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
            ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
            ['space', 'shift', 'esc']
        ]
        
        key_frame = tk.Frame(self.root, bg="#1a1a1a")
        key_frame.pack(pady=10)

        for r_idx, row in enumerate(layout):
            for c_idx, key in enumerate(row):
                lbl = tk.Label(key_frame, text=key.upper(), bg="gray", fg="white", 
                               width=6, height=2, font=("Arial", 10, "bold"))
                lbl.grid(row=r_idx, column=c_idx, padx=2, pady=2)
                self.keys[key] = lbl

        self.status_label = tk.Label(self.root, text="NOT PRIMED", bg="red", 
                                     fg="white", font=("Arial", 14, "bold"), width=30)
        self.status_label.pack(pady=10)
        
        self.tele_label = tk.Label(self.root, text="T: 1000 | AUX1: 1000", bg="#1a1a1a", 
                                    fg="cyan", font=("Courier", 12))
        self.tele_label.pack(pady=5)

    def on_press(self, key):
        try: k = key.char.lower()
        except: k = key.name
        
        if k in self.keys:
            self.pressed.add(k)
            self.keys[k].config(bg="yellow")
            
        if k == 'o': 
            self.aux1 = 2000
            self.armed = True
            self.status_label.config(text="ARMED (AUX1: 2000)", bg="green")
        if k == 'p' or k == 'esc':
            self.aux1 = 1000
            self.armed = False
            self.throttle = 1000
            self.status_label.config(text="DISARMED (AUX1: 1000)", bg="red")

    def on_release(self, key):
        try: k = key.char.lower()
        except: k = key.name
        if k in self.pressed:
            self.pressed.discard(k)
            if k in self.keys: self.keys[k].config(bg="gray")

    def udp_sender_loop(self):
        while self.running:
            # Control Logic
            self.pitch = 1400 if 'w' in self.pressed else (1600 if 's' in self.pressed else 1500)
            self.roll = 1400 if 'a' in self.pressed else (1600 if 'd' in self.pressed else 1500)
            self.yaw = 1400 if 'q' in self.pressed else (1600 if 'e' in self.pressed else 1500)
            
            if 'space' in self.pressed: self.throttle = min(self.throttle + 10, 2000)
            if 'shift' in self.pressed: self.throttle = max(self.throttle - 10, 1000)

            # Send 5 channels
            msg = f"{self.roll},{self.pitch},{self.throttle},{self.yaw},{self.aux1}"
            try:
                self.sock.sendto(msg.encode(), (PI_IP, UDP_PORT))
            except:
                pass
            
            self.tele_label.config(text=f"THR: {self.throttle} | AUX1: {self.aux1}")
            time.sleep(1/UPDATE_HZ)

if __name__ == "__main__":
    root = tk.Tk()
    app = DroneGUI(root)
    root.mainloop()
