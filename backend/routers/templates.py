"""
Router pour les templates de contenu.
Liste et récupère les templates disponibles.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import Template, TemplateType


router = APIRouter(tags=["templates"])


# Templates hard-codés pour MVP
# Dans un vrai contexte, ils seraient en DB
TEMPLATES_DB = [
    {
        "id": "linkedin-post-classic",
        "name": "Post LinkedIn Classique",
        "template_type": TemplateType.POST,
        "structure": {
            "sections": ["hook", "body", "cta", "hashtags"],
            "max_length": 1200,
            "format": "viral"
        },
        "preview_image": None
    },
    {
        "id": "linkedin-post-storytelling",
        "name": "Post LinkedIn Storytelling",
        "template_type": TemplateType.POST,
        "structure": {
            "sections": ["hook", "story", "lesson", "cta"],
            "max_length": 1500,
            "format": "narrative"
        },
        "preview_image": None
    },
    {
        "id": "linkedin-carousel-5",
        "name": "Carousel LinkedIn 5 slides",
        "template_type": TemplateType.CAROUSEL,
        "structure": {
            "num_slides": 5,
            "slide_sections": ["title", "content"],
            "cover_required": True
        },
        "preview_image": None
    },
    {
        "id": "linkedin-carousel-7",
        "name": "Carousel LinkedIn 7 slides",
        "template_type": TemplateType.CAROUSEL,
        "structure": {
            "num_slides": 7,
            "slide_sections": ["title", "content"],
            "cover_required": True
        },
        "preview_image": None
    },
    {
        "id": "instagram-post-classic",
        "name": "Post Instagram Classique",
        "template_type": TemplateType.POST,
        "structure": {
            "sections": ["text", "hashtags"],
            "max_length": 2200,
            "format": "casual"
        },
        "preview_image": None
    }
]


@router.get("/templates", response_model=List[Template])
async def list_templates(template_type: TemplateType = None):
    """
    Liste tous les templates disponibles.
    Filtre optionnel par type.
    """
    templates = TEMPLATES_DB

    if template_type:
        templates = [t for t in templates if t["template_type"] == template_type]

    return [
        Template(
            id=t["id"],
            name=t["name"],
            template_type=t["template_type"],
            structure=t["structure"],
            preview_image=t.get("preview_image"),
            created_at="2025-01-01T00:00:00Z"  # Placeholder
        )
        for t in templates
    ]


@router.get("/templates/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """
    Récupère un template spécifique par ID.
    """
    template = next((t for t in TEMPLATES_DB if t["id"] == template_id), None)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

    return Template(
        id=template["id"],
        name=template["name"],
        template_type=template["template_type"],
        structure=template["structure"],
        preview_image=template.get("preview_image"),
        created_at="2025-01-01T00:00:00Z"
    )
