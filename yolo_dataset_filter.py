"""
YOLO Dataset Filter

A Python script to filter and copy YOLO format datasets based on label content or specific classes.
Useful for creating subsets of your dataset for specific training purposes.

"""

import os
import shutil
import argparse
from pathlib import Path
import sys

# ===== DEFAULT CONFIGURATION PARAMETERS =====
# These can be overridden via command line arguments or by editing this section

# Default path to your YOLO dataset (can be overridden with --input argument)
DEFAULT_DATASET_PATH = r"/path/to/dataset"

# Default names of the output folders (can be overridden with --output-images and --output-labels)
DEFAULT_OUTPUT_IMAGES_FOLDER = "filtered_images"
DEFAULT_OUTPUT_LABELS_FOLDER = "filtered_labels"

# Subdirectories to process (standard YOLO structure)
DEFAULT_SUBDIRS_TO_PROCESS = ['train', 'test', 'valid']

# Supported image extensions
DEFAULT_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']

# Default filter mode: "content" or "classes"
DEFAULT_FILTER_MODE = "classes"

# Default target classes to filter (only used when filter_mode = "classes") example [0, 1, 3] classes 0, 1 and 3 filtered
DEFAULT_TARGET_CLASSES = [0]

# ===== END CONFIGURATION =====


def check_label_has_content(label_path):
    """
    Check if a label file has content (not empty or only whitespace)
    
    Args:
        label_path (Path): Path to the label file
        
    Returns:
        bool: True if file has content, False otherwise
    """
    try:
        with open(label_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            return len(content) > 0 and content != ""
    except Exception as e:
        print(f"Error reading {label_path}: {e}")
        return False


def check_label_has_target_classes(label_path, target_classes):
    """
    Check if a label file contains one of the target classes
    YOLO format: class_id center_x center_y width height
    
    Args:
        label_path (Path): Path to the label file
        target_classes (list): List of target class IDs to look for
        
    Returns:
        bool: True if file contains target classes, False otherwise
    """
    try:
        with open(label_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                parts = line.split()
                if len(parts) >= 1:  # At least class_id must be present
                    try:
                        class_id = int(parts[0])
                        if class_id in target_classes:
                            return True
                    except ValueError:
                        # If class_id is not an integer, skip this line
                        continue
        return False
        
    except Exception as e:
        print(f"Error reading {label_path}: {e}")
        return False


def should_copy_label(label_path, filter_mode, target_classes):
    """
    Determine if a label should be copied based on the filter mode
    
    Args:
        label_path (Path): Path to the label file
        filter_mode (str): Either "content" or "classes"
        target_classes (list): List of target class IDs
        
    Returns:
        bool: True if label should be copied, False otherwise
    """
    if filter_mode == "content":
        return check_label_has_content(label_path)
    elif filter_mode == "classes":
        return check_label_has_target_classes(label_path, target_classes)
    else:
        print(f"Unknown filter mode: {filter_mode}")
        return False


def get_image_extensions():
    """
    Get list of supported image extensions
    
    Returns:
        list: List of supported image file extensions
    """
    return DEFAULT_IMAGE_EXTENSIONS


def find_matching_image(label_path, images_dir):
    """
    Find the corresponding image file for a label file
    
    Args:
        label_path (Path): Path to the label file
        images_dir (Path): Directory containing images
        
    Returns:
        Path or None: Path to matching image file, or None if not found
    """
    label_name = Path(label_path).stem  # Filename without extension
    image_extensions = get_image_extensions()
    
    for ext in image_extensions:
        image_path = images_dir / f"{label_name}{ext}"
        if image_path.exists():
            return image_path
    
    return None


def process_yolo_dataset(base_path, output_images_dir, output_labels_dir, 
                        filter_mode, target_classes, subdirs_to_process):
    """
    Process the YOLO dataset and copy files based on filter criteria
    
    Args:
        base_path (Path): Base path of the YOLO dataset
        output_images_dir (Path): Output directory for filtered images
        output_labels_dir (Path): Output directory for filtered labels
        filter_mode (str): Filter mode ("content" or "classes")
        target_classes (list): List of target class IDs
        subdirs_to_process (list): List of subdirectories to process
    """
    # Create output directories
    output_images_dir.mkdir(exist_ok=True)
    output_labels_dir.mkdir(exist_ok=True)
    
    total_copied = 0
    total_processed = 0
    
    for subdir in subdirs_to_process:
        labels_dir = base_path / subdir / "labels"
        images_dir = base_path / subdir / "images"
        
        if not labels_dir.exists():
            print(f"Directory {labels_dir} does not exist, skipping...")
            continue
            
        if not images_dir.exists():
            print(f"Directory {images_dir} does not exist, skipping...")
            continue
        
        print(f"\nProcessing {subdir} directory...")
        
        # Loop through all label files
        for label_file in labels_dir.glob("*.txt"):
            total_processed += 1
            
            # Check if label meets filter criteria
            if should_copy_label(label_file, filter_mode, target_classes):
                # Find corresponding image
                image_file = find_matching_image(label_file, images_dir)
                
                if image_file:
                    try:
                        # Copy label to output labels directory
                        target_label = output_labels_dir / label_file.name
                        shutil.copy2(label_file, target_label)
                        
                        # Copy image to output images directory
                        target_image = output_images_dir / image_file.name
                        shutil.copy2(image_file, target_image)
                        
                        print(f"Copied: {label_file.name} + {image_file.name}")
                        total_copied += 1
                        
                    except Exception as e:
                        print(f"Error copying {label_file.name}: {e}")
                else:
                    print(f"No matching image found for {label_file.name}")
            else:
                if filter_mode == "content":
                    print(f"Label {label_file.name} is empty, skipping...")
                elif filter_mode == "classes":
                    print(f"Label {label_file.name} does not contain target classes {target_classes}, skipping...")
    
    print(f"\n=== CONFIGURATION ===")
    print(f"Filter mode: {filter_mode}")
    if filter_mode == "classes":
        print(f"Target classes: {target_classes}")
    print(f"=== SUMMARY ===")
    print(f"Total processed labels: {total_processed}")
    print(f"Total copied pairs: {total_copied}")
    print(f"Output images directory: {output_images_dir}")
    print(f"Output labels directory: {output_labels_dir}")


def get_user_input():
    """
    Get user input interactively
    
    Returns:
        dict: Dictionary with user choices
    """
    print("=" * 50)
    print("YOLO Dataset Filter - Interactive Mode")
    print("=" * 50)
    
    # Get dataset path
    while True:
        dataset_input = input(f"Enter dataset path (default: {DEFAULT_DATASET_PATH}): ").strip()
        if not dataset_input:
            dataset_path = Path(DEFAULT_DATASET_PATH)
        else:
            dataset_path = Path(dataset_input)
        
        if dataset_path.exists():
            break
        else:
            print(f"Error: Path '{dataset_path}' does not exist. Please try again.")
    
    # Get filter mode
    print("\nFilter modes:")
    print("1. content - Copy all non-empty label files")
    print("2. classes - Copy labels containing specific classes")
    
    while True:
        mode_choice = input(f"Choose filter mode (1/2, default: {'2' if DEFAULT_FILTER_MODE == 'classes' else '1'}): ").strip()
        if not mode_choice:
            filter_mode = DEFAULT_FILTER_MODE
            break
        elif mode_choice == "1":
            filter_mode = "content"
            break
        elif mode_choice == "2":
            filter_mode = "classes"
            break
        else:
            print("Please enter 1 or 2")
    
    # Get target classes if needed
    target_classes = DEFAULT_TARGET_CLASSES
    if filter_mode == "classes":
        while True:
            classes_input = input(f"Enter target classes (space-separated, default: {' '.join(map(str, DEFAULT_TARGET_CLASSES))}): ").strip()
            if not classes_input:
                target_classes = DEFAULT_TARGET_CLASSES
                break
            else:
                try:
                    target_classes = [int(x) for x in classes_input.split()]
                    break
                except ValueError:
                    print("Please enter valid integers separated by spaces")
    
    # Get output folder names
    output_images = input(f"Output images folder name (default: {DEFAULT_OUTPUT_IMAGES_FOLDER}): ").strip()
    if not output_images:
        output_images = DEFAULT_OUTPUT_IMAGES_FOLDER
    
    output_labels = input(f"Output labels folder name (default: {DEFAULT_OUTPUT_LABELS_FOLDER}): ").strip()
    if not output_labels:
        output_labels = DEFAULT_OUTPUT_LABELS_FOLDER
    
    # Get subdirectories to process
    subdirs_input = input(f"Subdirectories to process (space-separated, default: {' '.join(DEFAULT_SUBDIRS_TO_PROCESS)}): ").strip()
    if not subdirs_input:
        subdirs = DEFAULT_SUBDIRS_TO_PROCESS
    else:
        subdirs = subdirs_input.split()
    
    return {
        'dataset_path': dataset_path,
        'filter_mode': filter_mode,
        'target_classes': target_classes,
        'output_images': output_images,
        'output_labels': output_labels,
        'subdirs': subdirs
    }


def parse_arguments():
    """
    Parse command line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Filter and copy YOLO format datasets based on label content or specific classes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in interactive mode
  python yolo_filter.py
  
  # Filter by content (copy all non-empty labels)
  python yolo_filter.py --input /path/to/dataset --mode content
  
  # Filter by specific class (copy only labels containing class 1)
  python yolo_filter.py --input /path/to/dataset --mode classes --classes 1
  
  # Filter by multiple classes
  python yolo_filter.py --input /path/to/dataset --mode classes --classes 0 1 2
  
  # Specify custom output directories
  python yolo_filter.py --input /path/to/dataset --output-images my_images --output-labels my_labels
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Path to input YOLO dataset directory'
    )
    
    parser.add_argument(
        '--output-images',
        type=str,
        help=f'Name of output images directory (default: {DEFAULT_OUTPUT_IMAGES_FOLDER})'
    )
    
    parser.add_argument(
        '--output-labels',
        type=str,
        help=f'Name of output labels directory (default: {DEFAULT_OUTPUT_LABELS_FOLDER})'
    )
    
    parser.add_argument(
        '--mode', '-m',
        choices=['content', 'classes'],
        help=f'Filter mode: "content" (copy non-empty labels) or "classes" (copy specific classes) (default: {DEFAULT_FILTER_MODE})'
    )
    
    parser.add_argument(
        '--classes', '-c',
        type=int,
        nargs='+',
        help=f'Target class IDs to filter (only used with --mode classes) (default: {DEFAULT_TARGET_CLASSES})'
    )
    
    parser.add_argument(
        '--subdirs',
        type=str,
        nargs='+',
        help=f'Subdirectories to process (default: {DEFAULT_SUBDIRS_TO_PROCESS})'
    )
    
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Force interactive mode (ask for parameters)'
    )
    
    return parser.parse_args()


def main():
    """
    Main function
    """
    args = parse_arguments()
    
    # Check if we should run in interactive mode
    # Interactive mode is triggered if:
    # 1. --interactive flag is used, OR
    # 2. No input path is provided via command line
    run_interactive = args.interactive or args.input is None
    
    if run_interactive:
        # Interactive mode
        user_input = get_user_input()
        dataset_path = user_input['dataset_path']
        filter_mode = user_input['filter_mode']
        target_classes = user_input['target_classes']
        output_images_dir = dataset_path / user_input['output_images']
        output_labels_dir = dataset_path / user_input['output_labels']
        subdirs = user_input['subdirs']
        no_confirm = False
        
    else:
        # Command line mode
        dataset_path = Path(args.input)
        if not dataset_path.exists():
            print(f"Error: The path {dataset_path} does not exist!")
            print("Please check the path and try again.")
            return
        
        filter_mode = args.mode if args.mode else DEFAULT_FILTER_MODE
        target_classes = args.classes if args.classes else DEFAULT_TARGET_CLASSES
        output_images_name = args.output_images if args.output_images else DEFAULT_OUTPUT_IMAGES_FOLDER
        output_labels_name = args.output_labels if args.output_labels else DEFAULT_OUTPUT_LABELS_FOLDER
        output_images_dir = dataset_path / output_images_name
        output_labels_dir = dataset_path / output_labels_name
        subdirs = args.subdirs if args.subdirs else DEFAULT_SUBDIRS_TO_PROCESS
        no_confirm = args.no_confirm
    
    # Display configuration
    print(f"\nYOLO Dataset Filter")
    print(f"==================")
    print(f"Input dataset: {dataset_path}")
    print(f"Filter mode: {filter_mode}")
    if filter_mode == "classes":
        print(f"Target classes: {target_classes}")
    print(f"Output images directory: {output_images_dir.name}")
    print(f"Output labels directory: {output_labels_dir.name}")
    print(f"Subdirectories to process: {subdirs}")
    
    # Confirmation prompt (unless --no-confirm is used or we're in interactive mode that already confirmed)
    if not no_confirm:
        response = input("\nDo you want to continue? (yes/y): ").lower()
        if response not in ['yes', 'y']:
            print("Cancelled.")
            return
    
    try:
        process_yolo_dataset(
            dataset_path,
            output_images_dir,
            output_labels_dir,
            filter_mode,
            target_classes,
            subdirs
        )
        print("\nScript executed successfully!")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
