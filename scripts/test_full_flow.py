"""Prueba de flujo completo: Scraping + IA + Output JSON (Sin Supabase)."""
import asyncio
import json
import os
import sys
import ssl

# Agregar src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import aiohttp
from src.scraper import Scraper
from src.ai_analyzer import AIAnalyzer

# URLs REALES de organizaciones en Canarias
TEST_URLS = [
    ("https://www.gobiernodecanarias.org", "Gobierno de Canarias"),
    ("https://holaislascanarias.com", "Turismo Canarias"),
    ("https://www.fedac.org", "FEDAC Gran Canaria"),
]

# Keywords para filtro Canarias
CANARIAS_KEYWORDS = [
    "canarias", "tenerife", "gran canaria", "lanzarote", "fuerteventura", 
    "la palma", "la gomera", "el hierro", "las palmas", "santa cruz"
]


async def test_full_flow():
    """Ejecuta el flujo completo con URLs reales."""
    print("\n" + "="*70)
    print("  PRUEBA DE FLUJO COMPLETO - SCRAPING + IA")
    print("="*70)
    
    scraper = Scraper()
    ai = AIAnalyzer()
    
    results = []
    
    # Desactivar verificación SSL para webs gubernamentales
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for url, name in TEST_URLS:
            print(f"\n{'='*60}")
            print(f"PROCESANDO: {name}")
            print(f"URL: {url}")
            print("="*60)
            
            try:
                # 1. SCRAPING
                print("\n[1/3] Scraping...")
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as response:
                    html = await response.text()
                
                scraped = scraper.parse(html, url)
                print(f"  ✓ Título: {scraped['meta'].get('title', 'N/A')[:50]}...")
                print(f"  ✓ Emails: {scraped['emails'][:3]}")
                print(f"  ✓ Teléfonos: {scraped['phones'][:3]}")
                print(f"  ✓ RRSS: {list(scraped['social'].keys())}")
                
                # 2. FILTRO CANARIAS
                print("\n[2/3] Filtro geográfico...")
                text_lower = scraped["text_content"].lower()
                meta_lower = str(scraped["meta"]).lower()
                
                is_canarias = any(kw in text_lower or kw in meta_lower for kw in CANARIAS_KEYWORDS)
                
                if not is_canarias:
                    print(f"  ✗ DESCARTADO (No es Canarias)")
                    continue
                
                print(f"  ✓ ACEPTADO (Es Canarias)")
                
                # 3. ANÁLISIS IA
                print("\n[3/3] Análisis IA (OpenRouter)...")
                ai_result = await ai.analyze(scraped["text_content"], scraped["meta"])
                
                if ai_result:
                    print(f"  ✓ Análisis completado")
                    
                    # Mostrar conocimiento profundo
                    if "conocimiento_profundo" in ai_result:
                        kp = ai_result["conocimiento_profundo"]
                        print(f"\n  CONOCIMIENTO PROFUNDO:")
                        print(f"    Sector: {kp.get('sector', 'N/A')}")
                        print(f"    Actividades: {kp.get('actividades_principales', [])[:2]}")
                        print(f"    Retos: {kp.get('retos_objetivos', [])[:2]}")
                        print(f"    Financiación: {kp.get('financiacion', [])[:2]}")
                    
                    if "oportunidades_detectadas" in ai_result:
                        op = ai_result["oportunidades_detectadas"]
                        print(f"\n  OPORTUNIDADES:")
                        print(f"    Encajan: {op.get('productos_encajan', [])}")
                        print(f"    No encajan: {op.get('productos_no_encajan', [])}")
                else:
                    print(f"  ✗ Fallo en análisis IA")
                    ai_result = {}
                
                # Guardar resultado
                results.append({
                    "url": url,
                    "nombre": name,
                    "titulo": scraped["meta"].get("title"),
                    "emails": scraped["emails"],
                    "telefonos": scraped["phones"],
                    "redes_sociales": scraped["social"],
                    "analisis_ia": ai_result,
                })
                
            except Exception as e:
                print(f"\n  ✗ ERROR: {type(e).__name__}: {e}")
                continue
    
    # Guardar resultados en JSON
    output_path = "data/resultados/test_output.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"  RESUMEN")
    print(f"{'='*70}")
    print(f"  URLs procesadas: {len(TEST_URLS)}")
    print(f"  Resultados guardados: {len(results)}")
    print(f"  Output: {output_path}")
    print(f"  Tokens IA: {ai.get_token_count()}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    asyncio.run(test_full_flow())
