"""Worker principal del sistema de scraping."""
import asyncio
import logging
import signal
from typing import Optional
from urllib.parse import urlparse

import redis.asyncio as redis

from src.config import get_config
from src.scraper import Scraper
from src.ai_analyzer import AIAnalyzer
from src.scoring import Scorer
from src.models import Organizacion, AnalisisIA, TareaURL
from src.utils.tor_client import TorClient
from src.utils.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class Worker:
    """Worker asíncrono que procesa URLs de la cola Redis."""

    def __init__(self):
        self.cfg = get_config()
        self.running = True
        self.processed = 0
        self.errors = 0
        
        # Componentes
        self.scraper = Scraper()
        self.ai = AIAnalyzer()
        self.scorer = Scorer()
        self.tor: Optional[TorClient] = None
        self.db: Optional[SupabaseClient] = None
        self.redis: Optional[redis.Redis] = None

    async def start(self):
        """Inicia el worker."""
        # Registrar señales para apagado gracioso
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._handle_shutdown)
        
        # Inicializar conexiones
        self.tor = TorClient()
        self.db = SupabaseClient()
        self.redis = redis.from_url(self.cfg.REDIS_URL)
        
        logger.info(f"Worker iniciado [{self.cfg.MACHINE_ID}] - Max threads: {self.cfg.MAX_THREADS}")
        
        # Verificar IP inicial
        ip = await self.tor.check_ip()
        logger.info(f"IP Tor actual: {ip}")
        
        # Bucle principal
        while self.running:
            task_data = await self.redis.lpop("scraping_queue")
            
            if task_data is None:
                # Cola vacía, esperar
                await asyncio.sleep(5)
                continue
            
            try:
                tarea = TareaURL.model_validate_json(task_data)
                await self._process_url(tarea)
                self.processed += 1
                
                # Rotar IP cada 10 requests
                if self.processed % 10 == 0:
                    await self.tor.renew_identity()
                    
            except Exception as e:
                logger.error(f"Error procesando tarea: {e}")
                self.errors += 1
        
        await self._cleanup()

    async def _process_url(self, tarea: TareaURL):
        """Pipeline completo para una URL."""
        url = str(tarea.url)
        domain = urlparse(url).netloc
        
        logger.info(f"Procesando: {url}")
        
        # 1. Verificar si ya existe
        if await self.db.check_domain_exists(domain):
            logger.debug(f"Dominio ya existe: {domain}")
            return
        
        # 2. Scrape
        try:
            html = await self.tor.get(url)
        except Exception as e:
            await self.db.log_error(url, "scrape_error", str(e))
            return
        
        scraped = self.scraper.parse(html, url)
        
        # 3. Análisis IA
        ai_result = await self.ai.analyze(
            scraped["text_content"],
            scraped["meta"]
        )
        
        # 4. Scoring
        score = self.scorer.calculate(scraped, ai_result)
        tier = self.scorer.get_tier(score)
        
        # 5. Construir modelo
        org = Organizacion(
            url=url,
            dominio=domain,
            titulo=scraped["meta"].get("title"),
            descripcion=scraped["meta"].get("description"),
            emails=scraped["emails"],
            telefonos=scraped["phones"],
            redes_sociales=scraped["social"],
            analisis=AnalisisIA(**ai_result) if ai_result else None,
            score=score,
            tier=tier,
            machine_id=self.cfg.MACHINE_ID,
            nicho_origen=tarea.nicho,
        )
        
        # 6. Guardar en Supabase
        await self.db.upsert_organizacion(org)
        
        # 7. Encolar URLs externas descubiertas (nivel 1)
        if tarea.nivel == 0:
            for ext_url in scraped["external_links"][:5]:
                nueva_tarea = TareaURL(url=ext_url, nivel=1, nicho=tarea.nicho)
                await self.redis.rpush("scraping_queue", nueva_tarea.model_dump_json())

    def _handle_shutdown(self):
        """Maneja señales de apagado."""
        logger.info("Iniciando apagado gracioso...")
        self.running = False

    async def _cleanup(self):
        """Limpia conexiones."""
        if self.tor:
            await self.tor.close()
        if self.redis:
            await self.redis.close()
        
        logger.info(f"Worker finalizado. Procesados: {self.processed}, Errores: {self.errors}")
        logger.info(f"Tokens IA consumidos: {self.ai.get_token_count()}")
