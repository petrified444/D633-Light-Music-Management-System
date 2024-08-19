import customtkinter as ctk
from tkinter import messagebox
import bulb_config
import asyncio
from kasa import SmartBulb

class ControlLights(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Control Lights")
        self.geometry("400x600")

        ctk.CTkLabel(self, text="Control Lights", font=("Arial", 16)).pack(pady=20)

        self.bulb_vars = [ctk.BooleanVar() for _ in bulb_config.BULB_DATABASE]
        self.bulb_checkboxes = []
        for i, (name, _) in enumerate(bulb_config.BULB_DATABASE.items()):
            cb = ctk.CTkCheckBox(self, text=name, variable=self.bulb_vars[i])
            cb.pack()
            self.bulb_checkboxes.append(cb)

        self.select_all_var = ctk.BooleanVar()
        self.select_all_cb = ctk.CTkCheckBox(self, text="Select All", variable=self.select_all_var, command=self.toggle_all_bulbs)
        self.select_all_cb.pack(pady=10)

        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(pady=20)

        self.individual_on_button = ctk.CTkButton(self.control_frame, text="Turn Selected On", command=self.turn_selected_on)
        self.individual_on_button.grid(row=0, column=0, padx=10, pady=10)

        self.individual_off_button = ctk.CTkButton(self.control_frame, text="Turn Selected Off", command=self.turn_selected_off)
        self.individual_off_button.grid(row=0, column=1, padx=10, pady=10)

    def toggle_all_bulbs(self):
        state = self.select_all_var.get()
        for var in self.bulb_vars:
            var.set(state)

    def turn_selected_on(self):
        selected_bulbs = [ip for i, (_, ip) in enumerate(bulb_config.BULB_DATABASE.items()) if self.bulb_vars[i].get()]
        if not selected_bulbs:
            messagebox.showerror("Error", "No bulbs selected")
            return

        asyncio.run(self.control_selected_bulbs(selected_bulbs, True))

    def turn_selected_off(self):
        selected_bulbs = [ip for i, (_, ip) in enumerate(bulb_config.BULB_DATABASE.items()) if self.bulb_vars[i].get()]
        if not selected_bulbs:
            messagebox.showerror("Error", "No bulbs selected")
            return

        asyncio.run(self.control_selected_bulbs(selected_bulbs, False))

    async def control_selected_bulbs(self, bulb_ips, on):
        successful_changes = False  # Track if any bulb's state was successfully changed
        for ip in bulb_ips:
            changed = await self.control_single_bulb(ip, on)
            if changed:
                successful_changes = True

        if successful_changes:
            action = "on" if on else "off"
            messagebox.showinfo("Success", f"Selected bulbs turned {action}")

    async def control_single_bulb(self, ip, on):
        bulb = SmartBulb(ip)
        try:
            await bulb.update()
            if on and bulb.is_on:
                messagebox.showerror("Error", f"Bulb {ip} is already on")
                return False
            elif not on and not bulb.is_on:
                messagebox.showerror("Error", f"Bulb {ip} is already off")
                return False
            else:
                if on:
                    await bulb.turn_on()
                else:
                    await bulb.turn_off()
                return True
        except Exception as e:
            print(f"Error controlling bulb {ip}: {e}")
            return False

if __name__ == "__main__":
    root = ctk.CTk()
    app = ControlLights(master=root)
    root.mainloop()
