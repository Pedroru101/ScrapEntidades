"""Cliente Supabase con backup local."""
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from supabase import create_client, Client

from src.config import get_config
from src.models import Organizacion

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Cliente para operaciones CRUD en Supabase con fallback a CSV."""

    def __init__(self):
        cfg = get_config()
        self.client: Client = create_client(cfg.SUPABASE_URL, cfg.SUPABASE_KEY)
        self.backup_dir = Path("data/backup")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._backup_file: Optional[Path] = None

    async def upsert_organizacion(self, org: Organizacion) -> bool:
        """Inserta o actualiza una organización en Supabase."""
        try:
            data = org.to_supabase_dict()
            result = self.client.table("organizaciones").upsert(
                data,
                on_conflict="dominio"
            ).execute()
            
            logger.debug(f"Upsert exitoso: {org.dominio}")
            return True
            
        except Exception as e:
            logger.error(f"Error Supabase upsert {org.dominio}: {e}")
            self._save_to_backup(org)
            return False

    async def check_domain_exists(self, domain: str) -> bool:
        """Verifica si un dominio ya existe en la DB (check ligero)."""
        try:
            result = self.client.table("organizaciones").select("dominio").eq("dominio", domain).limit(1).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.warning(f"Error verificando dominio {domain}: {e}")
            return False  # Asumir que no existe para no perder oportunidades

    async def log_error(self, url: str, error_type: str, message: str):
        """Registra un error en la tabla de logs."""
        try:
            cfg = get_config()
            self.client.table("scraping_logs").insert({
                "url": url,
                "error_type": error_type,
                "message": message[:500],  # Truncar mensajes largos
                "machine_id": cfg.MACHINE_ID,
                "created_at": datetime.utcnow().isoformat(),
            }).execute()
        except Exception as e:
            logger.error(f"Error guardando log en Supabase: {e}")

    def _save_to_backup(self, org: Organizacion):
        """Guarda en CSV local si Supabase falla."""
        if self._backup_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._backup_file = self.backup_dir / f"backup_{timestamp}.csv"
        
        file_exists = self._backup_file.exists()
        
        with open(self._backup_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(org.to_supabase_dict().keys()))
            if not file_exists:
                writer.writeheader()
            writer.writerow(org.to_supabase_dict())
        
        logger.info(f"Backup local: {self._backup_file}")

    async def get_backup_count(self) -> int:
        """Retorna cantidad de registros pendientes en backup."""
        count = 0
        for csv_file in self.backup_dir.glob("backup_*.csv"):
            with open(csv_file, "r", encoding="utf-8") as f:
                count += sum(1 for _ in f) - 1  # Resta header
        return max(0, count)
