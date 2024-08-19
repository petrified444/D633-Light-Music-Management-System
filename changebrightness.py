import customtkinter as ctk
from tkinter import messagebox
import bulb_config
import asyncio
from kasa import SmartBulb

class ChangeBrightness(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Change Brightness")
        self.geometry("400x600")

        ctk.CTkLabel(self, text="Change Brightness", font=("Arial", 16)).pack(pady=20)

        self.bulb_vars = [ctk.BooleanVar() for _ in bulb_config.BULB_DATABASE]
        self.bulb_checkboxes = []
        for i, (name, _) in enumerate(bulb_config.BULB_DATABASE.items()):
            cb = ctk.CTkCheckBox(self, text=name, variable=self.bulb_vars[i])
            cb.pack()
            self.bulb_checkboxes.append(cb)

        self.select_all_var = ctk.BooleanVar()
        self.select_all_cb = ctk.CTkCheckBox(self, text="Select All", variable=self.select_all_var, command=self.toggle_all_bulbs)
        self.select_all_cb.pack(pady=10)

        self.brightness_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.update_brightness_label)
        self.brightness_slider.pack(pady=20)

        self.brightness_value_label = ctk.CTkLabel(self, text="Brightness: 50%")
        self.brightness_value_label.pack(pady=5)

        self.apply_button = ctk.CTkButton(self, text="Apply Brightness", command=self.apply_brightness)
        self.apply_button.pack(pady=10)

        self.brightness_slider.set(50)

    def toggle_all_bulbs(self):
        state = self.select_all_var.get()
        for var in self.bulb_vars:
            var.set(state)

    def update_brightness_label(self, value):
        brightness = int(float(value))
        self.brightness_value_label.configure(text=f"Brightness: {brightness}%")

    def apply_brightness(self):
        brightness = int(self.brightness_slider.get())
        selected_bulbs = [ip for i, (_, ip) in enumerate(bulb_config.BULB_DATABASE.items()) if self.bulb_vars[i].get()]
        
        if not selected_bulbs:
            messagebox.showerror("Error", "No bulbs selected")
            return

        asyncio.run(self.set_bulb_brightness(selected_bulbs, brightness))

    async def set_bulb_brightness(self, bulb_ips, brightness):
        tasks = []
        for ip in bulb_ips:
            bulb = SmartBulb(ip)
            tasks.append(self.set_single_bulb_brightness(bulb, brightness))
        await asyncio.gather(*tasks)
        messagebox.showinfo("Success", f"Brightness {brightness}% applied to selected bulbs")

    async def set_single_bulb_brightness(self, bulb, brightness):
        try:
            await bulb.update()
            await bulb.set_brightness(brightness)
        except Exception as e:
            print(f"Error setting brightness for bulb {bulb.host}: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = ChangeBrightness(master=root)
    root.mainloop()