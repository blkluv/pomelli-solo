"""
Service d'export de contenu vers format JSON Figma.
Génère des JSON compatibles avec Figma pour import manuel.
"""

from typing import Dict, Any, List, Optional
from models.schemas import (
    ColorPalette, GeneratedVariation, CarouselSlide,
    ContentType
)


class FigmaExporter:
    """Exporte du contenu généré vers JSON Figma"""

    def export_linkedin_post(
        self,
        variation: GeneratedVariation,
        brand_colors: Optional[ColorPalette] = None
    ) -> Dict[str, Any]:
        """
        Exporte un post LinkedIn vers Figma JSON.
        Format simplifié pour import manuel.
        """
        # Couleurs par défaut
        primary_color = brand_colors.primary if brand_colors else "#000000"
        secondary_color = brand_colors.secondary if brand_colors else "#FFFFFF"
        accent_color = brand_colors.accent if brand_colors else "#4A90E2"

        figma_json = {
            "name": "LinkedIn Post",
            "type": "POST",
            "content": {
                "hook": variation.hook or "",
                "body": variation.text,
                "cta": variation.cta or "",
                "hashtags": " ".join(variation.hashtags) if variation.hashtags else ""
            },
            "colors": {
                "primary": primary_color,
                "secondary": secondary_color,
                "accent": accent_color,
                "background": secondary_color,
                "text": primary_color
            },
            "layout": {
                "width": 1080,
                "height": 1080,
                "padding": 60
            },
            "typography": {
                "hook": {
                    "fontSize": 48,
                    "fontWeight": "bold",
                    "lineHeight": 1.2,
                    "color": primary_color
                },
                "body": {
                    "fontSize": 28,
                    "fontWeight": "normal",
                    "lineHeight": 1.5,
                    "color": primary_color
                },
                "cta": {
                    "fontSize": 32,
                    "fontWeight": "bold",
                    "lineHeight": 1.3,
                    "color": accent_color
                },
                "hashtags": {
                    "fontSize": 24,
                    "fontWeight": "normal",
                    "lineHeight": 1.4,
                    "color": accent_color
                }
            },
            "metadata": variation.metadata or {}
        }

        return figma_json

    def export_linkedin_carousel(
        self,
        carousel_title: str,
        slides: List[CarouselSlide],
        cover_text: Optional[str] = None,
        brand_colors: Optional[ColorPalette] = None
    ) -> Dict[str, Any]:
        """
        Exporte un carousel LinkedIn vers Figma JSON.
        """
        primary_color = brand_colors.primary if brand_colors else "#000000"
        secondary_color = brand_colors.secondary if brand_colors else "#FFFFFF"
        accent_color = brand_colors.accent if brand_colors else "#4A90E2"

        # Convertir slides
        figma_slides = []

        # Slide 1 (Cover)
        figma_slides.append({
            "slideNumber": 1,
            "type": "COVER",
            "title": carousel_title,
            "subtitle": cover_text or "",
            "colors": {
                "background": primary_color,
                "title": secondary_color,
                "subtitle": accent_color
            },
            "layout": {
                "width": 1080,
                "height": 1080
            }
        })

        # Slides de contenu
        for slide in slides:
            figma_slides.append({
                "slideNumber": slide.slide_number,
                "type": "CONTENT",
                "title": slide.title,
                "content": slide.content,
                "visualHint": slide.visual_hint,
                "colors": {
                    "background": secondary_color,
                    "title": primary_color,
                    "content": primary_color,
                    "accent": accent_color
                },
                "layout": {
                    "width": 1080,
                    "height": 1080,
                    "padding": 60
                },
                "typography": {
                    "title": {
                        "fontSize": 44,
                        "fontWeight": "bold",
                        "lineHeight": 1.2
                    },
                    "content": {
                        "fontSize": 28,
                        "fontWeight": "normal",
                        "lineHeight": 1.5
                    }
                }
            })

        figma_json = {
            "name": f"LinkedIn Carousel - {carousel_title}",
            "type": "CAROUSEL",
            "totalSlides": len(figma_slides),
            "slides": figma_slides,
            "colors": {
                "primary": primary_color,
                "secondary": secondary_color,
                "accent": accent_color
            }
        }

        return figma_json

    def export_instagram_post(
        self,
        variation: GeneratedVariation,
        brand_colors: Optional[ColorPalette] = None
    ) -> Dict[str, Any]:
        """
        Exporte un post Instagram vers Figma JSON.
        """
        primary_color = brand_colors.primary if brand_colors else "#000000"
        secondary_color = brand_colors.secondary if brand_colors else "#FFFFFF"
        accent_color = brand_colors.accent if brand_colors else "#E1306C"

        figma_json = {
            "name": "Instagram Post",
            "type": "POST",
            "content": {
                "text": variation.text,
                "hashtags": " ".join(variation.hashtags) if variation.hashtags else ""
            },
            "colors": {
                "primary": primary_color,
                "secondary": secondary_color,
                "accent": accent_color,
                "background": secondary_color
            },
            "layout": {
                "width": 1080,
                "height": 1080,
                "padding": 80
            },
            "typography": {
                "text": {
                    "fontSize": 36,
                    "fontWeight": "normal",
                    "lineHeight": 1.4,
                    "color": primary_color
                },
                "hashtags": {
                    "fontSize": 28,
                    "fontWeight": "normal",
                    "lineHeight": 1.3,
                    "color": accent_color
                }
            }
        }

        return figma_json

    def generate_filename(
        self,
        content_type: ContentType,
        topic: Optional[str] = None
    ) -> str:
        """
        Génère un nom de fichier pour le download.
        """
        type_map = {
            ContentType.LINKEDIN_POST: "linkedin-post",
            ContentType.LINKEDIN_CAROUSEL: "linkedin-carousel",
            ContentType.INSTAGRAM_POST: "instagram-post",
            ContentType.INSTAGRAM_CAROUSEL: "instagram-carousel"
        }

        base_name = type_map.get(content_type, "content")

        if topic:
            # Slugify topic
            slug = topic.lower().replace(" ", "-")[:30]
            return f"{base_name}-{slug}.json"

        return f"{base_name}.json"


# Instance globale
figma_exporter = FigmaExporter()
