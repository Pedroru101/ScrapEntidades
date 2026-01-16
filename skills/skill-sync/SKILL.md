---
name: skill-sync
description: >
  Sincroniza metadata de skills a las secciones Auto-invoke de GEMINI.md.
  Trigger: Después de crear o modificar skills.
license: MIT
metadata:
  author: ScrapEntidades
  version: "1.0"
  scope: [root]
  auto_invoke: "Después de crear/modificar una skill"
---

## Uso

```powershell
# Sincronizar todas las skills a archivos GEMINI.md
.\skills\skill-sync\assets\sync.ps1

# Modo prueba (muestra qué cambiaría)
.\skills\skill-sync\assets\sync.ps1 -DryRun
```

## Qué Hace

1. Lee todos los archivos `skills/*/SKILL.md`
2. Extrae `metadata.scope` y `metadata.auto_invoke`
3. Actualiza la tabla "Invocación Automática" en archivos `GEMINI.md` correspondientes

## Metadata Requerida

```yaml
metadata:
  scope: [root, src, scripts] # Qué GEMINI.md actualizar
  auto_invoke: "Descripción de la acción" # Texto del trigger
```

## Mapeo de Scopes

| Scope     | GEMINI.md Actualizado |
| --------- | --------------------- |
| `root`    | `./GEMINI.md`         |
| `src`     | `./src/GEMINI.md`     |
| `scripts` | `./scripts/GEMINI.md` |
| `tests`   | `./tests/GEMINI.md`   |
