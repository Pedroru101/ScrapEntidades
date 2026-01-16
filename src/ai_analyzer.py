"""Analizador IA con fallback multi-modelo para detección de prospectos de gabinete de prensa."""
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

SYSTEM_PROMPT = """Eres un analista de inteligencia de negocios experto.

Tu objetivo es extraer TODO el conocimiento posible sobre una organización para construir un perfil profundo ("Conocimiento Profundo").
NO filtres información pensando en si "sirve" para un producto específico. Tu trabajo es entender quiénes son, qué hacen y qué les duele.

Extrae la información en JSON estricto siguiendo este esquema:

{
  "conocimiento_profundo": {
    "sector": "Sector específico (ej: ONG ambiental, Cooperativa agrícola)",
    "actividades_principales": ["Lista de qué hacen realmente, proyectos, servicios"],
    "retos_objetivos": ["Qué quieren lograr", "Qué problemas mencionan", "Metas estratégicas"],
    "estructura_interna": ["Nº empleados", "Voluntarios", "Delegaciones", "Socios"],
    "financiacion": ["Subvenciones", "Cuotas", "Ventas", "Patrocinios"],
    "colaboradores": ["Con quién trabajan", "Redes a las que pertenecen"],
    "particularidades": ["Datos únicos, premios, historia, reconocimientos"]
  },
  "oportunidades_detectadas": {
    "productos_encajan": ["Lista de productos potenciales (MMI, Automatización, IA, Licitador, Mentorías)"],
    "productos_no_encajan": ["Lista de productos descartados y POR QUÉ"]
  }
}

CRITERIOS DE EXTRACCIÓN:
- Sé exhaustivo. Si mencionan un presupuesto, extráelo. Si mencionan un problema de gestión, extráelo.
- En 'financiacion', busca pistas en secciones de transparencia o memorias.
- En 'retos', infiere problemas a partir de sus objetivos (ej: 'Queremos llegar a más gente' -> Reto: Alcance/Marketing).

PRODUCTOS DISPONIBLES (Para sugerir en oportunidades):
1. MMI: Seguimiento de medios (para quienes comunican mucho).
2. Automatizaciones: CRM, gestión de socios/expedientes, emails.
3. IA Contenidos: Generación de posts, recetas, materiales educativos.
4. Mentorías: Estrategia, fondos europeos, negocio.
5. Licitador: Búsqueda de fondos públicos/concursos.

Responde SOLO con el JSON válido."""


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
        return f"""Analiza esta organización para identificar si es prospecto para servicios de gabinete de prensa:

TÍTULO: {meta.get('title', 'Sin título')}
DESCRIPCIÓN: {meta.get('description', 'Sin descripción')}

CONTENIDO DE LA WEB:
{text[:4000]}

Extrae la información en formato JSON. Presta especial atención a:
1. Si están ubicados en Canarias (prioridad máxima)
2. Si tienen sala de prensa, notas de prensa, o sección de noticias
3. Si son activos en RRSS y qué tan profesional es su comunicación
4. Posibles pain points de comunicación que podríamos resolver"""

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
