import os
import sys
from PIL import Image

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the icon path
icon_path = os.path.join(current_dir, 'resources', 'icone.reservas.ico')

print(f"Checking icon at: {icon_path}")
print(f"Icon exists: {os.path.exists(icon_path)}")

if os.path.exists(icon_path):
    try:
        # Try to open the icon file with PIL
        img = Image.open(icon_path)
        print(f"Icon format: {img.format}")
        print(f"Icon size: {img.size}")
        print(f"Icon mode: {img.mode}")
        print("Icon is valid and can be opened with PIL")
    except Exception as e:
        print(f"Error opening icon: {e}")
else:
    print("Icon file not found!")

# Print the absolute path that should be used in PyInstaller
print(f"\nAbsolute path for PyInstaller: {os.path.abspath(icon_path)}")