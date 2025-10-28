import os
import random
import shutil

# === Settings ===
NUM_IMAGES = 5  # How many images do you want to copy?
SOURCE_FOLDER = r"C:\path\to\source"
DEST_FOLDER = r"C:\path\to\destination"

# === Script ===
def copy_random_images(source, destination, num):
    # Create destination folder if it doesn't exist
    os.makedirs(destination, exist_ok=True)

    # Filter only image files
    extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    images = [f for f in os.listdir(source) if f.lower().endswith(extensions)]

    if not images:
        print("No images found in the source folder.")
        return

    # Pick a random subset
    num = min(num, len(images))
    chosen = random.sample(images, num)

    # Copy files
    for name in chosen:
        shutil.copy(os.path.join(source, name), os.path.join(destination, name))

    print(f"{num} images copied to {destination}")

if __name__ == "__main__":
    copy_random_images(SOURCE_FOLDER, DEST_FOLDER, NUM_IMAGES)
