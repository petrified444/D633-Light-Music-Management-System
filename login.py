import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import homepage

def login(event=None):  # Accept the event argument
    username = username_entry.get()
    password = password_entry.get()
    if (username == "user" or username == "Henri" or username == "D633") and (password == "pass" or password == "12345"):
        root.withdraw()  # Hide the login window
        homepage.show_homepage()  # Show the homepage
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def show_login():
    global root, username_entry, password_entry
    root = ctk.CTk()  # Use CTk instead of tk.Tk()
    root.title("Login")
    root.geometry("400x600")

    ctk.set_appearance_mode("system")  # Set the appearance mode
    ctk.set_default_color_theme("green")  # Set the color theme

    # Load and resize the first image (logobulb.png)
    image1 = Image.open("logobulb.png")
    image1 = image1.resize((100, 100), Image.LANCZOS)  # Resize if necessary
    logo_image1 = ImageTk.PhotoImage(image1)

    # Load and resize the second image (VU.png)
    image2 = Image.open("VU.png")
    image2 = image2.resize((100, 100), Image.LANCZOS)  # Resize if necessary
    logo_image2 = ImageTk.PhotoImage(image2)

    # Create and pack the image labels
    logo_label1 = ctk.CTkLabel(root, image=logo_image1, text="")
    logo_label1.image = logo_image1  # Keep a reference to avoid garbage collection
    logo_label1.pack(pady=10)

    logo_label2 = ctk.CTkLabel(root, image=logo_image2, text="")
    logo_label2.image = logo_image2  # Keep a reference to avoid garbage collection
    logo_label2.pack(pady=10)

    # Create and pack the rest of the login form
    ctk.CTkLabel(root, text="Login", font=("Arial", 16)).pack(pady=20)
    ctk.CTkLabel(root, text="Username:").pack(pady=5)
    username_entry = ctk.CTkEntry(root)
    username_entry.pack(pady=5)
    ctk.CTkLabel(root, text="Password:").pack(pady=5)
    password_entry = ctk.CTkEntry(root, show="*")
    password_entry.pack(pady=5)
    ctk.CTkButton(root, text="Login", command=login).pack(pady=20)

    # Bind the Enter key to the login function
    root.bind('<Return>', login)

    root.mainloop()

if __name__ == "__main__":
    show_login()
