# ScrapEntidades

Sistema de scraping distribuido con análisis IA y scoring automático de leads empresariales.

## Inicio Rápido

```bash
# 1. Configurar credenciales
cp .env.example .env
# Editar .env con tus API keys

# 2. Ejecutar con Docker
docker-compose up --build
```

## Estructura del Proyecto

```
ScrapEntidades/
├── src/                    # Código fuente principal
│   ├── config.py           # Configuración (singleton)
│   ├── scraper.py          # Extracción de datos web
│   ├── ai_analyzer.py      # Análisis con IA (OpenRouter)
│   ├── scoring.py          # Scoring de leads 0-10
│   ├── worker.py           # Pipeline de procesamiento
│   └── utils/              # Tor y Supabase
├── scripts/                # Scripts de automatización
├── tests/                  # Tests unitarios
├── skills/                 # Skills para Antigravity
└── docs/                   # Documentación adicional
```

## Variables de Entorno

| Variable             | Descripción               | Requerida                          |
| -------------------- | ------------------------- | ---------------------------------- |
| `SUPABASE_URL`       | URL del proyecto Supabase | Sí                                 |
| `SUPABASE_KEY`       | API Key de Supabase       | Sí                                 |
| `OPENROUTER_API_KEY` | API Key de OpenRouter     | Sí                                 |
| `REDIS_URL`          | URL de Redis              | No (default: redis://redis:6379/0) |
| `MACHINE_ID`         | Identificador de máquina  | No (default: maquina_01)           |
| `MAX_THREADS`        | Hilos concurrentes        | No (default: 12)                   |

## Comandos

```bash
# Desarrollo
docker-compose up --build      # Levantar servicios
python scripts/init_dirs.py    # Crear estructura de carpetas

# Tests
pytest tests/ -v               # Ejecutar tests
python scripts/stress_test.py  # Test de carga con 50 URLs
```

---

## Sistema de Skills (Antigravity)

Este proyecto incluye un sistema de skills para mejorar la asistencia de Antigravity.

### ¿Qué son las Skills?

Las skills son documentos `.md` con reglas y patrones que Antigravity lee automáticamente cuando trabaja en el proyecto. Contienen:

- Reglas críticas del proyecto
- Patrones de código recomendados
- Comandos útiles
- Arquitectura del sistema

### Skills Disponibles

| Skill             | Cuándo se usa       | Ubicación                         |
| ----------------- | ------------------- | --------------------------------- |
| `scrap-entidades` | Desarrollo general  | `skills/scrap-entidades/SKILL.md` |
| `skill-creator`   | Crear nuevas skills | `skills/skill-creator/SKILL.md`   |
| `skill-sync`      | Sincronizar skills  | `skills/skill-sync/SKILL.md`      |

### Archivos Clave

- **`GEMINI.md`** (raíz): Reglas globales del proyecto que Antigravity lee al iniciar
- **`src/GEMINI.md`**: Reglas específicas del código fuente
- **`skills/*/SKILL.md`**: Skills invocables manualmente

### Cómo Funciona

1. Al abrir el proyecto, Antigravity lee `GEMINI.md` automáticamente
2. Las skills se invocan cuando realizas ciertas acciones:
   - Preguntas de desarrollo → `scrap-entidades`
   - Crear una skill → `skill-creator`
   - Modificar skills → `skill-sync`

### Configurar Skills

```powershell
# Ejecutar desde la raíz del proyecto
.\skills\setup.ps1
```

Este script copia los archivos necesarios para que Antigravity los detecte.

---

## Documentación

- [Concepto Original](docs/concepto-original.md) - Idea inicial del sistema
- [Skills README](skills/README.md) - Documentación de skills
