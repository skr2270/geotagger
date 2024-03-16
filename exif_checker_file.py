import tkinter as tk
from tkinter import filedialog
from PIL import Image, ExifTags
import os  # Import the os module

def print_exif_data(image_path):
    """
    Print EXIF data of a given image.
    """
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data is not None:
                exif = {
                    ExifTags.TAGS.get(k, k): v
                    for k, v in exif_data.items()
                }
                print(f"\nEXIF data for {os.path.basename(image_path)}:")
                for tag, value in exif.items():
                    print(f"  {tag}: {value}")
            else:
                print("No EXIF data found.")
    except IOError:
        print("Error in opening or processing the image file.")

# Create a Tkinter root window and hide it
root = tk.Tk()
root.withdraw()

# Open file dialog and ask user to select an image file
image_file_path = filedialog.askopenfilename(title="Select an Image File", filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")])

# Print EXIF data if a file is selected
if image_file_path:
    print_exif_data(image_file_path)
else:
    print("No file selected.")
