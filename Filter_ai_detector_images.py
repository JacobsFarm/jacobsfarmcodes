import os
import shutil
from pathlib import Path
from ultralytics import YOLO

# CONFIGURATION PARAMETERS
# List all directories you want to scan for images
SOURCE_FOLDERS = [
    "path/to/source_folder_1",
    "path/to/source_folder_2",
    # Add more paths here, separated by a comma
]

# Path where the top-performing images will be moved to
TARGET_FOLDER = "path/to/destination_folder"

# Path to your custom YOLO model
MODEL_PATH = "custom_model.pt"

# Number of top images to extract per subfolder
NUM_TOP_IMAGES = 2

# Minimum confidence threshold (0.0 to 1.0)
MIN_CONFIDENCE_THRESHOLD = 0.1

# Valid image extensions
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}

# Main code
def main():
    # Ensure target directory exists
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    
    print(f"Loading model: {MODEL_PATH}...")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"ERROR: Could not load model. Check the path. ({e})")
        return

    # Iterate through all specified source root folders
    for source_root in SOURCE_FOLDERS:
        if not os.path.exists(source_root):
            print(f"\nWARNING: Path not found, skipping: {source_root}")
            continue

        print(f"\n======= Scanning Root: {source_root} =======")
        print(f"Minimum score threshold: {MIN_CONFIDENCE_THRESHOLD}")

        for item in os.listdir(source_root):
            subfolder_path = os.path.join(source_root, item)
            
            # Only process directories
            if not os.path.isdir(subfolder_path):
                continue

            print(f"\n--- Processing subfolder: {item} ---")
            
            image_scores = []
            files = [f for f in os.listdir(subfolder_path) if os.path.splitext(f)[1].lower() in VALID_EXTENSIONS]
            
            if not files:
                print("No images found in this folder.")
                continue

            # Run predictions on each image
            for filename in files:
                full_path = os.path.join(subfolder_path, filename)
                
                # Run inference
                results = model(full_path, verbose=False)
                
                max_conf = 0.0
                for result in results:
                    boxes = result.boxes
                    if boxes is not None and len(boxes) > 0:
                        confs = boxes.conf.cpu().numpy()
                        if len(confs) > 0:
                            max_conf = max(confs)
                
                # Only keep images that meet the threshold
                if max_conf >= MIN_CONFIDENCE_THRESHOLD:
                    image_scores.append((filename, max_conf))

            # Sort images by confidence score (highest first)
            image_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select the top N images
            best_selection = image_scores[:NUM_TOP_IMAGES]
            
            if not best_selection:
                print(f"No images in '{item}' met the threshold of {MIN_CONFIDENCE_THRESHOLD}.")
            else:
                print(f"Selected top {len(best_selection)} (above threshold):")

                for filename, score in best_selection:
                    source_file = os.path.join(subfolder_path, filename)
                    
                    # Create a unique filename to prevent overwriting in the target folder
                    new_name = f"{item}_{filename}"
                    target_file = os.path.join(TARGET_FOLDER, new_name)

                    # Handle duplicate filenames in the target directory
                    counter = 1
                    name_parts = os.path.splitext(new_name)
                    while os.path.exists(target_file):
                        target_file = os.path.join(TARGET_FOLDER, f"{name_parts[0]}_{counter}{name_parts[1]}")
                        counter += 1
                    
                    print(f" -> Moving: {filename} (Score: {score:.2f})")
                    try:
                        shutil.move(source_file, target_file)
                    except Exception as e:
                        print(f"    ERROR during move: {e}")

    print("\n--- Process Completed Successfully! ---")

if __name__ == "__main__":
    main()
