---
name: skill-creator
description: >
  Crea nuevas skills de agente IA siguiendo el estándar agentskills.io.
  Trigger: Cuando el usuario pide crear una nueva skill.
license: MIT
metadata:
  author: ScrapEntidades
  version: "1.0"
  scope: [root]
  auto_invoke: "Crear nuevas skills"
---

## Estructura de una Skill

```
skills/{nombre-skill}/
├── SKILL.md      # Requerido - Archivo principal
├── assets/       # Opcional - Plantillas, scripts
└── references/   # Opcional - Links a docs locales
```

## Plantilla SKILL.md

````markdown
---
name: { nombre-skill }
description: >
  {Qué hace la skill}.
  Trigger: {Cuándo invocar esta skill}.
license: MIT
metadata:
  author: { organizacion }
  version: "1.0"
  scope: [{ root|src|scripts|tests }]
  auto_invoke: "{Acción que dispara}"
---

## Patrones Críticos

### Nombre del Patrón

- SIEMPRE: {Regla}
- NUNCA: {Prohibición}

## Comandos

```bash
{comandos relevantes}
```
````

```

## Campos Requeridos en Frontmatter

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `name` | minúsculas-con-guiones | `scrap-entidades` |
| `description` | Qué + Trigger | `Skill principal. Trigger: dev` |
| `metadata.scope` | Dónde aplica | `[root, src, scripts]` |
| `metadata.auto_invoke` | Disparador | `Crear scrapers` |

## Convenciones de Nombres

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Proyecto | `{proyecto}` | `scrap-entidades` |
| Componente | `{proyecto}-{comp}` | `scrap-entidades-worker` |
| Test | `{proyecto}-test` | `scrap-entidades-test` |
```
