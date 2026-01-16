---
name: scrap-entidades
description: >
  Skill principal del sistema ScrapEntidades (Canarias).
  Trigger: Preguntas de desarrollo, decisiones de arquitectura, crear scrapers.
license: MIT
metadata:
  author: ScrapEntidades
  version: "2.0"
  scope: [root]
  auto_invoke: "Preguntas generales de desarrollo"
---

## Arquitectura del Sistema

```
Lista de Nichos (Input)
       ↓
  [Searcher] → Búsqueda Google → URLs
                                   ↓
                             Cola Redis
                                   ↓
  [Worker] → Request Tor → Scraper → Filtro Canarias
                                        ↓
                                   Etiquetado IA (Si es Canarias)
                                        ↓
                                     Supabase
```

## Componentes

| Componente   | Rol                             | Ubicación            |
| ------------ | ------------------------------- | -------------------- |
| **Searcher** | Convierte Nichos en URLs        | `src/searcher.py`    |
| **Worker**   | Procesa, Filtra, Etiqueta       | `src/worker.py`      |
| Scraper      | Extracción RAW                  | `src/scraper.py`     |
| IA           | Etiquetado (Sector/Pain Points) | `src/ai_analyzer.py` |
| Config       | Singleton                       | `src/config.py`      |

## Patrones Críticos

### Filtro Geográfico Estricto

```python
CANARIAS_KEYWORDS = [
    "canarias", "tenerife", "gran canaria", "lanzarote", "fuerteventura",
    "la palma", "la gomera", "el hierro", "las palmas", "santa cruz"
]
# Si NO contiene keywords -> Descartar inmediatamente
```

### Extracción Profunda (Conocimiento Holístico)

- **Objetivo**: Conocer la organización a fondo (Retos, Financiación, Estructura).
- **Prohibido**: Filtrar pensando "¿sirve para MMI?".
- **Regla**: Extraer TODO. La decisión de producto (MMI, Automatización, IA) es posterior.

### Etiquetado IA

- Input: Texto completo scrapeado.
- Output: JSON rico con `conocimiento_profundo` y `oportunidades_detectadas`.
- Fallo de IA -> Se guarda el lead sin etiquetas (graceful degradation).

## Comandos Rápidos

```bash
# Test de Filtro Canarias
python scripts/test_canarias.py

# Inyectar Nichos (Searcher)
python src/searcher.py
```
