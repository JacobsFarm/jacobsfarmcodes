from ultralytics import YOLO
import os
from pathlib import Path
import cv2
import shutil
import glob

# Load trained model
model = YOLO("your_model.pt")  # Replace with your model file

# Set parameters
source_folder = Path(r"path/to/input/folder")  # Replace with your input folder
conf_threshold = 0.75  # Adjust confidence threshold as needed

# Define the output folder
output_folder = Path(r"path/to/output/folder")  # Replace with your output folder
output_folder.mkdir(parents=True, exist_ok=True)

# Get all image files
image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
image_files = []
for ext in image_extensions:
    image_files.extend(source_folder.glob(ext))
    image_files.extend(source_folder.glob(ext.upper()))

print(f"Found {len(image_files)} images to process\n")

# Process images one by one
saved_count = 0
skipped_count = 0

for img_path in image_files:
    # Run prediction on single image
    results = model.predict(
        source=str(img_path),
        show=False,
        save=False,
        conf=conf_threshold,
        verbose=False
    )
    
    result = results[0]
    
    # Check if there are any detections
    if len(result.boxes) > 0:
        # Copy image to output folder (change to shutil.move() to move instead)
        destination_path = output_folder / img_path.name
        
        if img_path.exists():
            shutil.copy2(str(img_path), str(destination_path))  # Use shutil.move() to move files
            saved_count += 1
            print(f"Copied: {img_path.name} - {len(result.boxes)} detections")
        else:
            print(f"Warning: {img_path.name} doesn't exist")
    else:
        skipped_count += 1
        print(f"Skipped: {img_path.name} - No detections above conf={conf_threshold}")

print(f"\n{'='*60}")
print(f"Total images copied: {saved_count}")
print(f"Images processed: {len(image_files)}")
print(f"Images skipped: {skipped_count}")
print(f"Output folder: {output_folder}")
