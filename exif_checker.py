from PIL import Image, ExifTags
import os

def print_exif_data(directory):
    """
    Print EXIF data of all images in the specified directory.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):  # Check for JPEG images
            image_path = os.path.join(directory, filename)
            with Image.open(image_path) as img:
                exif_data = img._getexif()
                if exif_data is not None:
                    exif = {
                        ExifTags.TAGS[k]: v
                        for k, v in exif_data.items()
                        if k in ExifTags.TAGS
                    }
                    print(f"EXIF data for {filename}:")
                    for tag, value in exif.items():
                        print(f"  {tag}: {value}")
                else:
                    print(f"No EXIF data found for {filename}")
            print("\n")

# Example usage
# Example usage
directory = "C:/Saikumar/Projects/geotagger/DJI_0055_frames"  # Replace with your directory path
print_exif_data(directory)