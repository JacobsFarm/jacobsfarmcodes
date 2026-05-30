import os
import glob
import shutil
from tqdm import tqdm  # pip install tqdm

# ==========================================
# GLOBAL SETTINGS
# ==========================================

# Set to True to also copy the matching image files to the output folder.
# Set to False to only convert the label files (faster, no image disk usage).
COPY_IMAGES = True

# Supported image extensions (checked in this order, both lower- and uppercase).
IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp']

# Minimum number of polygon points required (YOLO needs at least 3 points = 7 values).
MIN_POLYGON_POINTS = 3  # → len(parts) must be >= 1 + MIN_POLYGON_POINTS * 2

# ==========================================
# DATASETS
# ==========================================
# Each entry must have:
#   active      : True/False  — skip this set without deleting it
#   src_labels  : folder with segmentation .txt files
#   src_images  : folder with original images (only used when COPY_IMAGES=True)
#   dst_labels  : output folder for converted bbox .txt files
#   dst_images  : output folder for copied images  (only used when COPY_IMAGES=True)
#
# Copy-paste the template block at the bottom to add more datasets.
# ==========================================

DATASETS = [
    # --- SET 1 ---
    {
        "active": True,
        "src_labels": r"C:\Projects\Car_Detection\labels_seg",
        "src_images": r"C:\Projects\Car_Detection\images",
        "dst_labels": r"C:\Projects\Car_Detection\yolo_labels",
        "dst_images": r"C:\Projects\Car_Detection\yolo_images",
    },

    # --- SET 2 (disabled) ---
    {
        "active": False,
        "src_labels": r"D:\Datasets\Old_Data\segmentation",
        "src_images": r"D:\Datasets\Old_Data\imgs",
        "dst_labels": r"D:\Datasets\Old_Data\bbox_out",
        "dst_images": r"D:\Datasets\Old_Data\imgs_out",
    },

    # --- TEMPLATE (copy this block to add a new dataset) ---
    {
        "active": False,
        "src_labels": r"C:\PATH\TO\INPUT\LABELS",
        "src_images": r"C:\PATH\TO\INPUT\IMAGES",
        "dst_labels": r"C:\PATH\TO\OUTPUT\LABELS",
        "dst_images": r"C:\PATH\TO\OUTPUT\IMAGES",
    },
]

# ==========================================
# FUNCTIONS
# ==========================================

def convert_segmentation_to_bbox(line: str) -> str | None:
    """
    Convert a YOLO segmentation line to a YOLO bounding-box line.

    Input  : <class_id> x1 y1 x2 y2 x3 y3 ...   (normalised 0-1)
    Output : <class_id> x_center y_center width height  (normalised, clamped 0-1)

    Returns None for empty/comment lines or lines with too few points.
    """
    line = line.strip()
    if not line or line.startswith('#'):
        return None

    parts = line.split()
    min_values = 1 + MIN_POLYGON_POINTS * 2  # class_id + at least N (x,y) pairs

    if len(parts) < min_values:
        return None

    class_id = parts[0]

    try:
        coords = [float(v) for v in parts[1:]]
    except ValueError:
        return None  # non-numeric value in the line

    # Split into x and y lists
    x_coords = coords[0::2]
    y_coords = coords[1::2]

    # Bounding box from extremes
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)

    x_center = (x_min + x_max) / 2.0
    y_center = (y_min + y_max) / 2.0
    width    = x_max - x_min
    height   = y_max - y_min

    # Clamp to [0, 1] to guard against tiny floating-point overshoots
    x_center = max(0.0, min(1.0, x_center))
    y_center = max(0.0, min(1.0, y_center))
    width    = max(0.0, min(1.0, width))
    height   = max(0.0, min(1.0, height))

    return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"


def find_image_file(base_name: str, search_folder: str) -> str | None:
    """Return the full path of the image matching base_name, or None if not found."""
    for ext in IMG_EXTENSIONS:
        for variant in [ext, ext.upper()]:
            path = os.path.join(search_folder, base_name + variant)
            if os.path.exists(path):
                return path
    return None


def process_dataset(config: dict, set_index: int, copy_images: bool) -> None:
    src_labels_dir = config["src_labels"]
    src_images_dir = config["src_images"]
    dst_labels_dir = config["dst_labels"]
    dst_images_dir = config["dst_images"]

    print(f"\n{'='*50}")
    print(f"  SET {set_index + 1}")
    print(f"  Labels in  : {src_labels_dir}")
    print(f"  Labels out : {dst_labels_dir}")
    if copy_images:
        print(f"  Images in  : {src_images_dir}")
        print(f"  Images out : {dst_images_dir}")
    else:
        print(f"  Images     : not copied  (COPY_IMAGES=False)")
    print(f"{'='*50}")

    # Validate input
    if not os.path.exists(src_labels_dir):
        print(f"  ERROR: Input label directory not found: {src_labels_dir}")
        print("  Tip: Check the path, or set 'active': False to skip this set.")
        return

    if copy_images and not os.path.exists(src_images_dir):
        print(f"  WARNING: Image source directory not found: {src_images_dir}")
        print("  Images will be skipped for this set.")
        copy_images = False  # degrade gracefully

    # Create output directories
    os.makedirs(dst_labels_dir, exist_ok=True)
    if copy_images:
        os.makedirs(dst_images_dir, exist_ok=True)

    txt_files = glob.glob(os.path.join(src_labels_dir, "*.txt"))
    if not txt_files:
        print(f"  WARNING: No .txt files found in {src_labels_dir}")
        return

    count_labels_ok    = 0
    count_labels_empty = 0  # files that had no valid lines after conversion
    count_img_copied   = 0
    count_img_missing  = 0
    count_lines_bad    = 0

    for txt_file in tqdm(txt_files, desc=f"  Set {set_index + 1}", unit="file"):
        filename      = os.path.basename(txt_file)
        file_basename = os.path.splitext(filename)[0]

        # --- Convert labels ---
        new_lines = []
        with open(txt_file, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                bbox_line = convert_segmentation_to_bbox(line)
                if bbox_line:
                    new_lines.append(bbox_line)
                elif line.strip() and not line.strip().startswith('#'):
                    count_lines_bad += 1

        dst_label_path = os.path.join(dst_labels_dir, filename)
        with open(dst_label_path, 'w', encoding='utf-8') as f_out:
            f_out.write("\n".join(new_lines))
            if new_lines:
                f_out.write("\n")  # trailing newline

        if new_lines:
            count_labels_ok += 1
        else:
            count_labels_empty += 1

        # --- Copy image (optional) ---
        if copy_images:
            src_img = find_image_file(file_basename, src_images_dir)
            if src_img:
                dst_img = os.path.join(dst_images_dir, os.path.basename(src_img))
                shutil.copy2(src_img, dst_img)
                count_img_copied += 1
            else:
                count_img_missing += 1

    # Summary
    print(f"\n  Results for Set {set_index + 1}:")
    print(f"    Labels converted  : {count_labels_ok}")
    print(f"    Labels empty/bad  : {count_labels_empty}  (written as empty file)")
    if count_lines_bad:
        print(f"    Lines skipped     : {count_lines_bad}  (too few polygon points)")
    if copy_images:
        print(f"    Images copied     : {count_img_copied}")
        if count_img_missing:
            print(f"    Images not found  : {count_img_missing}")


# ==========================================
# MAIN
# ==========================================

def main() -> None:
    active_sets = [cfg for cfg in DATASETS if cfg.get("active", True)]
    total_sets  = len(DATASETS)

    print(f"\nSeg → BBox converter")
    print(f"Datasets configured : {total_sets}  |  Active : {len(active_sets)}")
    print(f"Copy images         : {COPY_IMAGES}")

    for i, config in enumerate(DATASETS):
        if config.get("active", True):
            process_dataset(config, i, copy_images=COPY_IMAGES)
        else:
            print(f"\n>>> SET {i + 1} skipped (active=False).")

    print(f"\n{'='*50}")
    print("  All done.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
