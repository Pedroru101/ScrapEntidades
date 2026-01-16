"""Script de stress test con 50 URLs dummy."""
import asyncio
import json
import time
from pathlib import Path

import redis.asyncio as redis

# URLs de prueba (sitios públicos de empresas chilenas)
DUMMY_URLS = [
    "https://www.sercotec.cl",
    "https://www.corfo.cl",
    "https://www.sii.cl",
    "https://www.chilecompra.cl",
    "https://www.bcentral.cl",
    "https://www.mineduc.cl",
    "https://www.minsalud.cl",
    "https://www.mop.cl",
    "https://www.minvu.cl",
    "https://www.economia.gob.cl",
]


async def load_dummy_urls(redis_url: str, count: int = 50):
    """Carga URLs dummy a la cola de Redis."""
    client = redis.from_url(redis_url)
    
    # Limpiar cola existente
    await client.delete("scraping_queue")
    
    for i in range(count):
        url = DUMMY_URLS[i % len(DUMMY_URLS)]
        task = {
            "url": url,
            "nicho": "gobierno",
            "prioridad": 1,
            "nivel": 0,
            "reintentos": 0
        }
        await client.rpush("scraping_queue", json.dumps(task))
    
    queue_size = await client.llen("scraping_queue")
    print(f"[OK] Cargadas {queue_size} URLs a la cola")
    
    await client.close()


async def monitor_progress(redis_url: str, duration_seconds: int = 300):
    """Monitorea el progreso del procesamiento."""
    client = redis.from_url(redis_url)
    start_time = time.time()
    initial_size = await client.llen("scraping_queue")
    
    print(f"\n=== Iniciando monitoreo ({duration_seconds}s) ===")
    print(f"Cola inicial: {initial_size} tareas")
    
    while time.time() - start_time < duration_seconds:
        current_size = await client.llen("scraping_queue")
        processed = initial_size - current_size
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        
        print(f"[{elapsed:.0f}s] Cola: {current_size} | Procesados: {processed} | Rate: {rate:.2f}/s")
        
        if current_size == 0:
            print("\n[DONE] Cola vacía!")
            break
        
        await asyncio.sleep(10)
    
    await client.close()
    
    total_time = time.time() - start_time
    print(f"\n=== Resumen ===")
    print(f"Tiempo total: {total_time:.1f}s")
    print(f"Procesados: {processed}")
    print(f"Rate promedio: {processed/total_time:.2f} URLs/s")


async def main():
    """Ejecuta stress test."""
    import os
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    print("=== Stress Test: 50 URLs con 12 workers ===\n")
    
    # Cargar URLs
    await load_dummy_urls(redis_url, count=50)
    
    # Monitorear (el docker-compose debe estar corriendo)
    await monitor_progress(redis_url, duration_seconds=300)


if __name__ == "__main__":
    asyncio.run(main())
