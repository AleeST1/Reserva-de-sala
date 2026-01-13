import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    
    return os.path.join(base_path, relative_path)

# Create a simple window to test icon loading
root = tk.Tk()
root.title('Icon Test')
root.geometry('400x300')

# Try to load the primary icon
primary_icon_path = get_resource_path(os.path.join('resources', 'icone.reservas.ico'))
secondary_icon_path = get_resource_path(os.path.join('resources', 'icone.reservas96.ico'))

# Display information about the icon paths
info_text = f"Primary icon path: {primary_icon_path}\n"
info_text += f"Primary icon exists: {os.path.exists(primary_icon_path)}\n\n"
info_text += f"Secondary icon path: {secondary_icon_path}\n"
info_text += f"Secondary icon exists: {os.path.exists(secondary_icon_path)}\n"

# Try to set the window icon
try:
    if os.path.exists(primary_icon_path):
        root.iconbitmap(primary_icon_path)
        info_text += "\nPrimary icon loaded successfully!"
    elif os.path.exists(secondary_icon_path):
        root.iconbitmap(secondary_icon_path)
        info_text += "\nSecondary icon loaded successfully!"
    else:
        info_text += "\nNo icon files found!"
except Exception as e:
    info_text += f"\nError loading icon: {e}"

# Display the information
label = tk.Label(root, text=info_text, justify='left', padx=20, pady=20)
label.pack(expand=True, fill='both')

# Run the application
root.mainloop()