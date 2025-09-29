from pathlib import Path
from PIL import Image
from typing import Iterable
import sys

# --- Volitelné: pro MP4 -> GIF ---
# pip install moviepy imageio-ffmpeg
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except Exception:
    MOVIEPY_AVAILABLE = False

# ===== Nastavení =====
INPUT_DIR  = Path("Galerie")      # můžeš přepsat na "Galerie" apod.
OUTPUT_DIR = Path("Galerie_naweb")

# Obrázky
MAX_WIDTH_IMG = 1200                  # cílová šířka pro web
JPEG_QUALITY  = 80                    # 0–100

# GIF z videa
GIF_TARGET_WIDTH = 640                # menší, ať to není obří
GIF_FPS          = 10                 # snížené FPS kvůli velikosti
GIF_MAX_DURATION = None               # např. 6 (sekund), nebo None = celé video
GIF_LOOP         = 0                  # 0 = loop forever, nebo číslo opakování
GIF_PALETTE      = 256                # max 256, méně = menší soubor

IMAGE_EXTS: Iterable[str] = (".jpg", ".jpeg", ".png", ".webp")
VIDEO_EXTS: Iterable[str] = (".mp4",)

def ensure_dirs():
    if not INPUT_DIR.exists():
        print(f"[i] Složka {INPUT_DIR} neexistuje – vytvářím ji a končím. Nahraj sem soubory a spusť znovu.")
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        sys.exit(0)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def resize_image_for_web(src: Path, dst: Path):
    with Image.open(src) as img:
        # přepočet při překročení šířky
        if img.width > MAX_WIDTH_IMG:
            ratio = MAX_WIDTH_IMG / float(img.width)
            new_h = int(img.height * ratio)
            img = img.resize((MAX_WIDTH_IMG, new_h), Image.LANCZOS)

        # konverze režimu kvůli JPEG
        save_kwargs = dict(optimize=True)
        ext = src.suffix.lower()

        if ext in (".png", ".webp"):
            # zachovej formát, jen optimalizace (PNG nebude mít quality parametr)
            if ext == ".png":
                img.save(dst.with_suffix(".png"), **save_kwargs)
                out = dst.with_suffix(".png")
            else:
                # u webp můžeme dát kvalitu (lossy)
                img.save(dst.with_suffix(".webp"), quality=JPEG_QUALITY, method=6)
                out = dst.with_suffi_
