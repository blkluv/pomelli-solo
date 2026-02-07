"""
Service d'IA pour génération de contenu.
Supporte Groq (gratuit) et Mistral AI.
"""

import os
from typing import List, Optional, Dict, Any
from config import settings
from models.schemas import (
    BrandDNA, GeneratedVariation, CarouselSlide,
    Tone, Sector, ContentType
)


class AIService:
    """Service de génération de contenu avec IA"""

    def __init__(self):
        self.provider = settings.AI_PROVIDER

        if self.provider == "groq":
            try:
                from groq import Groq
                self.client = Groq(api_key=settings.GROQ_API_KEY)
                self.model = settings.GROQ_MODEL
            except ImportError:
                raise ImportError("Groq package not installed. Run: pip install groq")

        elif self.provider == "mistral":
            try:
                from mistralai import Mistral
                self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
                self.model = settings.MISTRAL_MODEL
            except ImportError:
                raise ImportError("Mistral package not installed. Run: pip install mistralai")

        else:
            raise ValueError(f"Unknown AI provider: {self.provider}")

    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """
        Appel générique au LLM (Groq ou Mistral).
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        if self.provider == "groq":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048
            )
            return response.choices[0].message.content

        elif self.provider == "mistral":
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048
            )
            return response.choices[0].message.content

    # === GENERATION DE POSTS ===

    def generate_linkedin_post(
        self,
        topic: str,
        brand_dna: Optional[BrandDNA] = None,
        tone: Optional[Tone] = None,
        sector: Optional[Sector] = None,
        num_variations: int = 3
    ) -> List[GeneratedVariation]:
        """
        Génère plusieurs variations de posts LinkedIn.
        """
        # Construire le contexte Brand DNA
        brand_context = ""
        if brand_dna:
            tone = tone or brand_dna.tone
            sector = sector or brand_dna.sector
            brand_context = f"""
BRAND DNA:
- Ton: {tone.value}
- Secteur: {sector.value}
- Valeurs: {', '.join(brand_dna.values) if brand_dna.values else 'Non spécifiées'}
- Mots-clés: {', '.join(brand_dna.keywords) if brand_dna.keywords else 'Non spécifiés'}
- Audience: {brand_dna.target_audience or 'Générale'}
- Angle unique: {brand_dna.unique_angle or 'Non spécifié'}
"""
        else:
            tone = tone or Tone.PROFESSIONNEL
            sector = sector or Sector.AUTRE
            brand_context = f"""
BRAND DNA:
- Ton: {tone.value}
- Secteur: {sector.value}
"""

        system_prompt = f"""Tu es un expert en personal branding LinkedIn pour solopreneurs.

{brand_context}

RÈGLES STRICTES:
1. Format LinkedIn viral (hook + développement + CTA)
2. Hook percutant en 1ère ligne (max 10 mots)
3. Retours à la ligne fréquents (lisibilité mobile)
4. Ton {tone.value} mais toujours authentique
5. Pas de bullshit corporate
6. Call-to-action clair
7. 2-5 hashtags pertinents max
8. Longueur: 800-1200 caractères

STRUCTURE:
[Hook percutant]

[Développement en 3-5 paragraphes courts]

[CTA clair]

[Hashtags]
"""

        user_prompt = f"""Génère {num_variations} variations de posts LinkedIn sur le sujet:

"{topic}"

Retourne UNIQUEMENT les {num_variations} posts, séparés par "---VARIATION---"
Format pour chaque post:
HOOK: [hook]
POST:
[contenu complet du post]
HASHTAGS: [hashtags séparés par des espaces]
"""

        # Appel LLM
        response = self._call_llm(system_prompt, user_prompt, temperature=0.8)

        # Parser les variations
        variations = []
        raw_variations = response.split("---VARIATION---")

        for raw in raw_variations[:num_variations]:
            raw = raw.strip()
            if not raw:
                continue

            # Extraire hook, post, hashtags
            hook = ""
            post_text = ""
            hashtags = []

            lines = raw.split("\n")
            current_section = None

            for line in lines:
                line_stripped = line.strip()

                if line_stripped.startswith("HOOK:"):
                    hook = line_stripped.replace("HOOK:", "").strip()
                    current_section = "hook"
                elif line_stripped.startswith("POST:"):
                    current_section = "post"
                elif line_stripped.startswith("HASHTAGS:"):
                    hashtags_raw = line_stripped.replace("HASHTAGS:", "").strip()
                    hashtags = [tag.strip() for tag in hashtags_raw.split() if tag.strip()]
                    current_section = "hashtags"
                elif current_section == "post":
                    post_text += line + "\n"

            post_text = post_text.strip()

            # Extraire CTA (dernière phrase avant hashtags)
            cta = None
            if post_text:
                paragraphs = [p.strip() for p in post_text.split("\n\n") if p.strip()]
                if paragraphs:
                    last_para = paragraphs[-1]
                    if any(keyword in last_para.lower() for keyword in ["?", "comment", "partage", "avis", "expérience", "raconte"]):
                        cta = last_para

            variations.append(GeneratedVariation(
                text=post_text,
                hook=hook or None,
                cta=cta,
                hashtags=hashtags,
                metadata={"topic": topic, "tone": tone.value, "sector": sector.value}
            ))

        return variations if variations else [
            GeneratedVariation(
                text=response,
                hook=None,
                cta=None,
                hashtags=[],
                metadata={"topic": topic}
            )
        ]

    # === GENERATION DE CAROUSELS ===

    def generate_linkedin_carousel(
        self,
        topic: str,
        brand_dna: Optional[BrandDNA] = None,
        num_slides: int = 5,
        tone: Optional[Tone] = None
    ) -> Dict[str, Any]:
        """
        Génère un carousel LinkedIn (structure texte).
        """
        tone = tone or (brand_dna.tone if brand_dna else Tone.PROFESSIONNEL)
        sector = brand_dna.sector if brand_dna else Sector.AUTRE

        brand_context = ""
        if brand_dna:
            brand_context = f"""
BRAND DNA:
- Ton: {tone.value}
- Secteur: {sector.value}
- Valeurs: {', '.join(brand_dna.values) if brand_dna.values else 'Non spécifiées'}
"""

        system_prompt = f"""Tu es un expert en création de carousels LinkedIn viraux.

{brand_context}

RÈGLES STRICTES:
1. Carousel de {num_slides} slides (Cover + {num_slides - 1} slides de contenu)
2. Chaque slide: TITRE (max 60 caractères) + CONTENU (max 300 caractères)
3. Ton {tone.value}
4. Progressif et pédagogique
5. Slide 1 = Cover accrocheuse
6. Dernière slide = CTA

STRUCTURE:
Slide 1 (Cover): Titre accrocheur + promesse
Slides 2-{num_slides - 1}: Contenu éducatif
Slide {num_slides}: Récap + CTA
"""

        user_prompt = f"""Génère un carousel de {num_slides} slides sur:

"{topic}"

Retourne au format:
TITRE_CAROUSEL: [titre global]
COVER: [texte de la slide cover]

SLIDE_2_TITRE: [titre]
SLIDE_2_CONTENU: [contenu]

SLIDE_3_TITRE: [titre]
SLIDE_3_CONTENU: [contenu]

...
"""

        response = self._call_llm(system_prompt, user_prompt, temperature=0.75)

        # Parser les slides
        lines = response.split("\n")
        carousel_title = ""
        cover_text = ""
        slides = []

        current_slide = {}
        for line in lines:
            line_stripped = line.strip()

            if line_stripped.startswith("TITRE_CAROUSEL:"):
                carousel_title = line_stripped.replace("TITRE_CAROUSEL:", "").strip()
            elif line_stripped.startswith("COVER:"):
                cover_text = line_stripped.replace("COVER:", "").strip()
            elif line_stripped.startswith("SLIDE_") and "_TITRE:" in line_stripped:
                if current_slide:
                    slides.append(current_slide)
                slide_num = int(line_stripped.split("_")[1])
                current_slide = {
                    "slide_number": slide_num,
                    "title": line_stripped.split("_TITRE:")[1].strip(),
                    "content": "",
                    "visual_hint": None
                }
            elif line_stripped.startswith("SLIDE_") and "_CONTENU:" in line_stripped:
                if current_slide:
                    current_slide["content"] = line_stripped.split("_CONTENU:")[1].strip()

        if current_slide:
            slides.append(current_slide)

        # Convertir en CarouselSlide
        carousel_slides = [
            CarouselSlide(
                slide_number=s["slide_number"],
                title=s["title"],
                content=s["content"],
                visual_hint=s.get("visual_hint")
            )
            for s in slides
        ]

        return {
            "title": carousel_title or topic,
            "slides": carousel_slides,
            "cover_text": cover_text,
            "metadata": {"topic": topic, "tone": tone.value}
        }

    # === ANALYSE DE SITE WEB ===

    def analyze_website_content(
        self,
        website_text: str,
        website_title: Optional[str] = None,
        website_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyse le contenu d'un site pour détecter ton, secteur, mots-clés.
        """
        system_prompt = """Tu es un expert en analyse de personal branding.

À partir du contenu d'un site web, tu dois détecter:
1. TON de communication (professionnel, inspirant, pédagogique, provocateur, authentique)
2. SECTEUR d'activité (coaching, consulting, design, développement, marketing, santé, finance, e-commerce, éducation, autre)
3. 5-10 MOTS-CLÉS principaux
4. AUDIENCE cible (en 1 phrase)
5. ANGLE UNIQUE (ce qui différencie, en 1 phrase)

Retourne au format:
TON: [ton]
SECTEUR: [secteur]
KEYWORDS: [mot1, mot2, mot3, ...]
AUDIENCE: [description audience]
ANGLE: [angle unique]
"""

        user_prompt = f"""Analyse ce site web:

TITRE: {website_title or 'Non disponible'}
DESCRIPTION: {website_description or 'Non disponible'}

CONTENU:
{website_text[:3000]}

Détecte le ton, secteur, mots-clés, audience, angle unique.
"""

        response = self._call_llm(system_prompt, user_prompt, temperature=0.3)

        # Parser la réponse
        result = {
            "detected_tone": None,
            "detected_sector": None,
            "suggested_keywords": [],
            "target_audience": None,
            "unique_angle": None
        }

        lines = response.split("\n")
        for line in lines:
            line_stripped = line.strip()

            if line_stripped.startswith("TON:"):
                tone_str = line_stripped.replace("TON:", "").strip().lower()
                try:
                    result["detected_tone"] = Tone(tone_str)
                except ValueError:
                    result["detected_tone"] = Tone.PROFESSIONNEL

            elif line_stripped.startswith("SECTEUR:"):
                sector_str = line_stripped.replace("SECTEUR:", "").strip().lower()
                try:
                    result["detected_sector"] = Sector(sector_str)
                except ValueError:
                    result["detected_sector"] = Sector.AUTRE

            elif line_stripped.startswith("KEYWORDS:"):
                keywords_raw = line_stripped.replace("KEYWORDS:", "").strip()
                result["suggested_keywords"] = [
                    kw.strip() for kw in keywords_raw.split(",") if kw.strip()
                ][:10]

            elif line_stripped.startswith("AUDIENCE:"):
                result["target_audience"] = line_stripped.replace("AUDIENCE:", "").strip()

            elif line_stripped.startswith("ANGLE:"):
                result["unique_angle"] = line_stripped.replace("ANGLE:", "").strip()

        return result


# Instance globale
ai_service = AIService()
