from pathlib import Path
from typing import Iterable
import sys

from PIL import Image, ImageOps

# --- HEIC/HEIF podpora ---
# pip install pillow-heif
HEIF_AVAILABLE = False
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_AVAILABLE = True
except Exception:
    HEIF_AVAILABLE = False  # budeme jen varovat u .heic/.heif

# --- Volitelné: pro MP4 -> GIF ---
# pip install moviepy imageio imageio-ffmpeg
MOVIEPY_AVAILABLE = False
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except Exception:
    MOVIEPY_AVAILABLE = False

# ===== Nastavení =====
INPUT_DIR  = Path("Galerie")      # přepiš dle libosti (např. "Galerie")
OUTPUT_DIR = Path("Galerie_naweb")

# Obrázky
MAX_WIDTH_IMG = 1200                  # cílová šířka pro web
JPEG_QUALITY  = 80                    # 0–100

# GIF z videa
GIF_TARGET_WIDTH = 640                # menší = menší soubor
GIF_FPS          = 10                 # snížené FPS kvůli velikosti
GIF_MAX_DURATION = None               # např. 6 (sekundy), None = celé video
GIF_LOOP         = 0                  # 0 = loop forever
GIF_COLORS       = 256                # 2–256

IMAGE_EXTS: Iterable[str] = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif")
VIDEO_EXTS: Iterable[str] = (".mp4",)

# Pillow kompat: LANCZOS alias
try:
    RESAMPLE_LANCZOS = Image.Resampling.LANCZOS  # Pillow ≥ 10
except AttributeError:
    RESAMPLE_LANCZOS = Image.LANCZOS             # Pillow < 10


def ensure_dirs():
    if not INPUT_DIR.exists():
        print(f"[i] Složka {INPUT_DIR} neexistuje – vytvářím ji a končím. Nahraj sem soubory a spusť znovu.")
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        sys.exit(0)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def resize_image_for_web(src: Path, dst: Path):
    ext = src.suffix.lower()

    # Pokud je HEIC/HEIF a chybí dekodér, dej friendly message
    if ext in (".heic", ".heif") and not HEIF_AVAILABLE:
        print(f"[!] {src.name}: HEIC/HEIF vyžaduje balíček 'pillow-heif'. Nainstaluj: pip install pillow-heif")
        return

    with Image.open(src) as im:
        # Fix EXIF rotace (hlavně z mobilu)
        im = ImageOps.exif_transpose(im)

        # Resize podle šířky
        if im.width > MAX_WIDTH_IMG:
            ratio = MAX_WIDTH_IMG / float(im.width)
            new_h = max(1, int(im.height * ratio))
            im = im.resize((MAX_WIDTH_IMG, new_h), resample=RESAMPLE_LANCZOS)

        save_kwargs = dict(optimize=True)

        # Taktika: PNG ponecháme PNG, WEBP ponecháme WEBP (lossy s kvalitou),
        # ostatní (JPG/HEIC/HEIF/…) převedeme na JPG (bez průhlednosti).
        if ext == ".png":
            out = dst.with_suffix(".png")
            im.save(out, **save_kwargs)
        elif ext == ".webp":
            out = dst.with_suffix(".webp")
            im.save(out, quality=JPEG_QUALITY, method=6)
        else:
            # default: JPEG (včetně HEIC/HEIF)
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            out = dst.with_suffix(".jpg")
            im.save(out, quality=JPEG_QUALITY, **save_kwargs)

        print(f"✓ IMG {src.name} → {out.name}")


def mp4_to_gif(src: Path, dst: Path):
    if not MOVIEPY_AVAILABLE:
        print(f"[!] Přeskakuji {src.name} – chybí moviepy/imageio-ffmpeg. Nainstaluj: pip install moviepy imageio imageio-ffmpeg")
        return

    with VideoFileClip(src.as_posix()) as clip:
        if GIF_MAX_DURATION is not None and clip.duration > GIF_MAX_DURATION:
            clip = clip.subclip(0, GIF_MAX_DURATION)

        if clip.w > GIF_TARGET_WIDTH:
            clip = clip.resize(width=GIF_TARGET_WIDTH)

        out = dst.with_suffix(".gif")
        clip.write_gif(
            out.as_posix(),
            fps=GIF_FPS,
            program="imageio",   # použije imageio-ffmpeg backend
            loop=GIF_LOOP,
            colors=GIF_COLORS,
            logger=None
        )
        print(f"✓ GIF {src.name} → {out.name}")


def main():
    ensure_dirs()

    files = list(INPUT_DIR.iterdir())
    if not files:
        print(f"[i] Ve složce {INPUT_DIR} nejsou žádné soubory.")
        return

    for file in files:
        if not file.is_file():
            continue

        ext = file.suffix.lower()
        try:
            if ext in IMAGE_EXTS:
                resize_image_for_web(file, OUTPUT_DIR / file.stem)  # NOTE: sjednotím výstupy na .stem (bez dup přípon)
            elif ext in VIDEO_EXTS:
                mp4_to_gif(file, OUTPUT_DIR / file.stem)
            else:
                print(f"… Skipping {file.name} (nepodporovaný typ)")
        except Exception as e:
            print(f"[x] Chyba při zpracování {file.name}: {e}")


if __name__ == "__main__":
    main()
