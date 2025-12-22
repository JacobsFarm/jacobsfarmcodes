import os
import glob
import shutil
from tqdm import tqdm  # pip install tqdm

# ==========================================
# CONFIGURATION
# ==========================================

DATASETS = [
    # --- SET 1 (Example Project A) ---
    {
        "active": True,
        "src_labels": r"C:\Projects\Car_Detection\labels_seg",
        "src_images": r"C:\Projects\Car_Detection\images",
        "dst_labels": r"C:\Projects\Car_Detection\yolo_labels",
        "dst_images": r"C:\Projects\Car_Detection\yolo_images"
    },

    # --- SET 2 (Example Project B - Skipped) ---
    {
        "active": False,
        "src_labels": r"D:\Datasets\Old_Data\segmentation",
        "src_images": r"D:\Datasets\Old_Data\imgs",
        "dst_labels": r"D:\Datasets\Old_Data\bbox_out",
        "dst_images": r"D:\Datasets\Old_Data\imgs_out"
    },

    # --- SET 3 (GHOST / TEMPLATE) ---
    # Fill in the paths below and set "active" to True to run this set.
    # You can copy-paste this block to add as many datasets as needed.
    {
        "active": False, 
        "src_labels": r"C:\PATH\TO\INPUT\LABELS",
        "src_images": r"C:\PATH\TO\INPUT\IMAGES",
        "dst_labels": r"C:\PATH\TO\OUTPUT\LABELS",
        "dst_images": r"C:\PATH\TO\OUTPUT\IMAGES"
    },
]

IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tif']

# ==========================================
# FUNCTIONS
# ==========================================

def convert_segmentation_to_bbox(line):
    """
    Converts a segmentation line (class x1 y1 x2 y2 ...) 
    to a bounding-box line (class x_center y_center width height).
    """
    parts = line.strip().split()
    if len(parts) < 5: 
        return None

    class_id = parts[0]
    coords = [float(x) for x in parts[1:]]

    x_coords = coords[0::2]
    y_coords = coords[1::2]

    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)

    width = max_x - min_x
    height = max_y - min_y
    x_center = min_x + (width / 2)
    y_center = min_y + (height / 2)

    return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"

def find_image_file(base_name, search_folder):
    """
    Finds the image corresponding to a label name (checks multiple extensions).
    """
    for ext in IMG_EXTENSIONS:
        for extension in [ext, ext.upper()]:
            potential_path = os.path.join(search_folder, base_name + extension)
            if os.path.exists(potential_path):
                return potential_path
    return None

def process_dataset(config, set_index):
    src_labels_dir = config["src_labels"]
    src_images_dir = config["src_images"]
    dst_labels_dir = config["dst_labels"]
    dst_images_dir = config["dst_images"]

    print(f"\n=== Processing SET {set_index + 1} ===")
    print(f"Input: {src_labels_dir}")

    # Check if input exists (prevents crashing on empty ghost paths)
    if not os.path.exists(src_labels_dir):
        print(f"ERROR: Input directory not found: {src_labels_dir}")
        print("Tip: Did you forget to update the path in the Ghost Set?")
        return

    # Create output directories
    os.makedirs(dst_labels_dir, exist_ok=True)
    os.makedirs(dst_images_dir, exist_ok=True)

    txt_files = glob.glob(os.path.join(src_labels_dir, "*.txt"))
    
    if len(txt_files) == 0:
        print(f"WARNING: No .txt files found in {src_labels_dir}")
        return

    count_processed = 0
    count_skipped = 0

    for txt_file in tqdm(txt_files, desc=f"Set {set_index+1}"):
        filename = os.path.basename(txt_file)
        file_basename = os.path.splitext(filename)[0]
        
        # --- Conversion ---
        new_lines = []
        with open(txt_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                bbox_line = convert_segmentation_to_bbox(line)
                if bbox_line:
                    new_lines.append(bbox_line)

        dst_label_path = os.path.join(dst_labels_dir, filename)
        with open(dst_label_path, 'w') as f_out:
            f_out.write("\n".join(new_lines))

        # --- Copy Image ---
        src_img_path = find_image_file(file_basename, src_images_dir)
        
        if src_img_path:
            img_filename = os.path.basename(src_img_path)
            dst_img_path = os.path.join(dst_images_dir, img_filename)
            shutil.copy2(src_img_path, dst_img_path)
            count_processed += 1
        else:
            count_skipped += 1

    print(f"--- Finished Set {set_index + 1}: Processed {count_processed} / Skipped {count_skipped} ---")

def main():
    print(f"Datasets configured: {len(DATASETS)}")
    
    for i, config in enumerate(DATASETS):
        is_active = config.get("active", True)
        if is_active:
            process_dataset(config, i)
        else:
            print(f"\n>>> SET {i + 1} skipped (active=False).")

    print("\n" + "=" * 30)
    print("Done.")
    print("=" * 30)

if __name__ == "__main__":
    main()
