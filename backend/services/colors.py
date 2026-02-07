"""
Service d'extraction de couleurs depuis images.
Utilise ColorThief pour extraction server-side.
"""

import io
import requests
from typing import List, Tuple, Optional
from PIL import Image
from colorthief import ColorThief
from models.schemas import ColorPalette


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convertit RGB en hex"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper()


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convertit hex en RGB"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calcule la luminance d'une couleur (0-1)"""
    r, g, b = [x / 255.0 for x in rgb]
    # Formule de luminance relative
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def is_neutral(rgb: Tuple[int, int, int]) -> bool:
    """Détecte si une couleur est neutre (gris/noir/blanc)"""
    r, g, b = rgb
    # Écart max entre composantes
    max_diff = max(r, g, b) - min(r, g, b)
    return max_diff < 30  # Seuil pour considérer comme neutre


def classify_colors(colors_rgb: List[Tuple[int, int, int]]) -> ColorPalette:
    """
    Classe les couleurs en primary, secondary, accent, neutrals.
    Logique simple mais efficace.
    """
    if not colors_rgb:
        # Palette par défaut
        return ColorPalette(
            primary="#000000",
            secondary="#FFFFFF",
            accent="#CCCCCC",
            neutrals=["#F5F5F5", "#333333"],
            all_colors=["#000000", "#FFFFFF", "#CCCCCC", "#F5F5F5", "#333333"]
        )

    # Séparer couleurs vives et neutres
    vibrant_colors = []
    neutral_colors = []

    for rgb in colors_rgb:
        if is_neutral(rgb):
            neutral_colors.append(rgb)
        else:
            vibrant_colors.append(rgb)

    # Trier couleurs vives par saturation (approximation)
    def saturation(rgb):
        r, g, b = rgb
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        return max_val - min_val

    vibrant_colors.sort(key=saturation, reverse=True)

    # Trier neutres par luminance
    neutral_colors.sort(key=calculate_luminance)

    # Assigner primary, secondary, accent
    primary_rgb = vibrant_colors[0] if vibrant_colors else colors_rgb[0]
    secondary_rgb = vibrant_colors[1] if len(vibrant_colors) > 1 else (
        neutral_colors[0] if neutral_colors else colors_rgb[1] if len(colors_rgb) > 1 else primary_rgb
    )
    accent_rgb = vibrant_colors[2] if len(vibrant_colors) > 2 else (
        vibrant_colors[1] if len(vibrant_colors) > 1 else primary_rgb
    )

    # Convertir en hex
    primary_hex = rgb_to_hex(primary_rgb)
    secondary_hex = rgb_to_hex(secondary_rgb)
    accent_hex = rgb_to_hex(accent_rgb)
    neutrals_hex = [rgb_to_hex(n) for n in neutral_colors[:3]]
    all_colors_hex = [rgb_to_hex(c) for c in colors_rgb]

    return ColorPalette(
        primary=primary_hex,
        secondary=secondary_hex,
        accent=accent_hex,
        neutrals=neutrals_hex,
        all_colors=all_colors_hex
    )


def extract_colors_from_image(
    image_source: str | bytes,
    num_colors: int = 6,
    quality: int = 10
) -> ColorPalette:
    """
    Extrait les couleurs dominantes d'une image.

    Args:
        image_source: URL de l'image ou bytes
        num_colors: Nombre de couleurs à extraire (3-12)
        quality: Qualité de l'analyse (1-10, plus bas = plus précis mais plus lent)

    Returns:
        ColorPalette avec couleurs classifiées
    """
    # Charger l'image
    if isinstance(image_source, str):
        # C'est une URL
        response = requests.get(image_source, timeout=10)
        response.raise_for_status()
        image_bytes = io.BytesIO(response.content)
    else:
        # C'est déjà des bytes
        image_bytes = io.BytesIO(image_source)

    # Vérifier que c'est bien une image
    try:
        img = Image.open(image_bytes)
        img.verify()
        image_bytes.seek(0)  # Reset après verify
    except Exception as e:
        raise ValueError(f"Invalid image: {e}")

    # Extraire couleur dominante
    color_thief = ColorThief(image_bytes)
    dominant_color = color_thief.get_color(quality=quality)

    # Extraire palette
    image_bytes.seek(0)  # Reset
    color_thief = ColorThief(image_bytes)

    try:
        palette = color_thief.get_palette(color_count=num_colors, quality=quality)
    except Exception:
        # Fallback si échec
        palette = [dominant_color]

    # Classifier les couleurs
    return classify_colors(palette)


def extract_colors_from_url(url: str, num_colors: int = 6) -> ColorPalette:
    """
    Extrait couleurs depuis une URL d'image.
    """
    return extract_colors_from_image(url, num_colors=num_colors)


def extract_colors_from_bytes(image_bytes: bytes, num_colors: int = 6) -> ColorPalette:
    """
    Extrait couleurs depuis bytes d'image.
    """
    return extract_colors_from_image(image_bytes, num_colors=num_colors)


def merge_palettes(palette1: ColorPalette, palette2: ColorPalette) -> ColorPalette:
    """
    Fusionne 2 palettes (ex: logo + site web).
    Priorise palette1 pour primary/secondary.
    """
    # Combiner toutes les couleurs
    all_colors = list(set(palette1.all_colors + palette2.all_colors))

    # Garder primary de palette1, secondary de palette2
    return ColorPalette(
        primary=palette1.primary,
        secondary=palette2.primary,  # Primary de palette2 devient secondary
        accent=palette1.accent,
        neutrals=list(set(palette1.neutrals + palette2.neutrals))[:4],
        all_colors=all_colors[:12]
    )
