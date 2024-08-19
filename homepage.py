import customtkinter as ctk
from PIL import Image, ImageTk
import changecolor
import changepatterns
import login
import controllights
import changebrightness
import selectlightthemes
import syncmusic

class Homepage(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Homepage")
        self.geometry("400x800")

        ctk.CTkLabel(self, text="D633-Lights Management System", font=("Arial", 16)).pack(pady=10)
        ctk.CTkLabel(self, text="Glow and groove: where light meets the beats.", font=("Arial", 14)).pack(pady=10)

        self.create_button("Control Lights", self.open_control_lights).pack(pady=5)
        self.create_button("Change Color", self.open_change_color).pack(pady=5)
        self.create_button("Change Brightness", self.open_change_brightness).pack(pady=5)
        self.create_button("Change Patterns", self.open_change_patterns).pack(pady=5)
        self.create_button("Select Light Themes", self.open_select_light_themes).pack(pady=5)
        self.create_button("Sync Music", self.open_sync_music).pack(pady=5)

        logout_button = ctk.CTkButton(self, text="Logout", command=self.logout, fg_color="#ff3333", hover_color="#ff5555")
        logout_button.pack(pady=20, padx=20, anchor="s")

        self.windows = {}  # Store references to opened windows

    def create_button(self, text, command):
        return ctk.CTkButton(self, text=text, command=command, fg_color="#964B00", hover_color="#D3D3D3")

    def open_window(self, window_class, window_name):
        if window_name not in self.windows or not self.windows[window_name].winfo_exists():
            # Create a new Toplevel window
            new_window = window_class(self)
            new_window.transient(self)  # Set to be transient to the main window
            new_window.focus()  # Focus on the new window
            new_window.lift()  # Lift above all windows
            new_window.after(100, lambda: new_window.attributes('-topmost', False))  # Allow normal behavior after lifting
            self.windows[window_name] = new_window
        else:
            existing_window = self.windows[window_name]
            existing_window.deiconify()  # Restore the window if it was minimized
            existing_window.lift()
            existing_window.focus()

    def open_control_lights(self):
        self.open_window(controllights.ControlLights, "control_lights")

    def open_change_color(self):
        self.open_window(changecolor.ChangeColor, "change_color")

    def open_change_brightness(self):
        self.open_window(changebrightness.ChangeBrightness, "change_brightness")

    def open_change_patterns(self):
        self.open_window(changepatterns.ChangePatterns, "change_patterns")

    def open_select_light_themes(self):
        self.open_window(selectlightthemes.SelectLightThemes, "select_light_themes")

    def open_sync_music(self):
        self.open_window(syncmusic.SyncLightsWithMusic, "sync_music")

    def logout(self):
        self.destroy()
        login.show_login()

def show_homepage():
    app = Homepage()
    app.mainloop()
