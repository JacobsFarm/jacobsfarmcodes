import cv2
import os
from datetime import datetime

# ===================== CONFIGURATION =====================
# SOURCE_DIR can now be a FOLDER or a specific FILE path
SOURCE_PATH = r'path/to/input/folder/file.mp4' 
OUTPUT_DIR = r'path/to/output/folder'

# Timing
INTERVAL_SECONDS = 5  

# File Naming
CUSTOM_PREFIX = "custom_filename"  
INCLUDE_DATE = True                   
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv', '.webm')
# ========================================================

def extract_frames(video_path, output_root, interval, prefix, include_date):
    """
    Extracts frames from a single video file.
    """
    video_filename = os.path.basename(video_path)
    video_name_no_ext = os.path.splitext(video_filename)[0]
    
    save_folder = os.path.join(output_root, video_name_no_ext)
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open {video_filename}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        print(f"Error: Invalid FPS for {video_filename}")
        return

    frame_interval = int(fps * interval)
    frame_count = 0
    saved_count = 0
    date_str = datetime.now().strftime("%Y-%m-%d")

    print(f"Processing: {video_filename}")

    while True:
        success, frame = cap.read()
        if not success:
            break

        if frame_count % frame_interval == 0:
            timestamp = int(frame_count / fps)
            
            parts = []
            if prefix: parts.append(prefix)
            if include_date: parts.append(date_str)
            parts.append(f"t{timestamp:04d}s")
            
            file_name = "_".join(parts) + f"_{saved_count}.jpg"
            cv2.imwrite(os.path.join(save_folder, file_name), frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Done: {saved_count} frames saved to {save_folder}\n")

def main():
    if not os.path.exists(SOURCE_PATH):
        print(f"Error: Path '{SOURCE_PATH}' does not exist.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # CHECK: Is it a single file or a directory?
    if os.path.isfile(SOURCE_PATH):
        # Process just this one file
        extract_frames(SOURCE_PATH, OUTPUT_DIR, INTERVAL_SECONDS, CUSTOM_PREFIX, INCLUDE_DATE)
    elif os.path.isdir(SOURCE_PATH):
        # Process all videos in the directory
        video_files = [f for f in os.listdir(SOURCE_PATH) if f.lower().endswith(VIDEO_EXTENSIONS)]
        if not video_files:
            print("No video files found in directory.")
            return
        for video_file in video_files:
            extract_frames(os.path.join(SOURCE_PATH, video_file), OUTPUT_DIR, INTERVAL_SECONDS, CUSTOM_PREFIX, INCLUDE_DATE)

if __name__ == "__main__":
    main()