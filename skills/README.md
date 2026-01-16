# Skills de Agente IA

Las skills proveen patrones específicos de dominio para asistentes de código IA.

## Configuración

```powershell
# Ejecutar desde la raíz del proyecto
.\skills\setup.ps1
```

## Skills Disponibles

| Skill             | Descripción                                |
| ----------------- | ------------------------------------------ |
| `scrap-entidades` | Patrones y arquitectura del proyecto       |
| `skill-creator`   | Crear nuevas skills siguiendo el estándar  |
| `skill-sync`      | Sincronizar metadata de skills a GEMINI.md |

## Agregar Nuevas Skills

1. Crear directorio: `skills/{nombre-skill}/`
2. Crear `SKILL.md` con frontmatter YAML
3. Ejecutar sync para actualizar archivos GEMINI.md
