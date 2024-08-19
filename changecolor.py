import customtkinter as ctk
from tkinter import colorchooser, messagebox
import bulb_config
import asyncio
from kasa import SmartBulb
import threading

class ChangeColor(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Change Color")
        self.geometry("500x600")

        ctk.CTkLabel(self, text="Change Color", font=("Arial", 16)).pack(pady=20)

        self.bulb_vars = [ctk.BooleanVar() for _ in bulb_config.BULB_DATABASE]
        self.bulb_checkboxes = []
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Select Bulbs")
        self.scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Add Select All Checkbox
        self.select_all_var = ctk.BooleanVar()
        self.select_all_checkbox = ctk.CTkCheckBox(self.scrollable_frame, text="Select All", variable=self.select_all_var, command=self.toggle_select_all)
        self.select_all_checkbox.pack(pady=2, padx=10, anchor="w")

        for i, (name, _) in enumerate(bulb_config.BULB_DATABASE.items()):
            cb = ctk.CTkCheckBox(self.scrollable_frame, text=name, variable=self.bulb_vars[i])
            cb.pack(pady=2, padx=10, anchor="w")
            self.bulb_checkboxes.append(cb)

        colors_frame = ctk.CTkFrame(self)
        colors_frame.pack(pady=10)

        self.color_buttons = []
        colors = {"Red": (255, 0, 0), "Green": (0, 255, 0), "Blue": (0, 0, 255), 
                  "Yellow": (255, 255, 0), "Purple": (128, 0, 128), "Cyan": (0, 255, 255)}
        for color_name, rgb in colors.items():
            button = ctk.CTkButton(colors_frame, text=color_name, 
                                   command=lambda c=rgb: self.select_color(c),
                                   fg_color='#{:02x}{:02x}{:02x}'.format(*rgb),
                                   text_color="black" if color_name in ["Yellow", "Cyan"] else "white")
            button.pack(side="left", padx=5)
            self.color_buttons.append(button)

        self.custom_color_button = ctk.CTkButton(self, text="Select Custom Color", command=self.open_color_chooser)
        self.custom_color_button.pack(pady=20)

        self.apply_button = ctk.CTkButton(self, text="Apply Color", command=self.apply_color)
        self.apply_button.pack(pady=10)

        self.selected_color_label = ctk.CTkLabel(self, text="Selected Color: None", font=("Arial", 12))
        self.selected_color_label.pack(pady=10)

        self.selected_color = None

    def toggle_select_all(self):
        select_all = self.select_all_var.get()
        for var in self.bulb_vars:
            var.set(select_all)

    def select_color(self, color):
        self.selected_color = color
        self.selected_color_label.configure(text=f"Selected Color: RGB{color}")

    def open_color_chooser(self):
        color = colorchooser.askcolor()[0]
        if color:
            self.select_color(tuple(map(int, color)))

    def apply_color(self):
        if not self.selected_color:
            messagebox.showerror("Error", "No color selected")
            return
        
        selected_bulbs = [ip for i, (_, ip) in enumerate(bulb_config.BULB_DATABASE.items()) if self.bulb_vars[i].get()]
        if not selected_bulbs:
            messagebox.showerror("Error", "No bulbs selected")
            return

        threading.Thread(target=self._apply_color_thread, args=(selected_bulbs, self.selected_color)).start()

    def _apply_color_thread(self, selected_bulbs, color):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._set_bulb_colors(selected_bulbs, color))
            self.after(0, lambda: messagebox.showinfo("Success", f"Color RGB{color} applied to selected bulbs"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to apply color: {str(e)}"))
        finally:
            loop.close()

    async def _set_bulb_colors(self, bulb_ips, color):
        tasks = []
        for ip in bulb_ips:
            bulb = SmartBulb(ip)
            tasks.append(self._set_bulb_color(bulb, color))
        await asyncio.gather(*tasks)

    async def _set_bulb_color(self, bulb, color):
        try:
            await bulb.update()
            h, s, v = self._rgb_to_hsv(*color)
            await bulb.set_hsv(h, s, v)
        except Exception as e:
            print(f"Error setting color for bulb {bulb.host}: {e}")
            raise

    def _rgb_to_hsv(self, r, g, b):
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
        return int(h), int(s), int(v)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ChangeColor(root)
    root.mainloop()
