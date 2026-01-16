"""Test funcional del pipeline completo."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Mock de config antes de importar módulos
import os
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["OPENROUTER_API_KEY"] = "test-api-key"

from src.scraper import Scraper
from src.scoring import Scorer


class TestScraper:
    """Tests del motor de scraping."""

    def test_extract_emails(self):
        """Extrae emails correctamente."""
        scraper = Scraper()
        html = """
        <html>
            <body>
                <p>Contacto: info@empresa.cl</p>
                <a href="mailto:ventas@empresa.cl">Email</a>
            </body>
        </html>
        """
        result = scraper.parse(html, "https://empresa.cl")
        
        assert "info@empresa.cl" in result["emails"]
        assert "ventas@empresa.cl" in result["emails"]

    def test_extract_phones(self):
        """Extrae teléfonos chilenos."""
        scraper = Scraper()
        html = """
        <html>
            <body>
                <p>Llamar al +56 9 1234 5678</p>
                <a href="tel:+56912345678">Teléfono</a>
            </body>
        </html>
        """
        result = scraper.parse(html, "https://empresa.cl")
        
        assert len(result["phones"]) >= 1

    def test_extract_meta(self):
        """Extrae meta tags."""
        scraper = Scraper()
        html = """
        <html>
            <head>
                <title>Mi Empresa - Servicios</title>
                <meta name="description" content="Descripción de la empresa">
            </head>
            <body></body>
        </html>
        """
        result = scraper.parse(html, "https://empresa.cl")
        
        assert result["meta"]["title"] == "Mi Empresa - Servicios"
        assert result["meta"]["description"] == "Descripción de la empresa"

    def test_filter_blacklist(self):
        """Filtra dominios en blacklist."""
        scraper = Scraper()
        html = """
        <html>
            <body>
                <a href="https://facebook.com/empresa">Facebook</a>
                <a href="https://proveedor.cl">Proveedor</a>
            </body>
        </html>
        """
        result = scraper.parse(html, "https://empresa.cl")
        
        # Facebook debe ser capturado como red social, no como link externo
        assert "facebook" in result["social"]
        # Proveedor sí debe aparecer
        assert "https://proveedor.cl" in result["external_links"]


class TestScorer:
    """Tests del sistema de scoring."""

    def test_score_completo(self):
        """Score alto para lead completo."""
        scorer = Scorer()
        
        scraped = {
            "emails": ["info@empresa.cl"],
            "phones": ["+56912345678"],
            "social": {"linkedin": "https://linkedin.com/empresa"}
        }
        
        ai_analysis = {
            "tamaño_estimado": "mediana",
            "sector": "construccion",
            "tecnologias_detectadas": ["wordpress"],
            "indicadores_calidad": {
                "sitio_profesional": True,
                "tiene_ssl": True
            }
        }
        
        score = scorer.calculate(scraped, ai_analysis)
        
        assert score >= 7.0  # Lead de alta calidad

    def test_score_minimo(self):
        """Score bajo para lead vacío."""
        scorer = Scorer()
        
        scraped = {"emails": [], "phones": [], "social": {}}
        
        score = scorer.calculate(scraped, None)
        
        assert score < 3.0  # Lead de baja calidad

    def test_tier_classification(self):
        """Clasificación correcta en tiers."""
        scorer = Scorer()
        
        assert scorer.get_tier(9.0) == "A"
        assert scorer.get_tier(7.0) == "B"
        assert scorer.get_tier(5.0) == "C"
        assert scorer.get_tier(2.0) == "D"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
