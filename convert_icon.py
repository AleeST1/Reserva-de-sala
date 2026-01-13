from PIL import Image
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths
icon_path = os.path.join(current_dir, 'resources', 'icone.reservas.ico')
output_path = os.path.join(current_dir, 'resources', 'icone.reservas.png')

print(f"Converting icon from {icon_path} to {output_path}")

if os.path.exists(icon_path):
    try:
        # Open the ICO file and convert to PNG
        img = Image.open(icon_path)
        img.save(output_path)
        print(f"Successfully converted icon to PNG format")
    except Exception as e:
        print(f"Error converting icon: {e}")
else:
    print(f"Icon file not found: {icon_path}")

# Also create a PNG version of the secondary icon if it exists
secondary_icon_path = os.path.join(current_dir, 'resources', 'icone.reservas96.ico')
secondary_output_path = os.path.join(current_dir, 'resources', 'icone.reservas96.png')

if os.path.exists(secondary_icon_path):
    try:
        # Open the secondary ICO file and convert to PNG
        img = Image.open(secondary_icon_path)
        img.save(secondary_output_path)
        print(f"Successfully converted secondary icon to PNG format")
    except Exception as e:
        print(f"Error converting secondary icon: {e}")
else:
    print(f"Secondary icon file not found: {secondary_icon_path}")