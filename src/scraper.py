"""Motor de scraping con extracción de datos estructurados."""
import re
import logging
from typing import List, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Dominios a ignorar en el descubrimiento de URLs
DOMAIN_BLACKLIST = {
    "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
    "youtube.com", "google.com", "googleapis.com", "gstatic.com",
    "cloudflare.com", "jsdelivr.net", "unpkg.com", "cdn.jsdelivr.net",
    "maps.google.com", "analytics.google.com", "fonts.googleapis.com",
}

# Regex patrones
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\+56\s?)?(?:9\s?)?\d{4}[\s-]?\d{4}")


class Scraper:
    """Extractor de datos de páginas web."""

    def __init__(self, blacklist: Set[str] = None):
        self.blacklist = blacklist or DOMAIN_BLACKLIST

    def parse(self, html: str, base_url: str) -> dict:
        """Extrae datos estructurados del HTML."""
        soup = BeautifulSoup(html, "lxml")
        
        return {
            "meta": self._extract_meta(soup),
            "emails": self._extract_emails(soup),
            "phones": self._extract_phones(soup),
            "social": self._extract_social(soup),
            "text_content": self._extract_text(soup),
            "internal_links": self._extract_internal_links(soup, base_url),
            "external_links": self._extract_external_links(soup, base_url),
        }

    def _extract_meta(self, soup: BeautifulSoup) -> dict:
        """Extrae meta tags relevantes."""
        meta = {}
        
        # Title
        title_tag = soup.find("title")
        meta["title"] = title_tag.get_text(strip=True) if title_tag else ""
        
        # Meta description
        desc_tag = soup.find("meta", attrs={"name": "description"})
        meta["description"] = desc_tag.get("content", "") if desc_tag else ""
        
        # Keywords
        kw_tag = soup.find("meta", attrs={"name": "keywords"})
        meta["keywords"] = kw_tag.get("content", "") if kw_tag else ""
        
        # OG tags
        og_title = soup.find("meta", property="og:title")
        og_desc = soup.find("meta", property="og:description")
        meta["og_title"] = og_title.get("content", "") if og_title else ""
        meta["og_description"] = og_desc.get("content", "") if og_desc else ""
        
        return meta

    def _extract_emails(self, soup: BeautifulSoup) -> List[str]:
        """Extrae emails únicos del contenido."""
        text = soup.get_text()
        emails = set(EMAIL_PATTERN.findall(text))
        
        # También buscar en hrefs mailto:
        for a in soup.find_all("a", href=True):
            if a["href"].startswith("mailto:"):
                email = a["href"].replace("mailto:", "").split("?")[0]
                emails.add(email)
        
        return list(emails)

    def _extract_phones(self, soup: BeautifulSoup) -> List[str]:
        """Extrae teléfonos del contenido."""
        text = soup.get_text()
        phones = set(PHONE_PATTERN.findall(text))
        
        # También buscar en hrefs tel:
        for a in soup.find_all("a", href=True):
            if a["href"].startswith("tel:"):
                phone = a["href"].replace("tel:", "").strip()
                phones.add(phone)
        
        return list(phones)

    def _extract_social(self, soup: BeautifulSoup) -> dict:
        """Extrae links a redes sociales."""
        social = {}
        social_domains = {
            "facebook.com": "facebook",
            "twitter.com": "twitter",
            "x.com": "twitter",
            "instagram.com": "instagram",
            "linkedin.com": "linkedin",
            "youtube.com": "youtube",
        }
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            for domain, name in social_domains.items():
                if domain in href and name not in social:
                    social[name] = href
                    break
        
        return social

    def _extract_text(self, soup: BeautifulSoup, max_chars: int = 5000) -> str:
        """Extrae texto limpio para análisis IA."""
        # Remover scripts y estilos
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        text = soup.get_text(separator=" ", strip=True)
        # Limpiar espacios múltiples
        text = re.sub(r"\s+", " ", text)
        
        return text[:max_chars]

    def _extract_internal_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extrae links internos (mismo dominio)."""
        base_domain = urlparse(base_url).netloc
        internal = set()
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            
            if parsed.netloc == base_domain and parsed.scheme in ("http", "https"):
                # Normalizar: sin fragmentos ni parámetros de tracking
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                internal.add(clean_url.rstrip("/"))
        
        return list(internal)[:50]  # Limitar cantidad

    def _extract_external_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extrae links externos (otros dominios), filtrando blacklist."""
        base_domain = urlparse(base_url).netloc
        external = set()
        
        for a in soup.find_all("a", href=True):
            href = a["href"]
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            
            if parsed.netloc and parsed.netloc != base_domain:
                # Filtrar blacklist
                if not any(bl in parsed.netloc for bl in self.blacklist):
                    external.add(f"{parsed.scheme}://{parsed.netloc}")
        
        return list(external)[:20]
