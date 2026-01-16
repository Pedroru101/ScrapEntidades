"""Cliente Tor asíncrono con rotación de IP."""
import asyncio
import logging
from typing import Optional

import aiohttp
from aiohttp_socks import ProxyConnector
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import get_config

logger = logging.getLogger(__name__)


class TorClient:
    """Cliente HTTP que enruta tráfico a través de Tor."""

    def __init__(self):
        cfg = get_config()
        self.socks_port = cfg.TOR_SOCKS_PORT
        self.control_port = cfg.TOR_CONTROL_PORT
        self.timeout = cfg.REQUEST_TIMEOUT
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea la sesión HTTP."""
        if self._session is None or self._session.closed:
            # Desactivar SSL verify para evitar errores en webs gubernamentales/antiguas
            connector = ProxyConnector.from_url(
                f"socks5://127.0.0.1:{self.socks_port}",
                ssl=False
            )
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self._session

    async def close(self):
        """Cierra la sesión HTTP."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def get(self, url: str, headers: dict = None) -> str:
        """Realiza GET request a través de Tor."""
        session = await self._get_session()
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        if headers:
            default_headers.update(headers)
        
        async with session.get(url, headers=default_headers) as response:
            response.raise_for_status()
            return await response.text()

    async def renew_identity(self):
        """Solicita nueva identidad Tor (cambio de IP)."""
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", self.control_port)
            writer.write(b"AUTHENTICATE\r\n")
            await writer.drain()
            await reader.readline()
            
            writer.write(b"SIGNAL NEWNYM\r\n")
            await writer.drain()
            response = await reader.readline()
            
            writer.close()
            await writer.wait_closed()
            
            # Cerrar sesión actual para forzar nueva conexión
            await self.close()
            
            # Esperar a que Tor aplique el cambio
            await asyncio.sleep(5)
            
            logger.info("Identidad Tor renovada")
            return b"250" in response
        except Exception as e:
            logger.warning(f"Error renovando identidad Tor: {e}")
            return False

    async def check_ip(self) -> str:
        """Verifica la IP actual de salida de Tor."""
        try:
            html = await self.get("https://check.torproject.org/api/ip")
            import json
            data = json.loads(html)
            return data.get("IP", "unknown")
        except Exception as e:
            logger.error(f"Error verificando IP: {e}")
            return "error"

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
