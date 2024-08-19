import customtkinter as ctk
from tkinter import filedialog, messagebox
import pyaudio
import wave
import threading
import librosa
import time
from pydub import AudioSegment
import io
import numpy as np
import bulb_config
from kasa import SmartBulb
import asyncio
import os

class SyncLightsWithMusic(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Sync Lights with Music")
        self.geometry("500x700")

        ctk.CTkLabel(self, text="Sync Lights with Music", font=("Arial", 16)).pack(pady=20)

        self.bulb_vars = [ctk.BooleanVar() for _ in bulb_config.BULB_DATABASE]
        self.bulb_checkboxes = []
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Select Bulbs")
        self.scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        for i, (name, _) in enumerate(bulb_config.BULB_DATABASE.items()):
            cb = ctk.CTkCheckBox(self.scrollable_frame, text=name, variable=self.bulb_vars[i])
            cb.pack(pady=2, padx=10, anchor="w")
            self.bulb_checkboxes.append(cb)

        self.select_all_var = ctk.BooleanVar()
        self.select_all_cb = ctk.CTkCheckBox(self, text="Select All", variable=self.select_all_var, command=self.toggle_all_bulbs)
        self.select_all_cb.pack(pady=10)

        self.load_button = ctk.CTkButton(self, text="Load Music File", command=self.load_music_file)
        self.load_button.pack(pady=10)
        
        self.mood_var = ctk.StringVar(value="happy")
        self.mood_menu = ctk.CTkOptionMenu(self, values=["happy", "sad", "rock"], variable=self.mood_var)
        self.mood_menu.pack(pady=10)
        
        self.start_button = ctk.CTkButton(self, text="Start Sync", command=self.start_sync, state="disabled")
        self.start_button.pack(pady=10)
        self.stop_button = ctk.CTkButton(self, text="Stop Sync", command=self.stop_sync, state="disabled")
        self.stop_button.pack(pady=10)
        self.status_label = ctk.CTkLabel(self, text="Status: Not Started")
        self.status_label.pack(pady=20)

        self.is_running = False
        self.stream = None
        self.music_file = None
        self.beat_times = []
        self.bulbs = {}

    def toggle_all_bulbs(self):
        state = self.select_all_var.get()
        for var in self.bulb_vars:
            var.set(state)

    def load_music_file(self):
        self.music_file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if self.music_file:
            self.status_label.configure(text=f"Loading: {os.path.basename(self.music_file)}")
            self.after(0, self._process_music_file)

    def _process_music_file(self):
        try:
            if not os.path.exists(self.music_file):
                raise FileNotFoundError(f"The file {self.music_file} does not exist.")
            
            threading.Thread(target=self._detect_beats, daemon=True).start()
            self.start_button.configure(state="normal")
            self.status_label.configure(text=f"Loaded: {os.path.basename(self.music_file)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process music file: {e}")
            self.status_label.configure(text="Error loading file")

    def _detect_beats(self):
        try:
            y, sr = librosa.load(self.music_file, duration=300)  # Increased duration for longer songs
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            self.beat_times = librosa.frames_to_time(beat_frames, sr=sr)
            print(f"Detected {len(self.beat_times)} beats.")
        except Exception as e:
            print(f"Error detecting beats: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to detect beats: {e}"))

    def start_sync(self):
        if not self.music_file:
            messagebox.showerror("Error", "No music file loaded")
            return

        selected_bulbs = [ip for i, (_, ip) in enumerate(bulb_config.BULB_DATABASE.items()) if self.bulb_vars[i].get()]
        if not selected_bulbs:
            messagebox.showinfo("Info", "No bulbs selected. Running in simulation mode.")

        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="Status: Running")

        self.audio_thread = threading.Thread(target=self.play_music)
        self.sync_thread = threading.Thread(target=lambda: asyncio.run(self.sync_lights_with_beats(selected_bulbs)))
        self.audio_thread.start()
        self.sync_thread.start()

    def stop_sync(self):
        self.is_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Status: Stopped")

        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def play_music(self):
        try:
            print(f"Attempting to play music file: {self.music_file}")
            if self.music_file.lower().endswith('.mp3'):
                print("Converting MP3 to WAV")
                audio = AudioSegment.from_mp3(self.music_file)
                audio_data = io.BytesIO()
                audio.export(audio_data, format="wav")
                audio_data.seek(0)
                wf = wave.open(audio_data, 'rb')
            elif self.music_file.lower().endswith('.wav'):
                print("Opening WAV file directly")
                wf = wave.open(self.music_file, 'rb')
            else:
                raise ValueError(f"Unsupported file format: {os.path.splitext(self.music_file)[1]}")

            p = pyaudio.PyAudio()

            def callback(in_data, frame_count, time_info, status):
                data = wf.readframes(frame_count)
                return (data, pyaudio.paContinue)

            print("Opening audio stream")
            self.stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True,
                                 stream_callback=callback)

            print("Starting audio stream")
            self.stream.start_stream()

            while self.stream.is_active() and self.is_running:
                time.sleep(0.1)

            print("Stopping audio stream")
            self.stream.stop_stream()
            self.stream.close()
            wf.close()
            p.terminate()
            
            print("Audio playback completed")
        except Exception as e:
            print(f"Error playing music: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to play music: {e}"))

    async def sync_lights_with_beats(self, selected_bulbs):
        try:
            if selected_bulbs:
                self.bulbs = {ip: SmartBulb(ip) for ip in selected_bulbs}
                for bulb in self.bulbs.values():
                    await asyncio.wait_for(bulb.update(), timeout=5.0)
            else:
                print("Running in simulation mode (no bulbs selected)")

            start_time = time.time()
            colors = self.get_mood_colors()
            color_index = 0
            for beat_time in self.beat_times:
                if not self.is_running:
                    break
                sleep_time = beat_time - (time.time() - start_time)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                if selected_bulbs:
                    await self.update_bulb_colors(colors[color_index])
                else:
                    print(f"Simulated color change: {colors[color_index]}")
                color_index = (color_index + 1) % len(colors)
                await asyncio.sleep(0.05)  # Shorter duration to make colors more dynamic
        except asyncio.TimeoutError:
            self.after(0, lambda: messagebox.showerror("Error", "Timed out while connecting to bulbs. Are they powered on and connected to the network?"))
        except Exception as e:
            print(f"Error in sync_lights_with_beats: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to sync lights: {e}"))

    def get_mood_colors(self):
        mood = self.mood_var.get()
        if mood == "happy":
            return [(30, 100, 100), (120, 100, 100)]  # Bright Orange, Bright Green
        elif mood == "sad":
            return [(0, 0, 100), (240, 100, 54)]  # White, Dark Blue
        else:  # rock
            return [(0, 100, 100), (0, 0, 100)]  # Red, White

    async def update_bulb_colors(self, hsv_color):
        tasks = []
        for bulb in self.bulbs.values():
            tasks.append(bulb.set_hsv(*hsv_color))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    app = ctk.CTk()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    sync_lights_with_music = SyncLightsWithMusic(app)
    sync_lights_with_music.mainloop()
