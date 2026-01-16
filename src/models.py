"""Modelos de datos con validación Pydantic."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Contacto(BaseModel):
    """Información de contacto extraída."""
    tipo: str = Field(..., description="email|telefono|red_social")
    valor: str
    verificado: bool = False


class IndicadoresCalidad(BaseModel):
    """Indicadores de calidad del sitio."""
    tiene_ssl: bool = False
    tiene_contacto: bool = False
    sitio_profesional: bool = False


class AnalisisIA(BaseModel):
    """Resultado del análisis de IA."""
    nombre_empresa: Optional[str] = None
    actividad_principal: Optional[str] = None
    sector: Optional[str] = None
    tamaño_estimado: Optional[str] = None
    servicios: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)
    tecnologias_detectadas: List[str] = Field(default_factory=list)
    indicadores_calidad: IndicadoresCalidad = Field(default_factory=IndicadoresCalidad)


class Organizacion(BaseModel):
    """Modelo principal de una organización/lead."""
    url: HttpUrl
    dominio: str
    
    # Metadatos del sitio
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    
    # Contactos
    emails: List[str] = Field(default_factory=list)
    telefonos: List[str] = Field(default_factory=list)
    redes_sociales: dict = Field(default_factory=dict)
    
    # Análisis IA
    analisis: Optional[AnalisisIA] = None
    
    # Scoring
    score: float = 0.0
    tier: str = "D"
    
    # Metadatos de proceso
    machine_id: str = "local"
    nicho_origen: Optional[str] = None
    scrapeado_en: datetime = Field(default_factory=datetime.utcnow)
    
    def to_supabase_dict(self) -> dict:
        """Convierte a diccionario para upsert en Supabase."""
        return {
            "url": str(self.url),
            "dominio": self.dominio,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "emails": self.emails,
            "telefonos": self.telefonos,
            "redes_sociales": self.redes_sociales,
            "nombre_empresa": self.analisis.nombre_empresa if self.analisis else None,
            "actividad": self.analisis.actividad_principal if self.analisis else None,
            "sector": self.analisis.sector if self.analisis else None,
            "tamaño": self.analisis.tamaño_estimado if self.analisis else None,
            "servicios": self.analisis.servicios if self.analisis else [],
            "pain_points": self.analisis.pain_points if self.analisis else [],
            "tecnologias": self.analisis.tecnologias_detectadas if self.analisis else [],
            "score": self.score,
            "tier": self.tier,
            "machine_id": self.machine_id,
            "nicho_origen": self.nicho_origen,
            "scrapeado_en": self.scrapeado_en.isoformat(),
        }


class TareaURL(BaseModel):
    """Tarea de scraping en la cola."""
    url: HttpUrl
    nicho: Optional[str] = None
    prioridad: int = 1
    nivel: int = 0  # 0 = seed, 1 = descubierto
    reintentos: int = 0
