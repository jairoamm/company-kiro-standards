# Kiro Standards Hub

Repositorio de referencia para versionar y distribuir un conjunto pequeño de Steering y Skills compartidos entre equipos de desarrollo y calidad.

## Qué resuelve

- Mantiene estándares comunes en una única fuente versionada.
- Distribuye solo los activos apropiados para cada rol mediante bundles.
- Muestra cambios antes de instalarlos.
- Evita sobrescribir archivos locales que esta herramienta no administra.
- Crea respaldos y permite revertir la última instalación.
- Separa reglas organizacionales de contexto específico de cada aplicación.

## Qué es nativo de Kiro

Kiro reconoce:

- Steering de workspace en `.kiro/steering/` y Steering global en `~/.kiro/steering/`.
- Skills portables que empaquetan instrucciones y recursos reutilizables.
- Configuración por capas, donde el contexto más específico complementa o prevalece sobre el más general.

Fuentes oficiales:

- [Steering](https://kiro.dev/docs/steering/)
- [Agent Skills](https://kiro.dev/docs/skills/)
- [Configuration scopes](https://kiro.dev/docs/configuration/)

El contenido de esas páginas se resume y reformula aquí.

## Qué agrega este repositorio

`catalog.json`, `bundles/`, `tools/` y `checks/` son convenciones de este proyecto. No son funciones nativas llamadas “bundles” o “Standards Hub” dentro de Kiro.

```text
Repositorio central versionado
        ↓
Bundle common, developer o qa
        ↓
Dry-run y revisión
        ↓
Instalación en KIRO_HOME
        +
Steering específico del proyecto
        +
Spec específica de la Historia de Usuario
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
│   └── performance/
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

## Bundles disponibles

| Bundle | Contenido |
|---|---|
| `common` | Seguridad, calidad de ingeniería y flujo Dev + QA |
| `developer` | `common` más estándares de desarrollo |
| `qa` | `common`, automatización y tres Skills de performance |

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

## Instalación global deliberada

Primero fija y revisa una versión o tag. Después ejecuta siempre un dry-run:

```bash
./tools/sync.sh \
  --bundle developer \
  --kiro-home "$HOME/.kiro" \
  --dry-run
```

Solo después de revisar el resultado:

```bash
./tools/sync.sh \
  --bundle developer \
  --kiro-home "$HOME/.kiro" \
  --apply
```

En Windows utiliza `tools/sync.ps1` con los mismos argumentos.

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

Esta información cambia junto con el código y no debe instalarse globalmente.

## Asegurar adopción en computadores y proyectos

El repositorio central por sí solo no garantiza instalación. Usa el manifiesto y `--verify` para comprobar el baseline global de cada computador; en proyectos que exigen una versión auditable, instala también el bundle en `<proyecto>/.kiro`, versiona los activos y comprueba sus hashes en CI.

Consulta [docs/adoption.md](docs/adoption.md) para el modelo híbrido, las garantías de cada control y el proceso de incorporación.

## Validación

```bash
python3 checks/validate.py
```

El validador revisa JSON, bundles, herencia, fuentes, destinos, frontmatter, symlinks, rutas personales y patrones básicos de secretos o instrucciones peligrosas. No ejecuta Skills.

## Gobierno y publicación

Consulta [docs/governance.md](docs/governance.md). Nunca distribuyas directamente desde `main`; publica un tag inmutable después de revisión y validación.

## Demostración

Consulta [docs/demo-runbook.md](docs/demo-runbook.md) para un recorrido de ocho a diez minutos usando exclusivamente un KIRO_HOME temporal.

## Licencia

Este repositorio no declara una licencia pública. Su existencia en un repositorio privado no concede permiso para redistribuirlo. Define ownership y licencia antes de compartirlo fuera de la organización autorizada.
