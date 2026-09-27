#!/usr/bin/env python3
"""
generate_og_image.py — рисует static/assets/og-image.png (1200x630) из resume.yaml,
теми же цветами/шрифтами, что и сайт. Запускать вручную при смене имени/роли,
в CI не нужен — картинка коммитится в репозиторий как обычный статический файл.

Установка:
    pip install Pillow pyyaml

Шрифты (те же, что в static/style.css) — скачать с Google Fonts и положить сюда:
    static/assets/fonts/SourceSerif4-SemiBold.ttf
      https://fonts.google.com/specimen/Source+Serif+4
    static/assets/fonts/JetBrainsMono-Medium.ttf
      https://fonts.google.com/specimen/JetBrains+Mono

Запуск:
    python generate_og_image.py
"""

from pathlib import Path
import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "resume.yaml"
FONTS_DIR = ROOT / "static" / "assets" / "fonts"
OUTPUT = ROOT / "static" / "assets" / "og-image.png"

# Те же значения, что в static/style.css :root — держи в синхроне при смене палитры
BG = "#0f1013"
FG = "#e7e4dd"
ACCENT = "#c9972f"
MUTED = "#8b8a86"

W, H = 1200, 630
PAD = 90  # safe zone от краёв


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise SystemExit(
            f"Не найден шрифт {path}\n"
            f"Скачай .ttf с Google Fonts (см. докстринг файла) и положи сюда."
        )
    return ImageFont.truetype(str(path), size)


def main() -> None:
    data = yaml.safe_load(DATA_FILE.read_text(encoding="utf-8"))

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    serif_bold = load_font(FONTS_DIR / "SourceSerif4-SemiBold.ttf", 72)
    mono = load_font(FONTS_DIR / "JetBrainsMono-Medium.ttf", 28)
    mono_small = load_font(FONTS_DIR / "JetBrainsMono-Medium.ttf", 22)

    # Левая акцентная полоса — тот же приём, что у section__title на сайте
    draw.rectangle([PAD, PAD, PAD + 6, PAD + 90], fill=ACCENT)

    draw.text((PAD + 30, PAD - 8), data["name"], font=serif_bold, fill=FG)
    draw.text((PAD + 30, PAD + 78), data["role"], font=mono, fill=ACCENT)

    # Тэглайн внизу, приглушённым цветом — как .hero__tagline
    draw.text((PAD, H - PAD - 30), data["tagline"], font=mono_small, fill=MUTED)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUTPUT)
    print(f"OK: {OUTPUT}")


if __name__ == "__main__":
    main()
