# Kiro Standards Hub

Repositorio de referencia para versionar y distribuir un conjunto pequeño de Steering y Skills compartidos entre equipos de desarrollo y calidad.

## Qué resuelve

- Mantiene estándares comunes en una única fuente versionada.
- Distribuye estándares de proyecto mediante bundles de workspace y comportamiento personal mediante perfiles por rol.
- Muestra cambios antes de instalar activos de workspace.
- Evita sobrescribir archivos locales que esta herramienta no administra.
- Crea respaldos y permite revertir la última instalación.
- Separa reglas organizacionales, comportamiento por rol y contexto específico de cada aplicación.

## Qué es nativo de Kiro

Kiro reconoce:

- Steering de workspace en `.kiro/steering/` y Steering global en `~/.kiro/steering/`.
- Skills portables que empaquetan instrucciones y recursos reutilizables.
- Configuración por capas, donde el contexto más específico complementa o prevalece sobre el más general.
- Steering con inclusión `manual` o `auto`; ambos aparecen como comandos y `auto` puede activarse cuando la solicitud coincide con su descripción.

Fuentes oficiales:

- [Steering](https://kiro.dev/docs/steering/)
- [Agent Skills](https://kiro.dev/docs/skills/)
- [Configuration scopes](https://kiro.dev/docs/configuration/)
- [Slash commands](https://kiro.dev/docs/ide/chat/slash-commands/)

El contenido de esas páginas se resume y reformula aquí.

## Qué agrega este repositorio

`catalog.json`, `bundles/`, `profiles/`, `tools/` y `checks/` son convenciones de este proyecto. No son funciones nativas llamadas “bundles”, “profiles” o “Standards Hub” dentro de Kiro. Las Skills de Selenium, Karate y JMeter son assets versionados que describen procedimientos; Kiro no incorpora esas herramientas ni produce su evidencia de ejecución por el solo hecho de instalar el bundle.

```text
Release central revisada
        ├── bundle de workspace ──→ <repo>/.kiro/ mediante pull request
        └── perfil por rol ───────→ ~/.kiro/steering/ para una persona

<repo>/.kiro/ + perfil personal + Spec de la Historia de Usuario
                            ↓
                           Kiro
```

## Estructura

```text
.
├── catalog.json
├── steering/
│   ├── core/
│   ├── development/
│   └── qa/
├── skills/
│   ├── development/
│   ├── qa/
│   ├── shared/
│   └── performance/
├── profiles/
│   ├── development/steering/
│   └── qa/steering/
├── bundles/
│   ├── common.json
│   ├── developer.json
│   └── qa.json
├── tools/
│   ├── sync.py
│   ├── sync.sh
│   └── sync.ps1
├── checks/
│   └── validate.py
└── docs/
```

## Alcance y destino

| Fuente | Alcance | Destino | Instalación |
|---|---|---|---|
| `steering/core/`, `steering/development/`, `steering/qa/` y Skills seleccionados por los bundles | Workspace; aplica a toda persona que abre el proyecto | `<repo>/.kiro/` | Release revisada mediante pull request en el repositorio consumidor |
| `profiles/development/` | Usuario que actúa como Development | `~/.kiro/steering/` | Solo en el perfil Development; nunca en el repositorio de la aplicación |
| `profiles/qa/` | Usuario que actúa como QA | `~/.kiro/steering/` | Solo en el perfil QA; nunca en el repositorio de la aplicación |

Los hechos del producto y del proyecto permanecen en el workspace. El comportamiento que depende de la persona o de su rol permanece en el perfil. Un procedimiento puntual y reutilizable puede ser un Skill.

Los perfiles no forman parte de `catalog.json`, no se incluyen en bundles y no los instala `tools/sync.py`. Una persona con doble rol debe usar perfiles o configuraciones separadas, o conservar inclusión manual y activar un solo rol por sesión. Nunca debe instalar dos Steering contradictorios con inclusión `auto` en la misma configuración.

Steering guía a Kiro, pero no es un control de acceso. Los permisos del repositorio, protección de ramas, ownership y revisiones obligatorias deben aplicar los límites reales.

Consulta [docs/scopes-and-profiles.md](docs/scopes-and-profiles.md) para el modelo completo y el flujo QA diagnóstico → handoff → Development corrección.

## Bundles disponibles

Todos los bundles son assets de workspace y se instalan en `<repo>/.kiro/`.

| Bundle | Contenido |
|---|---|
| `common` | Seguridad, calidad de ingeniería y flujo Dev + QA |
| `developer` | `common`, estándares de desarrollo, testabilidad UI, preparación de handoff y trazabilidad |
| `qa` | `common`, automatización de caja negra, generación Selenium y Karate, trazabilidad y las tres Skills de performance |

## Skills operativos del catálogo

Cada `SKILL.md` define entradas, bloqueos, pasos, rutas de salida, ejemplos, validación finita, manejo de fallos y responsabilidades. El catálogo incluye:

| Skill | Resultado preparado |
|---|---|
| `prepare-qa-handoff` | Contrato `ui-selectors.json`, contexto del pipeline, datos sintéticos y limitaciones para QA |
| `test-plan-traceability` | Transcripción aprobada, brechas y matriz; no elige una herramienta automáticamente |
| `generate-selenium-tests` | Java 21/JUnit 5 para E2E web, compilado antes de cualquier ejecución remota autorizada |
| `generate-karate-tests` | Features Karate y runner JUnit para la única suite versionada de regresión API |
| `create-performance-plan` | Plan con carga y umbrales trazados a fuentes aprobadas |
| `generate-jmeter-project` | JMX parametrizado y checklist, sin enviar tráfico |
| `analyze-jmeter-report` | Análisis de JTL, `errorCount`, criterios y observabilidad de un run terminado |

Las Skills preparan artefactos o analizan evidencia existente. La autorización de ejecución y la certificación permanecen en las personas y herramientas responsables.

Las Specs nunca se distribuyen desde este repositorio. Pertenecen a una Historia de Usuario y a un proyecto concretos.

## Requisitos

- Python 3.10 o posterior, sin paquetes externos.
- Checkout local de una versión revisada de este repositorio.
- Ruta de destino explícita.
- Permiso de escritura sobre el destino.

El sincronizador no descarga ni ejecuta contenido remoto.

## Demostración segura en un directorio temporal

```bash
TEMP_ROOT="$(mktemp -d)"
KIRO_HOME_DEMO="$TEMP_ROOT/.kiro"

./tools/sync.sh \
  --bundle qa \
  --kiro-home "$KIRO_HOME_DEMO" \
  --dry-run

./tools/sync.sh \
  --bundle qa \
  --kiro-home "$KIRO_HOME_DEMO" \
  --apply

cat "$KIRO_HOME_DEMO/.standards-hub/manifest.json"

./tools/sync.sh \
  --kiro-home "$KIRO_HOME_DEMO" \
  --rollback latest
```

La demostración no modifica la configuración real de Kiro.

## Instalación deliberada en un workspace

Primero fija y revisa una versión o tag. Después apunta `--kiro-home` al `.kiro` del proyecto y ejecuta un dry-run:

```bash
PROJECT_ROOT="/ruta/absoluta/al/proyecto"

./tools/sync.sh \
  --bundle developer \
  --kiro-home "$PROJECT_ROOT/.kiro" \
  --dry-run
```

Después de revisar el resultado, aplica la instalación y presenta los archivos administrados mediante un pull request del proyecto consumidor:

```bash
./tools/sync.sh \
  --bundle developer \
  --kiro-home "$PROJECT_ROOT/.kiro" \
  --apply
```

En Windows utiliza `tools/sync.ps1` con los mismos argumentos. No uses este sincronizador para copiar perfiles globales.

## Distribución de perfiles por rol

La distribución administrada debe copiar exactamente el archivo del rol correspondiente:

```text
profiles/development/steering/dev-bug-resolution.md
    → ~/.kiro/steering/dev-bug-resolution.md

profiles/qa/steering/qa-bug-investigation.md
    → ~/.kiro/steering/qa-bug-investigation.md
```

Ambos perfiles usan inclusión manual para que el rol se seleccione de forma explícita durante un bugfix. Estos archivos no se copian a `.kiro/` de una aplicación.

## Comportamiento seguro del sincronizador

- `--dry-run` es el comportamiento predeterminado.
- `--apply` es obligatorio para escribir.
- `--kiro-home` debe ser una ruta absoluta y su padre debe existir.
- Rechaza `/`, el home del usuario, este repositorio y rutas con symlinks.
- Rechaza archivos de destino que no estén registrados como administrados.
- No cambia de bundle sobre un mismo destino de forma implícita.
- Cada aplicación crea un backup y un manifiesto con hashes SHA-256.
- El rollback se niega a sobrescribir un archivo modificado después de instalarlo.
- `--verify` falla si el bundle, la versión o cualquier hash no coincide.
- Nunca ejecuta el contenido de un Skill.

## Contexto que debe permanecer en cada proyecto

Cada aplicación debería conservar información propia en su repositorio:

```text
proyecto/.kiro/steering/
├── product-context.md
├── project-structure.md
├── technology-stack.md
└── test-commands.md
```

Esta información cambia junto con el código y no debe instalarse como perfil global.

## Asegurar adopción en proyectos y perfiles

El repositorio central por sí solo no garantiza instalación. Cada proyecto adopta un bundle en `<repo>/.kiro/` mediante una release revisada y un pull request. La administración de equipos distribuye por separado un único perfil personal a `~/.kiro/steering/` según el rol.

Las actualizaciones de workspace siguen este flujo:

```text
Release central inmutable
→ pull request de actualización en el proyecto consumidor
→ revisión del diff y del manifiesto
→ validación
→ merge
```

No se recomienda una sincronización manual diaria ni consumir `main` directamente. Consulta [docs/adoption.md](docs/adoption.md) para las garantías de cada control y el proceso de incorporación.

## Validación

```bash
python3 checks/validate.py
```

El validador revisa JSON, bundles, herencia, fuentes, destinos, frontmatter, perfiles, symlinks, rutas personales y patrones básicos de secretos o instrucciones peligrosas. Para cada Skill exige la estructura operativa mínima, pasos numerados, ejemplos, comandos finitos, una prohibición explícita de almacenar secretos y ausencia de afirmaciones de ejecución o certificación autónoma. También comprueba que todas las Skills estén catalogadas y que los perfiles no entren en los bundles. No ejecuta Skills.

## Gobierno y publicación

Consulta [docs/governance.md](docs/governance.md). Nunca distribuyas directamente desde `main`; publica un tag inmutable después de revisión y validación.

## Demostración

Consulta [docs/demo-runbook.md](docs/demo-runbook.md) para un recorrido de ocho a diez minutos usando exclusivamente un KIRO_HOME temporal.

## Licencia

Este repositorio no declara una licencia pública. Su existencia en un repositorio privado no concede permiso para redistribuirlo. Define ownership y licencia antes de compartirlo fuera de la organización autorizada.
