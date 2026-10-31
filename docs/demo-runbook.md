# Runbook: demostrar distribución centralizada

**Duración:** 8–10 minutos
**Objetivo:** mostrar catálogo, bundles, dry-run, instalación, manifiesto y rollback sin modificar el Kiro real del presentador.

## Preparación

- Checkout limpio sobre un tag revisado.
- Python 3 disponible.
- Terminal con tamaño de fuente legible.
- `checks/validate.py` ejecutado previamente.
- Capturas del resultado esperado como contingencia.
- Ningún dato o configuración de cliente en el repositorio.

## Guion

### 1. Mostrar la fuente central — 1 minuto

Abre:

- `catalog.json`.
- `bundles/developer.json`.
- `bundles/qa.json`.

Explica que un bundle es una convención de distribución de este repositorio, no una función nativa de Kiro.

### 2. Mostrar las capas — 1 minuto

```text
Global: seguridad, calidad y flujo Dev + QA
Proyecto: arquitectura, comandos y producto
Spec: Historia de Usuario concreta
```

### 3. Crear un destino aislado — 30 segundos

```bash
TEMP_ROOT="$(mktemp -d)"
KIRO_HOME_DEMO="$TEMP_ROOT/.kiro"
```

Muestra el valor y confirma que no es `$HOME/.kiro`.

### 4. Ejecutar dry-run — 1 minuto

```bash
./tools/sync.sh --bundle qa --kiro-home "$KIRO_HOME_DEMO" --dry-run
```

Señala `ADD` y la ausencia de escrituras.

### 5. Aplicar — 1 minuto

```bash
./tools/sync.sh --bundle qa --kiro-home "$KIRO_HOME_DEMO" --apply
```

Anota el backup ID que imprime el comando.

### 6. Mostrar resultado — 2 minutos

```bash
find "$KIRO_HOME_DEMO/steering" "$KIRO_HOME_DEMO/skills" -type f -print
cat "$KIRO_HOME_DEMO/.standards-hub/manifest.json"
```

Explica que el manifiesto registra bundle, versión, fuentes, destinos y hashes.

### 7. Demostrar protección de archivos locales — 1 minuto

Describe, sin alterar la demo principal, que un archivo ya existente y no registrado produce `CONFLICT`. No fuerces la sobreescritura en vivo.

### 8. Rollback — 1 minuto

```bash
./tools/sync.sh --kiro-home "$KIRO_HOME_DEMO" --rollback latest
```

Confirma que los archivos instalados desaparecieron y que el destino real nunca cambió.

### 9. Conectar con la Historia de Usuario — 1 minuto

Abre el proyecto de la demo y muestra que su `.kiro/steering/` conserva arquitectura y comandos específicos. Después abre la Spec de la HU.

## Mensajes clave

- Centralizar no significa cargar todo en todos los equipos.
- El repositorio publica versiones; los usuarios no consumen `main` directamente.
- Steering global, Steering del proyecto y Spec tienen responsabilidades diferentes.
- Los Skills se reservan para procedimientos especializados.
- Instalar archivos no autoriza a ejecutar sus instrucciones sin revisión.

## Contingencias

| Fallo | Respuesta |
|---|---|
| Python no disponible | Mostrar salida preparada y continuar con la arquitectura |
| El dry-run no coincide | No aplicar; explicar que el comportamiento fail-closed protege el equipo |
| El apply falla | Mostrar el checkpoint preparado; no escribir en el Kiro real |
| Falta tiempo | Omitir la demostración de conflicto y conservar dry-run, apply y manifiesto |

## Cierre

Elimina el directorio temporal únicamente después de confirmar que contiene solo artefactos de esta demostración.
