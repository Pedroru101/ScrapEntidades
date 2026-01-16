# Sistema de Scraping Nocturno por Microsegmentación de Nichos

## + Scoring Automático de Valor Potencial del Cliente

### El cambio conceptual clave

Le pasamos a los workers **NICHOS/MICROSEGMENTOS** (conceptos, no URLs).

1.  **Workers buscan autónomamente** organizaciones en ese nicho.
2.  **Workers scrapean** cada organización encontrada.
3.  **Workers extraen** contactos + _pain points_.

**ESCALABILIDAD MASIVA:** El sistema genera las organizaciones, no los humanos.

---

## Arquitectura Real del Sistema

### Input: Lista infinita de nichos (no de URLs)

**Google Sheets "Nichos a explorar"**

| ID  | Nicho/Microsegmento                 | Sector         | Búsqueda sugerida                       | Prioridad | Estado    |
| :-- | :---------------------------------- | :------------- | :-------------------------------------- | :-------- | :-------- |
| 001 | Asociaciones ecologistas Canarias   | Asociaciones   | "asociación ecologista Canarias"        | Alta      | Pendiente |
| 002 | Cooperativas agrícolas Tenerife     | Empresas       | "cooperativa agrícola Tenerife"         | Alta      | Pendiente |
| 003 | Fundaciones educación especial      | Asociaciones   | "fundación educación especial Canarias" | Media     | Pendiente |
| 004 | Clubs deportivos fútbol regional    | Deportes       | "club fútbol regional Canarias"         | Media     | Pendiente |
| 005 | Colegios profesionales arquitectura | Colegios Prof. | "colegio arquitectos Canarias"          | Alta      | Pendiente |
| 006 | Asociaciones vecinales Gran Canaria | Asociaciones   | "asociación vecinos Gran Canaria"       | Baja      | Pendiente |
| ... | ...                                 | ...            | ...                                     | ...       | ...       |
| 500 | Empresas turismo activo Lanzarote   | Empresas       | "turismo activo aventura Lanzarote"     | Media     | Pendiente |

**Característica clave:** Esta lista puede ser **INFINITA**. Cada nicho genera múltiples organizaciones.

---

### Proceso Nocturno Completo (00:00 - 06:00)

#### 00:00 - Sistema arranca

1.  Docker lee Google Sheets "Nichos a explorar".
2.  Filtra: `Estado = "Pendiente"` AND `Prioridad = Alta/Media`.
3.  Selecciona **120 nichos** (10 por worker).
4.  Distribuye entre **12 workers**.
5.  Marca nichos como "En proceso".

#### 00:05 - Workers comienzan búsqueda autónoma

**Worker 1 recibe:**

- Nicho 001: "Asociaciones ecologistas Canarias"
- Nicho 013: "Cooperativas pesca artesanal"
- Nicho 025: "Fundaciones mayores dependencia"
- ... (10 nichos totales)

**Worker 1 ejecuta por cada nicho:**

**PASO 1: BÚSQUEDA DE ORGANIZACIONES (Google Search automatizado)**

- Busca en Google: `"asociación ecologista Canarias"`
- Extrae primeros **50 resultados orgánicos**.
- Filtra: Solo URLs `.org`, `.es`, `.com` con palabras clave relevantes.
- **Resultado ejemplo:**
  - `https://benmagec.org`
  - `https://terramare.es`
  - `https://wwfcanarias.org`
  - `https://seobirdlife.org/grupos-locales/canarias`
  - ... (20-30 organizaciones encontradas por nicho)

**PASO 2: SCRAPING DE CADA ORGANIZACIÓN**
Para cada URL encontrada:

1.  Entra en web.
2.  Busca secciones: "Equipo", "Contacto", "Quiénes somos", "Sobre nosotros".
3.  Extrae:
    - Nombres de personas & Cargos
    - Emails & Teléfonos
    - Texto descriptivo (500-1000 palabras)
4.  Captura screenshots.
5.  Identifica enlaces a redes sociales.

**PASO 3: ANÁLISIS PRELIMINAR CON IA LOCAL**
Envía texto extraído a API de Claude/ChatGPT:

> **Prompt:**
> "Analiza esta organización y extrae:
>
> 1. Descripción breve (50 palabras)
> 2. Actividad principal
> 3. Ámbito geográfico
> 4. Tres pain points comunicativos detectables (Falta de seguimiento, comunicación reactiva, etc).
>    Texto: [texto scrapeado]"

**PASO 4: CONSOLIDACIÓN DE RESULTADOS**
Worker 1 genera por cada nicho un registro tipo:

```json
{
  "nicho_id": "001",
  "nicho": "Asociaciones ecologistas Canarias",
  "organizacion": "Ben Magec",
  "url": "https://benmagec.org",
  "contactos": [
    {
      "nombre": "María González",
      "cargo": "Coordinadora Comunicación",
      "email": "comunicacion@benmagec.org",
      "telefono": "+34 922 xxx xxx"
    },
    {
      "nombre": "Juan Pérez",
      "cargo": "Presidente",
      "email": "presidencia@benmagec.org"
    }
  ],
  "descripcion": "ONG canaria defensa medio ambiente con 40 años trayectoria",
  "actividad_principal": "Conservación naturaleza y educación ambiental",
  "ambito": "Canarias (todas las islas)",
  "pain_points": [
    "Realizan 5-10 campañas anuales sin sistema medición impacto mediático",
    "Dependencia de alertas Google y seguimiento manual prensa",
    "Sin análisis sentimiento en redes sociales",
    "Comunicación basada en voluntarios sin formación específica",
    "Dificultad demostrar impacto ante financiadores"
  ],
  "redes_sociales": {
    "twitter": "@benmagec",
    "instagram": "@benmagec_ecologistas",
    "facebook": "benmagec.canarias"
  },
  "fecha_scraping": "2025-01-15 02:37:00",
  "worker": "Worker_1"
}
```

#### 03:00 - Workers a mitad de proceso

Progreso típico:

- **Total parcial:** 60 nichos → ~1.500 organizaciones → ~4.800 contactos.

#### 06:00 - Sistema consolida y reporta

**RESULTADO NOCTURNO TÍPICO:**

- **Nichos procesados:** 120
- **Organizaciones encontradas:** 2.847
- **Contactos extraídos:** 9.341
- **Pain points generados (IA):** 8.541

**Desglose por sector:**

- Asociaciones: 1.234 org → 4.127 contactos
- Empresas: 892 org → 2.876 contactos
- Colegios profesionales: 234 org → 1.203 contactos
- Fundaciones: 487 org → 1.135 contactos

---

### Enriquecimiento Automático Post-Scraping (06:00-08:00)

**Proceso n8n automático:**
Para cada organización con contactos:

1.  **Verifica duplicados** en `notas.can` (por email) → Marca: NUEVO / DUPLICADO / ACTUALIZACIÓN.
2.  **Enriquece pain points** con análisis cruzado:
    - Busca en Google News: "[organización] noticias recientes".
    - Analiza últimas 5 notas de prensa.
    - Consulta redes sociales (frecuencia, engagement).
    - Genera "perfil comunicativo" (Activo/Inactivo, Profesional/Amateur, Proactivo/Reactivo).
3.  **Asigna SCORING de prioridad comercial:**
    - **Alta:** Organizaciones activas sin seguimiento profesional.
    - **Media:** Organizaciones con potencial pero menor actividad.
    - **Baja:** Organizaciones inactivas o con seguimiento propio.
4.  **Categoriza automáticamente:** Sector, Subsector, Ámbito geográfico, Tamaño estimado.

**Resultado 08:00:** Hoja "Contactos Validados IA" con **9.341 registros enriquecidos**.

---

### Validación Humana Selectiva (08:00-10:00)

Andrea/Paula NO validan 9.000 contactos. Se usa validación por **muestreo estratificado**:

- **Scoring ALTO (1.200 contactos):** Validación **100% humana** (2 horas). Verifican emails, pain points, categorización.
- **Scoring MEDIO (4.500 contactos):** Validación **20% muestral** (30 minutos). Si muestra pasa → resto se aprueba.
- **Scoring BAJO (3.641 contactos):** Validación **10% muestral** (20 minutos). Quedan en "pool secundario".

**Resultado 10:00:** Total útil: **5.164 contactos listos para carga**.

---

### Carga y Disponibilidad (10:30)

- Andrea exporta 5.164 contactos validados a `notas.can`.
- **Estructura:** Sector > Subsector > Nicho específico | Pain points | Scoring | Perfil comunicativo.

---

## La Magia de la Microsegmentación Infinita

### Ejemplo Práctico

- **Nivel 1 - Sector:** Asociaciones
- **Nivel 2 - Subsector:** Ecologistas
- **Nivel 3 - Nicho (LO QUE ALIMENTA EL SISTEMA):**
  - Ecologistas → Conservación marina Canarias
  - Ecologistas → Energías renovables Gran Canaria
  - Ecologistas → Protección espacios naturales Tenerife
  - Ecologistas → Educación ambiental escolar
  - Ecologistas → Agricultura ecológica y sostenibilidad
  - Ecologistas → Gestión residuos y economía circular
  - ... (50+ nichos solo en este subsector)

**Resultado:** Un solo subsector genera **1.000-1.500 organizaciones** y **3.000-5.000 contactos**.

### Escalabilidad del Sistema

- **Input humano (2-3 horas/semana):** Definir 50-100 nichos nuevos (creatividad pura).
- **Output automatizado (5 noches):**
  - Nichos procesados: 600
  - Organizaciones: 10.000-15.000
  - **Contactos validados: 25.000-40.000/semana**

### Ventajas vs Propuesta Anterior

| Aspecto             | Mi propuesta (URLs específicas)   | Tu propuesta (Nichos)               |
| :------------------ | :-------------------------------- | :---------------------------------- |
| **Input humano**    | Identificar 50 organizaciones/día | Definir 50 nichos/semana            |
| **Escalabilidad**   | Limitada por capacidad humana     | **Ilimitada** (nichos infinitos)    |
| **Descubrimiento**  | Solo conocidas                    | **Encuentra organizaciones nuevas** |
| **Cobertura**       | Parcial                           | Cobertura total por microsegmentos  |
| **Mantenimiento**   | Continuo (buscar URLs)            | Bajo (nichos generan contenido)     |
| **Contactos/noche** | 200-400                           | **6.000-10.000**                    |

---

## Ejemplo de Campaña Ultra-Segmentada Resultante

**Nicho:** "Cooperativas agrícolas ecológicas Tenerife norte"
**Organizaciones:** Cooperativa Agroecológica Tacoronte, Asociación Productores Ecológicos Anaga, etc.

**Email resultante:**

> Asunto: ¿Cómo comunican su valor las cooperativas ecológicas que venden 3x más?
>
> Hola [Nombre],
> Analizamos 47 cooperativas agroecológicas en Canarias... el 73% dependen de mercados locales. Las 3 que crecieron tenían algo en común: seguimiento profesional de su impacto.
>
> Específicamente para [Cooperativa]:
>
> - Certificación ecológica = ventaja competitiva desaprovechada.
> - Sin datos de apariciones en "gastronomía km0".
>
> ¿15 minutos para ver cómo duplicaron distribución? [Reserva aquí]

**Tasa de conversión esperada:** 8-12% (vs 1-2% genérico).

---

## Implementación Técnica Simplificada

1.  **Google Sheets "Nichos"**: Andrea define microsegmentos.
2.  **Docker con modificación clave**:
    ```python
    # CAMBIO PRINCIPAL:
    # AHORA (nichos):
    input = lista_nichos_microsegmentos
    for nicho in input:
        urls = buscar_en_google(nicho.busqueda_sugerida, limit=50)
        urls_filtradas = filtrar_relevantes(urls, nicho.keywords)
        for url in urls_filtradas:
            datos = scrapear_organizacion(url)
            pain_points = analizar_con_ia(datos.texto) # Integración API Claude/ChatGPT local
            guardar_resultados(datos + pain_points)
    ```
3.  **Integración IA**: Análisis local durante scraping.
4.  **n8n para consolidación**: Recoge, elimina duplicados, enriquece y consolda.

**Timeline:**

- **Semana 1:** Modificar Docker + Primero 200 nichos + Piloto.
- **Semana 2:** Sistema completo 12 workers + Primera noche real.
- **Semana 3:** Producción estable (60k-80k contactos para el 15 Feb).

---

## ADENDA: Scoring Automático de Valor Potencial

Ya que estamos scrapeando, la IA puede asignar un **scoring de 0-10** que estime el valor comercial potencial.

- **Coste adicional:** CERO.
- **Valor estratégico:** PRIORIZACIÓN AUTOMÁTICA.

### Variables para el Scoring (Extracción + IA)

```python
scoring_variables = {
    # TAMAÑO ORGANIZACIONAL (30%)
    "presupuesto_anual": "extraer memorias/informes",
    "numero_empleados": "equipo/linkedin",
    "ambito_geografico": "local/regional/nacional",

    # ACTIVIDAD COMUNICATIVA (25%)
    "frecuencia_notas_prensa": "sección noticias",
    "presencia_medios": "google news",
    "redes_sociales": "followers/engagement",

    # MADUREZ DIGITAL (20%)
    "calidad_web": "diseño/actualización",
    "blog_activo": "posts recientes",

    # OTROS (25%)
    "tipo_financiacion": "público/privado",
    "sector_actividad": "potencial del sector"
}
```

### Dashboard Automático de Priorización (Reporte 08:00)

**=== SEGMENTACIÓN POR SCORING ===**

🔥 **PRIORIDAD MÁXIMA (Scoring 9-10):**

- Organizaciones: 187 | Contactos: 623
- Valor estimado: 140k-180k€/mes
- **Acción:** Validación 100% humana, propuesta Premium (1.5k-3k€/mes).

⭐ **PRIORIDAD ALTA (Scoring 7-8):**

- Organizaciones: 634 | Contactos: 2.107
- Valor estimado: 380k-570k€/mes
- **Acción:** Validación humana, propuesta Media (600-1.2k€/mes).

✓ **PRIORIDAD MEDIA (Scoring 5-6):**

- Organizaciones: 1.243
- **Acción:** Muestreo, producto Básico.

⊗ **SIN POTENCIAL (Scoring 0-2):**

- **Acción:** No contactar.

### Ventajas Estratégicas

1.  **Priorización inteligente:** Foco en los 623 contactos de alto valor (vs 9.000 totales). Conversión sube a 20-25%.
2.  **Desarrollo de productos:** Premium, Medio, Básico y Low-cost según scoring.
3.  **Forecasting financiero:** "Esta noche generamos 116k€/mes de pipeline realista".

### Coste Adicional

- 9.341 organizaciones x 0,003€ (API) = **28€/noche**.
- **ROI:** 28€ coste vs 116.000€ pipeline generado.
