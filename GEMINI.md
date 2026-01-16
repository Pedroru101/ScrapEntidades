# Guía del Proyecto - ScrapEntidades

## Cómo Usar Esta Guía

- Empieza aquí para normas generales del proyecto.
- Cada componente tiene reglas específicas en `src/GEMINI.md`.
- Las reglas de componente tienen prioridad sobre las globales.

## Skills Disponibles

| Skill             | Descripción                    | Ubicación                                   |
| ----------------- | ------------------------------ | ------------------------------------------- |
| `scrap-entidades` | Skill principal del proyecto   | [SKILL.md](skills/scrap-entidades/SKILL.md) |
| `skill-creator`   | Crear nuevas skills            | [SKILL.md](skills/skill-creator/SKILL.md)   |
| `skill-sync`      | Sincronizar skills a GEMINI.md | [SKILL.md](skills/skill-sync/SKILL.md)      |

### Invocación Automática

Cuando realices estas acciones, SIEMPRE invoca la skill correspondiente PRIMERO:

| Acción                            | Skill             |
| --------------------------------- | ----------------- |
| Preguntas generales de desarrollo | `scrap-entidades` |
| Crear nuevas skills               | `skill-creator`   |
| Después de modificar skills       | `skill-sync`      |

---

## Resumen del Proyecto

| Componente     | Ubicación            | Stack Tecnológico                   |
| -------------- | -------------------- | ----------------------------------- |
| Scraper Core   | `src/`               | Python 3.11, aiohttp, BeautifulSoup |
| Analizador IA  | `src/ai_analyzer.py` | OpenRouter (Gemini/DeepSeek)        |
| Sistema Worker | `src/worker.py`      | asyncio, Redis                      |
| Utilidades     | `src/utils/`         | Tor, Supabase                       |
| Scripts        | `scripts/`           | Automatización Python               |
| Tests          | `tests/`             | pytest                              |

---

## REGLAS CRÍTICAS - NO NEGOCIABLES

### Calidad de Código

- SIEMPRE: Usar async/await para todas las operaciones I/O
- SIEMPRE: Validar datos con Pydantic antes de operaciones DB
- SIEMPRE: Manejar excepciones con logging apropiado
- NUNCA: Hardcodear secretos o API keys
- NUNCA: Dejar bloques try-catch vacíos

### Arquitectura

- SIEMPRE: Usar `get_config()` para configuración
- SIEMPRE: Usar `TorClient` para requests externos
- NUNCA: Hacer llamadas HTTP directas sin proxy Tor
- NUNCA: Insertar datos sin calcular score primero

---

## Comandos de Desarrollo

```bash
# Ejecutar con Docker
docker-compose up --build

# Ejecutar tests
pytest tests/ -v

# Inicializar directorios
python scripts/init_dirs.py

# Test de estrés
python scripts/stress_test.py
```

---

## Guía de Commits

Seguir conventional-commit: `<tipo>[alcance]: <descripción>`

Tipos: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

Alcances: `scraper`, `ai`, `worker`, `db`, `infra`
