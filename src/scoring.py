"""Sistema de scoring de leads 0-10 para servicios de gabinete de prensa."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Pesos para cada factor (total = 10 puntos máximo)
WEIGHTS = {
    "ubicacion_canarias": 2.5,    # Canarias = máxima prioridad
    "ubicacion_espana": 1.5,      # España peninsular
    "actividad_comunicativa": 2.0, # Señales de necesidad de seguimiento
    "tamaño_organizacion": 1.5,   # Mayor tamaño = más presupuesto
    "presencia_digital": 1.5,     # Web profesional, RRSS activas
    "sector_priority": 1.0,       # Sectores con más necesidad de gabinete
}

# Sectores con alta necesidad de gabinete de prensa
HIGH_PRIORITY_SECTORS = {
    "gobierno", "administracion_publica", "institucional",
    "salud", "educacion", "turismo", "cultura",
    "asociaciones", "fundaciones", "ong",
    "construccion", "energia", "tecnologia",
}

# Palabras clave que indican necesidad de servicios de comunicación
PAIN_POINT_KEYWORDS = [
    "sin gabinete de comunicación",
    "comunicación interna básica",
    "sin seguimiento de medios",
    "no miden impacto mediático",
    "sin análisis de RRSS",
    "prensa reactiva",
    "dependencia de alertas Google",
    "comunicación manual",
    "sin clipping profesional",
    "sin informes ROI",
]

# Indicadores de ubicación en Canarias
CANARIAS_KEYWORDS = [
    "canarias", "tenerife", "gran canaria", "lanzarote", "fuerteventura",
    "la palma", "la gomera", "el hierro", "santa cruz", "las palmas",
]


class Scorer:
    """Calcula score de valor potencial para servicios de gabinete de prensa."""

    def calculate(self, scraped_data: dict, ai_analysis: Optional[dict]) -> float:
        """
        Calcula score 0-10 basado en datos extraídos y análisis IA.
        
        Criterios principales:
        - Ubicación (Canarias >> España >> Otros)
        - Actividad comunicativa (notas de prensa, noticias, RRSS)
        - Tamaño de la organización
        - Presencia digital profesional
        - Sector de actividad
        """
        score = 0.0
        
        # Factor: Ubicación (Canarias = prioridad máxima)
        ubicacion_score = self._score_ubicacion(scraped_data, ai_analysis)
        score += ubicacion_score
        
        # Factor: Presencia digital
        score += self._score_presencia_digital(scraped_data)
        
        # Factores que requieren análisis IA
        if ai_analysis:
            # Factor: Actividad comunicativa
            score += self._score_actividad_comunicativa(ai_analysis)
            
            # Factor: Tamaño organización
            score += self._score_tamaño(ai_analysis)
            
            # Factor: Sector prioritario
            score += self._score_sector(ai_analysis)
        
        # Normalizar a 0-10 (ya está en escala correcta)
        return round(min(10.0, score), 1)

    def _score_ubicacion(self, scraped_data: dict, ai_analysis: Optional[dict]) -> float:
        """Puntúa ubicación: Canarias > España > Otros."""
        text_to_check = ""
        
        # Revisar meta tags
        meta = scraped_data.get("meta", {})
        text_to_check += f" {meta.get('title', '')} {meta.get('description', '')}"
        
        # Revisar análisis IA
        if ai_analysis:
            text_to_check += f" {ai_analysis.get('ambito_geografico', '')}"
            text_to_check += f" {ai_analysis.get('ubicacion', '')}"
        
        text_lower = text_to_check.lower()
        
        # Canarias = máxima prioridad
        if any(kw in text_lower for kw in CANARIAS_KEYWORDS):
            return WEIGHTS["ubicacion_canarias"]
        
        # España peninsular
        spain_keywords = ["españa", "madrid", "barcelona", "valencia", "sevilla", "bilbao"]
        if any(kw in text_lower for kw in spain_keywords):
            return WEIGHTS["ubicacion_espana"]
        
        return 0.5  # Otros países (bajo interés)

    def _score_presencia_digital(self, scraped_data: dict) -> float:
        """Puntúa calidad de presencia digital."""
        score = 0.0
        max_score = WEIGHTS["presencia_digital"]
        
        # Tiene email corporativo (no gmail/hotmail)
        emails = scraped_data.get("emails", [])
        if emails:
            has_corporate = any(
                not any(free in e for free in ["gmail", "hotmail", "yahoo", "outlook"])
                for e in emails
            )
            if has_corporate:
                score += max_score * 0.3
        
        # Tiene teléfono de contacto
        if scraped_data.get("phones"):
            score += max_score * 0.2
        
        # Tiene redes sociales
        social = scraped_data.get("social", {})
        if len(social) >= 2:
            score += max_score * 0.5
        elif len(social) == 1:
            score += max_score * 0.25
        
        return score

    def _score_actividad_comunicativa(self, ai_analysis: dict) -> float:
        """Puntúa actividad comunicativa y necesidad de seguimiento."""
        score = 0.0
        max_score = WEIGHTS["actividad_comunicativa"]
        
        # Pain points detectados relacionados con comunicación
        pain_points = ai_analysis.get("pain_points", [])
        if pain_points:
            # Más pain points = más oportunidad
            pain_score = min(len(pain_points) / 3, 1.0)
            score += max_score * 0.6 * pain_score
        
        # Indicadores de actividad en prensa/comunicación
        indicators = ai_analysis.get("indicadores_calidad", {})
        if indicators.get("tiene_sala_prensa"):
            score += max_score * 0.2  # Ya tienen estructura, pueden necesitar mejora
        if indicators.get("activo_comunicacion"):
            score += max_score * 0.2
        
        return score

    def _score_tamaño(self, ai_analysis: dict) -> float:
        """Puntúa tamaño de la organización."""
        max_score = WEIGHTS["tamaño_organizacion"]
        
        size_scores = {
            "grande": 1.0,
            "mediana": 0.8,
            "pequeña": 0.5,
            "micro": 0.3,
            "desconocido": 0.4,
        }
        
        size = ai_analysis.get("tamaño_estimado", "desconocido").lower()
        multiplier = size_scores.get(size, 0.4)
        
        return max_score * multiplier

    def _score_sector(self, ai_analysis: dict) -> float:
        """Puntúa sector de actividad."""
        max_score = WEIGHTS["sector_priority"]
        
        sector = ai_analysis.get("sector", "").lower()
        
        if sector in HIGH_PRIORITY_SECTORS:
            return max_score
        
        # Sectores con algo de necesidad
        medium_sectors = {"retail", "servicios", "manufactura", "inmobiliario"}
        if sector in medium_sectors:
            return max_score * 0.5
        
        return max_score * 0.2

    def get_tier(self, score: float) -> str:
        """Clasifica el lead según su score."""
        if score >= 8:
            return "A"  # Hot lead - Canarias + alta actividad
        elif score >= 6:
            return "B"  # Warm lead - España o Canarias medio
        elif score >= 4:
            return "C"  # Cool lead - Potencial pero bajo
        else:
            return "D"  # Cold lead - Poco interés

    def get_tier_description(self, tier: str) -> str:
        """Descripción del tier para reporting."""
        descriptions = {
            "A": "Prioridad máxima - Contactar inmediatamente",
            "B": "Alta prioridad - Incluir en campaña principal",
            "C": "Media prioridad - Pool secundario",
            "D": "Baja prioridad - No contactar",
        }
        return descriptions.get(tier, "Desconocido")
