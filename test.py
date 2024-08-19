import customtkinter as ctk
from tkinter import messagebox
import pyaudio
import numpy as np
import threading

class SyncLightsWithMusic(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sync Lights with Music")
        self.geometry("400x600")

        ctk.CTkLabel(self, text="Sync Lights with Music", font=("Arial", 16)).pack(pady=20)
        
        self.bulb_buttons = []
        for i in range(5):
            bulb_button = ctk.CTkButton(self, text=f"Bulb {i+1}", fg_color="gray")
            bulb_button.pack(pady=5)
            self.bulb_buttons.append(bulb_button)

        self.start_button = ctk.CTkButton(self, text="Start Sync", command=self.start_sync)
        self.start_button.pack(pady=10)
        self.stop_button = ctk.CTkButton(self, text="Stop Sync", command=self.stop_sync, state="disabled")
        self.stop_button.pack(pady=10)
        self.status_label = ctk.CTkLabel(self, text="Status: Not Started")
        self.status_label.pack(pady=20)

        self.is_running = False
        self.stream = None

    def start_sync(self):
        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="Status: Running")

        self.audio_thread = threading.Thread(target=self.sync_lights_with_music)
        self.audio_thread.start()

    def stop_sync(self):
        self.is_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Status: Stopped")

        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def sync_lights_with_music(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024)
        self.stream = stream

        while self.is_running:
            data = np.frombuffer(stream.read(1024), dtype=np.int16)
            volume = np.linalg.norm(data)
            self.update_bulb_colors(volume)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def update_bulb_colors(self, volume):
        # Normalize volume for color intensity (Assuming volume ranges from 0 to some max value)
        max_volume = 10000  # You can adjust this value based on your audio input
        normalized_volume = min(volume / max_volume, 1.0)

        # Convert volume to a color intensity
        intensity = int(normalized_volume * 255)
        color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"

        for button in self.bulb_buttons:
            button.configure(fg_color=color)

if __name__ == "__main__":
    app = SyncLightsWithMusic()
    app.mainloop()
