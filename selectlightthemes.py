import customtkinter as ctk
from tkinter import messagebox
import bulb_config
import asyncio
from kasa import SmartBulb
import threading

class SelectLightThemes(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Select Light Themes")
        self.geometry("500x750")

        ctk.CTkLabel(self, text="Select Light Themes", font=("Arial", 16)).pack(pady=20)

        # Bulb selection
        self.bulb_vars = [ctk.BooleanVar() for _ in bulb_config.BULB_DATABASE]
        self.bulb_frame = ctk.CTkScrollableFrame(self, label_text="Select Bulbs")
        self.bulb_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Add Select All Checkbox
        self.select_all_var = ctk.BooleanVar()
        self.select_all_checkbox = ctk.CTkCheckBox(self.bulb_frame, text="Select All", variable=self.select_all_var, command=self.toggle_select_all)
        self.select_all_checkbox.pack(pady=2, padx=10, anchor="w")

        for i, (name, _) in enumerate(bulb_config.BULB_DATABASE.items()):
            cb = ctk.CTkCheckBox(self.bulb_frame, text=name, variable=self.bulb_vars[i])
            cb.pack(pady=2, padx=10, anchor="w")

        # Theme buttons
        self.theme_buttons = []
        themes = [
            ("Emergency Lights", self.apply_emergency_lights),
            ("Diwali Lights", self.apply_diwali_lights),
            ("Christmas Lights", self.apply_christmas_lights),
            ("Chinese New Year Lights", self.apply_chinese_new_year_lights)
        ]
        
        for theme, command in themes:
            button = ctk.CTkButton(self, text=theme, command=command)
            button.pack(pady=5)
            self.theme_buttons.append(button)

        # Stop button
        self.stop_button = ctk.CTkButton(self, text="Stop Theme", command=self.stop_theme, state="disabled")
        self.stop_button.pack(pady=10)

        self.current_theme = None
        self.theme_running = False

    def toggle_select_all(self):
        select_all = self.select_all_var.get()
        for var in self.bulb_vars:
            var.set(select_all)

    def apply_theme(self, colors, theme_name):
        if self.theme_running:
            self.stop_theme()

        selected_bulbs = [ip for i, (_, ip) in enumerate(bulb_config.BULB_DATABASE.items()) if self.bulb_vars[i].get()]
        if not selected_bulbs:
            messagebox.showerror("Error", "No bulbs selected")
            return

        self.theme_running = True
        self.stop_button.configure(state="normal")

        # Create an asyncio event loop and run the theme
        self.current_theme = threading.Thread(target=self.run_theme, args=(selected_bulbs, colors))
        self.current_theme.start()

    def run_theme(self, bulb_ips, colors):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.control_theme(bulb_ips, colors))
        finally:
            loop.close()

    async def control_theme(self, bulb_ips, colors):
        bulbs = [SmartBulb(ip) for ip in bulb_ips]
        await asyncio.gather(*[bulb.update() for bulb in bulbs])

        try:
            while self.theme_running:
                for color in colors:
                    tasks = [self.set_bulb_color(bulb, color) for bulb in bulbs]
                    await asyncio.gather(*tasks)
                    await asyncio.sleep(1)  # Control the speed of color change
        except Exception as e:
            print(f"Error during theme control: {e}")

    async def set_bulb_color(self, bulb, color):
        try:
            rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            h, s, v = self.rgb_to_hsv(*rgb)
            await bulb.set_hsv(int(h), int(s), int(v))
        except Exception as e:
            print(f"Error setting color for bulb {bulb.host}: {e}")

    def rgb_to_hsv(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        diff = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / diff) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / diff) + 120) % 360
        else:
            h = (60 * ((r - g) / diff) + 240) % 360
        s = 0 if mx == 0 else (diff / mx) * 100
        v = mx * 100
        return h, s, v

    def stop_theme(self):
        self.theme_running = False
        if self.current_theme:
            self.current_theme.join()
        self.stop_button.configure(state="disabled")
        messagebox.showinfo("Theme Stopped", "The current theme has been stopped.")

    def apply_emergency_lights(self):
        colors = ["#FF0000", "#0827F5"]  # Red and Blue
        self.apply_theme(colors, "Emergency Lights")

    def apply_diwali_lights(self):
        colors = ["#FFA500", "#FFFF00", "#FF4500"]  # Orange, Yellow, Red-Orange
        self.apply_theme(colors, "Diwali Lights")

    def apply_christmas_lights(self):
        colors = ["#FF0000", "#00FF00", "#FFFFFF"]  # Red, Green, White
        self.apply_theme(colors, "Christmas Lights")

    def apply_chinese_new_year_lights(self):
        colors = ["#FF0000", "#FFD700"]  # Red, Gold
        self.apply_theme(colors, "Chinese New Year Lights")

if __name__ == "__main__":
    root = ctk.CTk()
    app = SelectLightThemes(master=root)
    root.mainloop()
