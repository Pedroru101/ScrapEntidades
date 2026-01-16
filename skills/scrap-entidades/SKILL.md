---
name: scrap-entidades
description: >
  Skill principal del sistema de scraping distribuido ScrapEntidades.
  Trigger: Preguntas de desarrollo, decisiones de arquitectura, crear scrapers.
license: MIT
metadata:
  author: ScrapEntidades
  version: "1.0"
  scope: [root]
  auto_invoke: "Preguntas generales de desarrollo"
---

## Arquitectura del Sistema

```
CSV URLs → Cola Redis → Pool de Workers (12 hilos)
                              ↓
              Request Tor → Scraper → Análisis IA → Scoring → Supabase
```

## Componentes

| Componente    | Stack                              | Ubicación                      |
| ------------- | ---------------------------------- | ------------------------------ |
| Config        | Singleton Python                   | `src/config.py`                |
| Scraper       | BeautifulSoup, regex               | `src/scraper.py`               |
| Analizador IA | OpenRouter (Gemini/DeepSeek/Haiku) | `src/ai_analyzer.py`           |
| Scoring       | Algoritmo ponderado 0-10           | `src/scoring.py`               |
| Worker        | asyncio, Redis                     | `src/worker.py`                |
| Cliente Tor   | aiohttp-socks                      | `src/utils/tor_client.py`      |
| Base de Datos | Supabase + backup CSV              | `src/utils/supabase_client.py` |

## Comandos Rápidos

```bash
# Desarrollo
docker-compose up --build

# Tests
pytest tests/ -v

# Inicializar directorios
python scripts/init_dirs.py
```

## Patrones Críticos

### Cadena de Fallback IA

```python
MODELS = [
    "google/gemini-flash-1.5",    # Primario
    "deepseek/deepseek-chat",     # Fallback 1
    "anthropic/claude-3-haiku",   # Fallback 2
]
```

### Pesos del Scoring

```python
WEIGHTS = {
    "contacto_completo": 2.0,  # Email + Teléfono
    "sitio_profesional": 1.5,  # Calidad del diseño
    "tamaño_empresa": 2.0,     # Tamaño de empresa
    "sector_target": 1.5,      # Sectores prioritarios
}
```

## Skills Relacionadas

- `skill-creator` - Crear nuevas skills
- `skill-sync` - Sincronizar skills a GEMINI.md
