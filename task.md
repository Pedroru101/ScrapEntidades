# Task List - Sistema de Scraping Distribuido con Supabase

## Fase 1: Configuración e Infraestructura Local

- [x] **Entorno y Dependencias Base** <!-- id: 0 -->

  - [x] Crear `requirements.txt` con: `supabase`, `aiohttp`, `asyncio`, `redis`, `beautifulsoup4`, `openai`, `fake-useragent`, `requests[socks]`.
  - [x] Crear `Dockerfile` optimizado (Python 3.11-slim) con instalación de Tor y compilación de dependencias.
  - [x] Crear `.env.example` documentando: `SUPABASE_URL`, `SUPABASE_KEY`, `OPENROUTER_API_KEY`, `REDIS_URL`, `MACHINE_ID` (default: local).

- [x] **Orquestación con Docker Compose** <!-- id: 1 -->

  - [x] Definir servicio `app` con soporte de escalado horizontal (`deploy.replicas` no necesario localmente, pero sí estructura lista).
  - [x] Configurar servicio `redis` local para cola de tareas interna.
  - [x] Configurar volúmenes para persistencia de logs y CSVs de backup (`./data:/app/data`).
  - [x] Configurar healthcheck para Redis y Tor.

- [x] **Gestión de Configuración (`config.py`)** <!-- id: 2 -->

  - [x] Implementar clase `Config` singleton.
  - [x] Validar variables de entorno críticas al inicio (FAIL FAST).
  - [x] Configurar logging estructurado (JSON logs opcional) para monitoreo fácil.

- [x] **Estructura de Datos Local** <!-- id: 3 -->
  - [x] Script de inicialización `init_dirs.py` para crear: `data/urls_iniciales`, `data/resultados`, `data/logs`.
  - [x] Generar CSV de plantilla `data/urls_iniciales/template.csv`.

## Fase 2: Desarrollo del Core (Scraping & IA)

- [x] **Cliente Tor (`src/utils/tor_client.py`)** <!-- id: 4 -->

  - [x] Implementar clase `TorClient` con sesión `aiohttp`.
  - [x] Método `renew_identity()`: enviar señal SIGNAL NEWNYM al puerto de control de Tor.
  - [x] Método `check_ip()`: consultar API externa para validar cambio de IP.
  - [x] Manejo de reintentos con backoff exponencial para fallos de conexión.

- [x] **Motor de Scraping (`src/scraper.py`)** <!-- id: 5 -->

  - [x] Implementar extracción robusta: Meta tags, emails (regex), teléfonos, rrss.
  - [x] Lógica de descubrimiento de URLs (Nivel 0 -> 1):
    - Extraer links internos vs externos.
    - Filtrar dominios irrelevantes (blacklist).
    - Validar si el dominio ya existe en Supabase (check ligero).
  - [x] Guardado local temporal de HTML (opcional para debug) o solo extracción en memoria.

- [x] **Analizador IA (`src/ai_analyzer.py`)** <!-- id: 6 -->

  - [x] Cliente OpenRouter con soporte para múltiples modelos (Gemini Flash, DeepSeek).
  - [x] Implementar fallback automático: Si Gemini falla -> DeepSeek -> Claude Haiku.
  - [x] Prompt engineering: System prompt optimizado para extracción de JSON estricto (actividad, pain points).
  - [x] Manejo de errores de API (Rate Limits) y conteo de tokens.

- [x] **Sistema de Scoring (`src/scoring.py`)** <!-- id: 7 -->
  - [x] Algoritmo de cálculo 0-10.
  - [x] Normalización de datos extraídos (tamaño empresa, teconologías detectadas).

## Fase 3: Integración y Ejecución (Worker System)

- [x] **Integración Supabase (`src/utils/supabase_client.py`)** <!-- id: 15 -->

  - [x] Cliente asíncrono usando `supabase-py` (o `httpx` directo si la lib oficial es bloqueante).
  - [x] Métodos CRUD: `upsert_organizacion`, `insert_contactos`, `log_error`.
  - [x] Manejo de errores de red: Guardar en CSV local si Supabase falla (Backup Strategy).

- [x] **Modelos de Datos (`src/models.py`)** <!-- id: 16 -->

  - [x] Definir dataclasses/Pydantic models para validación interna antes de enviar a DB.
  - [x] Mapper: Objeto Python -> Diccionario Supabase.

- [x] **Lógica del Worker (`src/worker.py`)** <!-- id: 8 -->

  - [x] Bucle principal de consumo de Redis.
  - [x] Pipeline: `Pop URL` -> `Tor Request` -> `Parse` -> `IA Analysis` -> `Supabase Upsert` -> `Next`.
  - [x] Manejo de señales (SIGINT, SIGTERM) para apagado gracioso (terminar tarea actual antes de salir).

- [x] **Punto de Entrada (`src/main.py`)** <!-- id: 9 -->
  - [x] Cargar CSV inicial (`maquina_XX.csv`) a Redis si la cola está vacía.
  - [x] Disparar `N` tareas asíncronas (`asyncio.create_task`) según variable `MAX_THREADS`.
  - [x] Monitor de "Cola vacía": Esperar o terminar según config.

## Fase 4: Verificación y Pruebas (Estrategia Progresiva)

- [x] **Prueba Nivel 1: Funcional Single-Thread** <!-- id: 12 -->

  - [x] Crear test unitario `tests/test_flow.py` que corre todo el pipeline con 1 URL mockeada o real.
  - [ ] Verificar salida en consola y registro en Supabase.
  - [ ] Validar formato de datos en Supabase.

- [x] **Prueba Nivel 2: Stress Local (12 Hilos)** <!-- id: 13 -->

  - [x] Script de prueba `scripts/stress_test.py` que carga 50 URLs dummy.
  - [ ] Ejecutar con `MAX_THREADS=12`.
  - [ ] Monitorear uso de RAM/CPU del contenedor.
  - [ ] Validar que Tor no seature y rote IPs correctamente bajo carga.

- [ ] **Prueba Nivel 3: Simulacro de Producción** <!-- id: 14 -->
  - [ ] Empaquetar imagen Docker final.
  - [ ] Ejecutar contenedor "aislado" (sin volúmenes de código montados, solo config).
  - [ ] Validar recuperación ante reinicio (persistencia de cola Redis).
