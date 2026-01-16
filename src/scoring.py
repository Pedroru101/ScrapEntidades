"""Sistema de scoring de leads 0-10."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Pesos para cada factor
WEIGHTS = {
    "contacto_completo": 2.0,      # Tiene email + teléfono
    "sitio_profesional": 1.5,      # Diseño profesional detectado
    "tamaño_empresa": 2.0,         # Mediana/grande vale más
    "sector_target": 1.5,          # Sectores prioritarios
    "tecnologias": 1.0,            # Usa tecnologías modernas
    "redes_sociales": 0.5,         # Presencia en RRSS
    "ssl": 0.5,                    # Tiene HTTPS
}

# Sectores de alto valor
HIGH_VALUE_SECTORS = {"construccion", "salud", "tecnologia", "manufactura"}

# Tamaños y sus puntajes
SIZE_SCORES = {
    "grande": 1.0,
    "mediana": 0.8,
    "pequeña": 0.5,
    "micro": 0.2,
    "desconocido": 0.3,
}


class Scorer:
    """Calcula score de valor potencial de un lead."""

    def calculate(self, scraped_data: dict, ai_analysis: Optional[dict]) -> float:
        """
        Calcula score 0-10 basado en datos extraídos y análisis IA.
        
        Args:
            scraped_data: Datos del scraper (emails, phones, social, etc)
            ai_analysis: Resultado del análisis IA (puede ser None)
        
        Returns:
            Score normalizado entre 0 y 10
        """
        score = 0.0
        max_score = sum(WEIGHTS.values())
        
        # Factor: Contacto completo
        has_email = bool(scraped_data.get("emails"))
        has_phone = bool(scraped_data.get("phones"))
        if has_email and has_phone:
            score += WEIGHTS["contacto_completo"]
        elif has_email or has_phone:
            score += WEIGHTS["contacto_completo"] * 0.5
        
        # Factor: Redes sociales
        social = scraped_data.get("social", {})
        if len(social) >= 2:
            score += WEIGHTS["redes_sociales"]
        elif len(social) == 1:
            score += WEIGHTS["redes_sociales"] * 0.5
        
        # Factores que requieren análisis IA
        if ai_analysis:
            # Factor: Sitio profesional
            indicators = ai_analysis.get("indicadores_calidad", {})
            if indicators.get("sitio_profesional"):
                score += WEIGHTS["sitio_profesional"]
            
            # Factor: SSL
            if indicators.get("tiene_ssl"):
                score += WEIGHTS["ssl"]
            
            # Factor: Tamaño empresa
            size = ai_analysis.get("tamaño_estimado", "desconocido")
            size_multiplier = SIZE_SCORES.get(size, 0.3)
            score += WEIGHTS["tamaño_empresa"] * size_multiplier
            
            # Factor: Sector target
            sector = ai_analysis.get("sector", "otro")
            if sector in HIGH_VALUE_SECTORS:
                score += WEIGHTS["sector_target"]
            
            # Factor: Tecnologías
            techs = ai_analysis.get("tecnologias_detectadas", [])
            if techs:
                score += WEIGHTS["tecnologias"] * min(len(techs) / 3, 1.0)
        
        # Normalizar a 0-10
        normalized = (score / max_score) * 10
        return round(normalized, 1)

    def get_tier(self, score: float) -> str:
        """Clasifica el lead según su score."""
        if score >= 8:
            return "A"  # Hot lead
        elif score >= 6:
            return "B"  # Warm lead
        elif score >= 4:
            return "C"  # Cool lead
        else:
            return "D"  # Cold lead
