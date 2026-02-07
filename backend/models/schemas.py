"""
Modèles Pydantic pour validation des données.
Compatible avec la base Supabase (database/schema.sql).
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


# === ENUMS ===

class Tone(str, Enum):
    """Tonalité de communication"""
    PROFESSIONNEL = "professionnel"
    INSPIRANT = "inspirant"
    PEDAGOGIQUE = "pédagogique"
    PROVOCATEUR = "provocateur"
    AUTHENTIQUE = "authentique"


class Sector(str, Enum):
    """Secteur d'activité"""
    COACHING = "coaching"
    CONSULTING = "consulting"
    DESIGN = "design"
    DEVELOPPEMENT = "développement"
    MARKETING = "marketing"
    SANTE = "santé"
    FINANCE = "finance"
    ECOMMERCE = "e-commerce"
    EDUCATION = "éducation"
    AUTRE = "autre"


class TemplateType(str, Enum):
    """Type de template"""
    POST = "post"
    CAROUSEL = "carousel"
    STORY = "story"


class ContentType(str, Enum):
    """Type de contenu généré"""
    LINKEDIN_POST = "linkedin_post"
    LINKEDIN_CAROUSEL = "linkedin_carousel"
    INSTAGRAM_POST = "instagram_post"
    INSTAGRAM_CAROUSEL = "instagram_carousel"


# === COLOR SCHEMAS ===

class ColorPalette(BaseModel):
    """Palette de couleurs extraite"""
    primary: str = Field(..., description="Couleur primaire (hex)")
    secondary: str = Field(..., description="Couleur secondaire (hex)")
    accent: str = Field(..., description="Couleur d'accent (hex)")
    neutrals: List[str] = Field(default_factory=list, description="Couleurs neutres (hex)")
    all_colors: List[str] = Field(default_factory=list, description="Toutes couleurs extraites")

    class Config:
        json_schema_extra = {
            "example": {
                "primary": "#FF6B6B",
                "secondary": "#4ECDC4",
                "accent": "#FFE66D",
                "neutrals": ["#F7F7F7", "#2C2C2C"],
                "all_colors": ["#FF6B6B", "#4ECDC4", "#FFE66D", "#F7F7F7", "#2C2C2C"]
            }
        }


# === BRAND DNA ===

class BrandDNA(BaseModel):
    """ADN de marque complet"""
    colors: ColorPalette
    tone: Tone = Field(default=Tone.PROFESSIONNEL)
    sector: Sector = Field(default=Sector.AUTRE)
    values: List[str] = Field(default_factory=list, max_length=5, description="Max 5 valeurs")
    keywords: List[str] = Field(default_factory=list, max_length=10, description="Max 10 mots-clés")
    target_audience: Optional[str] = Field(None, description="Audience cible")
    unique_angle: Optional[str] = Field(None, description="Angle unique/différenciant")

    class Config:
        json_schema_extra = {
            "example": {
                "colors": {
                    "primary": "#FF6B6B",
                    "secondary": "#4ECDC4",
                    "accent": "#FFE66D",
                    "neutrals": ["#F7F7F7"],
                    "all_colors": ["#FF6B6B", "#4ECDC4"]
                },
                "tone": "inspirant",
                "sector": "coaching",
                "values": ["authenticité", "impact", "liberté"],
                "keywords": ["personal branding", "solopreneur", "stratégie"],
                "target_audience": "Solopreneurs ambitieux 30-45 ans",
                "unique_angle": "Personal branding sans bullshit"
            }
        }


# === BRAND MODELS ===

class BrandBase(BaseModel):
    """Base pour Brand (création/update)"""
    name: str = Field(..., min_length=1, max_length=255)
    website_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    brand_dna: Optional[BrandDNA] = None


class BrandCreate(BrandBase):
    """Création d'un Brand"""
    pass


class BrandUpdate(BaseModel):
    """Update d'un Brand (tous champs optionnels)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    website_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    brand_dna: Optional[BrandDNA] = None


class Brand(BrandBase):
    """Brand complet (avec ID et timestamps)"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === PROJECT MODELS ===

class ProjectBase(BaseModel):
    """Base pour Project"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Création d'un Project"""
    brand_id: str


class ProjectUpdate(BaseModel):
    """Update d'un Project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class Project(ProjectBase):
    """Project complet"""
    id: str
    brand_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === GENERATION REQUESTS ===

class GeneratePostRequest(BaseModel):
    """Requête pour générer un post simple"""
    brand_id: str
    topic: str = Field(..., min_length=3, description="Sujet du post")
    tone: Optional[Tone] = Field(None, description="Override du tone du brand")
    template_id: Optional[str] = Field(None, description="Template spécifique")


class GenerateCarouselRequest(BaseModel):
    """Requête pour générer un carousel"""
    brand_id: str
    topic: str = Field(..., min_length=3)
    num_slides: int = Field(default=5, ge=3, le=10, description="Nombre de slides (3-10)")
    tone: Optional[Tone] = None


class QuickPostRequest(BaseModel):
    """Génération rapide sans Brand (test)"""
    topic: str = Field(..., min_length=3)
    tone: Tone = Field(default=Tone.PROFESSIONNEL)
    sector: Sector = Field(default=Sector.AUTRE)


# === GENERATION RESPONSES ===

class GeneratedVariation(BaseModel):
    """Une variation de contenu généré"""
    text: str = Field(..., description="Texte du post")
    hook: Optional[str] = Field(None, description="Hook (1ère ligne)")
    cta: Optional[str] = Field(None, description="Call-to-action")
    hashtags: List[str] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default_factory=dict, description="Métadonnées additionnelles")


class GeneratePostResponse(BaseModel):
    """Réponse de génération de post"""
    variations: List[GeneratedVariation] = Field(..., min_items=1, max_items=5)
    brand_colors: Optional[ColorPalette] = None
    template_used: Optional[str] = None


class CarouselSlide(BaseModel):
    """Une slide de carousel"""
    slide_number: int = Field(..., ge=1)
    title: str = Field(..., max_length=100)
    content: str = Field(..., max_length=500)
    visual_hint: Optional[str] = Field(None, description="Suggestion visuelle")


class CarouselResponse(BaseModel):
    """Réponse de génération de carousel"""
    title: str = Field(..., description="Titre du carousel")
    slides: List[CarouselSlide] = Field(..., min_items=3, max_items=10)
    cover_text: Optional[str] = Field(None, description="Texte de couverture")
    brand_colors: Optional[ColorPalette] = None


# === GENERATED CONTENT (DB) ===

class GeneratedContentBase(BaseModel):
    """Base pour contenu généré"""
    content_type: ContentType
    content_data: dict = Field(..., description="JSON du contenu")
    figma_json: Optional[dict] = Field(None, description="Export Figma")


class GeneratedContentCreate(GeneratedContentBase):
    """Création de contenu généré"""
    project_id: str
    brand_id: str


class GeneratedContent(GeneratedContentBase):
    """Contenu généré complet"""
    id: str
    project_id: str
    brand_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# === TEMPLATES ===

class TemplateBase(BaseModel):
    """Base pour Template"""
    name: str = Field(..., min_length=1, max_length=255)
    template_type: TemplateType
    structure: dict = Field(..., description="Structure du template (JSON)")
    preview_image: Optional[HttpUrl] = None


class Template(TemplateBase):
    """Template complet"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# === SCRAPING ===

class ScrapeWebsiteRequest(BaseModel):
    """Requête de scraping de site"""
    url: HttpUrl


class ScrapeWebsiteResponse(BaseModel):
    """Résultat du scraping"""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    detected_tone: Optional[Tone] = None
    detected_sector: Optional[Sector] = None
    suggested_keywords: List[str] = Field(default_factory=list)
    color_palette: Optional[ColorPalette] = None


# === COLOR EXTRACTION ===

class ExtractColorsRequest(BaseModel):
    """Requête d'extraction de couleurs"""
    image_url: Optional[HttpUrl] = Field(None, description="URL de l'image")
    num_colors: int = Field(default=6, ge=3, le=12, description="Nombre de couleurs à extraire")


class ExtractColorsResponse(BaseModel):
    """Réponse d'extraction de couleurs"""
    palette: ColorPalette
    num_colors_extracted: int


# === FIGMA EXPORT ===

class FigmaExportRequest(BaseModel):
    """Requête d'export Figma"""
    content_id: str = Field(..., description="ID du contenu généré")
    include_colors: bool = Field(default=True, description="Inclure palette de couleurs")


class FigmaExportResponse(BaseModel):
    """Réponse d'export Figma"""
    figma_json: dict = Field(..., description="JSON compatible Figma")
    content_type: ContentType
    download_filename: str = Field(..., description="Nom de fichier suggéré")


# === ANALYZE COMPLETE ===

class AnalyzeCompleteRequest(BaseModel):
    """Analyse complète (logo + site)"""
    logo_file: Optional[str] = Field(None, description="Path ou URL du logo")
    website_url: Optional[HttpUrl] = None


class AnalyzeCompleteResponse(BaseModel):
    """Résultat de l'analyse complète"""
    brand_dna: BrandDNA
    scrape_data: Optional[ScrapeWebsiteResponse] = None
    colors_from_logo: Optional[ColorPalette] = None
    colors_from_website: Optional[ColorPalette] = None


# === HEALTH CHECK ===

class HealthCheckResponse(BaseModel):
    """Réponse du health check"""
    status: Literal["healthy", "unhealthy"]
    ai_provider: Literal["groq", "mistral"]
    has_ai_key: bool
    version: str = "0.1.0"
