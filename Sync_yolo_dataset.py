"""
YOLO Dataset Synchronization Tool

This script synchronizes YOLO format datasets by ensuring that every image file
has a corresponding label file and vice versa. It helps maintain dataset integrity
by identifying and optionally removing orphaned files.

Supports multiple label formats: .txt, .json, .jsonl, .xml, .yaml, .yml

Usage:
    python sync_yolo_dataset.py <images_folder> <labels_folder> [--label-formats FORMAT1 FORMAT2 ...]

Example:
    python sync_yolo_dataset.py ./dataset/images ./dataset/labels
    python sync_yolo_dataset.py ./dataset/images ./dataset/labels --label-formats .txt .json
"""

import os
import sys
import argparse
from pathlib import Path


def sync_yolo_dataset(images_folder, labels_folder, label_formats=None):
    """
    Synchronizes a YOLO dataset by ensuring that each image file
    has a corresponding label file and vice versa.
    
    Args:
        images_folder (str): Path to the folder containing images
        labels_folder (str): Path to the folder containing labels
        label_formats (set): Set of label file extensions to consider (e.g., {'.txt', '.json'})
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
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'}
    
    # Default label formats if not specified
    if label_formats is None:
        label_formats = {'.txt', '.json', '.jsonl', '.xml', '.yaml', '.yml'}
    
    # Collect all image files
    image_files = set()
    image_file_map = {}  # Maps stem to full Path object
    for file in images_path.iterdir():
        if file.suffix.lower() in image_extensions:
            image_files.add(file.stem)
            image_file_map[file.stem] = file
    
    # Collect all label files
    label_files = set()
    label_file_map = {}  # Maps stem to full Path object
    for file in labels_path.iterdir():
        if file.suffix.lower() in label_formats:
            label_files.add(file.stem)
            label_file_map[file.stem] = file
    
    # Find images without labels
    images_without_labels = image_files - label_files
    
    # Find labels without images
    labels_without_images = label_files - image_files
    
    # Display statistics
    print("=" * 50)
    print("YOLO Dataset Synchronization Report")
    print("=" * 50)
    print(f"Image formats: {', '.join(sorted(image_extensions))}")
    print(f"Label formats: {', '.join(sorted(label_formats))}")
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
                img_path = image_file_map[img]
                print(f"  - {img_path.name}")
            if len(images_without_labels) > 10:
                print(f"  ... and {len(images_without_labels) - 10} more")
        
        if labels_without_images:
            print("\nLabels without images:")
            for lbl in sorted(labels_without_images)[:10]:  # Show first 10
                lbl_path = label_file_map[lbl]
                print(f"  - {lbl_path.name}")
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
            img_path = image_file_map[img_stem]
            if img_path.exists():
                img_path.unlink()
                removed_images += 1
                print(f"Removed: {img_path}")
        
        # Remove labels without images
        removed_labels = 0
        for lbl_stem in labels_without_images:
            lbl_path = label_file_map[lbl_stem]
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
    parser = argparse.ArgumentParser(
        description='Synchronize YOLO dataset by matching images with labels',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default label formats (.txt, .json, .jsonl, .xml, .yaml, .yml)
  python sync_yolo_dataset.py ./dataset/images ./dataset/labels
  
  # Specify specific label formats
  python sync_yolo_dataset.py ./dataset/images ./dataset/labels --label-formats .txt .json
  
  # Only use .txt files as labels
  python sync_yolo_dataset.py ./dataset/images ./dataset/labels --label-formats .txt
        """
    )
    
    parser.add_argument('images_folder', help='Path to the folder containing images')
    parser.add_argument('labels_folder', help='Path to the folder containing labels')
    parser.add_argument(
        '--label-formats',
        nargs='+',
        help='Label file formats to consider (e.g., .txt .json .xml). Default: all supported formats',
        default=None
    )
    
    args = parser.parse_args()
    
    # Convert label formats to lowercase set
    label_formats = None
    if args.label_formats:
        label_formats = set()
        for fmt in args.label_formats:
            # Add dot if not present
            if not fmt.startswith('.'):
                fmt = '.' + fmt
            label_formats.add(fmt.lower())
    
    try:
        sync_yolo_dataset(args.images_folder, args.labels_folder, label_formats)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
