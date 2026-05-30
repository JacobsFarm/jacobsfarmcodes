"""
YOLO Label Viewer – CustomTkinter
==================================
Start met een setup-popup voor het selecteren van de images-map,
labels-map en dataset.yaml. Daarna wordt de viewer geopend.
"""

import os
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import customtkinter as ctk
import yaml
from PIL import Image, ImageTk, ImageDraw, ImageFont

# ── Vaste weergave-instellingen ───────────────────────────────────────────────
MASK_ALPHA      = 0.35
BBOX_THICKNESS  = 2
SHOW_LABEL_TEXT = True

# Kleuren per klasse (RGB). Worden cyclisch hergebruikt als er meer klassen zijn.
CLASS_COLORS = [
    (255,  80,  80),
    ( 80, 200,  80),
    ( 80, 130, 255),
    (255, 200,   0),
    (200,   0, 255),
    (  0, 210, 200),
    (255, 140,   0),
    (160, 255,  80),
]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def load_classes_from_yaml(yaml_path: str) -> list[str]:
    """Leest klasse-namen uit een dataset.yaml (YOLO-formaat)."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # Ondersteunt zowel 'names: [...]' als 'names: {0: ..., 1: ...}'
    names = data.get("names", [])
    if isinstance(names, dict):
        names = [names[k] for k in sorted(names.keys())]
    return list(names)


def color_for_class(cls: int) -> tuple[int, int, int]:
    return CLASS_COLORS[cls % len(CLASS_COLORS)]


def find_image_label_pairs(images_dir: str, labels_dir: str) -> list[tuple[Path, Path]]:
    pairs, no_label = [], []
    img_dir, lbl_dir = Path(images_dir), Path(labels_dir)

    all_images = sorted(p for p in img_dir.iterdir()
                        if p.suffix.lower() in IMAGE_EXTS)

    print(f"\n{'─'*55}")
    print(f"  Afbeeldingenmap : {img_dir.resolve()}")
    print(f"  Labelmap        : {lbl_dir.resolve()}")
    print(f"{'─'*55}")

    for img_path in all_images:
        lbl_path = lbl_dir / (img_path.stem + ".txt")
        if lbl_path.exists():
            pairs.append((img_path, lbl_path))
            print(f"  ✓  {img_path.name:40s} → {lbl_path.name}")
        else:
            no_label.append(img_path)
            print(f"  ✗  {img_path.name:40s} → GEEN LABEL GEVONDEN")

    print(f"{'─'*55}")
    print(f"  Gematcht : {len(pairs)}   Zonder label : {len(no_label)}")
    print(f"{'─'*55}\n")
    return pairs


def parse_label(lbl_path: Path) -> list[dict]:
    annotations = []
    with open(lbl_path) as f:
        for line in f:
            vals = line.strip().split()
            if not vals:
                continue
            cls  = int(vals[0])
            nums = list(map(float, vals[1:]))
            if len(nums) >= 8:
                polygon = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
                xs = [p[0] for p in polygon]
                ys = [p[1] for p in polygon]
                cx = (min(xs) + max(xs)) / 2
                cy = (min(ys) + max(ys)) / 2
                w  = max(xs) - min(xs)
                h  = max(ys) - min(ys)
                annotations.append({"cls": cls, "bbox": (cx, cy, w, h), "polygon": polygon})
            elif len(nums) == 4:
                annotations.append({"cls": cls, "bbox": tuple(nums), "polygon": None})
    return annotations


def draw_annotations(img: Image.Image, annotations: list[dict],
                     class_names: list[str]) -> Image.Image:
    img_rgb = img.convert("RGB")
    W, H    = img_rgb.size
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    for ann in annotations:
        cls   = ann["cls"]
        color = color_for_class(cls)
        label = class_names[cls] if cls < len(class_names) else str(cls)

        if ann["polygon"]:
            poly_px = [(x * W, y * H) for x, y in ann["polygon"]]
            alpha   = int(MASK_ALPHA * 255)
            draw_ov.polygon(poly_px, fill=(*color, alpha))
            draw_ov.line(poly_px + [poly_px[0]], fill=(*color, 220),
                         width=BBOX_THICKNESS)

        if ann["bbox"]:
            cx, cy, bw, bh = ann["bbox"]
            x1 = int((cx - bw / 2) * W)
            y1 = int((cy - bh / 2) * H)
            x2 = int((cx + bw / 2) * W)
            y2 = int((cy + bh / 2) * H)
            draw_ov.rectangle([x1, y1, x2, y2],
                              outline=(*color, 230), width=BBOX_THICKNESS)

            if SHOW_LABEL_TEXT:
                bbox_text = font.getbbox(label)
                tw = bbox_text[2] - bbox_text[0]
                th = bbox_text[3] - bbox_text[1]
                tx1, ty1 = x1, max(0, y1 - th - 4)
                draw_ov.rectangle([tx1, ty1, tx1 + tw + 6, ty1 + th + 4],
                                  fill=(*color, 200))
                draw_ov.text((tx1 + 3, ty1 + 2), label,
                             fill=(255, 255, 255, 255), font=font)

    base = img_rgb.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


# ─────────────────────────────────────────────────────────────────────────────
# Setup-popup
# ─────────────────────────────────────────────────────────────────────────────

class SetupDialog(ctk.CTkToplevel):
    """
    Popup die vraagt om:
      - Images-map
      - Labels-map
      - dataset.yaml (optioneel; anders worden klasse-id's als naam gebruikt)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("YOLO Label Viewer – Setup")
        self.geometry("580x310")
        self.resizable(False, False)
        self.grab_set()          # modaal
        self.lift()
        self.focus_force()

        self.result = None       # wordt gevuld bij OK

        self._images_var = tk.StringVar()
        self._labels_var = tk.StringVar()
        self._yaml_var   = tk.StringVar()

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    # ── layout ────────────────────────────────────────────────────────────────

    def _build(self):
        pad = {"padx": 16, "pady": 6}

        ctk.CTkLabel(self, text="YOLO Label Viewer",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(18, 2))
        ctk.CTkLabel(self, text="Selecteer de mappen en (optioneel) de dataset.yaml",
                     font=ctk.CTkFont(size=12), text_color="gray60").pack(pady=(0, 14))

        # Drie rijen: label | invoerveld | 📁-knop
        rows_frame = ctk.CTkFrame(self, fg_color="transparent")
        rows_frame.pack(fill="x", **pad)
        rows_frame.columnconfigure(1, weight=1)

        self._make_row(rows_frame, 0, "Afbeeldingen-map",
                       self._images_var, self._browse_images)
        self._make_row(rows_frame, 1, "Labels-map",
                       self._labels_var, self._browse_labels)
        self._make_row(rows_frame, 2, "dataset.yaml  (optioneel)",
                       self._yaml_var,   self._browse_yaml, is_file=True)

        # Knoppen
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(18, 12))

        ctk.CTkButton(btn_frame, text="Annuleren", width=110,
                      fg_color="gray30", hover_color="gray40",
                      command=self._on_cancel).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_frame, text="Start viewer  ▶", width=140,
                      command=self._on_ok).pack(side="right")

        self._err_label = ctk.CTkLabel(btn_frame, text="",
                                       text_color="#ff6060",
                                       font=ctk.CTkFont(size=12))
        self._err_label.pack(side="left")

    def _make_row(self, parent, row: int, label_text: str,
                  var: tk.StringVar, browse_cmd, is_file=False):
        ctk.CTkLabel(parent, text=label_text,
                     font=ctk.CTkFont(size=13),
                     anchor="w").grid(row=row, column=0,
                                      sticky="w", padx=(0, 10), pady=7)

        entry = ctk.CTkEntry(parent, textvariable=var, width=320,
                             placeholder_text="Klik op 📁 of typ een pad…")
        entry.grid(row=row, column=1, sticky="ew", pady=7)

        btn = ctk.CTkButton(parent, text="📁", width=38, height=30,
                            font=ctk.CTkFont(size=16),
                            fg_color="#2b5278", hover_color="#3a6fa0",
                            command=browse_cmd)
        btn.grid(row=row, column=2, padx=(8, 0), pady=7)

    # ── browse callbacks ───────────────────────────────────────────────────────

    def _browse_images(self):
        path = filedialog.askdirectory(title="Selecteer de afbeeldingen-map",
                                       parent=self)
        if path:
            self._images_var.set(path)

    def _browse_labels(self):
        path = filedialog.askdirectory(title="Selecteer de labels-map",
                                       parent=self)
        if path:
            self._labels_var.set(path)

    def _browse_yaml(self):
        path = filedialog.askopenfilename(
            title="Selecteer dataset.yaml",
            filetypes=[("YAML bestanden", "*.yaml *.yml"), ("Alle bestanden", "*.*")],
            parent=self)
        if path:
            self._yaml_var.set(path)

    # ── validatie & afsluiten ──────────────────────────────────────────────────

    def _on_ok(self):
        images = self._images_var.get().strip()
        labels = self._labels_var.get().strip()
        yaml_p = self._yaml_var.get().strip()

        if not images:
            self._err_label.configure(text="⚠  Kies een afbeeldingen-map.")
            return
        if not Path(images).is_dir():
            self._err_label.configure(text="⚠  Afbeeldingen-map bestaat niet.")
            return
        if not labels:
            self._err_label.configure(text="⚠  Kies een labels-map.")
            return
        if not Path(labels).is_dir():
            self._err_label.configure(text="⚠  Labels-map bestaat niet.")
            return
        if yaml_p and not Path(yaml_p).is_file():
            self._err_label.configure(text="⚠  dataset.yaml niet gevonden.")
            return

        self.result = {
            "images": images,
            "labels": labels,
            "yaml":   yaml_p or None,
        }
        self.grab_release()
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.grab_release()
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# Hoofdviewer
# ─────────────────────────────────────────────────────────────────────────────

class LabelViewer(ctk.CTk):
    def __init__(self, pairs: list[tuple[Path, Path]], class_names: list[str]):
        super().__init__()
        self.pairs        = pairs
        self.class_names  = class_names
        self.index        = 0
        self.show_overlay = True

        self.title("YOLO Label Viewer")
        self.geometry("1100x750")

        self._build_ui()
        self._load_current()

    # ── UI constructie ─────────────────────────────────────────────────────────

    def _build_ui(self):
        top = ctk.CTkFrame(self, height=50)
        top.pack(fill="x", padx=10, pady=(10, 0))

        self.btn_prev = ctk.CTkButton(top, text="◀  Vorige", width=110,
                                      command=self.prev_image)
        self.btn_prev.pack(side="left", padx=8, pady=8)

        self.lbl_counter = ctk.CTkLabel(top, text="",
                                        font=ctk.CTkFont(size=14))
        self.lbl_counter.pack(side="left", padx=10)

        self.btn_next = ctk.CTkButton(top, text="Volgende  ▶", width=110,
                                      command=self.next_image)
        self.btn_next.pack(side="left", padx=8, pady=8)

        self.toggle_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(top, text="Overlay tonen",
                        variable=self.toggle_var,
                        command=self._on_toggle).pack(side="left", padx=20)

        self.lbl_info = ctk.CTkLabel(top, text="",
                                     font=ctk.CTkFont(size=12),
                                     text_color="gray70")
        self.lbl_info.pack(side="right", padx=12)

        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind("<Configure>", lambda e: self._redraw())

        self.legend_frame = ctk.CTkFrame(self)
        self.legend_frame.pack(fill="x", padx=10, pady=(0, 10))
        self._build_legend()

        self.bind("<Left>",  lambda e: self.prev_image())
        self.bind("<Right>", lambda e: self.next_image())
        self.bind("<space>", lambda e: self._toggle_overlay())

    def _build_legend(self):
        ctk.CTkLabel(self.legend_frame, text="Klassen:",
                     font=ctk.CTkFont(weight="bold")).pack(
                         side="left", padx=10, pady=6)
        for i, name in enumerate(self.class_names):
            r, g, b  = color_for_class(i)
            hex_col  = f"#{r:02x}{g:02x}{b:02x}"
            tk.Label(self.legend_frame, text="■", fg=hex_col,
                     bg="#2b2b2b", font=("Helvetica", 16)).pack(
                         side="left", padx=(8, 2))
            ctk.CTkLabel(self.legend_frame, text=name,
                         font=ctk.CTkFont(size=13)).pack(
                             side="left", padx=(0, 10))

    # ── navigatie ──────────────────────────────────────────────────────────────

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self._load_current()

    def next_image(self):
        if self.index < len(self.pairs) - 1:
            self.index += 1
            self._load_current()

    def _on_toggle(self):
        self.show_overlay = self.toggle_var.get()
        self._redraw()

    def _toggle_overlay(self):
        self.toggle_var.set(not self.toggle_var.get())
        self._on_toggle()

    # ── laden & tekenen ────────────────────────────────────────────────────────

    def _load_current(self):
        img_path, lbl_path = self.pairs[self.index]
        self.orig_img         = Image.open(img_path).convert("RGB")
        self.annotations      = parse_label(lbl_path)
        self.rendered_overlay = draw_annotations(
            self.orig_img, self.annotations, self.class_names)

        total = len(self.pairs)
        self.lbl_counter.configure(text=f"{self.index + 1} / {total}")
        n_seg  = sum(1 for a in self.annotations if a["polygon"])
        n_bbox = sum(1 for a in self.annotations if not a["polygon"])
        self.lbl_info.configure(
            text=f"{img_path.name}   │   {len(self.annotations)} objecten  "
                 f"({n_seg} seg, {n_bbox} bbox)   │   "
                 f"{self.orig_img.width}×{self.orig_img.height}")
        self.btn_prev.configure(
            state="normal" if self.index > 0 else "disabled")
        self.btn_next.configure(
            state="normal" if self.index < total - 1 else "disabled")
        self._redraw()

    def _redraw(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 2 or ch < 2:
            return

        src = self.rendered_overlay if self.show_overlay else self.orig_img
        iw, ih = src.size
        scale  = min(cw / iw, ch / ih)
        nw, nh = int(iw * scale), int(ih * scale)

        resized      = src.resize((nw, nh), Image.LANCZOS)
        self._tk_img = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2,
                                 anchor="center", image=self._tk_img)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Verborgen root-venster zodat de popup iets heeft om op te hangen
    root = ctk.CTk()
    root.withdraw()

    dialog = SetupDialog(root)
    root.wait_window(dialog)

    if dialog.result is None:
        # Gebruiker heeft geannuleerd
        root.destroy()
        return

    cfg = dialog.result

    # Klassen laden
    if cfg["yaml"]:
        try:
            class_names = load_classes_from_yaml(cfg["yaml"])
            print(f"Klassen uit yaml: {class_names}")
        except Exception as e:
            print(f"[WAARSCHUWING] Kon yaml niet lezen: {e}")
            class_names = []
    else:
        class_names = []

    # Paren zoeken
    pairs = find_image_label_pairs(cfg["images"], cfg["labels"])
    if not pairs:
        from tkinter import messagebox
        messagebox.showerror(
            "Geen paren gevonden",
            "Er zijn geen afbeeldingen met bijbehorend label-bestand gevonden.\n"
            "Controleer de gekozen mappen.",
            parent=root)
        root.destroy()
        return

    # Als er geen yaml was: genereer nummers als klasse-namen
    if not class_names:
        max_cls = max(
            ann["cls"]
            for _, lp in pairs
            for ann in parse_label(lp)
        )
        class_names = [str(i) for i in range(max_cls + 1)]
        print(f"Geen yaml opgegeven – klasse-id's als naam: {class_names}")

    root.destroy()

    viewer = LabelViewer(pairs, class_names)
    viewer.mainloop()


if __name__ == "__main__":
    main()
