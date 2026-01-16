"""Analizador IA con fallback multi-modelo."""
import json
import logging
from typing import Optional

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import get_config

logger = logging.getLogger(__name__)

# Modelos con prioridad de fallback
MODELS = [
    "google/gemini-flash-1.5",
    "deepseek/deepseek-chat",
    "anthropic/claude-3-haiku",
]

SYSTEM_PROMPT = """Eres un analista de negocios experto. Analiza el contenido de un sitio web empresarial y extrae información estructurada.

RESPONDE ÚNICAMENTE con JSON válido (sin markdown, sin explicaciones) siguiendo este esquema:
{
    "nombre_empresa": "string o null",
    "actividad_principal": "descripción breve del giro comercial",
    "sector": "construccion|salud|educacion|retail|servicios|tecnologia|manufactura|otro",
    "tamaño_estimado": "micro|pequeña|mediana|grande|desconocido",
    "servicios": ["lista", "de", "servicios"],
    "pain_points": ["posibles problemas o necesidades detectadas"],
    "tecnologias_detectadas": ["wordpress", "shopify", etc],
    "indicadores_calidad": {
        "tiene_ssl": true/false,
        "tiene_contacto": true/false,
        "sitio_profesional": true/false
    }
}

Si no puedes extraer un campo, usa null. Sé conciso pero preciso."""


class AIAnalyzer:
    """Cliente OpenRouter con fallback automático entre modelos."""

    def __init__(self):
        cfg = get_config()
        self.client = AsyncOpenAI(
            api_key=cfg.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        self.timeout = cfg.AI_TIMEOUT
        self.total_tokens = 0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
    )
    async def analyze(self, text_content: str, meta: dict) -> Optional[dict]:
        """Analiza contenido con fallback entre modelos."""
        user_prompt = self._build_prompt(text_content, meta)
        
        for model in MODELS:
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.1,
                )
                
                content = response.choices[0].message.content
                self.total_tokens += response.usage.total_tokens if response.usage else 0
                
                # Parsear JSON
                result = self._parse_json(content)
                if result:
                    logger.info(f"Análisis exitoso con {model}")
                    return result
                    
            except Exception as e:
                logger.warning(f"Error con {model}: {e}")
                continue
        
        logger.error("Todos los modelos fallaron")
        return None

    def _build_prompt(self, text: str, meta: dict) -> str:
        """Construye el prompt para el análisis."""
        return f"""Analiza este sitio web:

TÍTULO: {meta.get('title', 'Sin título')}
DESCRIPCIÓN: {meta.get('description', 'Sin descripción')}

CONTENIDO:
{text[:3000]}

Extrae la información empresarial en formato JSON."""

    def _parse_json(self, content: str) -> Optional[dict]:
        """Parsea JSON de la respuesta, limpiando markdown si existe."""
        content = content.strip()
        
        # Limpiar markdown code blocks
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Error parseando JSON: {e}")
            return None

    def get_token_count(self) -> int:
        """Retorna total de tokens consumidos."""
        return self.total_tokens
