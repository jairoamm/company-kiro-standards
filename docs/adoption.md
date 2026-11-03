# Asegurar adopción en proyectos y perfiles

Centralizar activos no garantiza que estén instalados. La garantía requiere distribución, evidencia y una comprobación periódica en cada alcance.

## Nivel 1: baseline versionado por proyecto

Instala el bundle aprobado dentro del workspace y versiona los activos administrados:

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

El destino contiene:

```text
<repo>/.kiro/steering/
<repo>/.kiro/skills/
<repo>/.kiro/.standards-hub/manifest.json
```

Recomendaciones:

- Versiona los Steering, Skills y `.kiro/.standards-hub/manifest.json`.
- Excluye `.kiro/.standards-hub/backups/` del repositorio de la aplicación.
- Ejecuta `--verify` en CI usando exactamente el tag central registrado en el manifiesto.
- Actualiza mediante un pull request generado desde una nueva release; no edites las copias administradas directamente.
- Mantén producto, arquitectura, comandos y Specs propios junto a la aplicación.

Validación del workspace:

```bash
./tools/sync.sh \
  --bundle developer \
  --kiro-home "$PROJECT_ROOT/.kiro" \
  --verify
```

## Nivel 2: perfil global por persona

Una herramienta corporativa de administración de equipos puede distribuir a `~/.kiro/steering/` únicamente el perfil correspondiente a la persona:

```text
Development → dev-bug-resolution.md
QA          → qa-bug-investigation.md
```

Los perfiles no se instalan con los bundles ni se versionan en el repositorio de la aplicación. Una persona con doble rol debe usar perfiles o configuraciones separadas, o mantener la inclusión manual y activar un solo perfil por sesión. No debe recibir dos perfiles contradictorios con inclusión automática.

La distribución del perfil demuestra presencia en un computador, pero no reemplaza permisos del repositorio ni protección de ramas.

## Flujo de actualización del workspace

```text
Cambio central revisado
→ release o tag inmutable
→ pull request en el proyecto consumidor
→ revisión del diff administrado y del manifiesto
→ gates del proyecto
→ merge
```

No sincronices manualmente cada día ni conectes un proyecto consumidor a `main`. La persona que mantiene el proyecto selecciona una release, ejecuta primero el dry-run y presenta la actualización para revisión.

## Modelo recomendado

```text
Workspace versionado
  Estándares y Skills del bundle para toda persona que abre el proyecto

Perfil global por rol
  Comportamiento personal de QA o Development

Steering local del proyecto
  Arquitectura, producto, stack y comandos

Spec
  Requisitos, diseño y tareas de una Historia de Usuario o bug
```

## Qué puede garantizar cada control

| Control | Garantiza | No garantiza |
|---|---|---|
| Repositorio central | Fuente oficial y auditable | Instalación en un proyecto o computador |
| Copia versionada en `.kiro/` | Configuración reproducible del proyecto | Comportamiento diferente por persona |
| Manifiesto del workspace | Bundle, versión y hashes instalados | Calidad semántica de las reglas |
| `--verify` en CI | Coincidencia con el checkout central | Que una persona siga correctamente las reglas |
| Distribución del perfil | Presencia del Steering asignado en `~/.kiro/` | Permisos o bloqueo técnico de acciones |
| Protección de ramas y revisiones | Control técnico del cambio aceptado | Activación correcta del perfil de Kiro |

## Incorporación de proyectos

1. Clasifica el proyecto y selecciona un bundle de workspace.
2. Fija una versión estable del repositorio central.
3. Ejecuta dry-run contra `<repo>/.kiro/`.
4. Revisa conflictos con Steering o Skills existentes.
5. Instala el bundle y presenta el cambio mediante pull request.
6. Añade contexto específico del proyecto.
7. Ejecuta `--verify`.
8. Distribuye por separado el perfil global que corresponda a cada persona.
9. Registra owners y estrategias de actualización para ambos alcances.

No conectes los proyectos directamente a `main`, no sobrescribas personalizaciones silenciosamente y no uses symlinks que dependan de disponibilidad de red.
