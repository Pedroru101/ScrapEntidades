# Sistema ScrapEntidades - Documentación Completa

> **Última actualización:** 16 Enero 2026
> **Estado:** Alineado con requerimientos de Enrique

## Resumen Ejecutivo

Sistema de scraping distribuido enfocado en **Canarias** que extrae conocimiento profundo de organizaciones para decisiones comerciales a posteriori.

**Principio Fundamental:** Extraer TODO. No filtrar pensando "¿sirve para MMI?".

---

## Flujo del Sistema

```
1. INPUT: Lista de Nichos ("Cooperativas agrícolas Tenerife")
       ↓
2. SEARCHER: Busca URLs en Google → Cola Redis
       ↓
3. WORKER: Scraping + Filtro Canarias
       ↓
4. IA: Extracción Profunda (Retos, Financiación, Estructura)
       ↓
5. OUTPUT: Registro rico en Supabase
```

---

## Qué Extraemos (Conocimiento Profundo)

| Dimensión            | Ejemplos                                  | Fuente Web                        |
| -------------------- | ----------------------------------------- | --------------------------------- |
| **Actividades**      | Proyectos, servicios, qué hacen           | "Qué hacemos", "Proyectos"        |
| **Retos/Objetivos**  | "Ampliar base social", "Conseguir fondos" | "Plan estratégico", "Memorias"    |
| **Estructura**       | Nº empleados, delegaciones, voluntarios   | "Equipo", "Organización"          |
| **Financiación**     | Subvenciones, cuotas, ventas              | "Transparencia", "Memorias"       |
| **Colaboradores**    | Partners, redes, patrocinadores           | "Colaboradores", "Patrocinadores" |
| **Particularidades** | Premios, historia, reconocimientos        | "Quiénes somos"                   |

---

## Ejemplo de Output

```json
{
  "organizacion": "Ben Magec",
  "conocimiento_profundo": {
    "sector": "ONG ambiental",
    "actividades_principales": [
      "Campañas conservación espacios naturales",
      "Educación ambiental en centros escolares"
    ],
    "retos_objetivos": [
      "Ampliar red de voluntarios activos",
      "Conseguir más socios que financien actividades"
    ],
    "estructura_interna": [
      "23 trabajadores",
      "5 delegaciones insulares",
      "Red 400 voluntarios"
    ],
    "financiacion": [
      "30% cuotas socios (1.200 socios)",
      "50% subvenciones públicas",
      "20% fondos europeos"
    ]
  },
  "oportunidades_detectadas": {
    "productos_encajan": ["MMI", "Automatización gestión voluntarios"],
    "productos_no_encajan": ["Licitador (ya lo manejan internamente)"]
  }
}
```

---

## Productos Disponibles

1. **MMI:** Seguimiento de medios (para quienes comunican mucho).
2. **Automatizaciones:** CRM, gestión de socios/expedientes, emails.
3. **IA Contenidos:** Generación de posts, materiales educativos.
4. **Mentorías:** Estrategia, fondos europeos.
5. **Licitador:** Búsqueda de fondos públicos/concursos.

---

## Instrucciones para scraper

✅ Qué hacen (actividades, proyectos, servicios)
✅ Sus objetivos y retos
✅ Cómo se financian
✅ Tamaño y estructura
✅ Particularidades únicas
✅ Con quién colaboran
✅ Qué les preocupa (menciones en blog, memorias)

**No filtres pensando "esto no sirve para MMI".**
Extrae todo. Luego nosotros decidiremos qué producto encaja mejor.

---

## Arquitectura Técnica

| Componente  | Ubicación            | Rol                                 |
| ----------- | -------------------- | ----------------------------------- |
| Searcher    | `src/searcher.py`    | Nichos → URLs                       |
| Worker      | `src/worker.py`      | Scrape + Filtro + IA                |
| AI Analyzer | `src/ai_analyzer.py` | Extracción profunda                 |
| Models      | `src/models.py`      | Pydantic con `ConocimientoProfundo` |
| Config      | `src/config.py`      | Singleton, FAIL FAST                |
