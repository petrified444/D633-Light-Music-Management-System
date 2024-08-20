# D633-Light-Music-Management-System
Henri, Misbah and Abdullah's Project (NEF3002 - Applied Project 2)
Overview
The TP-Link LB130 Smart Bulb Control System is a Python-based application designed to manage and control TP-Link LB130 smart bulbs in a classroom setting. The system provides a user-friendly graphical interface that allows for individual and group bulb control, color changing, brightness adjustment, pattern creation, theme selection, and synchronization of lights with music. This project is ideal for enhancing learning environments or creating dynamic lighting experiences.

Features
Control Lights: Manage individual or multiple smart bulbs, including turning them on/off.
Change Color: Customize bulb colors using preset options or a custom color picker.
Change Brightness: Adjust the brightness of selected bulbs.
Change Patterns: Create and save custom light patterns with multiple colors.
Select Light Themes: Apply preset themes like Emergency Lights, Diwali Lights, and Christmas Lights.
Sync Music: Synchronize lighting effects with music playback, with mood-based color selection.
Setup Instructions
Prerequisites
Python 3.7 or later
TP-Link LB130 Smart Bulbs
Bulbs and computer must be on the same Wi-Fi network
Connecting the Bulbs to the Router
Ensure all TP-Link LB130 bulbs are properly installed in their sockets.
Connect the bulbs to the Wi-Fi network:
Download and install the Kasa app from the Google Play Store or Apple App Store on your mobile device.
Open the Kasa app and follow the on-screen instructions to connect each bulb to the router.
Ensure all bulbs are connected to the same network as your computer.
Installation
Clone or download the project repository to your local machine.
Open a terminal/command prompt and navigate to the project directory.
Install the required packages:
sh
Copy code
pip install customtkinter pillow pyaudio librosa pydub numpy python-kasa asyncio threading wave audiosegment
Configuration
Open bulb_config.py.
Update the BULB_DATABASE dictionary with the correct IP addresses of your LB130 bulbs:
python
Copy code
BULB_DATABASE = {
    "Light A1": "192.168.1.100",
    "Light A2": "192.168.1.101",
    # Add all your bulbs here
}
Running the Application
Run the main application:
sh
Copy code
python main.py
Log in using the provided credentials:
Username: user
Password: pass
Main Features
Control Lights
Turn Individual Bulbs On/Off: Toggle lights on or off by clicking on their respective buttons.
Group Control: Use 'Turn All On' or 'Turn All Off' buttons to control all connected bulbs simultaneously.
Change Color
Select bulbs to change color and apply from preset options or custom colors.
Change Brightness
Adjust the brightness level of selected bulbs using a slider.
Change Patterns
Create light patterns with up to 5 colors, set intervals, and run the pattern on selected bulbs.
Select Light Themes
Choose from preset themes such as Emergency Lights, Diwali Lights, or Christmas Lights, and apply them to selected bulbs.
Sync Music
Synchronize bulbs with music, choose a mood, and watch the lights change in sync with the beat.
Troubleshooting
Connection Issues
Ensure that all bulbs and the computer are on the same Wi-Fi network.
Verify that the IP addresses in bulb_config.py are correct.
Ensure bulbs are powered on and connected to the network via the Kasa mobile app.
Performance Issues
Close other resource-heavy applications to improve performance.
Ensure your computer meets the minimum system requirements for Python and the required libraries.
Music Sync Problems
Check your computer's audio output settings.
Ensure that the music file format is supported (.mp3 or .wav).
Try different music files to rule out specific file issues.
Maintenance and Updates
Regularly check for updates to the python-kasa library and other dependencies.
Keep your TP-Link bulbs' firmware updated.
Periodically verify and update the IP addresses in bulb_config.py if they change.
License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgements
Thanks to the developers of the python-kasa library and other open-source tools used in this project.
