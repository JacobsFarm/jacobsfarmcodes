YOLO Dataset Synchronization Tool

This script synchronizes YOLO format datasets by ensuring that every image file
has a corresponding label file and vice versa. It helps maintain dataset integrity
by identifying and optionally removing orphaned files.

Usage:
    python sync_yolo_dataset.py <images_folder> <labels_folder>

Example:
    python sync_yolo_dataset.py ./dataset/images ./dataset/labels
"""

import os
import sys
from pathlib import Path


def sync_yolo_dataset(images_folder, labels_folder):
    """
    Synchronizes a YOLO dataset by ensuring that each image file
    has a corresponding label file and vice versa.
    
    Args:
        images_folder (str): Path to the folder containing images
        labels_folder (str): Path to the folder containing labels
    """
    # Convert to Path objects for better path handling
    images_path = Path(images_folder)
    labels_path = Path(labels_folder)
    
    # Check if directories exist
    if not images_path.exists():
        print(f"Error: Images folder does not exist: {images_folder}")
        return
    
    if not labels_path.exists():
        print(f"Error: Labels folder does not exist: {labels_folder}")
        return
    
    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # Collect all files
    image_files = set()
    for file in images_path.iterdir():
        if file.suffix.lower() in image_extensions:
            image_files.add(file.stem)  # Store filename without extension
    
    label_files = set()
    for file in labels_path.iterdir():
        if file.suffix == '.txt':
            label_files.add(file.stem)  # Store filename without extension
    
    # Find images without labels
    images_without_labels = image_files - label_files
    
    # Find labels without images
    labels_without_images = label_files - image_files
    
    # Display statistics
    print("=" * 50)
    print("YOLO Dataset Synchronization Report")
    print("=" * 50)
    print(f"Total images found: {len(image_files)}")
    print(f"Total labels found: {len(label_files)}")
    print(f"Images without labels: {len(images_without_labels)}")
    print(f"Labels without images: {len(labels_without_images)}")
    print("=" * 50)
    
    # If there are orphaned files, offer to remove them
    if images_without_labels or labels_without_images:
        # List orphaned files
        if images_without_labels:
            print("\nImages without labels:")
            for img in sorted(images_without_labels)[:10]:  # Show first 10
                print(f"  - {img}")
            if len(images_without_labels) > 10:
                print(f"  ... and {len(images_without_labels) - 10} more")
        
        if labels_without_images:
            print("\nLabels without images:")
            for lbl in sorted(labels_without_images)[:10]:  # Show first 10
                print(f"  - {lbl}.txt")
            if len(labels_without_images) > 10:
                print(f"  ... and {len(labels_without_images) - 10} more")
        
        # Ask for confirmation before deleting
        print("\n" + "=" * 50)
        confirm = input("Do you want to remove these orphaned files? (yes/no): ")
        
        if confirm.lower() not in ['yes', 'y']:
            print("Operation cancelled. No files were removed.")
            return
        
        # Remove images without labels
        removed_images = 0
        for img_stem in images_without_labels:
            for ext in image_extensions:
                img_path = images_path / f"{img_stem}{ext}"
                if img_path.exists():
                    img_path.unlink()
                    removed_images += 1
                    print(f"Removed: {img_path}")
                    break
        
        # Remove labels without images
        removed_labels = 0
        for lbl_stem in labels_without_images:
            lbl_path = labels_path / f"{lbl_stem}.txt"
            if lbl_path.exists():
                lbl_path.unlink()
                removed_labels += 1
                print(f"Removed: {lbl_path}")
        
        # Calculate remaining files
        remaining_images = len(image_files) - removed_images
        remaining_labels = len(label_files) - removed_labels
        
        print("\n" + "=" * 50)
        print("Synchronization Complete!")
        print("=" * 50)
        print(f"Removed: {removed_images} images and {removed_labels} labels")
        print(f"Dataset now contains: {remaining_images} images with {remaining_labels} labels")
    else:
        print("\n✓ Dataset is already synchronized!")
        print("All images have corresponding labels and vice versa.")


def main():
    """Main entry point of the script."""
    if len(sys.argv) != 3:
        print("Usage: python sync_yolo_dataset.py <images_folder> <labels_folder>")
        print("\nExamples:")
        print("  python sync_yolo_dataset.py ./dataset/images ./dataset/labels")
        print("  python sync_yolo_dataset.py /path/to/train/images /path/to/train/labels")
        sys.exit(1)
    
    images_folder = sys.argv[1]
    labels_folder = sys.argv[2]
    
    try:
        sync_yolo_dataset(images_folder, labels_folder)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
