# Asegurar adopción en computadores y proyectos

Centralizar activos no garantiza que estén instalados. La garantía requiere distribución, evidencia y una comprobación periódica.

## Nivel 1: baseline global por computador

Instala el bundle aprobado en el KIRO_HOME de cada persona:

```text
~/.kiro/steering/
~/.kiro/skills/
~/.kiro/.standards-hub/manifest.json
```

El manifiesto registra bundle, versión, archivos y hashes. Una herramienta corporativa de administración de equipos puede distribuir una release aprobada y verificar ese manifiesto. Este repositorio no administra dispositivos.

Validación local:

```bash
./tools/sync.sh \
  --bundle developer \
  --kiro-home "$HOME/.kiro" \
  --verify
```

La comprobación falla si la versión, el bundle o cualquier archivo administrado no coincide con el checkout central utilizado.

## Nivel 2: baseline versionado por proyecto

Cuando el proyecto necesita auditoría reproducible, instala el bundle dentro del workspace y versiona los activos administrados:

```bash
PROJECT_ROOT="/ruta/absoluta/al/proyecto"

./tools/sync.sh \
  --bundle developer \
  --kiro-home "$PROJECT_ROOT/.kiro" \
  --dry-run

./tools/sync.sh \
  --bundle developer \
  --kiro-home "$PROJECT_ROOT/.kiro" \
  --apply
```

Recomendaciones:

- Versiona los Steering, Skills y `.kiro/.standards-hub/manifest.json`.
- Excluye `.kiro/.standards-hub/backups/` del repositorio de la aplicación.
- Ejecuta `--verify` en CI usando exactamente el tag central registrado en el manifiesto.
- Actualiza mediante un pull request generado desde una nueva release; no edites las copias administradas directamente.
- Mantén producto, arquitectura, comandos y Specs propios junto a la aplicación.

## Modelo híbrido recomendado

```text
Baseline global
  Seguridad y reglas comunes disponibles en todo workspace

Baseline por proyecto
  Versión exacta y comprobable para proyectos que lo requieren

Steering local del proyecto
  Arquitectura, producto, stack y comandos

Spec
  Requisitos, diseño y tareas de una Historia de Usuario
```

## Qué puede garantizar cada control

| Control | Garantiza | No garantiza |
|---|---|---|
| Repositorio central | Fuente oficial y auditable | Instalación en cada PC |
| Distribución administrada | Presencia de una versión en un PC | Que un proyecto fije esa versión |
| Manifiesto local | Bundle, versión y hashes instalados | Calidad semántica de las reglas |
| `--verify` | Coincidencia con el checkout central | Que una persona siga correctamente las reglas |
| Copia versionada en `.kiro/` | Configuración reproducible del proyecto | Actualización automática |
| CI | Presencia e integridad en el repositorio | Estado del KIRO_HOME personal |

## Incorporación de proyectos

1. Clasifica el proyecto y selecciona un bundle.
2. Fija una versión estable del repositorio central.
3. Ejecuta dry-run.
4. Revisa conflictos con Steering o Skills existentes.
5. Instala globalmente o en el workspace según la exigencia.
6. Añade contexto específico del proyecto.
7. Ejecuta `--verify`.
8. Registra owner y estrategia de actualización.

No conectes los proyectos directamente a `main`, no sobrescribas personalizaciones silenciosamente y no uses symlinks que dependan de disponibilidad de red.
