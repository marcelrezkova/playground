from PIL import Image
from pathlib import Path

# Nastav cesty
INPUT_DIR = Path("Galerie")   # složka s původními fotkami
OUTPUT_DIR = Path("Galerie_naweb")    # složka s upravenými
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Parametry pro web
MAX_WIDTH = 1200
QUALITY = 90  # JPEG kvalita (0–100)

def resize_for_web(img_path: Path):
    with Image.open(img_path) as img:
        # Přepočítat výšku podle poměru stran
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / float(img.width)
            new_height = int(img.height * ratio)
            img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

        # Nastavit cílovou cestu
        out_path = OUTPUT_DIR / img_path.name
        # Uložit jako optimalizovaný JPEG/PNG
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")  # pro JPEG
        img.save(out_path, optimize=True, quality=QUALITY)
        print(f"✓ {img_path.name} → {out_path}")

def main():
    for file in INPUT_DIR.iterdir():
        if file.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
            resize_for_web(file)

if __name__ == "__main__":
    main()