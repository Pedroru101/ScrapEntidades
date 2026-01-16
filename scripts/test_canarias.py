"""Script de prueba: Extracción básica para Canarias (Sin IA)."""
import asyncio
import os
import logging
from urllib.parse import urlparse

# Mocks para dependencias
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

from src.scraper import Scraper
from src.models import Organizacion

# URLs de prueba - Mix de Canarias y península para validar filtro
TEST_URLS = [
    "https://www.gobiernodecanarias.org",   # Debería pasar
    "https://www.cabildodetenerife.es",     # Debería pasar
    "https://www.benmagec.org",             # Debería pasar
    "https://www.madrid.es",                # Debería descartarse
    "https://www.bcn.cl",                   # Debería descartarse (Chile)
    "https://holaislascanarias.com",        # Debería pasar
]

# Keywords de filtro (misma lógica que worker.py)
CANARIAS_KEYWORDS = [
    "canarias", "tenerife", "gran canaria", "lanzarote", "fuerteventura", 
    "la palma", "la gomera", "el hierro", "las palmas", "santa cruz"
]

async def test_extraction(url: str, scraper: Scraper):
    """Simula el proceso del worker simplificado."""
    print(f"\n{'='*50}")
    print(f"PROCESANDO: {url}")
    
    try:
        # 1. Scraping (simulado con aiohttp directo)
        import aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=10) as response:
                    html = await response.text()
            except Exception as e:
                print(f"[ERROR] No se pudo conectar: {e}")
                return

        # 2. Parse
        scraped = scraper.parse(html, url)
        
        # 3. FILTRO
        text_content = scraped["text_content"].lower()
        meta_content = str(scraped["meta"]).lower()
        
        is_canarias = any(kw in text_content for kw in CANARIAS_KEYWORDS) or \
                      any(kw in meta_content for kw in CANARIAS_KEYWORDS)
        
        status = "✅ ACEPTADO (Canarias)" if is_canarias else "❌ DESCARTADO (No es Canarias)"
        print(f"RESULTADO FILTRO: {status}")
        
        if is_canarias:
            print(f"DATOS EXTRAÍDOS:")
            print(f"  - Título: {scraped['meta'].get('title')}")
            print(f"  - Emails: {scraped['emails']}")
            print(f"  - Teléfonos: {scraped['phones']}")
            print(f"  - RRSS: {list(scraped['social'].keys())}")
            
    except Exception as e:
        print(f"[ERROR] Fallo en proceso: {e}")

async def main():
    print("=== TEST DE FILTRO GEOGRÁFICO CANARIAS ===")
    scraper = Scraper()
    
    for url in TEST_URLS:
        await test_extraction(url, scraper)
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
