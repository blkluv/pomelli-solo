"""
Router pour les endpoints Brand.
Gestion des marques et Brand DNA.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
from models.schemas import (
    ScrapeWebsiteRequest, ScrapeWebsiteResponse,
    ExtractColorsRequest, ExtractColorsResponse,
    AnalyzeCompleteRequest, AnalyzeCompleteResponse,
    BrandDNA, ColorPalette
)
from services.scraper import scraper
from services.colors import extract_colors_from_url, extract_colors_from_bytes, merge_palettes
from services.ai import ai_service


router = APIRouter(tags=["brand"])


@router.post("/brand/scrape-website", response_model=ScrapeWebsiteResponse)
async def scrape_website(request: ScrapeWebsiteRequest):
    """
    Scrape un site web pour extraire infos de brand.
    """
    try:
        # Scraper le site
        scraped_data = scraper.scrape_website(str(request.url))

        # Analyser le contenu avec IA
        analysis = ai_service.analyze_website_content(
            website_text=scraped_data["text"],
            website_title=scraped_data["title"],
            website_description=scraped_data["description"]
        )

        # Extraire couleurs depuis images si disponibles
        color_palette = None
        if scraped_data.get("images"):
            try:
                # Prendre la première image (souvent le logo)
                first_image_url = scraped_data["images"][0]
                color_palette = extract_colors_from_url(first_image_url, num_colors=6)
            except Exception:
                pass  # Ignore si échec extraction couleurs

        return ScrapeWebsiteResponse(
            url=str(request.url),
            title=scraped_data.get("title"),
            description=scraped_data.get("description"),
            detected_tone=analysis.get("detected_tone"),
            detected_sector=analysis.get("detected_sector"),
            suggested_keywords=analysis.get("suggested_keywords", []),
            color_palette=color_palette
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape website: {str(e)}")


@router.post("/brand/extract-colors", response_model=ExtractColorsResponse)
async def extract_colors(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = None,
    num_colors: int = 6
):
    """
    Extrait les couleurs depuis un logo (fichier ou URL).
    """
    if not file and not image_url:
        raise HTTPException(status_code=400, detail="Provide either file or image_url")

    try:
        if file:
            # Extraire depuis fichier uploadé
            image_bytes = await file.read()
            palette = extract_colors_from_bytes(image_bytes, num_colors=num_colors)
        else:
            # Extraire depuis URL
            palette = extract_colors_from_url(image_url, num_colors=num_colors)

        return ExtractColorsResponse(
            palette=palette,
            num_colors_extracted=len(palette.all_colors)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract colors: {str(e)}")


@router.post("/brand/analyze-complete", response_model=AnalyzeCompleteResponse)
async def analyze_complete(
    logo_file: Optional[UploadFile] = File(None),
    website_url: Optional[str] = None
):
    """
    Analyse complète : logo + site web → Brand DNA complet.
    """
    brand_dna_data = {
        "colors": None,
        "tone": "professionnel",
        "sector": "autre",
        "values": [],
        "keywords": [],
        "target_audience": None,
        "unique_angle": None
    }

    scrape_data = None
    colors_from_logo = None
    colors_from_website = None

    # Extraire couleurs du logo
    if logo_file:
        try:
            logo_bytes = await logo_file.read()
            colors_from_logo = extract_colors_from_bytes(logo_bytes, num_colors=6)
        except Exception:
            pass

    # Scraper le site
    if website_url:
        try:
            scraped = scraper.scrape_website(website_url)
            analysis = ai_service.analyze_website_content(
                website_text=scraped["text"],
                website_title=scraped["title"],
                website_description=scraped["description"]
            )

            scrape_data = ScrapeWebsiteResponse(
                url=website_url,
                title=scraped.get("title"),
                description=scraped.get("description"),
                detected_tone=analysis.get("detected_tone"),
                detected_sector=analysis.get("detected_sector"),
                suggested_keywords=analysis.get("suggested_keywords", []),
                color_palette=None
            )

            # Appliquer infos détectées au Brand DNA
            if analysis.get("detected_tone"):
                brand_dna_data["tone"] = analysis["detected_tone"]
            if analysis.get("detected_sector"):
                brand_dna_data["sector"] = analysis["detected_sector"]
            if analysis.get("suggested_keywords"):
                brand_dna_data["keywords"] = analysis["suggested_keywords"][:10]
            if analysis.get("target_audience"):
                brand_dna_data["target_audience"] = analysis["target_audience"]
            if analysis.get("unique_angle"):
                brand_dna_data["unique_angle"] = analysis["unique_angle"]

            # Extraire couleurs du site si images disponibles
            if scraped.get("images"):
                try:
                    first_image = scraped["images"][0]
                    colors_from_website = extract_colors_from_url(first_image, num_colors=6)
                except Exception:
                    pass

        except Exception:
            pass

    # Fusionner palettes de couleurs
    if colors_from_logo and colors_from_website:
        brand_dna_data["colors"] = merge_palettes(colors_from_logo, colors_from_website)
    elif colors_from_logo:
        brand_dna_data["colors"] = colors_from_logo
    elif colors_from_website:
        brand_dna_data["colors"] = colors_from_website
    else:
        # Palette par défaut
        brand_dna_data["colors"] = ColorPalette(
            primary="#000000",
            secondary="#FFFFFF",
            accent="#4A90E2",
            neutrals=["#F5F5F5", "#333333"],
            all_colors=["#000000", "#FFFFFF", "#4A90E2", "#F5F5F5", "#333333"]
        )

    # Créer Brand DNA
    brand_dna = BrandDNA(**brand_dna_data)

    return AnalyzeCompleteResponse(
        brand_dna=brand_dna,
        scrape_data=scrape_data,
        colors_from_logo=colors_from_logo,
        colors_from_website=colors_from_website
    )
