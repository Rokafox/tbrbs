from PIL import Image
import numpy as np
import os
from collections import defaultdict

# Function to calculate the average RGB color of an image
def get_dominant_color(image_path):
    image = Image.open(image_path).convert("RGB")  # Open image and convert to RGB
    np_image = np.array(image)  # Convert image to NumPy array
    np_image = np_image.reshape(-1, 3)  # Flatten the image
    avg_color = np.mean(np_image, axis=0)  # Calculate average color
    return avg_color

# Function to classify color based on RGB
def classify_color(rgb):
    r, g, b = rgb
    if r > 150 and g < 100 and b < 100:  # Predominantly red
        return "Red"
    elif r > 200 and g > 200 and b < 100:  # Predominantly yellow
        return "Yellow"
    elif r > 200 and g > 200 and b > 200:  # Mostly white
        return "White"
    elif r < 50 and g < 50 and b < 50:  # Mostly black
        return "Black"
    else:
        return "Other"

# Function to sort images by color
def sort_images_by_color(image_folder):
    color_groups = defaultdict(list)
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('png', 'jpg', 'jpeg', 'bmp')):
            path = os.path.join(image_folder, filename)
            try:
                dominant_color = get_dominant_color(path)
                color_category = classify_color(dominant_color)
                color_groups[color_category].append(filename)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return color_groups

# Folder path containing images
image_folder = "./images"  # Replace with your image folder path
sorted_images = sort_images_by_color(image_folder)

# Print sorted images
for color, files in sorted_images.items():
    print(f"{color} Images: {files}")
