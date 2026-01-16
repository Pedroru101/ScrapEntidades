# Código Fuente - Reglas para Antigravity

> **Referencia de Skills**:
>
> - [`scrap-entidades`](../skills/scrap-entidades/SKILL.md)

### Invocación Automática

| Acción                            | Skill             |
| --------------------------------- | ----------------- |
| Trabajar en código scraper/worker | `scrap-entidades` |

---

## Resumen del Proyecto

Sistema de scraping distribuido enfocado exclusivamente en **Canarias**, alimentado por una búsqueda basada en **Nichos**.

| Componente              | Ubicación                      | Stack Tecnológico                         |
| ----------------------- | ------------------------------ | ----------------------------------------- |
| **Buscador (Searcher)** | `src/searcher.py`              | Google Search / Mocks (Input: Nichos)     |
| Scraper Core            | `src/scraper.py`               | BeautifulSoup, Filtro Geográfico Estricto |
| Analizador IA           | `src/ai_analyzer.py`           | OpenRouter (Etiquetado a posteriori)      |
| Sistema Worker          | `src/worker.py`                | Procesamiento asíncrono, Redis            |
| Cliente Tor             | `src/utils/tor_client.py`      | aiohttp-socks (SSL off)                   |
| Base de Datos           | `src/utils/supabase_client.py` | Supabase + backup CSV                     |

---

## REGLAS CRÍTICAS - NO NEGOCIABLES

### Enfoque Geográfico

- **SIEMPRE**: El sistema debe filtrar estrictamente contenido relacionado con **Canarias** (islas, municipios).
- **NUNCA**: Procesar o guardar entidades fuera del ámbito de Canarias.

### Calidad de Código

- SIEMPRE: Usar async/await para todas las operaciones I/O
- SIEMPRE: Validar datos con Pydantic antes de operaciones DB
- SIEMPRE: Manejar excepciones con logging apropiado
- NUNCA: Hardcodear secretos o API keys
- NUNCA: Dejar bloques try-catch vacíos

### Arquitectura Async

- SIEMPRE: Usar `async def` para cualquier función con I/O
- SIEMPRE: Usar `aiohttp-socks` a través de `TorClient`, nunca `requests` directo
- NUNCA: Bloquear el event loop con I/O síncrono

---

## ESTRUCTURA DEL PROYECTO

```
src/
├── __init__.py
├── config.py         # Singleton config (FAIL FAST)
├── searcher.py       # Buscador de Nichos -> URLs
├── scraper.py        # Parsing RAW
├── ai_analyzer.py    # Etiquetado inteligente
├── worker.py         # Pipeline: Redis -> Scrape -> Filtro Canarias -> IA -> DB
├── main.py           # Entrypoint
└── utils/
    ├── tor_client.py      # Tor Client
    └── supabase_client.py # DB Client
```

## COMANDOS

```bash
# Desarrollo
docker-compose up --build

# Inyectar Nicho
python src/searcher.py

# Tests
python scripts/test_canarias.py
```
