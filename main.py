import cv2
import pysrt
import os
import re
import piexif
from PIL import Image
from tqdm import tqdm
from fractions import Fraction

def change_to_rational(number):
    """
    Convert a number to a rational number for EXIF data.
    """
    return int(number * 100), 100

def extract_exif_info(subtitle_text):
    """
    Extract various data from the subtitle text.
    """
    exif_data = {}

    # Regular expressions to find different data
    patterns = {
        'date': r"(\d{4}-\d{2}-\d{2})",
        'time': r"(\d{2}:\d{2}:\d{2}.\d{3})",
        'iso': r"\[iso : (\d+)\]",
        'shutter': r"\[shutter : ([\d/.]+)\]",
        'fnum': r"\[fnum : (\d+)\]",
        'ev': r"\[ev : ([\d.+-]+)\]",
        'ct': r"\[ct : (\d+)\]",
        'color_md': r"\[color_md : (\w+)\]",
        'focal_length': r"\[focal_len : (\d+)\]",
        'dzoom_ratio': r"\[dzoom_ratio: (\d+), delta:(\d+)\]",
        'latitude': r"\[latitude: ([\d.+-]+)\]",
        'longitude': r"\[longitude: ([\d.+-]+)\]",
        'rel_alt': r"\[rel_alt: ([\d.+-]+)\]",
        'abs_alt': r"\[abs_alt: ([\d.+-]+)\]"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, subtitle_text)
        if match:
            exif_data[key] = match.group(1)

    return exif_data

def add_metadata_to_image(image_path, exif_data):
    """
    Add metadata to the image at the given path.
    """
    exif_dict = piexif.load(image_path)

    # Convert GPS coordinates to the EXIF format
    gps_ifd = {}
    if 'latitude' in exif_data and 'longitude' in exif_data:
        gps_ifd.update({
            piexif.GPSIFD.GPSLatitudeRef: 'N' if float(exif_data['latitude']) >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: convert_to_dms(float(exif_data['latitude'])),
            piexif.GPSIFD.GPSLongitudeRef: 'E' if float(exif_data['longitude']) >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: convert_to_dms(float(exif_data['longitude'])),
        })
    if 'rel_alt' in exif_data:
        gps_ifd.update({
            piexif.GPSIFD.GPSAltitude: change_to_rational(float(exif_data['rel_alt'])),
            piexif.GPSIFD.GPSAltitudeRef: 0 if float(exif_data['rel_alt']) >= 0 else 1,
        })
    exif_dict['GPS'] = gps_ifd

    # Map other EXIF data
    # Replace the 'Make', 'Model', and 'Software' fields with actual data or remove if not needed
    zeroth_ifd = {
        piexif.ImageIFD.Make: 'DJI',
        piexif.ImageIFD.Model: 'Mini 3 Pro',
        piexif.ImageIFD.Software: 'Sai Kumar Rayavarapu',
    }

# Prepare Exif data dictionary
    exif_ifd = {}

# Handle the 'shutter' speed (exposure time)
    if 'shutter' in exif_data:
        shutter_speed = exif_data['shutter']
        # Check if shutter speed is in fractional form
        if '/' in shutter_speed:
            numerator, denominator = shutter_speed.split('/')
            shutter_speed = float(numerator) / float(denominator)
        else:
            shutter_speed = float(shutter_speed)

        exif_ifd[piexif.ExifIFD.ExposureTime] = change_to_rational(shutter_speed)

    # Add other Exif data
    if 'iso' in exif_data:
        exif_ifd[piexif.ExifIFD.ISOSpeedRatings] = int(exif_data['iso'])
    if 'fnum' in exif_data:
        exif_ifd[piexif.ExifIFD.FNumber] = change_to_rational(float(exif_data['fnum']))
    if 'ev' in exif_data:
        exif_ifd[piexif.ExifIFD.ExposureBiasValue] = change_to_rational(float(exif_data['ev']))
    if 'focal_length' in exif_data:
        exif_ifd[piexif.ExifIFD.FocalLength] = change_to_rational(float(exif_data['focal_length']))    # Add the zeroth and Exif fields to the EXIF dictionary
    exif_dict['0th'].update(zeroth_ifd)
    exif_dict['Exif'].update(exif_ifd)

    # Generate the bytes for the new EXIF data
    exif_bytes = piexif.dump(exif_dict)

    print(f"Attempting to write EXIF data to: {image_path}")
    exif_bytes = piexif.dump(exif_dict)
    try:
        piexif.insert(exif_bytes, image_path)
    except Exception as e:
        print(f"Error writing to {image_path}: {e}")

    # Insert the new EXIF data into the image
    piexif.insert(exif_bytes, image_path)
    
def convert_to_dms(decimal_degree):
    """
    Convert decimal degree to degrees, minutes, and seconds tuple in EXIF format.
    """
    degrees = int(decimal_degree)
    minutes = int((decimal_degree - degrees) * 60)
    seconds = int((decimal_degree - degrees - minutes/60) * 3600 * 100)

    # Represent as fractions (numerator, denominator)
    return ((degrees, 1), (minutes, 1), (seconds, 100))


def extract_frames(video_path, srt_path):
    """
    Extract frames from the video with user-defined frequency.
    """
    frame_frequency = int(input("Enter the frame extraction frequency: "))
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    directory_name = f"./{video_name}_frames"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    subs = pysrt.open(srt_path)
    frame_number = 0
    extracted_frame_count = 0
    with tqdm(total=total_frames//frame_frequency, desc="Extracting frames") as pbar:
        while True:
            ret, frame = video.read()
            if not ret:
                break
            if frame_number % frame_frequency == 0:
                for sub in subs:
                    if sub.start.ordinal <= frame_number <= sub.end.ordinal:
                        exif_data = extract_exif_info(sub.text)
                        frame_path = os.path.join(directory_name, f'frame_{extracted_frame_count}.jpg')
                        cv2.imwrite(frame_path, frame)
                        add_metadata_to_image(frame_path, exif_data)
                        extracted_frame_count += 1
                        pbar.update(1)
                        break
            frame_number += 1

# Example usage
video_path = "C:/Rosys/DJI/AU/DJI_0055.MP4"
srt_path = "C:/Rosys/DJI/AU/DJI_0055.SRT"
extract_frames(video_path, srt_path)
