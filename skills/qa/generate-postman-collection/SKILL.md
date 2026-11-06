---
name: generate-postman-collection
description: Genera una colección Postman compartible para exploración y reproducción rápida desde contratos aprobados, sin duplicar la regresión Karate del pipeline ni ejecutar Newman automáticamente.
---

# Generar colección Postman para exploración

## Propósito

Convertir casos de API aprobados en una colección compartible para exploración manual y reproducción rápida. Karate permanece como la única suite versionada de regresión en pipeline; esta Skill no duplica esos escenarios como otra suite ni ejecuta Postman por sí sola.

## Cuándo usarla

Úsala cuando QA necesite explorar un contrato, reproducir un comportamiento o compartir una solicitud sanitizada. No la uses para reemplazar la regresión Karate, inventar autenticación ni ejecutar contra un destino sin autorización.

## Políticas relacionadas

Aplica `steering/qa/test-automation-standards.md`, `steering/qa/black-box-test-automation.md` cuando exista handoff, y `steering/core/security.md`.

## Recursos incluidos

- [Colección completa y sintética](examples/credential-recovery.postman_collection.json)
- [Plantilla reutilizable de colección](templates/postman-collection.json)
- [Plantilla de environment sin secretos](templates/local.postman_environment.json)
- [Referencia de responsabilidades Postman y Karate](references/postman-and-karate-roles.md)
- [Validador estático de colección y environment](scripts/validate_postman_assets.py)

## Entradas obligatorias

- `qa-input/<HU>/user-story.md` y `qa-input/<HU>/test-plan.md`, aprobados.
- `qa-input/<HU>/api-spec/openapi.yaml` o contrato API versionado equivalente.
- `qa-input/<HU>/test-data/`, exclusivamente sintético.
- `qa-input/<HU>/deployment-context.json`, con ambiente, `BASE_URL`, build, commit y autorización.
- Casos elegidos para exploración o reproducción.
- Mecanismo de autenticación aprobado, si aplica, descrito sin valores secretos.

## Precondiciones y bloqueos

Confirma que HU, plan, API, datos y despliegue describen el mismo alcance. Verifica que la colección no se presente como otra regresión de pipeline. Método, path, headers funcionales, body y respuesta esperada MUST provenir del contrato aprobado.

Si falta un campo, hay contradicciones, el destino no está autorizado o la autenticación es ambigua, detente y lista el bloqueo. No copies tokens, cookies, credenciales ni una URL real.

## Procedimiento

1. Lee HU, plan, API, datos y contexto; registra versiones, build y commit.
2. Relaciona `caso → request → respuesta esperada → criterio` y marca brechas.
3. Confirma el rol del artefacto: exploración, reproducción rápida o intercambio sanitizado.
4. Busca el escenario equivalente en Karate y evita mantener dos suites de regresión; conserva la decisión en la descripción de la colección.
5. Crea `postman/credential-recovery.postman_collection.json` con Postman Collection v2.1 y carpetas por flujo.
6. Usa `{{BASE_URL}}` y paths relativos; no incrustes hosts de ambientes.
7. Incluye solo datos sintéticos y tests ligeros que ayuden a reproducir el comportamiento, sin afirmar certificación.
8. Genera un environment de plantilla con `NO_SUMINISTRADO`; no persistas secretos ni valores de sesión.
9. Valida ambos JSON con el script incluido, revisa el diff y entrega instrucciones de importación.
10. Si QA solicita Newman, prepara el comando y reportes, pero espera autorización antes de ejecutarlo.

## Archivos de salida

```text
postman/
├── credential-recovery.postman_collection.json
└── local.postman_environment.json
```

Una ejecución opcional posterior puede producir `build/postman/junit.xml` y `build/postman/report.html`; esos reportes no se generan durante esta Skill.

## Ejemplo de prompt

```text
Genera una colección Postman para reproducir CP-009 de recuperación de credenciales desde
la HU, el plan, OpenAPI, datos sintéticos y deployment-context.json. Usa BASE_URL,
crea un environment sin secretos y no dupliques la regresión Karate ni ejecutes Newman.
```

## Ejemplo de salida

```json
{
  "name": "CP-009 solicitar recuperación",
  "request": {
    "method": "POST",
    "url": "{{BASE_URL}}/credential-recovery"
  }
}
```

La [colección completa](examples/credential-recovery.postman_collection.json) usa un correo `.test` y explica su propósito exploratorio.

## Validación

Define `SKILL_DIR` como este directorio y ejecuta solo validación estática:

```bash
SKILL_DIR="${SKILL_DIR:?defina la ruta de generate-postman-collection}"
python3 "$SKILL_DIR/scripts/validate_postman_assets.py" \
  --collection postman/credential-recovery.postman_collection.json \
  --environment postman/local.postman_environment.json
git diff --check -- postman
```

Newman es opcional y posterior. Un comando aprobado puede generar JUnit y HTML con el reporter HTML ya fijado por el proyecto:

```bash
# NO EJECUTAR DURANTE LA GENERACIÓN
BASE_URL="${BASE_URL:?defina el destino autorizado}"
newman run postman/credential-recovery.postman_collection.json \
  -e postman/local.postman_environment.json \
  --env-var "BASE_URL=$BASE_URL" \
  --reporters cli,junit,html \
  --reporter-junit-export build/postman/junit.xml \
  --reporter-html-export build/postman/report.html
```

No instales un reporter durante la ejecución; el proyecto debe fijarlo y revisarlo previamente.

## Manejo de fallos

- **Contrato incompleto:** lista operación y caso; no deduzcas request o respuesta.
- **Duplicación con Karate:** conserva Postman como reproducción y deja la regresión en Karate.
- **Autenticación ausente:** no añadas headers ni ejecutes solicitudes.
- **Destino o build inconsistente:** bloquea Postman y Newman.
- **JSON inválido:** corrige solo la estructura generada y repite validación estática.
- **Environment con secreto:** elimina el valor, usa `NO_SUMINISTRADO` y solicita el proveedor seguro.
- **Newman no disponible:** entrega artefactos y comando; no instales dependencias sin aprobación.

## Límites y responsabilidades

- QA mantiene la colección para exploración y reproducción rápida.
- Karate conserva la regresión versionada que corre en pipeline.
- El owner de API mantiene contrato y autenticación.
- Postman no ejecuta la colección por el hecho de generarla o importarla.
- No despliegues, modifiques la API ni amplíes acceso de red.
- No almacenes secretos, tokens, cookies, credenciales, datos reales ni URLs sensibles.
- Una colección válida o un reporte Newman no certifican por sí solos la HU.
