#!/usr/bin/env python3
"""
Prépare les images du site à partir des photos sources.

Usage :
    python tools/prepare_images.py <dossier_sources> <dossier_sortie>

- génère des variantes WebP + JPG (480 / 800 / 1200 px selon la source)
- recadre la photo "garnissage" (bandes noires)
- crée l'image Open Graph 1200x630
- crée le favicon et l'icône Apple

Dépendance : Pillow
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "tools/sources")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "assets/img")
OUT.mkdir(parents=True, exist_ok=True)

NAVY = (30, 36, 48)
CREAM = (247, 241, 232)
TERRACOTTA = (194, 112, 79)

# Photos de la galerie : (nom source, largeur max utile)
GALLERY = [
    ("salle-bas.jpg", 800),
    ("salle-etage.jpg", 800),
    ("pizza-coppa.jpg", 800),
    ("ambiance.jpg", 800),
    ("sauce-tomate.jpg", 612),
    ("parme.jpg", 800),
    ("ile-flottante.jpg", 612),
    ("tiramisu.jpg", 612),
]


def save_variants(img: Image.Image, name: str, widths: list[int]) -> None:
    """Enregistre des variantes WebP et JPG, sans agrandir la source."""
    for width in widths:
        if width > img.width:
            continue
        height = round(img.height * width / img.width)
        resized = img.resize((width, height), Image.Resampling.LANCZOS)
        base = OUT / f"{name}-{width}"
        resized.save(base.with_suffix(".webp"), "WEBP", quality=82, method=6)
        resized.save(
            base.with_suffix(".jpg"),
            "JPEG",
            quality=82,
            optimize=True,
            progressive=True,
        )
        print(f"  {base.name}.webp / .jpg  ({width}x{height})")


def crop_dark_bars(img: Image.Image) -> Image.Image:
    """Recadre les bandes noires (letterbox / pillarbox) autour d'une photo."""
    mask = img.convert("L").point(lambda p: 255 if p > 25 else 0)
    bbox = mask.getbbox()
    if bbox:
        return img.crop(bbox)
    return img


def make_og(hero_path: Path) -> None:
    """Image de partage 1200x630 avec voile dégradé et titre."""
    img = Image.open(hero_path).convert("RGB")
    img = ImageOps.fit(img, (1200, 630), Image.Resampling.LANCZOS, centering=(0.5, 0.45))

    # Voile dégradé de gauche à droite pour la lisibilité du texte
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    px = overlay.load()
    for x in range(img.width):
        alpha = int(185 * (1 - x / img.width) ** 1.35 + 35)
        for y in range(img.height):
            px[x, y] = (12, 15, 22, alpha)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    serif = "C:/Windows/Fonts/georgiab.ttf"
    sans = "C:/Windows/Fonts/arial.ttf"
    try:
        title_font = ImageFont.truetype(serif, 74)
        sub_font = ImageFont.truetype(sans, 27)
        eyebrow_font = ImageFont.truetype(sans, 19)
    except OSError:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        eyebrow_font = ImageFont.load_default()

    x = 78
    draw.rectangle((x, 150, x + 74, 154), fill=TERRACOTTA)
    draw.text((x, 182), "PIZZERIA · CAFÉ · BUXY", font=eyebrow_font, fill=CREAM)
    draw.multiline_text(
        (x, 226),
        "Pizzeria Café\nde la Gare",
        font=title_font,
        fill=(255, 255, 255),
        spacing=6,
    )
    draw.text(
        (x, 444),
        "Pizzas napolitaines · Café & bar · À emporter",
        font=sub_font,
        fill=(247, 241, 232),
    )
    draw.text(
        (x, 494),
        "2 place de la Gare, 71390 Buxy · 03 58 93 36 13",
        font=sub_font,
        fill=(216, 203, 188),
    )

    img.save(OUT / "og-image.jpg", "JPEG", quality=88, optimize=True, progressive=True)
    print("  og-image.jpg (1200x630)")


def make_icons() -> None:
    """Favicon PNG, icône Apple et icône manifeste."""
    size = 512
    img = Image.new("RGB", (size, size), NAVY)
    draw = ImageDraw.Draw(img)
    draw.ellipse((64, 64, size - 64, size - 64), outline=TERRACOTTA, width=10)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 300)
    except OSError:
        font = ImageFont.load_default()
    text = "P"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1] - 16),
        text,
        font=font,
        fill=CREAM,
    )
    draw.ellipse((size - 150, size - 150, size - 128, size - 128), fill=TERRACOTTA)
    img.save(OUT / "icon-512.png", "PNG", optimize=True)
    img.resize((180, 180), Image.Resampling.LANCZOS).save(
        OUT / "apple-touch-icon.png", "PNG", optimize=True
    )
    img.resize((32, 32), Image.Resampling.LANCZOS).save(
        OUT / "favicon-32.png", "PNG", optimize=True
    )
    print("  icon-512.png / apple-touch-icon.png / favicon-32.png")


def main() -> None:
    print("Images de la galerie :")
    for filename, max_width in GALLERY:
        path = SRC / filename
        if not path.exists():
            print(f"  !! source manquante : {path}")
            continue
        img = Image.open(path).convert("RGB")
        if filename == "garnissage.jpg":
            img = crop_dark_bars(img)
        name = path.stem
        widths = sorted({480, max_width})
        save_variants(img, name, widths)

    # Photo "garnissage" utilisée dans la section "à propos"
    garnissage = SRC / "garnissage.jpg"
    if garnissage.exists():
        img = crop_dark_bars(Image.open(garnissage).convert("RGB"))
        img.save(OUT / "garnissage.jpg", "JPEG", quality=84, optimize=True, progressive=True)
        img.save(OUT / "garnissage.webp", "WEBP", quality=82, method=6)
        print("  garnissage.jpg / .webp (recadré)")

    print("Hero :")
    hero = SRC / "hero.jpg"
    if hero.exists():
        img = Image.open(hero).convert("RGB")
        save_variants(img, "hero", [800, 1200])
        make_og(hero)

    print("Icônes :")
    make_icons()

    # Logo original (42x40) : conservé tel quel pour l'avatar du header
    logo = SRC / "logo.jpg"
    if logo.exists():
        Image.open(logo).convert("RGB").save(
            OUT / "logo.jpg", "JPEG", quality=90, optimize=True
        )
        print("  logo.jpg")


if __name__ == "__main__":
    main()
