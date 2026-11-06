---
name: prepare-qa-handoff
description: Prepara un handoff verificable de Desarrollo hacia QA con selectores, datos sintéticos, contexto del pipeline y limitaciones. Úsalo al entregar un build a Testing.
---

# Preparar handoff para QA

## Propósito

Empaquetar la información que QA necesita para validar una interfaz sin depender del repositorio de Desarrollo. El handoff identifica implementación, estados observables y build desplegado; no crea Selenium ni certifica la entrega.

## Cuándo usarla

Úsala después de validar una HU con interfaz, antes de entregar un build o cuando cambia un selector publicado. No la uses para desplegar, iniciar servicios, ejecutar pruebas remotas ni investigar defectos.

## Políticas relacionadas

Aplica `steering/development/ui-testability.md`, `steering/core/dev-qa-workflow.md`, `steering/core/security.md` y `steering/core/engineering-quality.md`.

## Recursos incluidos

- [Handoff sintético completo de HU-DEMO-001](examples/qa-handoff/HU-DEMO-001/README.md)
- [README del paquete como plantilla](templates/README.md)
- [Contexto de despliegue como plantilla](templates/deployment-context.json)
- [Contrato de selectores como plantilla](templates/ui-selectors.json)
- [Limitaciones conocidas como plantilla](templates/known-limitations.md)
- [Guía de datos y fixture como plantillas](templates/test-data/README.md)

## Entradas obligatorias

- `product/<HU>/user-story.md` y plan QA aprobado o su referencia.
- Frontend del commit entregable y resultados de gates locales.
- Evidencia del pipeline con ambiente, `BASE_URL`, `buildId`, `applicationCommit` y referencia de ejecución.
- Datos completamente sintéticos, preparación y limpieza.
- Limitaciones y criterios implementados.

URL, build y commit MUST provenir del pipeline que desplegó la entrega; no se calculan ni se inventan.

## Precondiciones y bloqueos

Confirma mismo alcance entre HU y plan, commit abierto igual al reportado, gates terminados, selectores presentes y despliegue correcto. Si falta despliegue, prepara un paquete con estado `pendiente` y campos `NO_SUMINISTRADO`, pero no lo declares listo.

## Procedimiento

1. Relaciona `criterio → caso → control o estado observable`.
2. Prefiere roles, nombres y etiquetas accesibles; usa `data-testid` solo sin semántica estable.
3. Crea `ui-selectors.json` con versiones, HU y selectores trazables.
4. Incluye nombre, pantalla, estado, estrategia, valor, casos y nombre accesible cuando aplique.
5. Compara con la versión anterior; un cambio incompatible exige versión mayor y migración.
6. Verifica estáticamente cada selector en el commit entregable y documenta estados condicionales.
7. Copia contexto desde evidencia del pipeline; usa `BASE_URL` como variable y no persistas su valor.
8. Añade datos sintéticos mínimos, aislamiento, caducidad y limpieza.
9. Registra riesgos, exclusiones y restricciones en `known-limitations.md`.
10. Genera README con estado, gates, árbol, versión y enlaces relativos.
11. Revisa diff, JSON y gates finitos; presenta el paquete a QA.

## Archivos de salida

```text
qa-handoff/<HU>/
├── README.md
├── deployment-context.json
├── ui-selectors.json
├── known-limitations.md
└── test-data/
    ├── README.md
    └── cp-004.json
```

Consulta el [árbol completo de ejemplo](examples/qa-handoff/HU-DEMO-001/README.md). El contexto no contiene credenciales y queda pendiente mientras falte evidencia.

## Ejemplo de prompt

```text
Prepara el handoff de HU-DEMO-001 con el plan, el frontend actual y la evidencia del
pipeline. Incluye CP-004, datos sintéticos y limitaciones. No generes Selenium, no
despliegues y usa NO_SUMINISTRADO para cualquier dato sin evidencia.
```

## Ejemplo de salida

```text
qa-handoff/HU-DEMO-001/
├── README.md
├── deployment-context.json
├── ui-selectors.json
├── known-limitations.md
└── test-data/cp-004.json
```

El README declara el estado. `pendiente` o `bloqueado` nunca se presenta como listo.

## Validación

Usa comandos locales y finitos, sin iniciar la aplicación:

```bash
HU="${HU:?defina HU}"
python3 -m json.tool "qa-handoff/$HU/ui-selectors.json" >/dev/null
python3 -m json.tool "qa-handoff/$HU/deployment-context.json" >/dev/null
git diff --check -- "qa-handoff/$HU"
npm test -- --run
```

Sustituye el último comando por el gate finito ya documentado si el proyecto usa otra herramienta.

## Manejo de fallos

- **Pipeline ausente:** conserva estado pendiente y enumera campos faltantes.
- **Commit distinto:** detente y solicita despliegue o evidencia correcta.
- **Selector inexistente:** corrige frontend o retira la entrada; no publiques un contrato falso.
- **Cambio incompatible:** incrementa versión mayor y documenta migración.
- **Gate fallido:** reporta comando y error; no entregues como aprobado.
- **Dato no sintético o secreto:** exclúyelo y solicita reemplazo.

## Límites y responsabilidades

- Desarrollo mantiene frontend, pruebas locales y contrato de selectores.
- El pipeline aporta destino autorizado, build, commit y referencia.
- QA mantiene Selenium, ejecución independiente y certificación.
- No generes, modifiques ni ejecutes Selenium en este procedimiento.
- No despliegues, inicies servicios ni cambies ambientes.
- No almacenes secretos, tokens, cookies, datos reales ni URLs sensibles.
- Un handoff completo habilita a QA; no aprueba por sí mismo la HU.
