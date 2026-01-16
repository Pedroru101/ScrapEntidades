# Código Fuente - Reglas para Antigravity

> **Referencia de Skills**:
>
> - [`scrap-entidades`](../skills/scrap-entidades/SKILL.md)

### Invocación Automática

| Acción                            | Skill             |
| --------------------------------- | ----------------- |
| Trabajar en código scraper/worker | `scrap-entidades` |

---

## REGLAS CRÍTICAS - NO NEGOCIABLES

### Arquitectura Async

- SIEMPRE: Usar `async def` para cualquier función con I/O
- SIEMPRE: Usar `await` para todas las operaciones async
- SIEMPRE: Usar `aiohttp-socks` a través de `TorClient`, nunca `requests` directo
- NUNCA: Bloquear el event loop con I/O síncrono

### Flujo de Datos

- SIEMPRE: Validar con modelos Pydantic antes de insertar en Supabase
- SIEMPRE: Usar `Organizacion.to_supabase_dict()` para serialización
- SIEMPRE: Loggear errores vía `SupabaseClient.log_error()`
- NUNCA: Saltarse el paso de scoring antes de insertar en DB

### Configuración

- SIEMPRE: Usar singleton `get_config()`, nunca `os.getenv()` directamente
- SIEMPRE: Fallar rápido ante variables de entorno faltantes
- NUNCA: Hardcodear strings de conexión o API keys

---

## STACK TECNOLÓGICO

Python 3.11 | aiohttp 3.9 | Pydantic 2.5 | Redis 5.0 | Supabase | OpenRouter

---

## ESTRUCTURA DEL PROYECTO

```
src/
├── __init__.py
├── config.py         # Singleton config (FAIL FAST)
├── scraper.py        # Parsing HTML, extracción de datos
├── ai_analyzer.py    # OpenRouter multi-modelo con fallback
├── scoring.py        # Scoring de leads 0-10
├── models.py         # Modelos Pydantic
├── worker.py         # Pipeline principal de procesamiento
├── main.py           # Punto de entrada
└── utils/
    ├── tor_client.py      # Tor + aiohttp-socks
    └── supabase_client.py # CRUD + backup CSV
```

---

## COMANDOS

```bash
# Ejecutar main
python -m src.main

# Test de módulo individual
python -m pytest tests/test_flow.py -v

# Type check
mypy src/
```

---

## CHECKLIST DE QA

- [ ] Todas las funciones async correctamente awaited
- [ ] Config validada al inicio
- [ ] Modelos Pydantic usados para validación
- [ ] Manejo de errores con logging implementado
- [ ] Sin secretos hardcodeados
