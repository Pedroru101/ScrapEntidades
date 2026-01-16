"""Punto de entrada principal del sistema."""
import asyncio
import csv
import logging
from pathlib import Path

import redis.asyncio as redis

from src.config import get_config
from src.worker import Worker
from src.models import TareaURL

logger = logging.getLogger(__name__)


async def load_initial_urls(redis_client: redis.Redis, cfg) -> int:
    """Carga URLs iniciales desde CSV a Redis si la cola está vacía."""
    queue_size = await redis_client.llen("scraping_queue")
    
    if queue_size > 0:
        logger.info(f"Cola existente con {queue_size} tareas")
        return queue_size
    
    # Buscar archivo de la máquina
    csv_path = Path(f"data/urls_iniciales/{cfg.MACHINE_ID}.csv")
    
    if not csv_path.exists():
        # Fallback a template
        csv_path = Path("data/urls_iniciales/template.csv")
    
    if not csv_path.exists():
        logger.warning("No se encontró archivo de URLs iniciales")
        return 0
    
    loaded = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tarea = TareaURL(
                url=row["url"],
                nicho=row.get("nicho"),
                prioridad=int(row.get("prioridad", 1)),
                nivel=0,
            )
            await redis_client.rpush("scraping_queue", tarea.model_dump_json())
            loaded += 1
    
    logger.info(f"Cargadas {loaded} URLs iniciales desde {csv_path}")
    return loaded


async def run_workers(num_workers: int):
    """Ejecuta N workers en paralelo."""
    workers = [Worker() for _ in range(num_workers)]
    tasks = [asyncio.create_task(w.start()) for w in workers]
    
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Workers cancelados")


async def main():
    """Función principal."""
    cfg = get_config()
    
    logger.info("=== Sistema de Scraping Distribuido ===")
    logger.info(f"Machine ID: {cfg.MACHINE_ID}")
    logger.info(f"Max Threads: {cfg.MAX_THREADS}")
    
    # Conectar a Redis
    redis_client = redis.from_url(cfg.REDIS_URL)
    
    try:
        await redis_client.ping()
        logger.info("Conexión Redis OK")
    except Exception as e:
        logger.error(f"Error conectando a Redis: {e}")
        return
    
    # Cargar URLs iniciales
    await load_initial_urls(redis_client, cfg)
    await redis_client.close()
    
    # Ejecutar workers
    await run_workers(cfg.MAX_THREADS)


if __name__ == "__main__":
    asyncio.run(main())
