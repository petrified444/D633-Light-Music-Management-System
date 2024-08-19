import customtkinter as ctk
from tkinter import colorchooser, messagebox
import asyncio
from kasa import SmartBulb
import bulb_config
import threading

class ChangePatterns(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Change Patterns")
        self.geometry("500x700")

        ctk.CTkLabel(self, text="Change Patterns", font=("Arial", 16)).pack(pady=20)

        self.colors = []
        self.color_buttons = []

        for i in range(5):
            button = ctk.CTkButton(self, text=f"Select Color {i+1}", command=lambda i=i: self.select_color(i))
            button.pack(pady=5)
            self.color_buttons.append(button)

        self.interval_label = ctk.CTkLabel(self, text="Switch Interval (seconds):")
        self.interval_label.pack(pady=5)

        self.interval_entry = ctk.CTkEntry(self)
        self.interval_entry.pack(pady=5)
        self.interval_entry.insert(0, "1.0")  # Default interval

        self.save_button = ctk.CTkButton(self, text="Save Pattern", command=self.save_pattern)
        self.save_button.pack(pady=10)

        self.run_button = ctk.CTkButton(self, text="Run Pattern", command=self.run_pattern)
        self.run_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(self, text="Stop Pattern", command=self.stop_pattern, state="disabled")
        self.stop_button.pack(pady=10)

        self.pattern_label = ctk.CTkLabel(self, text="Pattern: None")
        self.pattern_label.pack(pady=10)

        self.bulb_frame = ctk.CTkScrollableFrame(self, label_text="Select Bulbs")
        self.bulb_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Add Select All Checkbox
        self.select_all_var = ctk.BooleanVar()
        self.select_all_checkbox = ctk.CTkCheckBox(self.bulb_frame, text="Select All", variable=self.select_all_var, command=self.toggle_select_all)
        self.select_all_checkbox.pack(pady=2, padx=10, anchor="w")

        self.bulb_vars = [ctk.BooleanVar() for _ in bulb_config.BULB_DATABASE]
        self.bulb_checkboxes = []
        for i, (name, _) in enumerate(bulb_config.BULB_DATABASE.items()):
            cb = ctk.CTkCheckBox(self.bulb_frame, text=name, variable=self.bulb_vars[i])
            cb.pack(pady=2, padx=10, anchor="w")
            self.bulb_checkboxes.append(cb)

        self.current_pattern = None
        self.is_running = False
        self.pattern_thread = None

    def toggle_select_all(self):
        select_all = self.select_all_var.get()
        for var in self.bulb_vars:
            var.set(select_all)

    def select_color(self, index):
        color = colorchooser.askcolor()[1]
        if color:
            if len(self.colors) > index:
                self.colors[index] = color
            else:
                self.colors.append(color)
            self.color_buttons[index].configure(fg_color=color)
            self.update_pattern_label()

    def update_pattern_label(self):
        pattern_text = "Pattern: " + ", ".join(self.colors)
        self.pattern_label.configure(text=pattern_text)

    def save_pattern(self):
        if len(self.colors) < 5:
            messagebox.showerror("Error", "Please select 5 colors")
            return
        
        try:
            interval = float(self.interval_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid interval in seconds")
            return

        self.current_pattern = {"colors": self.colors, "interval": interval}
        messagebox.showinfo("Success", "Pattern saved")

    def run_pattern(self):
        if not self.current_pattern:
            messagebox.showerror("Error", "No pattern saved")
            return
        
        selected_bulbs = [ip for i, (_, ip) in enumerate(bulb_config.BULB_DATABASE.items()) if self.bulb_vars[i].get()]
        if not selected_bulbs:
            messagebox.showerror("Error", "No bulbs selected")
            return

        self.is_running = True
        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.pattern_thread = threading.Thread(target=self._run_pattern, args=(selected_bulbs,))
        self.pattern_thread.start()

    def _run_pattern(self, selected_bulbs):
        asyncio.run(self._control_bulbs(selected_bulbs))

    async def _control_bulbs(self, selected_bulbs):
        try:
            bulbs = [SmartBulb(ip) for ip in selected_bulbs]
            await asyncio.gather(*[bulb.update() for bulb in bulbs])

            while self.is_running:
                tasks = []
                for i, bulb in enumerate(bulbs):
                    color = self.current_pattern["colors"][i % len(self.current_pattern["colors"])]
                    tasks.append(self.set_bulb_color(bulb, color))

                await asyncio.gather(*tasks)
                self.current_pattern["colors"].append(self.current_pattern["colors"].pop(0))  # Rotate colors
                await asyncio.sleep(self.current_pattern["interval"])
        except Exception as e:
            print(f"Error during bulb control: {e}")

    async def set_bulb_color(self, bulb, color):
        try:
            rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            h, s, v = self.rgb_to_hsv(*rgb)
            await bulb.set_hsv(int(h), int(s), int(v))
        except Exception as e:
            print(f"Error setting color for bulb {bulb.host}: {e}")

    def stop_pattern(self):
        self.is_running = False
        self.after(100, self._check_thread_stopped)

    def _check_thread_stopped(self):
        if self.pattern_thread and self.pattern_thread.is_alive():
            self.after(100, self._check_thread_stopped)
        else:
            self._update_ui_after_stop()

    def _update_ui_after_stop(self):
        self.run_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r/255.0, g/255.0, b/255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        diff = mx-mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g-b)/diff) + 360) % 360
        elif mx == g:
            h = (60 * ((b-r)/diff) + 120) % 360
        else:
            h = (60 * ((r-g)/diff) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = (diff/mx) * 100
        v = mx * 100
        return h, s, v

if __name__ == "__main__":
    root = ctk.CTk()
    app = ChangePatterns(root)
    root.mainloop()
