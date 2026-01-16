"""Buscador de Nichos: Transforma nombres de nichos en URLs para scraping."""
import asyncio
import logging
import urllib.parse
from typing import List

# TODO: Reemplazar con cliente real (Google Custom Search, Serper, etc)
# Por ahora simularemos búsqueda usando Google Search standard (con riesgo de bloqueo)
# o simplemente generaremos URLs de prueba para validar el flujo.
from src.config import get_config
from src.models import TareaURL
from redis import asyncio as aioredis
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# User-Agent rotativo básico para búsqueda
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

class NicheSearcher:
    """Busca URLs relevantes para un nicho dado."""

    def __init__(self):
        self.cfg = get_config()
        self.redis = aioredis.from_url(self.cfg.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def close(self):
        await self.redis.close()

    async def search_and_enqueue(self, nicho: str, limit: int = 20):
        """Busca URLs para un nicho y las encola en Redis."""
        logger.info(f"Buscando nicho: {nicho}")
        
        # 1. Obtener URLs (Simulado/Real)
        urls = await self._search_google_simulated(nicho, limit)
        
        count = 0
        for url in urls:
            # 2. Filtrar duplicados (bloom filter simplificado con Redis SET)
            if await self._is_duplicate(url):
                continue
                
            # 3. Encolar
            tarea = TareaURL(url=url, nivel=0, nicho=nicho)
            await self.redis.rpush("scraping_queue", tarea.model_dump_json())
            
            # Marcar como visto
            await self._mark_seen(url)
            count += 1
            
        logger.info(f"Encoladas {count} nuevas URLs para nicho '{nicho}'")
        return count

    async def _search_google_simulated(self, query: str, limit: int) -> List[str]:
        """
        Simula búsqueda. En producción usar Google Custom Search API.
        Aquí intentamos hacer scraping básico de SERP o devolvemos mocks si falla.
        """
        # MOCK TEMPORAL PARA VALIDAR FLUJO SIN API KEY DE GOOGLE
        # En producción: Implementar Google Custom Search JSON API
        logger.warning("Usando MOCK de búsqueda (Implementar API Real)")
        
        # Generar URLs ficticias pero válidas para probar el worker
        if "turismo" in query.lower():
            return [
                "https://www.turismodecanarias.com",
                "https://www.grancanaria.com",
                "https://www.webtenerife.com",
            ]
        elif "ecologistas" in query.lower():
            return [
                "https://www.benmagec.org",
                "https://www.wwf.es",
            ]
        
        return []

    async def _is_duplicate(self, url: str) -> bool:
        """Verifica si la URL ya fue procesada."""
        # Check simple en Redis (Set de dominios vistos)
        domain = urllib.parse.urlparse(url).netloc
        return await self.redis.sismember("processed_domains", domain)

    async def _mark_seen(self, url: str):
        """Marca dominio como visto."""
        domain = urllib.parse.urlparse(url).netloc
        await self.redis.sadd("processed_domains", domain)


# CLI para probar
if __name__ == "__main__":
    async def main():
        searcher = NicheSearcher()
        await searcher.search_and_enqueue("Asociaciones ecologistas Canarias")
        await searcher.close()
    
    asyncio.run(main())
