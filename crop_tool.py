import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path

class LivestockCameraCropTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # --- Settings ---
        self.use_fixed_res = True  # True = 1280x720, False = use original pixel distance
        self.target_w = 1280
        self.target_h = 720
        
        # Ask user for resolution preference
        choice = messagebox.askyesno("Resolution Settings", 
                                    f"Use standard resolution ({self.target_w}x{self.target_h})?\n\n"
                                    "Click 'Yes' for 1280x720\n"
                                    "Click 'No' to keep original pixel dimensions based on your selection.")
        self.use_fixed_res = choice

        # --- Folder Selection ---
        self.input_path = Path(filedialog.askdirectory(title="Select Folder with Original Images"))
        if not self.input_path or str(self.input_path) == ".": return

        self.output_path = Path(filedialog.askdirectory(title="Select Folder for Cropped Images"))
        if not self.output_path or str(self.output_path) == ".": return

        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.saved_pts = []
        self.current_pts = []
        
        extensions = ('.jpg', '.jpeg', '.png', '.JPG')
        self.files = sorted([f for f in self.input_path.iterdir() if f.suffix in extensions])
        
        if not self.files:
            messagebox.showerror("Error", "No images found.")
            return

        self.run_manual_mode()

    def get_dest_points(self, pts):
        """Calculates destination points based on fixed res or pixel distance."""
        if self.use_fixed_res:
            w, h = self.target_w, self.target_h
        else:
            # Calculate width and height based on the average distance between clicked points
            width_top = np.linalg.norm(np.array(pts[0]) - np.array(pts[1]))
            width_bottom = np.linalg.norm(np.array(pts[2]) - np.array(pts[3]))
            height_left = np.linalg.norm(np.array(pts[0]) - np.array(pts[3]))
            height_right = np.linalg.norm(np.array(pts[1]) - np.array(pts[2]))
            w = int(max(width_top, width_bottom))
            h = int(max(height_left, height_right))
        
        dst_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        return dst_pts, w, h

    def select_points(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.current_pts) < 4:
                self.current_pts.append((x, y))
                cv2.circle(self.display_img, (x, y), 6, (0, 255, 0), -1)
                cv2.imshow(self.window_name, self.display_img)

    def crop_image(self, img, pts, filename):
        dst_pts, w, h = self.get_dest_points(pts)
        src_pts = np.float32(pts)
        
        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        result = cv2.warpPerspective(img, matrix, (w, h))
        cv2.imwrite(str(self.output_path / f"crop_{filename}"), result)

    def draw_ui(self, idx):
        for p in self.current_pts:
            cv2.circle(self.display_img, (p[0], p[1]), 6, (0, 255, 0), -1)
        
        overlay = self.display_img.copy()
        cv2.rectangle(overlay, (0, 0), (750, 130), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, self.display_img, 0.4, 0, self.display_img)

        font = cv2.FONT_HERSHEY_SIMPLEX
        mode_str = f"FIXED ({self.target_w}x{self.target_h})" if self.use_fixed_res else "ORIGINAL RATIO"
        
        cv2.putText(self.display_img, f"Image: {idx+1}/{len(self.files)} | Mode: {mode_str}", (10, 25), font, 0.6, (255, 255, 255), 1)
        cv2.putText(self.display_img, "[SPACE] Save & Next", (10, 55), font, 0.6, (0, 255, 0), 1)
        cv2.putText(self.display_img, "[A] Start AUTO-mode", (10, 80), font, 0.6, (255, 200, 0), 1)
        cv2.putText(self.display_img, "[R] Reset | [Q] Quit", (10, 105), font, 0.6, (0, 0, 255), 1)

    def run_manual_mode(self):
        self.window_name = "Livestock Camera Crop Tool"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL) # Allows resizing window if image is huge
        cv2.setMouseCallback(self.window_name, self.select_points)

        idx = 0
        while idx < len(self.files):
            img = cv2.imread(str(self.files[idx]))
            if img is None:
                idx += 1
                continue

            self.display_img = img.copy()
            self.current_pts = list(self.saved_pts)
            self.draw_ui(idx)

            while True:
                cv2.imshow(self.window_name, self.display_img)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('r'):
                    self.current_pts, self.saved_pts = [], []
                    self.display_img = img.copy()
                    self.draw_ui(idx)
                elif key == ord(' '):
                    if len(self.current_pts) == 4:
                        self.saved_pts = list(self.current_pts)
                        self.crop_image(img, self.saved_pts, self.files[idx].name)
                        idx += 1
                        break
                elif key == ord('a'):
                    if len(self.current_pts) == 4:
                        self.saved_pts = list(self.current_pts)
                        self.run_auto_mode(idx)
                        return
                elif key == ord('q') or key == 27:
                    cv2.destroyAllWindows()
                    return

        cv2.destroyAllWindows()
        messagebox.showinfo("Finished", "Processing complete!")

    def run_auto_mode(self, start_idx):
        for i in range(start_idx, len(self.files)):
            img = cv2.imread(str(self.files[i]))
            if img is not None:
                self.crop_image(img, self.saved_pts, self.files[i].name)
        messagebox.showinfo("Finished", "Auto-processing complete!")

if __name__ == "__main__":
    LivestockCameraCropTool()
