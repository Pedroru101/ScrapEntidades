"""Configuración centralizada del sistema."""
import os
import sys
import logging
from functools import lru_cache


class ConfigError(Exception):
    """Error de configuración crítica."""


class Config:
    """Singleton de configuración con validación FAIL FAST."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config()
        return cls._instance

    def _init_config(self):
        """Carga y valida variables de entorno."""
        # Variables críticas (falla si no existen)
        self.SUPABASE_URL = self._require("SUPABASE_URL")
        self.SUPABASE_KEY = self._require("SUPABASE_KEY")
        
        # OpenRouter es opcional para pruebas sin IA
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
        
        # Variables con defaults
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.MACHINE_ID = os.getenv("MACHINE_ID", "local")
        self.MAX_THREADS = int(os.getenv("MAX_THREADS", "12"))
        
        # Tor config
        self.TOR_SOCKS_PORT = int(os.getenv("TOR_SOCKS_PORT", "9050"))
        self.TOR_CONTROL_PORT = int(os.getenv("TOR_CONTROL_PORT", "9051"))
        
        # Timeouts
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.AI_TIMEOUT = int(os.getenv("AI_TIMEOUT", "60"))

        self._setup_logging()

    def _require(self, key: str) -> str:
        """Obtiene variable o falla inmediatamente."""
        value = os.getenv(key)
        if not value:
            print(f"[FATAL] Variable de entorno requerida no encontrada: {key}", file=sys.stderr)
            sys.exit(1)
        return value

    def _setup_logging(self):
        """Configura logging estructurado."""
        log_format = os.getenv("LOG_FORMAT", "text")
        
        if log_format == "json":
            # JSON estructurado para monitoreo
            import json
            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    return json.dumps({
                        "time": self.formatTime(record),
                        "level": record.levelname,
                        "machine": self.machine_id,
                        "msg": record.getMessage(),
                    })
            fmt = JSONFormatter()
            fmt.machine_id = self.MACHINE_ID
        else:
            fmt = logging.Formatter(
                f"[%(asctime)s] [{self.MACHINE_ID}] %(levelname)s - %(message)s"
            )
        
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)
        
        logging.basicConfig(
            level=logging.INFO,
            handlers=[handler]
        )


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Obtiene la instancia singleton de Config."""
    return Config()
