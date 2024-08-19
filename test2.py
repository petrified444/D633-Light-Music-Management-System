import customtkinter as ctk
from tkinter import filedialog, messagebox
import pyaudio
import wave
import threading
import librosa
import time
from pydub import AudioSegment
import io

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

        self.load_button = ctk.CTkButton(self, text="Load Music File", command=self.load_music_file)
        self.load_button.pack(pady=10)
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

    def load_music_file(self):
        self.music_file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if self.music_file:
            self.start_button.configure(state="normal")
            self.status_label.configure(text=f"Loaded: {self.music_file}")
            self.detect_beats()

    def detect_beats(self):
        # Load the audio file for beat detection
        y, sr = librosa.load(self.music_file)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        self.beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        print(f"Detected {len(self.beat_times)} beats.")

    def start_sync(self):
        if not self.music_file:
            messagebox.showerror("Error", "No music file loaded")
            return

        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="Status: Running")

        # Start threads for music playback and light synchronization
        self.audio_thread = threading.Thread(target=self.play_music)
        self.sync_thread = threading.Thread(target=self.sync_lights_with_beats)
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
        # Handle both WAV and MP3 files
        if self.music_file.endswith('.mp3'):
            audio = AudioSegment.from_mp3(self.music_file)
            with io.BytesIO() as buffer:
                audio.export(buffer, format='wav')
                buffer.seek(0)
                wf = wave.open(buffer, 'rb')
                self._play_wave_file(wf)
        elif self.music_file.endswith('.wav'):
            wf = wave.open(self.music_file, 'rb')
            self._play_wave_file(wf)

    def _play_wave_file(self, wf):
        p = pyaudio.PyAudio()

        self.stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                             channels=wf.getnchannels(),
                             rate=wf.getframerate(),
                             output=True)

        data = wf.readframes(1024)
        while data and self.is_running:
            self.stream.write(data)
            data = wf.readframes(1024)

        wf.close()
        p.terminate()

    def sync_lights_with_beats(self):
        start_time = time.time()
        for beat_time in self.beat_times:
            if not self.is_running:
                break
            sleep_time = beat_time - (time.time() - start_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            self.update_bulb_colors()
            time.sleep(0.1)  # Keep the colors for 100 ms
            self.reset_bulb_colors()

    def update_bulb_colors(self):
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]
        for i, button in enumerate(self.bulb_buttons):
            button.configure(fg_color=colors[i % len(colors)])

    def reset_bulb_colors(self):
        for button in self.bulb_buttons:
            button.configure(fg_color="gray")

if __name__ == "__main__":
    app = SyncLightsWithMusic()
    app.mainloop()

