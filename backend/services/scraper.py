"""
Service de scraping de sites web.
Extrait titre, description, meta tags, contenu principal.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse


class WebScraper:
    """Scraper de sites web pour analyse Brand DNA"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape un site web et extrait les infos pertinentes.

        Returns:
            dict avec title, description, text, images, etc.
        """
        try:
            # Faire la requête
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            # Parser HTML
            soup = BeautifulSoup(response.content, "lxml")

            # Extraire infos
            result = {
                "url": url,
                "title": self._extract_title(soup),
                "description": self._extract_description(soup),
                "text": self._extract_main_text(soup),
                "images": self._extract_images(soup, url),
                "colors": self._extract_colors_from_css(soup),
                "meta": self._extract_meta_tags(soup)
            }

            return result

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to scrape {url}: {str(e)}")

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait le titre de la page"""
        # Essayer balise <title>
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text(strip=True)

        # Essayer meta og:title
        og_title = soup.find("meta", property="og:title")
        if og_title:
            return og_title.get("content", "").strip()

        # Essayer premier <h1>
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return None

    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extrait la description"""
        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            return meta_desc.get("content", "").strip()

        # Meta og:description
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            return og_desc.get("content", "").strip()

        # Premier paragraphe
        first_p = soup.find("p")
        if first_p:
            text = first_p.get_text(strip=True)
            return text[:300] if len(text) > 300 else text

        return None

    def _extract_main_text(self, soup: BeautifulSoup) -> str:
        """
        Extrait le texte principal de la page.
        Ignore nav, footer, scripts, styles.
        """
        # Supprimer éléments non pertinents
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Extraire texte des sections principales
        main_content = soup.find("main") or soup.find("article") or soup.find("body")

        if main_content:
            text = main_content.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)

        # Nettoyer espaces multiples
        text = " ".join(text.split())

        # Limiter à 5000 caractères
        return text[:5000]

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> list:
        """
        Extrait les URLs des images principales.
        """
        images = []

        # Logo (chercher dans header ou meta)
        logo_selectors = [
            soup.find("meta", property="og:image"),
            soup.find("link", rel="icon"),
            soup.find("link", rel="apple-touch-icon"),
            soup.find("img", class_=lambda x: x and "logo" in x.lower()),
        ]

        for selector in logo_selectors:
            if selector:
                img_url = selector.get("content") or selector.get("href") or selector.get("src")
                if img_url:
                    full_url = urljoin(base_url, img_url)
                    if full_url not in images:
                        images.append(full_url)

        # Autres images
        for img in soup.find_all("img", limit=5):
            src = img.get("src")
            if src:
                full_url = urljoin(base_url, src)
                if full_url not in images:
                    images.append(full_url)

        return images[:10]

    def _extract_colors_from_css(self, soup: BeautifulSoup) -> list:
        """
        Tente d'extraire des couleurs depuis les styles inline/CSS.
        (Basique, ne remplace pas l'extraction d'image)
        """
        colors = []

        # Chercher couleurs dans attributs style
        for element in soup.find_all(style=True):
            style = element["style"]
            # Regex basique pour hex colors
            import re
            hex_colors = re.findall(r"#[0-9a-fA-F]{6}", style)
            colors.extend(hex_colors)

        # Limiter et dédupliquer
        return list(set(colors))[:10]

    def _extract_meta_tags(self, soup: BeautifulSoup) -> dict:
        """Extrait les meta tags utiles"""
        meta = {}

        # Keywords
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag:
            meta["keywords"] = keywords_tag.get("content", "")

        # Author
        author_tag = soup.find("meta", attrs={"name": "author"})
        if author_tag:
            meta["author"] = author_tag.get("content", "")

        # OG tags
        og_tags = soup.find_all("meta", property=lambda x: x and x.startswith("og:"))
        for tag in og_tags:
            prop = tag.get("property", "").replace("og:", "")
            meta[f"og_{prop}"] = tag.get("content", "")

        return meta


# Instance globale
scraper = WebScraper()
