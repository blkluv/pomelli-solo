"""
Router pour la génération de contenu avec IA.
Posts LinkedIn, Carousels, etc.
"""

from fastapi import APIRouter, HTTPException
from models.schemas import (
    GeneratePostRequest, GeneratePostResponse,
    GenerateCarouselRequest, CarouselResponse,
    QuickPostRequest, GeneratePostResponse as QuickPostResponse,
    FigmaExportRequest, FigmaExportResponse,
    ContentType
)
from services.ai import ai_service
from services.figma_export import figma_exporter


router = APIRouter(tags=["generate"])


@router.post("/generate/post", response_model=GeneratePostResponse)
async def generate_post(request: GeneratePostRequest):
    """
    Génère un post LinkedIn avec Brand DNA.
    Retourne 3 variations.
    """
    try:
        # Note: Dans un vrai contexte, on chargerait le Brand depuis Supabase
        # Ici, on simule avec brand_dna = None (l'utilisateur doit passer brand_id)
        # Pour MVP, on génère sans Brand DNA complet

        variations = ai_service.generate_linkedin_post(
            topic=request.topic,
            brand_dna=None,  # TODO: Charger depuis Supabase avec brand_id
            tone=request.tone,
            num_variations=3
        )

        return GeneratePostResponse(
            variations=variations,
            brand_colors=None,  # TODO: Récupérer du Brand
            template_used=request.template_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/generate/carousel", response_model=CarouselResponse)
async def generate_carousel(request: GenerateCarouselRequest):
    """
    Génère un carousel LinkedIn.
    """
    try:
        result = ai_service.generate_linkedin_carousel(
            topic=request.topic,
            brand_dna=None,  # TODO: Charger depuis Supabase
            num_slides=request.num_slides,
            tone=request.tone
        )

        return CarouselResponse(
            title=result["title"],
            slides=result["slides"],
            cover_text=result.get("cover_text"),
            brand_colors=None  # TODO: Récupérer du Brand
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Carousel generation failed: {str(e)}")


@router.post("/generate/quick-post", response_model=QuickPostResponse)
async def quick_post(request: QuickPostRequest):
    """
    Génération rapide sans Brand (pour test).
    """
    try:
        variations = ai_service.generate_linkedin_post(
            topic=request.topic,
            brand_dna=None,
            tone=request.tone,
            sector=request.sector,
            num_variations=3
        )

        return QuickPostResponse(
            variations=variations,
            brand_colors=None,
            template_used=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick post generation failed: {str(e)}")


@router.post("/generate/export-figma", response_model=FigmaExportResponse)
async def export_figma(request: FigmaExportRequest):
    """
    Exporte du contenu généré vers JSON Figma.
    """
    try:
        # Note: Dans un vrai contexte, on chargerait le contenu depuis Supabase
        # Pour MVP, on retourne un exemple de structure Figma

        # TODO: Charger le GeneratedContent depuis Supabase avec content_id
        # Pour l'instant, on retourne un template vide

        figma_json = {
            "name": "Exported Content",
            "type": "POST",
            "content": {},
            "colors": {},
            "layout": {"width": 1080, "height": 1080}
        }

        return FigmaExportResponse(
            figma_json=figma_json,
            content_type=ContentType.LINKEDIN_POST,
            download_filename=figma_exporter.generate_filename(
                ContentType.LINKEDIN_POST,
                topic="export"
            )
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Figma export failed: {str(e)}")
