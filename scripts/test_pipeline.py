"""Script de prueba rápida del pipeline con URLs reales de Canarias."""
import asyncio
import os
import json

# Configurar variables de entorno para test
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")
# OPENROUTER_API_KEY debe estar configurada en .env real

from dotenv import load_dotenv
load_dotenv()

from src.scraper import Scraper
from src.ai_analyzer import AIAnalyzer
from src.scoring import Scorer


# URLs de prueba - organizaciones reales de Canarias
TEST_URLS = [
    # Instituciones públicas
    ("https://www.gobiernodecanarias.org", "Gobierno Canarias"),
    ("https://www.cabildodetenerife.es", "Cabildo Tenerife"),
    ("https://www.grancanaria.com", "Cabildo Gran Canaria"),
    
    # Asociaciones
    ("https://www.benmagec.org", "Ben Magec - Ecologistas"),
    
    # Empresas turismo
    ("https://www.holaislascanarias.com", "Turismo Canarias"),
]


async def test_single_url(url: str, name: str, scraper: Scraper, ai: AIAnalyzer, scorer: Scorer):
    """Prueba el pipeline completo con una URL."""
    print(f"\n{'='*60}")
    print(f"PROBANDO: {name}")
    print(f"URL: {url}")
    print("="*60)
    
    try:
        # 1. Simular scraping (sin Tor para test rápido)
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                html = await response.text()
        
        # 2. Parsear
        scraped = scraper.parse(html, url)
        print(f"\n[SCRAPER] Datos extraídos:")
        print(f"  - Título: {scraped['meta'].get('title', 'N/A')[:60]}...")
        print(f"  - Emails: {scraped['emails'][:3]}")
        print(f"  - Teléfonos: {scraped['phones'][:3]}")
        print(f"  - RRSS: {list(scraped['social'].keys())}")
        
        # 3. Análisis IA (solo si hay API key)
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if api_key and not api_key.startswith("sk-or-v1-..."):
            ai_result = await ai.analyze(scraped["text_content"], scraped["meta"])
            
            if ai_result:
                print(f"\n[IA] Análisis:")
                print(f"  - Tipo: {ai_result.get('tipo_entidad', 'N/A')}")
                print(f"  - Sector: {ai_result.get('sector', 'N/A')}")
                print(f"  - Ubicación: {ai_result.get('ubicacion', 'N/A')}")
                print(f"  - Tamaño: {ai_result.get('tamaño_estimado', 'N/A')}")
                print(f"  - Oportunidad: {ai_result.get('oportunidad_comercial', 'N/A')}")
                print(f"  - Pain Points: {ai_result.get('pain_points', [])[:3]}")
            else:
                ai_result = None
                print("\n[IA] No se pudo analizar")
        else:
            ai_result = None
            print("\n[IA] Saltado (no hay OPENROUTER_API_KEY configurada)")
        
        # 4. Scoring
        score = scorer.calculate(scraped, ai_result)
        tier = scorer.get_tier(score)
        tier_desc = scorer.get_tier_description(tier)
        
        print(f"\n[SCORING]")
        print(f"  - Score: {score}/10")
        print(f"  - Tier: {tier}")
        print(f"  - Acción: {tier_desc}")
        
        return {
            "url": url,
            "name": name,
            "score": score,
            "tier": tier,
            "success": True
        }
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        return {
            "url": url,
            "name": name,
            "score": 0,
            "tier": "X",
            "success": False,
            "error": str(e)
        }


async def main():
    """Ejecuta prueba con URLs de ejemplo."""
    print("\n" + "="*60)
    print("  PRUEBA DEL SISTEMA DE SCRAPING - GABINETE DE PRENSA")
    print("="*60)
    
    scraper = Scraper()
    ai = AIAnalyzer()
    scorer = Scorer()
    
    results = []
    
    for url, name in TEST_URLS[:3]:  # Solo 3 para prueba rápida
        result = await test_single_url(url, name, scraper, ai, scorer)
        results.append(result)
        await asyncio.sleep(2)  # Pausa entre requests
    
    # Resumen
    print("\n" + "="*60)
    print("  RESUMEN DE RESULTADOS")
    print("="*60)
    print(f"{'Nombre':<30} {'Score':>6} {'Tier':>5}")
    print("-"*45)
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"{r['name']:<30} {r['score']:>6.1f} {r['tier']:>5} {status}")
    
    print(f"\n[INFO] Tokens IA consumidos: {ai.get_token_count()}")


if __name__ == "__main__":
    asyncio.run(main())
